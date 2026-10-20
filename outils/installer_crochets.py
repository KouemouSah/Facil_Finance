"""Installe le crochet git pre-commit du dépôt : vérification complète et garde de confidentialité.

  python outils/installer_crochets.py

Le crochet refuse un commit rouge. Il utilise le Python de .venv s'il existe, sinon celui qui lance ce script.
"""
from __future__ import annotations

import stat
import subprocess
import sys
from pathlib import Path

DEPOT = Path(__file__).resolve().parents[1]

CROCHET = """#!/bin/sh
# Installé par outils/installer_crochets.py : refuse le commit si les packs, les tests, la parité ou la
# garde de confidentialité échouent. Ne jamais contourner par --no-verify.
RACINE="$(git rev-parse --show-toplevel)"
for PY in "$RACINE/.venv/Scripts/python.exe" "$RACINE/.venv/bin/python" "{secours}"; do
  [ -x "$PY" ] && break
done
"$PY" "$RACINE/outils/verifier_tout.py" || exit 1
"$PY" "$RACINE/outils/garde_confidentialite.py" || exit 1
"""


def main() -> int:
    dossier = Path(subprocess.run(["git", "rev-parse", "--git-path", "hooks"], cwd=DEPOT, capture_output=True,
                                  text=True, check=True).stdout.strip())
    if not dossier.is_absolute():
        dossier = DEPOT / dossier
    dossier.mkdir(parents=True, exist_ok=True)
    cible = dossier / "pre-commit"
    cible.write_text(CROCHET.replace("{secours}", Path(sys.executable).as_posix()), encoding="utf-8", newline="\n")
    cible.chmod(cible.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    print(f"crochet installé : {cible}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
