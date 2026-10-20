# -*- coding: utf-8 -*-
"""Falsification des gardes « sans Excel » : évaluateur de formules (test_formules_xl) et rendu natif (test_rendu_pdf).
Lancer : python tests/falsification_rendu.py   -> code 0 si toutes sont détectées.
"""
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join("skills", "dsf-syscohada", "scripts", "formules_xl.py")
R = os.path.join("skills", "dsf-syscohada", "scripts", "rendu_pdf.py")
MUT = [
    ("ROUND arrondi « au pair » (banquier)", F, "rounding=ROUND_HALF_UP", "rounding='ROUND_HALF_EVEN'", "test_formules_xl.py"),
    ("N() rend le texte au lieu de 0", F, "r = float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else (1.0 if v is True else 0.0)",
     "r = v", "test_formules_xl.py"),
    ("division par zéro sans #DIV/0!", F, '                a = Erreur("#DIV/0!")', "                a = 0.0", "test_formules_xl.py"),
    ("IF évalue les deux branches (erreur propagée)", F,
     "            r = arg(1) if vrai(arg(0)) else (arg(2) if n > 2 else False)",
     "            r = (arg(1), arg(2))[0] if vrai(arg(0)) else (arg(2) if n > 2 else False)", "test_formules_xl.py"),
    ("négatifs sans parenthèses", R, 'return f"({s})" if v < 0 and "(" in f else', 'return f"-{s}" if v < 0 and "(" in f else',
     "test_rendu_pdf.py"),
    ("montant jamais réduit (débordement)", R, "                if besoin < corps:", "                if False:", "test_rendu_pdf.py"),
    ("« une page » ignoré", R, "        une_page = bool(ws.page_setup.fitToHeight == 1 and ws.sheet_properties.pageSetUpPr.fitToPage)",
     "        une_page = False", "test_rendu_pdf.py"),
    ("pied de page sans total de pages", R, '.replace("&N", str(n))', '.replace("&N", "?")', "test_rendu_pdf.py"),
]


def main():
    aveugles = 0
    for name, rel, a, b, test in MUT:
        d = tempfile.mkdtemp()
        dst = os.path.join(d, "compta-ohada")
        shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns("dist", "datas", "__pycache__"))
        path = os.path.join(dst, rel)
        src = open(path, encoding="utf-8").read()
        assert src.count(a) == 1, f"motif introuvable ou multiple : {name}"
        open(path, "w", encoding="utf-8").write(src.replace(a, b))
        cp = subprocess.run([sys.executable, os.path.join(dst, "tests", test)], capture_output=True, text=True, encoding="utf-8")
        detectee = cp.returncode != 0 and "ÉCHEC" in cp.stdout
        aveugles += not detectee
        bilan = next((l.strip() for l in cp.stdout.splitlines() if "conformes" in l), "PLANTAGE : " + cp.stderr.strip()[-90:])
        print(f"  {name:48s} {'détectée' if detectee else '!! NON DÉTECTÉE'}   {bilan}")
        shutil.rmtree(d, ignore_errors=True)
    sys.exit(1 if aveugles else 0)


if __name__ == "__main__":
    main()
