#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comptabilisation à l'avancement (contrats BTP) — moteur paramétrique.

Aucun taux ni règle en dur. Entrées fournies par l'utilisateur d'après le
chantier et la méthode d'avancement retenue par l'entreprise.

Calcule :
  - % d'avancement (méthode des coûts encourus) = coût engagé / coût total estimé
  - CA à reconnaître à date = prix du marché * % d'avancement
  - marge totale prévue = prix du marché - coût total estimé
  - marge reconnue à date = marge totale prévue * % d'avancement
  - provision pour perte à terminaison (si contrat déficitaire), reconnue
    intégralement pour la part non encore courue (principe de prudence)

Si l'avancement est fourni directement (avancement physique), passer --pct.

Usage :
  python avancement.py --cout-engage 300000000 --cout-total 800000000 --prix 900000000
  python avancement.py --pct 0.35 --cout-total 800000000 --prix 750000000 --json
"""
import argparse
import json
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def calcul_avancement(prix_marche, cout_total_estime,
                      cout_engage=None, pct_fourni=None):
    if pct_fourni is not None:
        pct = pct_fourni
    else:
        if cout_engage is None:
            raise ValueError("Fournir --cout-engage ou --pct.")
        if cout_total_estime <= 0:
            raise ValueError("Coût total estimé doit être > 0.")
        pct = cout_engage / cout_total_estime
    pct = max(0.0, min(1.0, pct))

    ca_reconnu = prix_marche * pct
    marge_totale = prix_marche - cout_total_estime
    marge_reconnue = marge_totale * pct

    # Perte à terminaison : si le contrat est globalement déficitaire, la perte
    # future (part non courue) est provisionnée immédiatement.
    provision_perte = 0.0
    if marge_totale < 0:
        provision_perte = round(-marge_totale * (1 - pct), 2)

    return {
        "pct_avancement": round(pct, 4),
        "prix_marche": round(prix_marche, 2),
        "cout_total_estime": round(cout_total_estime, 2),
        "ca_a_reconnaitre": round(ca_reconnu, 2),
        "cout_engage": round(cout_engage, 2) if cout_engage is not None else None,
        "marge_totale_prevue": round(marge_totale, 2),
        "marge_reconnue_a_date": round(marge_reconnue, 2),
        "provision_perte_a_terminaison": provision_perte,
        "contrat_deficitaire": marge_totale < 0,
    }


def main():
    p = argparse.ArgumentParser(description="Avancement contrat BTP (paramétrique).")
    p.add_argument("--prix", type=float, required=True, help="Prix du marché (chiffre d'affaires total)")
    p.add_argument("--cout-total", type=float, required=True, help="Coût total estimé du chantier")
    p.add_argument("--cout-engage", type=float, default=None, help="Coûts engagés à date")
    p.add_argument("--pct", type=float, default=None, help="% d'avancement fourni (0-1) si méthode physique")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    r = calcul_avancement(a.prix, a.cout_total, a.cout_engage, a.pct)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(f"Avancement          : {r['pct_avancement']*100:.2f} %")
        print(f"CA à reconnaître    : {r['ca_a_reconnaitre']:,.2f}")
        print(f"Marge totale prévue : {r['marge_totale_prevue']:,.2f}")
        print(f"Marge reconnue/date : {r['marge_reconnue_a_date']:,.2f}")
        if r["contrat_deficitaire"]:
            print(f"[ALERTE] Contrat deficitaire - provision perte a terminaison : {r['provision_perte_a_terminaison']:,.2f}")


if __name__ == "__main__":
    main()
