# -*- coding: utf-8 -*-
"""Falsification de tests/test_tf345_ge.py : une mutation par règle protégée (dont les défauts réellement
rencontrés en mise au point), appliquée à une COPIE du plugin ; la garde doit échouer sur un contrôle métier.
Lancer : python tests/falsification_tf345.py   -> code 0 si toutes sont détectées.
"""
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = os.path.join("lib", "grand_livre.py")
T = os.path.join("lib", "tf345_ge.py")
MUT = [
    ("paiement au Trésor retranché de l'IVA facturée", T,
     "        if x[\"piece\"] in pieces_paiement:\n            if", "        if False:\n            if"),
    ("question « CA sans IVA » jamais posée", T, "        if rep is None:\n            questions.append(",
     "        if False:\n            questions.append("),
    ("grand livre « à plat » : colonne compte ignorée", G, "    for j in range(0, 8):\n        vals =",
     "    for j in range(0, 0):\n        vals ="),
    ("solde progressif exigé à 80 % d'utilisation", G, "if excl >= 0.9 and util >= 0.3:", "if excl >= 0.9 and util >= 0.8:"),
    ("lignes « Total compte au <date> » prises pour des écritures", G,
     "        if any(isinstance(v, str) and _SYNTHESE.match(v.strip()) for v in cells[first:first + 3]):\n            continue",
     "        pass"),
    ("IRPF non national non reconnu (libellé ignoré)", T,
     'return "non_national" if any(re.search(r"\\b" + re.escape(m), lib) for m in mots) else "national"',
     'return "national"'),
    ("charges sans code tiers passées sous silence", T,
     "            s = sans[x[\"compte\"]]; s[\"ht\"] += x[\"debit\"] - x[\"credit\"]; s[\"n\"] += 1\n",
     "            pass\n"),
    ("nom suggéré dépendant de l'ordre d'un ensemble", T, 'return " ".join(ordre[:3])',
     'return " ".join(list(set(ordre))[:3])'),
    ("taux d'IVA écrit en dur dans la formule", T, 'ws[f"{col}{rr}"] = f"=ROUND(H{rr}/{T},2)"',
     'ws[f"{col}{rr}"] = f"=ROUND(H{rr}/0.15,2)"'),
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
        cp = subprocess.run([sys.executable, os.path.join(dst, "tests", "test_tf345_ge.py")],
                            capture_output=True, text=True, encoding="utf-8")
        detectee = cp.returncode != 0 and "ÉCHEC" in cp.stdout
        aveugles += not detectee
        bilan = next((l.strip() for l in cp.stdout.splitlines() if "conformes" in l), "PLANTAGE : " + cp.stderr.strip()[-90:])
        print(f"  {name:55s} {'détectée' if detectee else '!! NON DÉTECTÉE'}   {bilan}")
        shutil.rmtree(d, ignore_errors=True)
    sys.exit(1 if aveugles else 0)


if __name__ == "__main__":
    main()
