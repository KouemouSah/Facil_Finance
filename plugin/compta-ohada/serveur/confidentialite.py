# -*- coding: utf-8 -*-
"""Passerelle de CONFIDENTIALITÉ du serveur MCP : ce qui part vers le modèle de langage est filtré, vérifié, journalisé.

Ce que Claude reçoit d'un outil n'est jamais la donnée brute :
  - NOMS -> pseudonymes stables : entité (ENTITE-A…), tiers (TIERS-001…), identité saisie (raison sociale, sigle,
    adresse, NIF, RCCM, dirigeant…), NIF des tiers. La table réel <-> pseudonyme (le COFFRE) reste sur le poste,
    dans <racine>/.facil_coffre.json, et n'est jamais transmise ;
  - MONTANTS -> « [montant] » (tout nombre de 5 chiffres et plus, ou avec séparateurs de milliers) ; les années
    (1990-2100) et les petits nombres (versions, comptes de questions, n° de compte à 3 ou 4 chiffres) restent ;
  - CHEMINS -> relatifs à la racine du dossier de travail (« <Facil-DEF>\\ENTITE-A\\2025\\… »).
En entrée, l'inverse : un pseudonyme reçu de Claude (entité, identifiant de question) est rendu à sa valeur réelle.

CONTRÔLE FINAL, en échec FERMÉ : après filtrage, la sortie est relue ; si une valeur réelle connue du coffre ou un
montant y subsiste, elle n'est PAS envoyée (une erreur neutre part à sa place) et l'incident est journalisé.
JOURNAL : chaque sortie effectivement transmise est ajoutée à <racine>/journal_sorties.jsonl (horodatage, outil,
empreinte, contenu) : l'utilisateur peut vérifier, a posteriori, tout ce qui a quitté le poste par ce canal.

Modes (variable FACIL_CONFIDENTIALITE, réglage de l'extension Desktop) :
  - « stricte » (défaut) : tout ce qui précède, y compris le nom de l'entité ;
  - « standard » : le nom de l'entité reste en clair (l'utilisateur l'a déjà écrit dans la conversation) ; tiers,
    identité, montants et chemins restent protégés.
Limite DÉCLARÉE : la passerelle ne protège que ce canal. Ce que l'utilisateur écrit lui-même dans la conversation,
ou un fichier qu'il y joint, part tel quel ; le hook du plugin (Claude Code) empêche Claude de LIRE le dossier de
travail, mais aucune passerelle ne peut filtrer ce que l'utilisateur choisit d'envoyer.
"""
import datetime
import hashlib
import json
import os
import re
import unicodedata

def MODE():
    """« stricte » par défaut ; « standard » si demandé (variable, ou case « entité en clair » de l'extension)."""
    if (os.environ.get("FACIL_ENTITE_EN_CLAIR") or "").strip().lower() in ("true", "1", "oui"):
        return "standard"
    return (os.environ.get("FACIL_CONFIDENTIALITE") or "stricte").strip().lower()
PREFIXES = {"entite": "ENTITE", "tiers": "TIERS", "identite": "IDENT", "nif": "NIF", "personne": "PERS"}
# montants : 5 chiffres et plus, ou groupes de milliers (espace, espace insécable, virgule, point), décimales comprises
# (jamais collé à un « - » précédé d'une lettre : « TIERS-001 297 008 247 » garde son pseudonyme, le montant est masqué)
MONTANT = re.compile(r"(?<![\w.,-])[-+]?\d{1,3}(?:[   ,.]\d{3})+(?:[.,]\d+)?(?![\w])"
                     r"|(?<![\w.,-])[-+]?\d{5,}(?:[.,]\d+)?(?![\w])")
MASQUE = "[montant]"
IDENTIFIANTS = ("id", "options")        # identifiants de question et choix permis : jamais masqués (n° de compte)


