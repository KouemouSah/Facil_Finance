# -*- coding: utf-8 -*-
"""Rejoue TOUTES les gardes du plugin (tests/test_*.py) avec le Python EMBARQUÉ (runtime/python.exe), sans aucun autre
Python : c'est la preuve que le plugin fonctionne sur un poste où Python n'est pas installé.
Lancer : python tools/gardes_sur_runtime.py      (code 0 = toutes conformes)
"""
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(ROOT, "runtime", "python.exe")


def main():
    if not os.path.exists(PY):
        print("runtime absent : python tools/construire_runtime.py")
        return 1
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV")}
    env["FACIL_PDF"] = "natif"                            # un poste sans Excel : rendu natif
    echecs = 0
    for t in sorted(os.listdir(os.path.join(ROOT, "tests"))):
        if not (t.startswith("test_") and t.endswith(".py")):
            continue
        cp = subprocess.run([PY, os.path.join(ROOT, "tests", t)], capture_output=True, text=True, encoding="utf-8",
                            errors="replace", env=env, timeout=1800)
        bilan = next((l.strip() for l in cp.stdout.splitlines() if "conformes" in l), (cp.stderr.strip().splitlines() or ["?"])[-1])
        print(f"  {t:32s} {'OK   ' if cp.returncode == 0 else 'ÉCHEC'} {bilan}")
        echecs += cp.returncode != 0
    print(f"\n{'toutes les gardes passent sur le runtime embarqué' if not echecs else f'{echecs} garde(s) en échec'}")
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
