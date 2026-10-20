"""Purge un classeur .xlsx de ce qu'il transporte sans qu'on le voie : liaisons externes (et leurs valeurs en cache),
noms définis qui pointent vers d'autres classeurs ou cachés, auteurs et société dans les propriétés.

Chirurgie au niveau de l'archive : le reste du classeur (feuilles, styles, formules, validations) est recopié
octet pour octet. Constat du 20/10/2026 : le gabarit GE portait 125 liaisons externes dont le cache contenait des
noms de personnes et un numéro de compte bancaire, sans qu'aucune cellule ne s'en serve.

  purger_classeur.py FICHIER.xlsx [...]          purge en place
  purger_classeur.py --verifier FICHIER.xlsx     n'écrit rien ; code 1 si quelque chose reste à purger
"""
from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

AUTEUR_NEUTRE = "Facil"
AUTEURS_OUTILS = {AUTEUR_NEUTRE, "openpyxl"}   # générateurs, pas des personnes
_LIEN = re.compile(r"^xl/externalLinks/")
_NOM = re.compile(r"<definedName\b([^>]*)>(.*?)</definedName>", re.S)
_EXTERNE = re.compile(r"\[\d+\]")


def _nom_a_retirer(attributs: str, valeur: str) -> bool:
    """Un nom part s'il désigne un autre classeur, s'il est caché (résidus de macros et de vues), ou s'il ne mène plus
    nulle part. Les noms système (_xlnm.Print_Area…) et les noms utiles du modèle restent."""
    if "_xlnm." in attributs:
        return bool(_EXTERNE.search(valeur))
    return bool(_EXTERNE.search(valeur)) or 'hidden="1"' in attributs or valeur.strip() in {"#REF!", "=#REF!"} \
        or re.fullmatch(r"'?[^!]*'?!#REF!", valeur.strip()) is not None


def diagnostic(chemin: Path) -> dict:
    with zipfile.ZipFile(chemin) as z:
        noms = z.namelist()
        wb = z.read("xl/workbook.xml").decode("utf-8")
        core = z.read("docProps/core.xml").decode("utf-8") if "docProps/core.xml" in noms else ""
        app = z.read("docProps/app.xml").decode("utf-8") if "docProps/app.xml" in noms else ""
    personnes = re.findall(r"<(?:dc:creator|cp:lastModifiedBy)>([^<]*)<", core) + re.findall(r"<(?:Company|Manager)>([^<]*)<", app)
    return {
        "liaisons_externes": sum(1 for n in noms if _LIEN.match(n) and n.endswith(".xml") and "/_rels/" not in n),
        "noms_a_retirer": sum(1 for a, v in _NOM.findall(wb) if _nom_a_retirer(a, v)),
        "proprietes_nominatives": [p for p in personnes if p and p not in AUTEURS_OUTILS],
    }


def a_purger(d: dict) -> bool:
    return bool(d["liaisons_externes"] or d["noms_a_retirer"] or d["proprietes_nominatives"])


def purger(chemin: Path) -> dict:
    avant = diagnostic(chemin)
    with zipfile.ZipFile(chemin) as z:
        parts = {i.filename: (i, z.read(i.filename)) for i in z.infolist()}

    sortie = {}
    for nom, (info, data) in parts.items():
        if _LIEN.match(nom):
            continue                                   # liaisons externes, leurs caches et leurs relations
        if nom == "xl/workbook.xml":
            t = data.decode("utf-8")
            t = re.sub(r"<externalReferences>.*?</externalReferences>", "", t, flags=re.S)
            t = _NOM.sub(lambda m: "" if _nom_a_retirer(m.group(1), m.group(2)) else m.group(0), t)
            t = re.sub(r"<definedNames>\s*</definedNames>", "", t)
            data = t.encode("utf-8")
        elif nom == "xl/_rels/workbook.xml.rels":
            t = data.decode("utf-8")
            data = re.sub(r"<Relationship\b[^>]*Target=\"externalLinks/[^\"]*\"[^>]*/>", "", t).encode("utf-8")
        elif nom == "[Content_Types].xml":
            t = data.decode("utf-8")
            data = re.sub(r"<Override\b[^>]*PartName=\"/xl/externalLinks/[^\"]*\"[^>]*/>", "", t).encode("utf-8")
        elif nom == "docProps/core.xml":
            t = data.decode("utf-8")
            t = re.sub(r"(<(dc:creator|cp:lastModifiedBy)>)[^<]*(</\2>)", rf"\g<1>{AUTEUR_NEUTRE}\g<3>", t)
            data = t.encode("utf-8")
        elif nom == "docProps/app.xml":
            t = data.decode("utf-8")
            data = re.sub(r"<(Company|Manager)>[^<]*</\1>", r"<\1></\1>", t).encode("utf-8")
        sortie[nom] = (info, data)

    tmp = chemin.with_suffix(".purge.tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for nom, (info, data) in sortie.items():
            z.writestr(info, data)
    tmp.replace(chemin)
    return {"avant": avant, "apres": diagnostic(chemin)}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("fichiers", nargs="+", type=Path)
    p.add_argument("--verifier", action="store_true", help="contrôle seulement (garde de CI)")
    a = p.parse_args()
    rouge = 0
    for f in a.fichiers:
        if a.verifier:
            d = diagnostic(f)
            if a_purger(d):
                rouge = 1
                print(f"À PURGER  {f} : {d['liaisons_externes']} liaisons, {d['noms_a_retirer']} noms, "
                      f"{len(d['proprietes_nominatives'])} propriétés nominatives")
        else:
            r = purger(f)
            print(f"purgé  {f} : {r['avant']['liaisons_externes']} liaisons, {r['avant']['noms_a_retirer']} noms retirés ; "
                  f"reste à purger : {a_purger(r['apres'])}")
    return rouge


if __name__ == "__main__":
    sys.exit(main())
