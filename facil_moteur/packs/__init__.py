"""Packs pays de Facil Finance — chargement, validation, signature, résolution des couches.

Spécification : projet_doc/specs/pack-pays.md (ADR 0006). Un pack est un DOSSIER de données
versionné, signé et daté par exercice ; le moteur ne contient aucune règle propre à un pays.

Couches (la plus spécifique gagne, chaque surcharge est tracée) :
    ohada/<version>  ←  cemac | uemoa/<version>  ←  <PAYS>/<version>

Fichiers d'un pack (tous facultatifs sauf pack.yaml) :
    pack.yaml                        manifeste
    correspondances/comptes.json     règles « préfixe de compte → poste (REF) », plus long préfixe gagnant
    correspondances/sn.json          lignes du formulaire SN → expression de postes / comptes
    correspondances/smt.json         idem pour le système minimal de trésorerie
    fiscal/parametres.json           taux, seuils, barèmes — CHACUN avec son article et sa source
    libelles/<langue>.json           libellés officiels
    controles.json                   contrôles propres à la couche
    declencheurs.json                quand une note extra-comptable est exigée
    gabarits/*.xlsx                  formulaires officiels vierges
    SOURCES.md, CHANGELOG.md         traçabilité
    SIGNATURE                        empreintes SHA-256 de chaque fichier + signature Ed25519
"""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# -- référentiels (listes fermées : on choisit, on ne saisit pas) -------------------------------
ETATS_OHADA = {
    "BJ": "Bénin", "BF": "Burkina Faso", "CI": "Côte d'Ivoire", "GW": "Guinée-Bissau", "ML": "Mali",
    "NE": "Niger", "SN": "Sénégal", "TG": "Togo",                                    # UEMOA
    "CM": "Cameroun", "CF": "Centrafrique", "CG": "Congo", "GA": "Gabon", "GQ": "Guinée équatoriale",
    "TD": "Tchad",                                                                    # CEMAC
    "GN": "Guinée", "KM": "Comores", "CD": "RD Congo",                                # hors zone
}
ZONES = {
    "uemoa": {"BJ", "BF", "CI", "GW", "ML", "NE", "SN", "TG"},
    "cemac": {"CM", "CF", "CG", "GA", "GQ", "TD"},
}
COUCHES_COMMUNES = {"ohada", *ZONES}
MONNAIES = {"XOF", "XAF", "GNF", "KMF", "CDF", "USD"}          # ISO 4217
LANGUES = {"fr", "es", "pt", "en"}
SYSTEMES = {"SN", "SMT"}
STATUTS = ("brouillon", "valide", "publie", "retire")
_VERSION = re.compile(r"^\d{4}\.\d+$")
FICHIERS_DE_DONNEES = ("correspondances/comptes.json", "correspondances/sn.json", "correspondances/smt.json",
                       "fiscal/parametres.json", "controles.json", "declencheurs.json")


@dataclass
class Anomalie:
    niveau: str          # « erreur » bloque ; « avertissement » se lit
    code: str
    message: str

    def __str__(self) -> str:
        return f"[{self.niveau}] {self.code} — {self.message}"


@dataclass
class Pack:
    dossier: Path
    manifeste: dict

    @property
    def ident(self) -> str:
        return f"{self.dossier.parent.name}/{self.dossier.name}"

    @property
    def couche(self) -> str:
        return self.dossier.parent.name

    def json(self, rel: str) -> dict | list | None:
        f = self.dossier / rel
        return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None


def charger(dossier: Path) -> Pack:
    dossier = Path(dossier)
    f = dossier / "pack.yaml"
    if not f.exists():
        raise FileNotFoundError(f"pack sans manifeste : {f}")
    return Pack(dossier, yaml.safe_load(f.read_text(encoding="utf-8")) or {})


# -- empreintes et signature -------------------------------------------------------------------
def fichiers_signes(dossier: Path) -> list[Path]:
    return sorted(p for p in dossier.rglob("*") if p.is_file() and p.name != "SIGNATURE")


