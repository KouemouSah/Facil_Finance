# -*- coding: utf-8 -*-
"""Falsification de tests/test_mapping_dsf.py : chaque mutation réintroduit un défaut
(de la v1 ou rencontré en mise au point) dans une COPIE du plugin ; la garde doit échouer
sur un contrôle métier (« ÉCHEC »), pas sur un plantage.
Lancer : python tests/falsification_mapping.py   -> code 0 si toutes sont détectées.
"""
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP = os.path.join("skills", "dsf-syscohada", "references", "mapping-comptes-dsf.json")
AGR = os.path.join("skills", "dsf-syscohada", "scripts", "agreger_balance_dsf.py")
MUT = [
    ("v1 : transports décalés (61 -> RH)", MAP, '"prefixe": "61", "ref": "RG"', '"prefixe": "61", "ref": "RH"'),
    ("v1 : classe 1 à la française (12 -> CJ)", MAP, '"prefixe": "12", "ref": "CH"', '"prefixe": "12", "ref": "CJ"'),
    ("banques compensées (52 sans éclatement)", MAP,
     '{"prefixe": "52", "debiteur": "BS", "crediteur": "DR"', '{"prefixe": "52", "ref": "BS", "nature": "actif"'),
    ("fournisseur débiteur non reclassé (40 -> DJ seul)", MAP,
     '{"prefixe": "40", "debiteur": "BH", "crediteur": "DJ"', '{"prefixe": "40", "ref": "DJ", "nature": "passif"'),
    ("amortissement du transport absent (2845)", MAP, '"prefixe": "2845", "ref": "AN"', '"prefixe": "9845", "ref": "AN"'),
    ("13 toujours en résultat de l'exercice", AGR, "            if cloturee:\n                add(montant, \"CJ\"",
     "            if True:\n                add(montant, \"CJ\""),
    ("signe du compte de résultat inversé", AGR,
     'elif nature in ("passif", "gestion"):\n            add(montant, r["ref"], -solde, compte)',
     'elif nature == "passif":\n            add(montant, r["ref"], -solde, compte)\n        elif nature == "gestion":\n            add(montant, r["ref"], solde, compte)'),
    ("clôture sans classes 6-8 non signalée", AGR, "    if cloturee:   #", "    if cloturee and gestion:   #"),
    ("compensation de trésorerie non signalée", AGR, "    if compense:\n", "    if False:\n"),
    ("56 compensé comme une banque", AGR, ' and not r["prefixe"].startswith("56")', ""),
]


def main():
    aveugles = 0
    for name, rel, a, b in MUT:
        d = tempfile.mkdtemp()
        dst = os.path.join(d, "compta-ohada")
        shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns("dist", "datas", "__pycache__"))
        path = os.path.join(dst, rel)
        src = open(path, encoding="utf-8").read()
        assert src.count(a) == 1, f"motif introuvable ou multiple : {name}"
        open(path, "w", encoding="utf-8").write(src.replace(a, b))
        cp = subprocess.run([sys.executable, os.path.join(dst, "tests", "test_mapping_dsf.py")],
                            capture_output=True, text=True, encoding="utf-8")
        detectee = cp.returncode != 0 and "ÉCHEC" in cp.stdout
        aveugles += not detectee
        bilan = next((l.strip() for l in cp.stdout.splitlines() if "conformes" in l), cp.stderr.strip()[-100:])
        print(f"  {name:48s} {'détectée' if detectee else '!! NON DÉTECTÉE'}   {bilan}")
        shutil.rmtree(d, ignore_errors=True)
    sys.exit(1 if aveugles else 0)


if __name__ == "__main__":
    main()
