"""Construit les couches communes des packs depuis les références du moteur actuel (plugin compta-ohada).

  convertir_references.py [--source plugin/compta-ohada]

Produit :
  packs/ohada/2017.1/  règles « compte → poste », postes, correspondances du formulaire SN, gabarit SN,
                       contrôles communs à l'OHADA
  packs/cemac/2025.1/  couche de zone (monnaie XAF) — sans paramètre fiscal : la fiscalité est nationale

Recette REJOUABLE : on ne recopie jamais une référence à la main. Rejouer après toute évolution des
références du moteur ; la validation (facil_pack.py valider-tout) doit rester verte.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import yaml

DEPOT = Path(__file__).resolve().parents[1]
PACKS = DEPOT / "packs"


def ecrire_json(chemin: Path, donnees) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(donnees, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def ecrire_yaml(chemin: Path, donnees: dict, entete: str) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(entete + yaml.safe_dump(donnees, allow_unicode=True, sort_keys=False), encoding="utf-8")


def regles_comptes(mapping: dict) -> list[dict]:
    """Deux formes dans le moteur : un poste unique, ou un poste par sens du solde → champ « sens »."""
    regles = []
    for r in mapping["regles"]:
        if "ref" in r:
            regles.append({"prefixe": r["prefixe"], "sens": "tous", "ref": r["ref"], "nature": r.get("nature"),
                           "libelle": r["libelle"]})
        else:
            for sens in ("debiteur", "crediteur"):
                if r.get(sens):
                    regles.append({"prefixe": r["prefixe"], "sens": sens, "ref": r[sens], "libelle": r["libelle"]})
    return regles


def correspondances_sn(auto: dict, manuelle: dict) -> dict:
    """Correspondance automatique (rapprochement de libellés) + correspondance écrite à la main, qui prime."""
    feuilles = {}
    for nom, f in auto["feuilles"].items():
        feuilles[nom] = {"feuille": f["feuille"], "colonne_n": f.get("colonne_n"), "roles": f.get("roles", {}),
                         "lignes": {l: {"expr": v["expr"], "libelle": v.get("libelle_sn"), "origine": "rapprochement",
                                        "score": v.get("score")} for l, v in f.get("lignes", {}).items()}}
    for nom, f in (manuelle.get("feuilles") or {}).items():
        cible = feuilles.setdefault(nom, {"feuille": f.get("feuille", nom), "lignes": {}})
        for l, v in (f.get("lignes") or {}).items():
            expr = v["expr"] if isinstance(v, dict) else v
            cible["lignes"][l] = {"expr": expr, "libelle": (v.get("libelle") if isinstance(v, dict) else None), "origine": "manuelle"}
    return {"feuilles": feuilles, "non_rapprochees": auto.get("non_rapprochees"),
            "non_ecrites": manuelle.get("_non_ecrites")}


CONTROLES_OHADA = [
    {"id": "OHADA-BILAN-EQUILIBRE", "expression": "bilan.actif.total == bilan.passif.total", "gravite": "bloquant",
     "message": {"fr": "Le total de l'actif est égal au total du passif.", "es": "El total del activo es igual al total del pasivo."}},
    {"id": "OHADA-RESULTAT", "expression": "compte_resultat.XI == bilan.passif.CJ", "gravite": "bloquant",
     "message": {"fr": "Le résultat net du compte de résultat (XI) est égal au résultat du bilan (CJ).",
                 "es": "El resultado neto de la cuenta de resultados (XI) es igual al resultado del balance (CJ)."}},
    {"id": "OHADA-NOTE-POSTE", "expression": "pour chaque note chiffrée : total(note) == poste(note)", "gravite": "bloquant",
     "message": {"fr": "Chaque note chiffrée est égale au poste des états qu'elle détaille.",
                 "es": "Cada nota cifrada es igual a la partida de los estados que detalla."}},
    {"id": "OHADA-POSTE-LIGNE", "expression": "pour chaque poste chiffré : une ligne existe dans le formulaire", "gravite": "bloquant",
     "message": {"fr": "Chaque poste chiffré a sa ligne dans le formulaire.", "es": "Cada partida cifrada tiene su línea en el formulario."}},
    {"id": "OHADA-TFT", "expression": "tft.variation_tresorerie == bilan.tresorerie_N - bilan.tresorerie_N1", "gravite": "bloquant",
     "message": {"fr": "La variation de trésorerie du TFT est égale à celle du bilan.",
                 "es": "La variación de tesorería del TFE es igual a la del balance."}},
    {"id": "OHADA-BALANCE", "expression": "balance.debits == balance.credits", "gravite": "bloquant",
     "message": {"fr": "La balance est équilibrée (soldes et mouvements).", "es": "El balance de comprobación está cuadrado."}},
]

SOURCES_OHADA = """# Sources — couche OHADA 2017.1

| Donnée | Source | Nature | Consulté le |
|---|---|---|---|
| Plan de comptes, états financiers, notes annexes | Acte uniforme relatif au droit comptable et à l'information financière (AUDCIF), adopté le 26/01/2017, et SYSCOHADA révisé | officielle | 15/10/2026 |
| Codes de postes (REF) et règles « compte → poste » | Moteur Facil `mapping-comptes-dsf.json` v2, contrôlé sur une liasse déposée d'un dossier pilote (anonymisé) : 99/99 postes rapprochés | interne, éprouvée | 28/09/2026 |
| Formulaire du système normal (gabarit) | Formulaire DSF système normal de la DGI du Cameroun (version vierge) ; ses feuilles fiscales camerounaises sont propres au pack CM | officielle | 01/10/2026 |
| Correspondance « ligne du formulaire SN → postes » | Rapprochement de libellés (seuil 0,72), et correspondance écrite à la main qui prime | interne | 01/10/2026 |