def empreintes(dossier: Path) -> dict[str, str]:
    return {p.relative_to(dossier).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in fichiers_signes(dossier)}


def _charge_utile(empr: dict[str, str]) -> bytes:
    return json.dumps(empr, sort_keys=True, separators=(",", ":")).encode("utf-8")


def signer(dossier: Path, cle_privee_pem: bytes, ident_cle: str) -> dict:
    from cryptography.hazmat.primitives import serialization
    cle = serialization.load_pem_private_key(cle_privee_pem, password=None)
    empr = empreintes(dossier)
    sig = base64.b64encode(cle.sign(_charge_utile(empr))).decode()
    contenu = {"algorithme": "ed25519", "cle": ident_cle, "signe_le": dt.datetime.now().isoformat(timespec="seconds"),
               "empreintes": empr, "signature": sig}
    (dossier / "SIGNATURE").write_text(json.dumps(contenu, ensure_ascii=False, indent=2), encoding="utf-8")
    return contenu


def verifier_signature(dossier: Path, cles_publiques: dict[str, bytes]) -> list[Anomalie]:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives import serialization
    f = dossier / "SIGNATURE"
    if not f.exists():
        return [Anomalie("erreur", "SIG-ABSENTE", "le pack n'est pas signé")]
    sig = json.loads(f.read_text(encoding="utf-8"))
    anomalies = []
    actuelles = empreintes(dossier)
    for rel in sorted(set(sig["empreintes"]) | set(actuelles)):
        if rel not in actuelles:
            anomalies.append(Anomalie("erreur", "SIG-FICHIER-RETIRE", f"{rel} signé mais absent"))
        elif rel not in sig["empreintes"]:
            anomalies.append(Anomalie("erreur", "SIG-FICHIER-AJOUTE", f"{rel} présent mais non signé"))
        elif sig["empreintes"][rel] != actuelles[rel]:
            anomalies.append(Anomalie("erreur", "SIG-FICHIER-MODIFIE", f"{rel} modifié depuis la signature"))
    pem = cles_publiques.get(sig.get("cle"))
    if pem is None:
        anomalies.append(Anomalie("erreur", "SIG-CLE-INCONNUE", f"clé « {sig.get('cle')} » non reconnue"))
        return anomalies
    try:
        serialization.load_pem_public_key(pem).verify(base64.b64decode(sig["signature"]), _charge_utile(sig["empreintes"]))
    except InvalidSignature:
        anomalies.append(Anomalie("erreur", "SIG-INVALIDE", "la signature ne correspond pas aux empreintes"))
    return anomalies


def cles_publiques_embarquees() -> dict[str, bytes]:
    dossier = Path(__file__).with_name("cles")
    return {p.stem: p.read_bytes() for p in dossier.glob("*.pub")}


