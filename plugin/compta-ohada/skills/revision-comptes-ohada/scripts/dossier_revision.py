# -*- coding: utf-8 -*-
"""Dossier de révision par cycle (moteur déterministe) — SYSCOHADA.

LECTURE PAR INVARIANTS COMPTABLES (detection_balance.py, copie synchronisée de lib/) :
aucun nom de colonne n'est présupposé. Sources du N-1, par ordre de préférence :
  1. colonnes « soldes N-1 » de la balance (gabarits « soldes N-1, soldes N ») ;
  2. à défaut, colonnes d'OUVERTURE : exactes pour le bilan (classes 1-5), mais les
     charges et produits N-1 sont alors INCONNUS (0) — signalé, jamais caché.
Si la détection est ambiguë (ex. deux paires de soldes sans en-tête), le script
s'arrête et demande --gabarit "<nom>".

Rattache chaque compte à un CYCLE (racine SYSCOHADA), produit les feuilles maîtresses
par cycle avec variation N/N-1 et alerte au-delà d'un seuil.

Usage :
  python dossier_revision.py --balance balance.xls --seuil 0.10
  python dossier_revision.py --balance b.xlsx --gabarit "4 col. (soldes N-1, soldes N)"
"""
import argparse
import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from detection_balance import LAYOUTS, analyse, rapport  # noqa: E402

CYCLES = [("40", "Achats/Fournisseurs"), ("41", "Ventes/Clients"), ("42", "Personnel"),
          ("43", "Personnel"), ("44", "État/Fiscal"), ("46", "Groupe/Associés"),
          ("47", "Débiteurs-créditeurs divers"), ("48", "HAO"), ("49", "Dépréciations"),
          ("1", "Capitaux"), ("2", "Immobilisations"), ("3", "Stocks"),
          ("5", "Trésorerie"), ("6", "Charges"), ("7", "Produits"), ("8", "HAO")]


def cycle_of(compte):
    c = str(compte).strip()
    for pref, lib in sorted(CYCLES, key=lambda x: -len(x[0])):
        if c.startswith(pref):
            return lib
    return "Non classé"


def read_balance(path, gabarit=None):
    """[{compte, libelle, solde_n, solde_n1}] + source du N-1 ('soldes N-1' | 'ouverture')."""
    res = analyse(path, gabarit)
    print(rapport(res), file=sys.stderr)
    if res["statut"] == "illisible":
        raise SystemExit(2)
    if res["statut"] == "ambigu":
        print("Gabarits possibles : " + " | ".join([res["gabarit"]] + res["rivaux"]), file=sys.stderr)
        raise SystemExit(2)
    if res.get("soldes_n1"):
        n1, source = res["soldes_n1"], "soldes N-1"
    elif res.get("soldes_ouverture"):
        n1, source = res["soldes_ouverture"], "ouverture"
        print("[révision] N-1 tiré des soldes d'OUVERTURE : exact pour le bilan ; charges et produits N-1 "
              "inconnus (0) — leurs variations ne sont pas significatives.", file=sys.stderr)
    else:
        raise SystemExit("[révision] Cette balance ne contient pas de N-1 (ni soldes N-1, ni ouverture). "
                         "Fournir une balance comparative, ou la balance N-1 à part.")
    lib = res.get("libelles", {})
    rows = [{"compte": a, "libelle": lib.get(a, ""), "solde_n": s, "solde_n1": n1.get(a, 0.0)}
            for a, s in sorted(res["soldes"].items())]
    return rows, source


def build(balance, seuil, source="soldes N-1"):
    cycles = {}
    for row in balance:
        sn, sn1 = row["solde_n"], row["solde_n1"]
        var = round(sn - sn1, 2)
        pct = (var / abs(sn1)) if sn1 else None
        gestion_sans_n1 = source == "ouverture" and str(row["compte"])[:1] in "678"
        alerte = not gestion_sans_n1 and ((pct is not None and abs(pct) >= seuil) or (sn1 == 0 and sn != 0))
        c = cycles.setdefault(cycle_of(row["compte"]), {"lignes": [], "tot_n": 0.0, "tot_n1": 0.0})
        c["lignes"].append({"compte": row["compte"], "libelle": row["libelle"], "solde_n": round(sn, 2),
                            "solde_n1": None if gestion_sans_n1 else round(sn1, 2), "variation": var,
                            "pct": (round(pct, 4) if pct is not None else None), "alerte": bool(alerte)})
        c["tot_n"] = round(c["tot_n"] + sn, 2); c["tot_n1"] = round(c["tot_n1"] + sn1, 2)
    return cycles


def main():
    p = argparse.ArgumentParser(description="Dossier de révision par cycle (lecture par invariants comptables).")
    p.add_argument("--balance", required=True)
    p.add_argument("--seuil", type=float, default=0.10)
    p.add_argument("--gabarit", default=None, choices=list(LAYOUTS),
                   help="impose la lecture des colonnes (après ambiguïté signalée)")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    rows, source = read_balance(a.balance, a.gabarit)
    cycles = build(rows, a.seuil, source)
    if a.json:
        print(json.dumps({"source_n1": source, "cycles": cycles}, ensure_ascii=False, indent=2)); return
    tot = 0
    print(f"Source du N-1 : {source}")
    for cyc, d in cycles.items():
        var = round(d["tot_n"] - d["tot_n1"], 2)
        print(f"\n== {cyc} == (N {d['tot_n']:,.0f} | N-1 {d['tot_n1']:,.0f} | var {var:,.0f})")
        for l in d["lignes"]:
            flag = "  <-- À INVESTIGUER" if l["alerte"] else ""
            pct = f"{l['pct']*100:+.1f}%" if l["pct"] is not None else "  n/d"
            n1 = f"{l['solde_n1']:>13,.0f}" if l["solde_n1"] is not None else f"{'inconnu':>13s}"
            tot += 1 if l["alerte"] else 0
            print(f"   {l['compte']:8s} {l['libelle'][:24]:24s} N {l['solde_n']:>13,.0f}  N-1 {n1}  {pct:>8s}{flag}")
    print(f"\nTotal points à investiguer : {tot}")


if __name__ == "__main__":
    main()
