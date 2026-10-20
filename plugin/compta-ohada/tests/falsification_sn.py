# -*- coding: utf-8 -*-
"""Falsification de tests/test_sn.py : chaque sabotage du modèle SYSCOHADA (def_sn.py), appliqué à une COPIE du plugin,
doit faire échouer la garde sur un contrôle métier.
Lancer : python tests/falsification_sn.py   (code 0 = tous détectés)
"""
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join("skills", "dsf-syscohada", "scripts", "def_sn.py")
MUT = [
    ("formule du total général laissée fausse", "            if ws is not None and t == \"bilan paysage\":\n                self.corriger_total_general(ws)",
     "            if False:\n                self.corriger_total_general(ws)"),
    ("correspondance manuelle ignorée (15A vide)", "        out.setdefault(k, {\"roles\": {}, \"colonne_n\": None, \"lignes\": {}})[\"lignes\"].update(",
     "        (lambda *x: None)(k, {\"roles\": {}, \"colonne_n\": None, \"lignes\": {}}) or {}.update("),
    ("annexes camerounaises gardées", "            if CAMEROUN.match(plat(ws.title)):", "            if False:"),
    ("tableaux fiscaux GE non ajoutés", "                ws = wb.create_sheet(src.title[:31])\n                copier_feuille(src, ws)\n                self.ajoutees.append(ws.title)",
     "                pass"),
    ("liasse non adaptée (notes vides gardées)", "        for t, motif in retirer:\n            del wb[t]", "        for t, motif in []:\n            del wb[t]"),
    ("mentions du Cameroun laissées", "                    if p.startswith(k):\n                        c.value = v", "                    if False:\n                        c.value = v"),
    ("en-tête sans exercice ni durée", "      Durée (en mois) : 12\"", "\""),
    ("brut du bilan non écrit", "                        elif ro == \"brut\":\n                            v = agg.get(ref, {}).get(\"brut\", pN.get(ref))",
     "                        elif ro == \"brut\":\n                            v = None"),
]


def main():
    aveugles = 0
    for nom, a, b in MUT:
        d = tempfile.mkdtemp()
        dst = os.path.join(d, "compta-ohada")
        shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns("dist", "runtime", "__pycache__"))
        p = os.path.join(dst, S)
        src = open(p, encoding="utf-8").read()
        assert src.count(a) == 1, f"motif introuvable ou multiple : {nom}"
        open(p, "w", encoding="utf-8").write(src.replace(a, b))
        cp = subprocess.run([sys.executable, os.path.join(dst, "tests", "test_sn.py")], capture_output=True, text=True,
                            encoding="utf-8")
        det = cp.returncode != 0 and "ÉCHEC" in cp.stdout
        aveugles += not det
        bilan = next((l.strip() for l in cp.stdout.splitlines() if "conformes" in l), "PLANTAGE : " + cp.stderr.strip()[-90:])
        print(f"  {nom:48s} {'détectée' if det else '!! NON DÉTECTÉE'}   {bilan}")
        shutil.rmtree(d, ignore_errors=True)
    sys.exit(1 if aveugles else 0)


if __name__ == "__main__":
    main()