# -- validation --------------------------------------------------------------------------------
def valider(pack: Pack, racine_packs: Path | None = None, cles: dict[str, bytes] | None = None) -> list[Anomalie]:
    """Toutes les règles du format. Les erreurs bloquent l'usage du pack ; aucune n'est « tranchée en silence »."""
    m, a = pack.manifeste, []
    err = lambda code, msg: a.append(Anomalie("erreur", code, msg))
    avert = lambda code, msg: a.append(Anomalie("avertissement", code, msg))

    # Identité
    couche = pack.couche
    if couche not in COUCHES_COMMUNES and couche not in ETATS_OHADA:
        err("PACK-COUCHE", f"dossier « {couche} » : ni un État OHADA (ISO 3166-1), ni une couche commune")
    pays = m.get("pays")
    if couche in ETATS_OHADA and pays != couche:
        err("PACK-PAYS", f"pays « {pays} » ≠ dossier « {couche} »")
    if couche in COUCHES_COMMUNES and m.get("couche") != couche:
        err("PACK-COUCHE", f"manifeste : couche « {m.get('couche')} » ≠ dossier « {couche} »")
    if not _VERSION.match(str(m.get("version", ""))):
        err("PACK-VERSION", f"version « {m.get('version')} » : format AAAA.n attendu")
    elif str(m["version"]) != pack.dossier.name:
        err("PACK-VERSION", f"version « {m['version']} » ≠ dossier « {pack.dossier.name} »")
    if m.get("monnaie") is not None and m.get("monnaie") not in MONNAIES:
        err("PACK-MONNAIE", f"monnaie « {m.get('monnaie')} » hors liste ISO 4217 retenue {sorted(MONNAIES)}")
    if couche in ETATS_OHADA and not m.get("monnaie"):
        err("PACK-MONNAIE", "monnaie absente")
    for l in m.get("langues_liasse") or []:
        if l not in LANGUES:
            err("PACK-LANGUE", f"langue « {l} » hors {sorted(LANGUES)}")
    for s in m.get("systemes") or []:
        if s not in SYSTEMES:
            err("PACK-SYSTEME", f"système « {s} » hors {sorted(SYSTEMES)}")

    # Validité et statut
    try:
        du = dt.date.fromisoformat(str(m.get("valide_du")))
        au = m.get("valide_au")
        if au is not None and dt.date.fromisoformat(str(au)) < du:
            err("PACK-VALIDITE", "valide_au avant valide_du")
    except ValueError:
        err("PACK-VALIDITE", f"valide_du « {m.get('valide_du')} » : date AAAA-MM-JJ attendue")
    statut = m.get("statut")
    if statut not in STATUTS:
        err("PACK-STATUT", f"statut « {statut} » hors {STATUTS}")
    val = m.get("validation") or {}
    if statut in ("valide", "publie"):
        if not val.get("expert"):
            err("PACK-EXPERT", f"statut « {statut} » sans expert signataire (validation.expert)")
        if statut == "publie" and int(val.get("liasses_reproduites") or 0) < 30:
            err("PACK-PREUVE", f"publication avec {val.get('liasses_reproduites') or 0} liasse(s) reproduite(s) (30 exigées)")
        if statut == "valide" and int(val.get("liasses_reproduites") or 0) < 10:
            err("PACK-PREUVE", f"validation avec {val.get('liasses_reproduites') or 0} liasse(s) reproduite(s) (10 exigées)")
    if statut == "retire" and not m.get("remplace_par"):
        err("PACK-RETRAIT", "pack retiré sans « remplace_par »")

    # Héritage
    for parent in m.get("herite_de") or []:
        if racine_packs is not None and not (racine_packs / parent / "pack.yaml").exists():
            err("PACK-HERITAGE", f"couche parente introuvable : {parent}")
    if couche in ETATS_OHADA:
        zone = next((z for z, e in ZONES.items() if couche in e), None)
        parents = [p.split("/")[0] for p in m.get("herite_de") or []]
        if "ohada" not in parents:
            err("PACK-HERITAGE", "un pack pays hérite de la couche ohada")
        if zone and zone not in parents:
            avert("PACK-HERITAGE", f"{couche} est en zone {zone.upper()} mais n'hérite pas de la couche {zone}")

    # Données
    illisibles = set()
    for rel in FICHIERS_DE_DONNEES:
        try:
            pack.json(rel)
        except ValueError as e:
            illisibles.add(rel)
            err("PACK-JSON", f"{rel} illisible : {e}")
    # Un fichier illisible est une erreur déjà signalée : on ne le relit pas (pas d'exception).
    if "fiscal/parametres.json" not in illisibles:
        _valider_parametres(pack, err)
    if "correspondances/comptes.json" not in illisibles:
        _valider_comptes(pack, err)
    if "controles.json" not in illisibles:
        _valider_controles(pack, err)
    if not (pack.dossier / "SOURCES.md").exists():
        err("PACK-SOURCES", "SOURCES.md absent : aucune donnée sans source")

    # Signature : exigée dès que le pack sort de l'atelier.
    if statut in ("valide", "publie", "retire") or (pack.dossier / "SIGNATURE").exists():
        a += verifier_signature(pack.dossier, cles if cles is not None else cles_publiques_embarquees())
    elif statut == "brouillon":
        avert("SIG-ABSENTE", "brouillon non signé : utilisable en mode atelier seulement")
    return a


