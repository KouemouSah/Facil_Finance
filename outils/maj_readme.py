"""Dérive les blocs générés du README depuis leur source unique, au lieu de les recopier.

  python outils/maj_readme.py            réécrit les blocs
  python outils/maj_readme.py --check    code 1 si le README a divergé de sa source (garde de CI)

Bloc géré : la feuille de route (Gantt Mermaid), source docs/plans/calendrier.yml, entre
<!-- gantt:debut --> et <!-- gantt:fin -->.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEPOT = Path(__file__).resolve().parents[1]
README = DEPOT / "README.md"
sys.path.insert(0, str(DEPOT / "docs" / "outils"))

from calendrier import Calendrier  # noqa: E402

BLOC = re.compile(r"(<!-- gantt:debut -->\n)(?:.*?\n)?(<!-- gantt:fin -->)", re.S)


def attendu(texte: str) -> str:
    cal = Calendrier(DEPOT / "docs" / "plans" / "calendrier.yml", produit="Facil Finance")
    if not BLOC.search(texte):
        raise SystemExit("README : marqueurs <!-- gantt:debut --> / <!-- gantt:fin --> introuvables")
    return BLOC.sub(lambda m: m.group(1) + cal.gantt().strip() + "\n" + m.group(2), texte)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--check", action="store_true")
    a = p.parse_args()
    actuel = README.read_text(encoding="utf-8")
    nouveau = attendu(actuel)
    if a.check:
        if nouveau != actuel:
            print("README divergent de docs/plans/calendrier.yml : lancer python outils/maj_readme.py")
            return 1
        print("README conforme à ses sources")
        return 0
    README.write_text(nouveau, encoding="utf-8", newline="\n")
    print("README : feuille de route régénérée depuis calendrier.yml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
