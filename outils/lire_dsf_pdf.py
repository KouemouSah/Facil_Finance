"""Lit une DSF publiée en PDF texte : relève, page par page, les lignes « code de poste + montants ».

  lire_dsf_pdf.py <dsf.pdf> [--json sortie.json] [--pages]

Une ligne retenue porte un code de poste (2 lettres majuscules) et au moins un montant. Les mots sont
regroupés par ligne d'après leur position verticale. Sert aux démonstrations sur des liasses publiées.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pymupdf

CODE = re.compile(r"^[A-Z]{2}$")
MONTANT = re.compile(r"^-?\(?\d{1,3}(?:[ .  ]?\d{3})*(?:,\d+)?\)?$")


def montant(s: str) -> float | None:
    s = s.replace(" ", " ").replace(" ", " ")
    if not MONTANT.match(s.replace(" ", "")) and not MONTANT.match(s):
        return None
    neg = s.startswith("-") or (s.startswith("(") and s.endswith(")"))
    chiffres = re.sub(r"[^\d,]", "", s).replace(",", ".")
    try:
        v = float(chiffres)
    except ValueError:
        return None
    return -v if neg else v


def lignes_de_page(page) -> list[list[tuple]]:
    mots = page.get_text("words")  # x0, y0, x1, y1, mot, bloc, ligne, n°
    rangees: dict[int, list] = {}
    for x0, y0, x1, y1, mot, *_ in mots:
        cle = round((y0 + y1) / 2 / 3)  # tolérance de 3 points
        rangees.setdefault(cle, []).append((x0, x1, mot))
    return [sorted(r) for _, r in sorted(rangees.items())]


ESPACE_MAX = 4.5  # points : au-delà, deux groupes de chiffres sont dans deux colonnes différentes


def fusionner_montants(mots: list[tuple]) -> list[str]:
    """« 1 234 567 » écrit en trois mots PROCHES → un seul montant ; séparés par une gouttière → deux."""
    sortie: list[list] = []
    for x0, x1, m in mots:
        if (sortie and re.fullmatch(r"\d{3}", m) and re.fullmatch(r"-?\(?\d{1,3}(?: \d{3})*", sortie[-1][2])
                and x0 - sortie[-1][1] <= ESPACE_MAX):
            sortie[-1][2] += " " + m
            sortie[-1][1] = x1
        else:
            sortie.append([x0, x1, m])
    return [m for _, _, m in sortie]


def relever(pdf: Path) -> dict:
    doc = pymupdf.open(pdf)
    releve = {}
    for i, page in enumerate(doc, start=1):
        titre = " ".join(page.get_text().split()[:12])
        for mots in lignes_de_page(page):
            mots = fusionner_montants(mots)
            # Bilan « en paysage » : un poste d'actif ET un poste de passif sur la même ligne → deux segments.
            positions = [k for k, m in enumerate(mots) if CODE.match(m)]
            if not positions or len(positions) > 2:
                continue
            bornes = positions + [len(mots)]
            for debut, fin in zip(bornes, bornes[1:]):
                segment = mots[debut:fin]
                nombres = [v for v in (montant(m) for m in segment[1:]) if v is not None]
                if nombres:
                    releve.setdefault(segment[0], []).append({"page": i, "montants": nombres,
                                                              "ligne": " ".join(segment)[:140], "titre_page": titre[:80]})
    return releve


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("pdf"); p.add_argument("--json"); p.add_argument("--pages", action="store_true")
    a = p.parse_args()
    if a.pages:
        doc = pymupdf.open(a.pdf)
        for i, page in enumerate(doc, start=1):
            print(i, " ".join(page.get_text().split()[:14])[:150])
        return 0
    r = relever(Path(a.pdf))
    if a.json:
        Path(a.json).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"codes relevés : {len(r)}")
    for code in sorted(r)[:200]:
        e = r[code][0]
        print(f"{code}  p.{e['page']:>2}  {e['montants'][:4]}  « {e['ligne'][:70]} »")
    return 0


if __name__ == "__main__":
    sys.exit(main())