def _valider_parametres(pack: Pack, err) -> None:
    donnees = pack.json("fiscal/parametres.json")
    if donnees is None:
        return
    for cle, p in (donnees.get("parametres") or {}).items():
        if not isinstance(p, dict) or "valeur" not in p:
            err("FISC-FORME", f"{cle} : objet avec « valeur » attendu"); continue
        if not str(p.get("article") or "").strip():
            err("FISC-ARTICLE", f"{cle} : aucun article cité — aucun taux sans article")
        if not str(p.get("source") or "").strip():
            err("FISC-SOURCE", f"{cle} : aucune source (texte et année)")
        if p.get("url") and not str(p["url"]).startswith(("https://", "http://", "datas/")):
            err("FISC-SOURCE", f"{cle} : url « {p['url']} » invalide")
        if p.get("unite") == "taux" and isinstance(p.get("valeur"), (int, float)) and not 0 <= p["valeur"] <= 1:
            err("FISC-TAUX", f"{cle} : taux {p['valeur']} hors de [0, 1] (exprimer 30 % en 0.30)")


def _valider_comptes(pack: Pack, err) -> None:
    donnees = pack.json("correspondances/comptes.json")
    if donnees is None:
        return
    vus: dict[tuple, str] = {}
    for r in donnees.get("regles") or []:
        prefixe, sens = str(r.get("prefixe", "")), r.get("sens", "tous")
        if not prefixe.isdigit():
            err("CPT-PREFIXE", f"préfixe « {prefixe} » non numérique"); continue
        if not r.get("ref") and r.get("nature") != "hors_etats":
            # Une exclusion des états est permise, mais seulement EXPLICITE (nature « hors_etats »).
            err("CPT-REF", f"préfixe {prefixe} sans poste (ref) et sans exclusion explicite (nature: hors_etats)")
        cle = (prefixe, sens, r.get("colonne", "net"))
        if cle in vus and vus[cle] != r.get("ref"):
            err("CPT-DOUBLON", f"compte {prefixe} ({sens}) alimente deux postes : {vus[cle]} et {r.get('ref')}")
        vus[cle] = r.get("ref")


def _valider_controles(pack: Pack, err) -> None:
    donnees = pack.json("controles.json")
    if donnees is None:
        return
    ids = set()
    for c in donnees.get("controles") or []:
        if c.get("id") in ids:
            err("CTL-DOUBLON", f"contrôle {c.get('id')} déclaré deux fois")
        ids.add(c.get("id"))
        if c.get("gravite") not in ("bloquant", "avertissement"):
            err("CTL-GRAVITE", f"{c.get('id')} : gravité « {c.get('gravite')} » ∉ {{bloquant, avertissement}}")
        if not (c.get("message") or {}).get("fr"):
            err("CTL-MESSAGE", f"{c.get('id')} : message en français absent")


# -- résolution : choisir le pack en vigueur, puis fusionner ses couches -----------------------
@dataclass
class PackResolu:
    pays: str
    versions: list[str]                              # de la plus générale à la plus spécifique
    parametres: dict = field(default_factory=dict)
    comptes: list = field(default_factory=list)
    postes: dict = field(default_factory=dict)
    sn: dict = field(default_factory=dict)
    smt: dict = field(default_factory=dict)
    controles: list = field(default_factory=list)
    libelles: dict = field(default_factory=dict)
    gabarits: dict = field(default_factory=dict)     # nom → chemin du fichier (couche la plus spécifique)
    surcharges: list = field(default_factory=list)   # (élément, couche remplacée, couche qui remplace)
    manifeste: dict = field(default_factory=dict)


