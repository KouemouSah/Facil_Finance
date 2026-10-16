"""Convertit la Guinée équatoriale (aujourd'hui dans le code du plugin compta-ohada) au format pack.

  convertir_ge.py [--source C:/DSF/compta-ohada]   →  packs/GQ/2025.1/

Recette REJOUABLE. Preuve d'équivalence : tests/test_pack_ge.py vérifie que les paramètres relus depuis
le pack résolu redonnent, clé par clé, le fichier d'origine — et que le calcul fiscal (TF1/TF2) sur le
jeu de référence donne les mêmes montants au franc près.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import yaml

DEPOT = Path(__file__).resolve().parents[1]
GQ = DEPOT / "packs" / "GQ" / "2025.1"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", default=str(DEPOT.parent / "compta-ohada"))
    src = Path(p.parse_args().source)
    origine = json.loads((src / "lib" / "parametres_fiscaux_ge.json").read_text(encoding="utf-8"))
    meta = origine["_meta"]

    if GQ.exists():
        shutil.rmtree(GQ)
    (GQ / "fiscal").mkdir(parents=True)

    # Paramètres : chaque taux garde son article et son texte ; la source et la date viennent du _meta d'origine.
    parametres = {}
    for cle, v in origine["parametres"].items():
        parametres[cle] = dict(v)
        parametres[cle].setdefault("source", "Ley n°1/2024 de 19 de noviembre — Código General de Impuestos de Guinea Ecuatorial")
        parametres[cle].setdefault("url", "datas/ley_tributaria_2024.md")
        parametres[cle].setdefault("consulte_le", meta.get("verifie_le"))
    fiscal = {"_meta": meta, "parametres": parametres}
    for cle in origine:                       # interprétations, comptes, faits, propositions : repris tels quels
        if cle not in ("_meta", "parametres"):
            fiscal[cle] = origine[cle]
    (GQ / "fiscal" / "parametres.json").write_text(json.dumps(fiscal, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # Gabarit DEF (format GE) et sa structure ; dictionnaire FR → ES des libellés de la DEF.
    (GQ / "gabarits").mkdir(); (GQ / "structure").mkdir(); (GQ / "libelles").mkdir()
    tpl = src / "skills" / "dsf-syscohada" / "templates"
    shutil.copy2(tpl / "def_ge_gabarit.xlsx", GQ / "gabarits" / "def_ge.xlsx")
    shutil.copy2(tpl / "def_ge_gabarit.json", GQ / "structure" / "def_ge.json")
    shutil.copy2(src / "skills" / "dsf-syscohada" / "references" / "i18n-def.json", GQ / "structure" / "i18n-def.json")

    # Mentions d'en-tête (le moteur les cherchait dans def_sn.py : GE_MENTIONS).
    (GQ / "libelles" / "fr.json").write_text(json.dumps({
        "entete.republique": "RÉPUBLIQUE DE GUINÉE ÉQUATORIALE",
        "entete.ministere": "MINISTÈRE DE L'ÉCONOMIE, DES FINANCES ET DE LA PLANIFICATION",
        "entete.administration": "DIRECTION GÉNÉRALE DES IMPÔTS ET CONTRIBUTIONS (DGIC)",
        "liasse.titre": "DÉCLARATION STATISTIQUE ET FISCALE (DEF)", "liasse.sigle": "DEF"},
        ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (GQ / "libelles" / "es.json").write_text(json.dumps({
        "entete.republique": "REPÚBLICA DE GUINEA ECUATORIAL",
        "entete.ministere": "MINISTERIO DE ECONOMÍA, HACIENDA Y PLANIFICACIÓN",
        "entete.administration": "DIRECCIÓN GENERAL DE IMPUESTOS Y CONTRIBUCIONES (DGIC)",
        "liasse.titre": "DECLARACIÓN ESTADÍSTICA Y FISCAL (DEF)", "liasse.sigle": "DEF"},
        ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    (GQ / "pack.yaml").write_text(
        "# Pack pays GUINÉE ÉQUATORIALE — converti depuis le plugin compta-ohada par outils/convertir_ge.py.\n"
        + yaml.safe_dump({
            "pays": "GQ", "version": "2025.1", "valide_du": "2025-01-01", "valide_au": None, "monnaie": "XAF",
            "langues_liasse": ["es", "fr"], "systemes": ["SN", "SMT"], "herite_de": ["ohada/2017.1", "cemac/2025.1"],
            # Le pack reproduit une DEF déposée réelle (dossier pilote) — une seule à ce jour : brouillon.
            "statut": "brouillon",
            "validation": {"expert": None, "date": None, "liasses_reproduites": 1,
                           "reference": "DEF 2025 déposée d'un dossier pilote (anonymisé) : 3 952 cellules identiques, 0 écart inexpliqué"},
            "moteur_minimal": "0.1",
            "gabarit_def": {"fichier": "gabarits/def_ge.xlsx", "structure": "structure/def_ge.json",
                            "traductions": "structure/i18n-def.json"},
        }, allow_unicode=True, sort_keys=False), encoding="utf-8")
    (GQ / "SOURCES.md").write_text(
        "# Sources — pack Guinée équatoriale 2025.1\n\n| Donnée | Source | Nature | Consulté le |\n|---|---|---|---|\n"
        f"| Paramètres fiscaux (IS, Cuota Mínima, IVA, déficits, plafonds) | {meta.get('source')} | officielle | {meta.get('verifie_le')} |\n"
        "| Gabarit DEF (format GE) | DEF 2025 déposée d'un dossier pilote, purgée de toute donnée du client (`tools/construire_gabarit.py` du plugin) | officielle (format déposé) | 01/10/2026 |\n"
        "| Mentions d'en-tête FR | Moteur compta-ohada (def_sn.py, GE_MENTIONS) | interne | 01/10/2026 |\n"
        "| Mentions d'en-tête ES | Gabarit DEF (« ECONOMIA, HACIENDA Y PLANIFICACIÓN ») ; nom officiel de l'État | officielle (partielle) | 16/10/2026 |\n\n"
        f"**Vigueur** : {meta.get('vigueur')}\n\n"
        "**À confirmer** : intitulé exact du ministère et de la DGIC en espagnol, sur un document officiel récent.\n", encoding="utf-8")
    (GQ / "CHANGELOG.md").write_text("# Journal — pack Guinée équatoriale\n\n## 2025.1 — 16/10/2026\n"
                                     "Converti depuis le plugin compta-ohada v0.10.0 (parametres_fiscaux_ge.json, gabarit DEF, dictionnaire FR→ES).\n",
                                     encoding="utf-8")
    print(f"GQ/2025.1 : {len(parametres)} paramètres fiscaux, gabarit DEF, dictionnaire FR→ES, mentions FR/ES")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
