#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Décompte d'une situation de travaux (BTP) — moteur paramétrique.

IMPORTANT : les TAUX (TVA, retenue de garantie) sont des ENTRÉES.
- Le taux de retenue de garantie vient du marché/contrat.
- Le taux de TVA vient de la loi fiscale (datas/ley_tributaria_2024.md) et doit
  être CITÉ par article. Le script ne contient aucun taux en dur.

Calcule : montant HT révisé, TVA, TTC, retenue de garantie, avance/acompte
déduit, net à payer.

Usage :
  python situation_travaux.py --ht 50000000 --tva 0.15 --rg 0.05 \
      --acompte 5000000 --revision 200000
"""
import argparse
import json
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def decompte(montant_ht, taux_tva, taux_retenue_garantie=0.0,
             acompte_a_deduire=0.0, revision_prix=0.0):
    ht_revise = montant_ht + revision_prix
    tva = ht_revise * taux_tva
    ttc = ht_revise + tva
    retenue = ht_revise * taux_retenue_garantie
    net_a_payer = ttc - retenue - acompte_a_deduire
    return {
        "montant_ht": round(montant_ht, 2),
        "revision_prix": round(revision_prix, 2),
        "montant_ht_revise": round(ht_revise, 2),
        "taux_tva_applique": taux_tva,
        "tva": round(tva, 2),
        "ttc": round(ttc, 2),
        "taux_retenue_garantie": taux_retenue_garantie,
        "retenue_garantie": round(retenue, 2),
        "acompte_deduit": round(acompte_a_deduire, 2),
        "net_a_payer": round(net_a_payer, 2),
    }


def main():
    p = argparse.ArgumentParser(description="Décompte situation de travaux BTP (paramétrique).")
    p.add_argument("--ht", type=float, required=True, help="Montant HT de la situation")
    p.add_argument("--tva", type=float, required=True, help="Taux de TVA (ex. 0.15) — À CITER depuis la loi")
    p.add_argument("--rg", type=float, default=0.0, help="Taux de retenue de garantie (contrat)")
    p.add_argument("--acompte", type=float, default=0.0, help="Acompte/avance à déduire")
    p.add_argument("--revision", type=float, default=0.0, help="Révision de prix")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    r = decompte(a.ht, a.tva, a.rg, a.acompte, a.revision)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        for k, v in r.items():
            print(f"{k:>22} : {v:,.2f}" if isinstance(v, float) else f"{k:>22} : {v}")
        print("\nRappel : taux de TVA à citer depuis ley_tributaria_2024.md ; à faire valider.")


if __name__ == "__main__":
    main()
