# -*- coding: utf-8 -*-
"""Falsification de tests/test_grand_livre_seul.py : chaque sabotage, appliqué à une COPIE du plugin, doit faire
échouer la garde sur un contrôle métier.
Lancer : python tests/falsification_grand_livre_seul.py   (code 0 = tous détectés)
"""
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join("skills", "dsf-syscohada", "scripts")
GL, ED, CD = os.path.join(S, "grand_livre.py"), os.path.join(S, "espace_def.py"), os.path.join(S, "classer_documents.py")
MUT = [
    ("comptes centralisés ignorés", GL, "        if p[\"compte\"] in detailles:\n            continue",
     "        if True:\n            continue"),
    ("écriture de clôture comptée", GL, "        if x[\"piece\"] and x[\"piece\"] in cloture:\n            continue",
     "        if False:\n            continue"),
    ("« report » dans un libellé pris pour une ouverture", GL,
     "_JOURNAL_AN.match(x[\"journal\"] or \"\") or _LIB_AN.match(x[\"libelle\"] or \"\")",
     "_JOURNAL_AN.match(x[\"journal\"] or \"\") or _OUVERTURE.search(x[\"libelle\"] or \"\")"),
    ("à-nouveau daté compté en mouvement", GL, "_JOURNAL_AN.match(x[\"journal\"] or \"\") or _LIB_AN",
     "False or _LIB_AN"),
    ("grand livre déséquilibré accepté", ED, "        if not ctrl[\"equilibree\"]:", "        if False:"),
    ("vraies dates .xlsx non reconnues", CD,
     "            date = serie or vraie or bool(", "            date = serie or bool("),
]


def main():
    aveugles = 0
    for nom, rel, a, b in MUT:
        d = tempfile.mkdtemp()
        dst = os.path.join(d, "compta-ohada")
        shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns("dist", "runtime", "__pycache__"))
        p = os.path.join(dst, rel)
        src = open(p, encoding="utf-8").read()
        assert src.count(a) == 1, f"motif introuvable ou multiple : {nom}"
        open(p, "w", encoding="utf-8").write(src.replace(a, b))
        cp = subprocess.run([sys.executable, os.path.join(dst, "tests", "test_grand_livre_seul.py")],
                            capture_output=True, text=True, encoding="utf-8")
        det = cp.returncode != 0 and "ÉCHEC" in cp.stdout
        aveugles += not det
        bilan = next((l.strip() for l in cp.stdout.splitlines() if "conformes" in l), "PLANTAGE : " + cp.stderr.strip()[-90:])
        print(f"  {nom:52s} {'détectée' if det else '!! NON DÉTECTÉE'}   {bilan}")
        shutil.rmtree(d, ignore_errors=True)
    sys.exit(1 if aveugles else 0)


if __name__ == "__main__":
    main()