def _plat(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", s).strip()


class Coffre:
    """Table locale réel <-> pseudonyme, stable d'une session à l'autre (un tiers garde le même pseudonyme)."""

    def __init__(self, racine):
        self.racine = os.path.abspath(racine)
        self.chemin = os.path.join(self.racine, ".facil_coffre.json")
        try:
            self.t = json.load(open(self.chemin, encoding="utf-8"))
        except (OSError, ValueError):
            self.t = {"vers_pseudo": {}, "vers_reel": {}, "compteurs": {}}

    def _sauver(self):
        os.makedirs(self.racine, exist_ok=True)
        tmp = self.chemin + ".tmp"
        json.dump(self.t, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        os.replace(tmp, self.chemin)

    def pseudo(self, reel, genre):
        reel = str(reel).strip()
        if not reel:
            return reel
        cle = _plat(reel)
        if cle in self.t["vers_pseudo"]:
            return self.t["vers_pseudo"][cle]
        n = self.t["compteurs"].get(genre, 0) + 1
        self.t["compteurs"][genre] = n
        p = f"{PREFIXES[genre]}-{chr(64 + n) if genre == 'entite' and n <= 26 else f'{n:03d}'}"
        self.t["vers_pseudo"][cle] = p
        self.t["vers_reel"][p] = reel
        self._sauver()
        return p

    def alias(self, autre, reel, genre):
        """Autre forme d'une même valeur (nom de dossier « slug » d'une entité) : MÊME pseudonyme."""
        p = self.pseudo(reel, genre)
        cle = _plat(autre)
        if autre and self.t["vers_pseudo"].get(cle) != p:
            self.t["vers_pseudo"][cle] = p
            self.t.setdefault("alias", {})[autre] = p
            self._sauver()
        return p

    def reel(self, valeur):
        """Pseudonymes -> valeurs réelles, dans une chaîne (identifiant « tf5nif.TIERS-003 », nom d'entité…)."""
        if not isinstance(valeur, str):
            return valeur
        return re.sub(r"\b(?:ENTITE|TIERS|IDENT|NIF|PERS)-(?:[A-Z]|\d{3})\b",
                      lambda m: self.t["vers_reel"].get(m.group(0), m.group(0)), valeur)

    def connus(self):
        """(réel, pseudonyme), le plus long d'abord (un nom qui en contient un autre est remplacé en premier)."""
        paires = [(r, p) for p, r in self.t["vers_reel"].items()] + list(self.t.get("alias", {}).items())
        return sorted(paires, key=lambda x: -len(x[0]))


class Passerelle:
    def __init__(self, racine):
        self.racine = os.path.abspath(racine)
        self.coffre = Coffre(racine)

    # ---------------------------------------------------------------- apprentissage : ce qui est sensible
    def apprendre_dossier(self, dossier):
        """Enregistre au coffre les valeurs sensibles connues d'un dossier : entité, identité saisie, tiers du TF5."""
        def lire(p, d):
            try:
                return json.load(open(p, encoding="utf-8"))
            except (OSError, ValueError):
                return d
        man = lire(os.path.join(dossier, "manifeste.json"), {})
        if man.get("entite") and MODE() == "stricte":
            self.coffre.alias(os.path.basename(os.path.dirname(dossier)), man["entite"], "entite")   # + nom de dossier
        rep = lire(os.path.join(dossier, "04_questions", "reponses.json"), {})
        entite = _plat(man.get("entite", ""))
        for k, v in rep.items():
            if not isinstance(v, str) or not v.strip():
                continue
            if k.startswith("identite.") and MODE() != "stricte" and _plat(v) == entite:
                continue                                   # standard : la raison sociale = l'entité, laissée en clair
            if k.startswith("identite."):
                self.coffre.pseudo(v, "personne" if k.endswith("dirigeant") else "identite")
            elif k.startswith("tf5nif."):
                self.coffre.pseudo(k.split(".", 1)[1], "tiers")
                if v.lower() not in ("inconnu", "?"):
                    self.coffre.pseudo(v, "nif")
        for q in lire(os.path.join(dossier, "04_questions", "questions.json"), []):
            if isinstance(q, dict) and str(q.get("id", "")).startswith("tf5nif."):
                self.coffre.pseudo(q["id"].split(".", 1)[1], "tiers")
            # identité REPRISE d'une source (DEF précédente, fiche entité) : aussi sensible qu'une identité saisie
            v = q.get("reponse") if isinstance(q, dict) else None
            if str(q.get("id", "") if isinstance(q, dict) else "").startswith("identite.") and isinstance(v, str) and v.strip() \
                    and not (MODE() != "stricte" and _plat(v) == entite):
                self.coffre.pseudo(v, "personne" if q["id"].endswith("dirigeant") else "identite")

    def apprendre_racine(self):
        if not os.path.isdir(self.racine):
            return
        for e in os.listdir(self.racine):
            pe = os.path.join(self.racine, e)
            if os.path.isdir(pe):
                for ex in os.listdir(pe):
                    if os.path.exists(os.path.join(pe, ex, "manifeste.json")):
                        self.apprendre_dossier(os.path.join(pe, ex))

    # ---------------------------------------------------------------- sortie
    def _noms(self, s):
        s = re.sub(re.escape(self.racine), "<Facil-DEF>", s, flags=re.I)
        for reel, p in self.coffre.connus():
            if len(reel) >= 3:
                for forme in {reel, reel.replace(" ", "_")}:               # forme « slug » des noms de dossier/fichier
                    s = re.sub(r"(?<![A-Za-z0-9])" + re.escape(forme) + r"(?![A-Za-z0-9])", p, s, flags=re.I)
        return s

    def _texte(self, s, cle=None):
        if not isinstance(s, str):
            return s
        s = self._noms(s)
        if cle in IDENTIFIANTS:                           # identifiant de question : n° de compte, pas un montant
            return s
        return MONTANT.sub(lambda m: m.group(0) if _annee(m.group(0)) else MASQUE, s)

    def filtrer(self, obj, cle=None):
        if isinstance(obj, dict):
            return {self._noms(k) if isinstance(k, str) else k: self.filtrer(v, k) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [self.filtrer(v, cle) for v in obj]
        if isinstance(obj, bool) or obj is None:
            return obj
        if isinstance(obj, (int, float)):
            return obj if abs(obj) < 10000 or cle in ("exercice", "modele_exercice") else MASQUE
        return self._texte(obj, cle)

    def fuites(self, obj, cle=None):
        """Ce qui subsisterait de sensible dans une sortie DÉJÀ filtrée : valeurs réelles du coffre, montants,
        chemin absolu du dossier de travail."""
        if isinstance(obj, dict):
            return [x for k, v in obj.items() for x in self.fuites(k) + self.fuites(v, k)]
        if isinstance(obj, (list, tuple)):
            return [x for v in obj for x in self.fuites(v, cle)]
        if isinstance(obj, (int, float)) and not isinstance(obj, bool):
            return [str(obj)] if abs(obj) >= 10000 and cle not in ("exercice", "modele_exercice") else []
        if not isinstance(obj, str):
            return []
        plat = _plat(obj)
        trouve = [p for r, p in self.coffre.connus() if len(r) >= 3
                  and re.search(r"(?<![a-z0-9])" + re.escape(_plat(r)) + r"(?![a-z0-9])", plat)]
        if cle not in IDENTIFIANTS:
            trouve += [m.group(0) for m in MONTANT.finditer(obj) if not _annee(m.group(0))]
        if self.racine.lower() in obj.lower():
            trouve.append("chemin absolu")
        return trouve

    def sortie(self, outil, obj, dossier=None):
        """Filtre, contrôle (échec fermé), journalise. Retourne ce qui peut partir vers le modèle."""
        f = self.filtrer(obj)
        reste = self.fuites(f)
        if reste:
            self._journal(outil, {"BLOQUEE": True, "motif": f"{len(reste)} élément(s) sensible(s) après filtrage"})
            err = {"erreur": "Sortie retenue par la garde de confidentialité (incident journalisé sur le poste). "
                             "Utilisez le formulaire local pour ce contenu."}
            return [err] if isinstance(obj, list) else err            # même forme que la sortie attendue
        self._journal(outil, f)
        return f

    def _journal(self, outil, contenu):
        s = json.dumps(contenu, ensure_ascii=False, sort_keys=True)
        ligne = {"le": datetime.datetime.now().isoformat(timespec="seconds"), "outil": outil,
                 "empreinte": hashlib.sha256(s.encode("utf-8")).hexdigest(), "transmis": contenu}
        os.makedirs(self.racine, exist_ok=True)
        with open(os.path.join(self.racine, "journal_sorties.jsonl"), "a", encoding="utf-8") as j:
            j.write(json.dumps(ligne, ensure_ascii=False) + "\n")

    # ---------------------------------------------------------------- entrée
    def entree(self, valeur):
        return self.coffre.reel(valeur)


def _annee(s):
    return s.isdigit() and len(s) == 4 and 1990 <= int(s) <= 2100