def en_vigueur(racine_packs: Path, pays: str, cloture: dt.date, atelier: bool = False) -> Pack:
    """Le pack publié du pays valable à la date de clôture (le plus récent si plusieurs).
    En mode atelier (équipe Facil), les brouillons et packs validés sont acceptés."""
    if pays not in ETATS_OHADA:
        raise ValueError(f"« {pays} » n'est pas un État OHADA (ISO 3166-1 alpha-2)")
    admis = {"publie", "retire"} | ({"brouillon", "valide"} if atelier else set())
    candidats = []
    for d in sorted((racine_packs / pays).glob("*/pack.yaml")) if (racine_packs / pays).is_dir() else []:
        p = charger(d.parent)
        m = p.manifeste
        du = dt.date.fromisoformat(str(m["valide_du"]))
        au = dt.date.fromisoformat(str(m["valide_au"])) if m.get("valide_au") else None
        if m.get("statut") in admis and du <= cloture and (au is None or cloture <= au):
            candidats.append((du, p))
    if not candidats:
        raise LookupError(f"aucun pack {'(atelier) ' if atelier else ''}en vigueur pour {pays} au {cloture.isoformat()}")
    return max(candidats, key=lambda c: c[0])[1]


def resoudre(racine_packs: Path, pack: Pack) -> PackResolu:
    """Fusionne les couches héritées puis le pack ; chaque surcharge est tracée."""
    couches = [charger(racine_packs / h) for h in pack.manifeste.get("herite_de") or []] + [pack]
    r = PackResolu(pays=pack.manifeste.get("pays", pack.couche), versions=[c.ident for c in couches], manifeste=pack.manifeste)
    origine: dict[tuple, str] = {}

    def poser(espace: str, cle, valeur, depuis: str, cible: dict) -> None:
        if (espace, cle) in origine:
            r.surcharges.append((f"{espace}:{cle}", origine[(espace, cle)], depuis))
        origine[(espace, cle)] = depuis
        cible[cle] = valeur

    regles: dict[tuple, dict] = {}
    controles: dict[str, dict] = {}
    for c in couches:
        for cle, v in ((c.json("fiscal/parametres.json") or {}).get("parametres") or {}).items():
            poser("param", cle, v, c.ident, r.parametres)
        for code, poste in ((c.json("correspondances/postes.json") or {}).get("postes") or {}).items():
            poser("poste", code, poste, c.ident, r.postes)
        for regle in (c.json("correspondances/comptes.json") or {}).get("regles") or []:
            poser("compte", (regle["prefixe"], regle.get("sens", "tous"), regle.get("colonne", "net")), regle, c.ident, regles)
        for systeme, cible in (("sn", r.sn), ("smt", r.smt)):
            for feuille, contenu in ((c.json(f"correspondances/{systeme}.json") or {}).get("feuilles") or {}).items():
                base = cible.setdefault(feuille, {k: v for k, v in contenu.items() if k != "lignes"} | {"lignes": {}})
                for ligne, v in (contenu.get("lignes") or {}).items():
                    poser(systeme, (feuille, ligne), v, c.ident, base["lignes"])
        for ctl in (c.json("controles.json") or {}).get("controles") or []:
            poser("controle", ctl["id"], ctl, c.ident, controles)
        for f in sorted((c.dossier / "libelles").glob("*.json")):
            for cle, v in json.loads(f.read_text(encoding="utf-8")).items():
                poser(f"libelle-{f.stem}", cle, v, c.ident, r.libelles.setdefault(f.stem, {}))
        for g in sorted((c.dossier / "gabarits").glob("*")):
            poser("gabarit", g.name, g, c.ident, r.gabarits)
    r.comptes = sorted(regles.values(), key=lambda x: (-len(str(x["prefixe"])), str(x["prefixe"])))
    r.controles = list(controles.values())
    return r


def poste_du_compte(r: PackResolu, compte: str, sens: str = "tous", colonne: str = "net") -> dict | None:
    """Plus long préfixe gagnant ; une règle propre au sens du solde prime sur « tous »."""
    for regle in r.comptes:
        if str(compte).startswith(str(regle["prefixe"])) and regle.get("colonne", "net") == colonne \
                and regle.get("sens", "tous") in (sens, "tous"):
            meilleurs = [x for x in r.comptes if x["prefixe"] == regle["prefixe"] and x.get("colonne", "net") == colonne
                         and x.get("sens", "tous") == sens]
            return meilleurs[0] if meilleurs else regle
    return None
