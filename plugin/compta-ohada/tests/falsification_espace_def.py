# -*- coding: utf-8 -*-
"""Falsification de tests/test_espace_def.py : une mutation par règle protégée du dossier de travail.
Lancer : python tests/falsification_espace_def.py   -> code 0 si toutes sont détectées.
"""
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = os.path.join("skills", "dsf-syscohada", "scripts", "espace_def.py")
MUT = [
    ("validation sans vérifier les questions ouvertes", E,
     '    return [x for x in qs if x["obligatoire"] and x.get("reponse") in (None, "")]', "    return []"),
    ("versions écrasées (toujours v1)", E,
     '    k = len(man.get("versions", [])) + 1', "    k = 1"),
    ("n'importe quelle image prise pour le logo", E,
     '    if "logo" not in n:\n        return 0', '    if False:\n        return 0'),
    ("version projet non signalée dans le nom", E,
     '    suffixe = "" if definitif else "_projet"', '    suffixe = ""'),
    ("réponse hors choix acceptée", E,
     '    if q and q.get("options") and valeur not in q["options"]:', "    if False:"),
    ("calcul lancé sans balance", E,
     "    if not bal:\n        bloquantes.append(", "    if False:\n        bloquantes.append("),
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
        cp = subprocess.run([sys.executable, os.path.join(dst, "tests", "test_espace_def.py")],
                            capture_output=True, text=True, encoding="utf-8")
        detectee = cp.returncode != 0 and "ÉCHEC" in cp.stdout
        aveugles += not detectee
        bilan = next((l.strip() for l in cp.stdout.splitlines() if "conformes" in l), "PLANTAGE : " + cp.stderr.strip()[-90:])
        print(f"  {name:48s} {'détectée' if detectee else '!! NON DÉTECTÉE'}   {bilan}")
        shutil.rmtree(d, ignore_errors=True)
    sys.exit(1 if aveugles else 0)


if __name__ == "__main__":
    main()
