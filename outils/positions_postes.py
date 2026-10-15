"""Compare la POSITION des postes (codes REF : AD, BH, XI…) entre deux formulaires de liasse.

  positions_postes.py <reference.xlsx> <candidat.xlsx>

Ce qui compte pour le moteur et pour la télédéclaration, c'est la cellule où chaque poste se saisit,
pas l'orthographe des libellés. Un code de poste est une cellule de 2 lettres majuscules isolée.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import openpyxl

CODE = re.compile(r"^[A-Z]{2}$")


def positions(chemin: Path) -> dict[str, dict[str, str]]:
    wb = openpyxl.load_workbook(chemin, data_only=False, read_only=True)
    sortie = {}
    for ws in wb.worksheets:
        codes = {}
        for ligne in ws.iter_rows():
            for c in ligne:
                if isinstance(c.value, str) and CODE.match(c.value.strip()):
                    codes.setdefault(c.value.strip(), c.coordinate)
        if len(codes) >= 5:  # feuille d'état (bilan, compte de résultat, TFT…)
            sortie[ws.title.strip().upper()] = codes
    return sortie


def main() -> int:
    a, b = positions(Path(sys.argv[1])), positions(Path(sys.argv[2]))
    ecarts_total = 0
    for feuille in sorted(set(a) | set(b)):
        pa, pb = a.get(feuille, {}), b.get(feuille, {})
        ecarts = [(k, pa.get(k, "∅"), pb.get(k, "∅")) for k in sorted(set(pa) | set(pb)) if pa.get(k) != pb.get(k)]
        ecarts_total += len(ecarts)
        print(f"{feuille:28} codes {len(pa):3} / {len(pb):3} · écarts de position : {len(ecarts)}"
              + (" — " + ", ".join(f"{k} {x}→{y}" for k, x, y in ecarts[:8]) if ecarts else ""))
    print(f"TOTAL écarts de position : {ecarts_total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
