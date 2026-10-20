# -*- coding: utf-8 -*-
"""Falsification de tests/test_detection_balance.py : une mutation par règle protégée.

Chaque mutation réintroduit un défaut réellement rencontré. Elle est appliquée à une COPIE
du plugin (lib/ puis synchronisation vers les skills) ; la garde doit échouer sur un
contrôle métier (« ÉCHEC »), pas sur un plantage.
Lancer : python tests/falsification_detection.py   -> code 0 si toutes sont détectées.
"""
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join("lib", "detection_balance.py")
AGR = os.path.join("skills", "dsf-syscohada", "scripts", "agreger_balance_dsf.py")
CLS = os.path.join("skills", "dsf-syscohada", "scripts", "classer_documents.py")
MUT = [
    ("net des paires ignoré (solde des soldes)", LIB, "return k % 2 == 0 and all(", "return False and all("),
    ("critère solde_gestion_active neutralisé", LIB, "len(gestion) else 0.3", "len(gestion) else 1.0"),
    ("parents traités dans l'ordre du fichier", LIB, 'key=lambda x: -len(x["acc"])', "key=lambda x: 0"),
    ("montant accepté comme numéro de compte", LIB, "j == first and j <= 3", "j <= 3"),
    ("lignes hors colonnes gardées comme comptes", LIB,
     'cand = [r for r in cand if any(c in cols for c, _ in r["nums"])]', "cand = cand"),
    ("dates .xlsx (entiers) non reconnues", CLS,
     "isinstance(v, (int, float)) and not isinstance(v, bool)", "isinstance(v, float)"),
    ("repli par en-têtes supprimé", CLS, "(2 if par_entetes else 0)", "0"),
    ("agrégation poursuivie malgré l'ambiguïté", AGR,
     '        print("Gabarits possibles : " + " | ".join([res["gabarit"]] + res["rivaux"]), file=sys.stderr)\n        raise SystemExit(2)',
     '        print("Gabarits possibles : " + " | ".join([res["gabarit"]] + res["rivaux"]), file=sys.stderr)'),
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
        subprocess.run([sys.executable, os.path.join(dst, "tools", "sync_lib.py")], capture_output=True)
        env = {k: v for k, v in os.environ.items() if not k.startswith(("DSF_", "VARIANTES_"))}
        cp = subprocess.run([sys.executable, os.path.join(dst, "tests", "test_detection_balance.py")],
                            capture_output=True, text=True, encoding="utf-8", env=env)
        detectee = cp.returncode != 0 and "ÉCHEC" in cp.stdout
        aveugles += not detectee
        bilan = next((l.strip() for l in cp.stdout.splitlines() if "conformes" in l), cp.stderr.strip()[-100:])
        print(f"  {name:45s} {'détectée' if detectee else '!! NON DÉTECTÉE'}   {bilan}")
        shutil.rmtree(d, ignore_errors=True)
    sys.exit(1 if aveugles else 0)


if __name__ == "__main__":
    main()
