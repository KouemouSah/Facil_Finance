"""Publie le noyau du moteur (source unique) vers le plugin compta-ohada, puis vérifie la parité.

  publier_vers_plugin.py [--plugin C:/DSF/compta-ohada]          copie, puis lance sync_lib.py du plugin
  publier_vers_plugin.py --check [--plugin …]                     code 1 si une copie du plugin diverge

Le plugin reste installable seul (il embarque ses copies) ; mais ses copies ne se modifient plus chez lui.
"""
from __future__ import annotations

import argparse
import filecmp
import shutil
import subprocess
import sys
from pathlib import Path

NOYAU = Path(__file__).resolve().parents[1] / "facil_moteur" / "noyau"
# module du noyau → emplacement de sa source dans le plugin (que sync_lib.py redistribue ensuite)
DESTINATIONS = {
    "detection_balance.py": "lib/detection_balance.py",
    "grand_livre.py": "lib/grand_livre.py",
    "rendu_pdf.py": "lib/rendu_pdf.py",
    "formules_xl.py": "skills/dsf-syscohada/scripts/formules_xl.py",
}


def ecarts(plugin: Path) -> list[str]:
    return [f"{m} ≠ {d}" for m, d in DESTINATIONS.items()
            if not (plugin / d).exists() or not filecmp.cmp(NOYAU / m, plugin / d, shallow=False)]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--plugin", default=str(Path(__file__).resolve().parents[2] / "compta-ohada"))
    p.add_argument("--check", action="store_true")
    a = p.parse_args()
    plugin = Path(a.plugin)
    if a.check:
        e = ecarts(plugin)
        print("parité noyau ↔ plugin :", "conforme" if not e else "DIVERGENCE — " + " ; ".join(e))
        return 1 if e else 0
    for m, d in DESTINATIONS.items():
        shutil.copy2(NOYAU / m, plugin / d)
    sync = plugin / "tools" / "sync_lib.py"
    if sync.exists():
        r = subprocess.run([sys.executable, str(sync)], capture_output=True, text=True, encoding="utf-8", errors="replace")
        print(r.stdout.strip()[-400:])
        if r.returncode:
            print(r.stderr[-400:]); return r.returncode
    e = ecarts(plugin)
    print("publié :", len(DESTINATIONS), "module(s) ;", "parité conforme" if not e else "DIVERGENCE " + "; ".join(e))
    return 1 if e else 0


if __name__ == "__main__":
    sys.exit(main())