**Lignes non écrites, volontairement** (compte incertain) : voir `non_ecrites` dans `correspondances/sn.json`. Le contrôle « note = poste » les signale si elles sont chiffrées.
"""


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", default=str(DEPOT / "plugin" / "compta-ohada"))
    a = p.parse_args()
    src = Path(a.source)
    refs = src / "skills" / "dsf-syscohada" / "references"
    mapping = json.loads((refs / "mapping-comptes-dsf.json").read_text(encoding="utf-8"))

    # -- couche OHADA ----------------------------------------------------------------------------
    o = PACKS / "ohada" / "2017.1"
    if o.exists():
        shutil.rmtree(o)
    ecrire_yaml(o / "pack.yaml", {
        "couche": "ohada", "version": "2017.1", "valide_du": "2018-01-01", "valide_au": None,
        "systemes": ["SN", "SMT"], "statut": "brouillon",
        "validation": {"expert": None, "date": None, "liasses_reproduites": 0},
        "moteur_minimal": "0.1", "referentiel": "AUDCIF 2017 — SYSCOHADA révisé",
        # Le gabarit SN commun est le formulaire de la DGI du Cameroun : ses feuilles fiscales sont
        # NATIONALES. Le producteur les retire, sauf si le pack pays les déclare (feuilles_conservees).
        "gabarit_sn": {"origine": "CM", "feuilles_nationales": r"^(cf\d|autres annexes fisca|c[o]?\d ?-? ?note)",
                       "mentions_entete": {"republique du cameroun": "entete.republique",
                                           "ministere des finances": "entete.ministere",
                                           "direction generale des impots": "entete.administration"}},
    }, "# Couche commune OHADA — générée par outils/convertir_references.py ; ne pas modifier à la main.\n")
    # Notes extra-comptables : quand elles s'appliquent (racines de comptes), toujours, ou sur saisie seulement.
    ecrire_json(o / "declencheurs.json", {
        "_regle": "une note extra-comptable n'est produite que si la balance montre qu'elle s'applique",
        "si_comptes": {"note 1": ["16", "17", "18"], "note 3b": ["17"], "note 3d": ["81", "82"], "note 3e": ["106"],
                       "note 16b": ["196"], "note 16bbis": ["196"], "note 27b": ["66"], "note 13": ["10"]},
        "toujours": ["note 2"],
        "si_renseignee": ["note 3f", "note 16c", "note 35", "notes stat sociale et envi", "notes stat a caractere commerci",
                          "note 32", "note 33"]})
    ecrire_json(o / "correspondances" / "comptes.json", {
        "_origine": "compta-ohada mapping-comptes-dsf.json v" + str(mapping["_meta"].get("version")),
        "_regle": "plus long préfixe gagnant ; une règle propre au sens du solde (debiteur/crediteur) prime sur « tous »",
        "regles": regles_comptes(mapping)})
    ecrire_json(o / "correspondances" / "postes.json", {"postes": mapping["postes"]})
    ecrire_json(o / "correspondances" / "sn.json", correspondances_sn(
        json.loads((refs / "correspondance-sn.json").read_text(encoding="utf-8")),
        json.loads((refs / "correspondance-sn-manuelle.json").read_text(encoding="utf-8"))))
    ecrire_json(o / "controles.json", {"controles": CONTROLES_OHADA})
    (o / "gabarits").mkdir()
    shutil.copy2(src / "skills" / "dsf-syscohada" / "templates" / "syscohada_sn_modele.xlsx", o / "gabarits" / "sn.xlsx")
    (o / "SOURCES.md").write_text(SOURCES_OHADA, encoding="utf-8")
    (o / "CHANGELOG.md").write_text("# Journal — couche OHADA\n\n## 2017.1 — 16/10/2026\nPremière version, convertie depuis les références du moteur compta-ohada v0.10.0.\n", encoding="utf-8")

    # -- couche CEMAC ----------------------------------------------------------------------------
    c = PACKS / "cemac" / "2025.1"
    if c.exists():
        shutil.rmtree(c)
    ecrire_yaml(c / "pack.yaml", {
        "couche": "cemac", "version": "2025.1", "valide_du": "2025-01-01", "valide_au": None, "monnaie": "XAF",
        "statut": "brouillon", "validation": {"expert": None, "date": None, "liasses_reproduites": 0},
        "herite_de": ["ohada/2017.1"],
        "remarque": "Aucun paramètre fiscal à ce niveau : IS, TVA et minimum de perception sont fixés par chaque loi de finances nationale.",
    }, "# Couche de zone CEMAC — générée par outils/convertir_references.py.\n")
    (c / "SOURCES.md").write_text("# Sources — couche CEMAC 2025.1\n\n| Donnée | Source | Nature | Consulté le |\n|---|---|---|---|\n"
                                  "| Monnaie : franc CFA BEAC (XAF), code ISO 4217 | Banque des États de l'Afrique centrale — https://www.beac.int | officielle | 16/10/2026 |\n", encoding="utf-8")
    (c / "CHANGELOG.md").write_text("# Journal — couche CEMAC\n\n## 2025.1 — 16/10/2026\nPremière version.\n", encoding="utf-8")

    regles = json.loads((o / "correspondances" / "comptes.json").read_text(encoding="utf-8"))["regles"]
    sn = json.loads((o / "correspondances" / "sn.json").read_text(encoding="utf-8"))
    print(f"ohada/2017.1 : {len(regles)} règles de comptes, {len(mapping['postes'])} postes, "
          f"{len(sn['feuilles'])} feuilles SN ({sum(len(f['lignes']) for f in sn['feuilles'].values())} lignes), "
          f"{len(CONTROLES_OHADA)} contrôles communs")
    print("cemac/2025.1 : couche de zone (XAF)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
