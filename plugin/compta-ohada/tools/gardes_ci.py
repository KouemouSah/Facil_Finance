# -*- coding: utf-8 -*-
"""Rejoue TOUTES les gardes du plugin (tests/test_*.py) avec le Python qui lance ce script : celui de la CI, ou
d'une session Claude Code web. Pendant de tools/gardes_sur_runtime.py, qui les rejoue sur le runtime EMBARQUÉ.

Lancer : python tools/gardes_ci.py [motif]      (code 0 = toutes conformes ; motif : filtre sur le nom du test)

Chaque garde a un délai : une garde qui pend (gel d'un serveur MCP, incident du 19/10/2026) échoue au lieu de
bloquer la chaîne.
"""
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DELAI = int(os.environ.get("FACIL_DELAI_GARDE", "2700"))


def main():
    motif = sys.argv[1] if len(sys.argv) > 1 else ""
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME")}
    env.setdefault("FACIL_PDF", "natif")                 # pas d'Excel en CI : rendu natif
    env["PYTHONIOENCODING"] = "utf-8"
    echecs, debut_total = [], time.time()
    tests = sorted(t for t in os.listdir(os.path.join(ROOT, "tests"))
                   if t.startswith("test_") and t.endswith(".py") and motif in t)
    for t in tests:
        debut = time.time()
        try:
            cp = subprocess.run([sys.executable, os.path.join(ROOT, "tests", t)], capture_output=True, text=True,
                                encoding="utf-8", errors="replace", env=env, timeout=DELAI, cwd=ROOT)
            code, sortie, erreur = cp.returncode, cp.stdout, cp.stderr
        except subprocess.TimeoutExpired:
            code, sortie, erreur = 124, "", f"délai de {DELAI} s dépassé"
        bilan = next((l.strip() for l in sortie.splitlines() if "conformes" in l),
                     (erreur.strip().splitlines() or ["?"])[-1])
        print(f"  {t:32s} {'OK   ' if code == 0 else 'ÉCHEC'} {time.time() - debut:6.1f} s  {bilan}", flush=True)
        if code:
            echecs.append(t)
            print("\n".join("      | " + l for l in (sortie + "\n" + erreur).strip().splitlines()[-25:]), flush=True)
    print(f"\n{len(tests) - len(echecs)}/{len(tests)} gardes conformes en {time.time() - debut_total:.0f} s"
          + (f" ; en échec : {', '.join(echecs)}" if echecs else ""))
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
