"""Recette unique de vérification du dépôt — lancée avant chaque commit (crochet git pre-commit).

  verifier_tout.py

1. validation de tous les packs (format, sources, signatures)
2. tests et contre-épreuves (pytest)
3. parité du noyau avec le plugin compta-ohada (plugin/compta-ohada, dans le dépôt)
Code 1 dès qu'une étape échoue : le commit est refusé.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

DEPOT = Path(__file__).resolve().parents[1]
ETAPES = [
    ("packs", [sys.executable, str(DEPOT / "outils" / "facil_pack.py"), "valider-tout"]),
    ("tests", [sys.executable, "-m", "pytest", "-q", str(DEPOT / "tests")]),
    ("parité noyau ↔ plugin", [sys.executable, str(DEPOT / "outils" / "publier_vers_plugin.py"), "--check"]),
]


def main() -> int:
    echec = False
    for nom, commande in ETAPES:
        r = subprocess.run(commande, cwd=DEPOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        derniere = (r.stdout.strip().splitlines() or [""])[-1]
        print(f"[{'ok' if r.returncode == 0 else 'ÉCHEC'}] {nom} — {derniere}")
        if r.returncode:
            print(r.stdout[-1500:], r.stderr[-800:]); echec = True
    return 1 if echec else 0


if __name__ == "__main__":
    sys.exit(main())
