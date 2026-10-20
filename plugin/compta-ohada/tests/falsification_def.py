# -*- coding: utf-8 -*-
"""Falsification de tests/test_def_ge.py : une mutation par règle protégée du générateur de DEF,
appliquée à une COPIE du plugin ; la garde doit échouer sur un contrôle métier.
Lancer : python tests/falsification_def.py   -> code 0 si toutes sont détectées.
"""
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = os.path.join("skills", "dsf-syscohada", "scripts", "def_ge.py")
MUT = [
    ("IS non intégré au bilan / compte de résultat", G,
     'bal, info_is = agr.avec_impot(sorted(det["soldes"].items()), impot)',
     'bal, info_is = sorted(det["soldes"].items()), {"mode": "aucun", "message": ""}'),
    ("CAFG sans réintégration des dotations", G, 'v["FA"] = g(pN, "XI") - g(pN, "RL")', 'v["FA"] = g(pN, "XI")'),
    ("annexe interne exportée avec la DEF", G, '    ws = wb.create_sheet("Controles")\n',
     '    ws = wb.create_sheet("Controles"); feuilles_def.append("Controles")\n'),
    ("acquisitions de la note 3 non reprises au TFT", G, 'v["FF"], v["FG"] = -aug(incorp), -aug(corp)',
     'v["FF"], v["FG"] = 0.0, 0.0'),
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
        cp = subprocess.run([sys.executable, os.path.join(dst, "tests", "test_def_ge.py")],
                            capture_output=True, text=True, encoding="utf-8")
        detectee = cp.returncode != 0 and "ÉCHEC" in cp.stdout
        aveugles += not detectee
        bilan = next((l.strip() for l in cp.stdout.splitlines() if "conformes" in l), "PLANTAGE : " + cp.stderr.strip()[-90:])
        print(f"  {name:50s} {'détectée' if detectee else '!! NON DÉTECTÉE'}   {bilan}")
        shutil.rmtree(d, ignore_errors=True)
    sys.exit(1 if aveugles else 0)


if __name__ == "__main__":
    main()
