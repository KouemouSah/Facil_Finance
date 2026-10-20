# -*- coding: utf-8 -*-
"""Intègre un tableau Excel dans un rapport/deck — LECTURE DÉTERMINISTE.

Lit une plage d'un classeur (valeurs exactes, jamais re-saisies) et l'exporte en :
  - tableau Markdown (pour les rapports .md → PDF/DOCX)
  - tableau HTML `table.fin` (pour les decks presentation-decks) [option --html]

But : ancrer les chiffres réels (pas d'invention). La 1re ligne de la plage = en-têtes.

⚠ Les cellules de FORMULE ne sont lues que si le classeur a été recalculé/enregistré
par Excel (openpyxl lit la valeur en cache). Sinon, fournir un export de valeurs.

Usage :
  python xlsx_to_table.py --fichier data.xlsx --feuille "SIG" --plage A3:E12
  python xlsx_to_table.py --fichier data.xlsx --html
"""
import argparse
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def _fmt(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, (int, float)):
        if float(v).is_integer():
            return f"{int(v):,}".replace(",", " ")
        return f"{v:,.2f}".replace(",", " ").replace(".", ",")
    return str(v).strip()


def _is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def read_range(path, feuille, plage):
    from openpyxl import load_workbook
    wb = load_workbook(path, data_only=True)
    ws = wb[feuille] if feuille else wb[wb.sheetnames[0]]
    if plage:
        cells = ws[plage]
        rows = [[c.value for c in row] for row in cells]
    else:
        rows = [[c for c in r] for r in ws.iter_rows(values_only=True)]
    wb.close()
    # retirer lignes entièrement vides
    rows = [r for r in rows if any(x not in (None, "") for x in r)]
    return rows


def to_markdown(rows):
    if not rows:
        return "_(plage vide)_"
    header, body = rows[0], rows[1:]
    ncol = len(header)
    # colonnes numériques = majorité de nombres dans le corps
    numeric = []
    for j in range(ncol):
        vals = [r[j] for r in body if j < len(r)]
        nums = sum(1 for v in vals if _is_num(v))
        numeric.append(vals and nums >= max(1, len(vals) // 2))
    head = "| " + " | ".join(_fmt(h) or f"col{j+1}" for j, h in enumerate(header)) + " |"
    sep = "| " + " | ".join(("---:" if numeric[j] else ":---") for j in range(ncol)) + " |"
    out = [head, sep]
    for r in body:
        cells = [_fmt(r[j]) if j < len(r) else "" for j in range(ncol)]
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def to_table_fin(rows):
    if not rows:
        return "<!-- plage vide -->"
    header, body = rows[0], rows[1:]
    ncol = len(header)
    numeric = []
    for j in range(ncol):
        vals = [r[j] for r in body if j < len(r)]
        nums = sum(1 for v in vals if _is_num(v))
        numeric.append(vals and nums >= max(1, len(vals) // 2))
    h = "".join(f'<th class="num">{_fmt(x)}</th>' if numeric[j] else f'<th>{_fmt(x)}</th>'
                for j, x in enumerate(header))
    lines = [f'<table class="fin"><thead><tr>{h}</tr></thead><tbody>']
    for r in body:
        tds = "".join(f'<td class="num">{_fmt(r[j]) if j < len(r) else ""}</td>' if numeric[j]
                      else f'<td>{_fmt(r[j]) if j < len(r) else ""}</td>' for j in range(ncol))
        lines.append(f"<tr>{tds}</tr>")
    lines.append("</tbody></table>")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description="Excel -> tableau Markdown / table.fin (déterministe).")
    p.add_argument("--fichier", required=True)
    p.add_argument("--feuille", default=None)
    p.add_argument("--plage", default=None, help="ex. A3:E12 (défaut : plage utilisée)")
    p.add_argument("--html", action="store_true", help="émettre aussi le HTML table.fin")
    a = p.parse_args()
    rows = read_range(a.fichier, a.feuille, a.plage)
    print("=== Markdown ===")
    print(to_markdown(rows))
    if a.html:
        print("\n=== HTML table.fin ===")
        print(to_table_fin(rows))
    print("\n(valeurs exactes lues du classeur — ne pas re-saisir à la main)", file=sys.stderr)


if __name__ == "__main__":
    main()
