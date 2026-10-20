# -*- coding: utf-8 -*-
"""TF1 / TF2 de la DEF Guinée équatoriale : résultat fiscal, IS, Cuota Mínima Fiscal.

Sources : une balance (lue par invariants comptables) OU des montants saisis ; plus, en
option, un fichier de DÉCISIONS (jugements de l'utilisateur) :
  {
    "propositions_acceptees": ["64710000", "65830000"] | "toutes",
    "reintegrations": [{"ligne": "diversos", "montant": 1000, "libelle": "...", "article": "..."}],
    "deductions":     [{"ligne": "diversos_1", "montant": 0, "libelle": "..."}],
    "deficits":       [{"exercice": 2023, "montant": 0}],
    "cmf_versee":     [{"date": "2025-07-15", "montant": 0, "piece": "quittance n°..."}],
    "nouvelle_societe": false,
    "base_cmf": "ca" | "produits_totaux"
  }
Lignes de réintégration : amort_non_deductibles, amort_differes, provisions, remuneration_exploitant,
interets_excedentaires, impuestos, multas, donaciones, diversos.
Lignes de déduction : amort_differes_anterieurs, provisions_anterieures, plus_values, diversos_1, diversos_2.

Rien ne bloque : ce qui manque prend une valeur par défaut VISIBLE (avertissements). Les
réintégrations proposées depuis la balance ne s'appliquent QUE si elles sont acceptées.
Taux et règles : parametres_fiscaux_ge.json (chaque valeur avec son article de la Ley 1/2024).

Usage :
  python calcul_is_ge.py --balance balance.xls --exercice 2025                   (propositions)
  python calcul_is_ge.py --balance balance.xls --exercice 2025 --decisions d.json --xlsx TF.xlsx
  python calcul_is_ge.py --resultat 1272700235.69 --ca 8384195031.24 --exercice 2025
"""
import argparse
import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fiscal_ge  # noqa: E402
from detection_balance import LAYOUTS, analyse, rapport  # noqa: E402


def main():
    p = argparse.ArgumentParser(description="TF1/TF2 GE : résultat fiscal, IS, Cuota Mínima Fiscal.")
    p.add_argument("--balance")
    p.add_argument("--gabarit", choices=list(LAYOUTS), default=None)
    p.add_argument("--resultat", type=float, help="résultat comptable AVANT impôt (si pas de balance)")
    p.add_argument("--ca", type=float, help="chiffre d'affaires, comptes 70 (si pas de balance)")
    p.add_argument("--autres-produits", type=float, default=0.0)
    p.add_argument("--exercice", type=int, required=True)
    p.add_argument("--date-cloture", default=None)
    p.add_argument("--decisions")
    p.add_argument("--profil", help="profil d'entreprise : interprétations, faits, justifications (voir references/)")
    p.add_argument("--xlsx")
    p.add_argument("--entite", default="")
    p.add_argument("--nif", default="")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    soldes = None
    if a.balance:
        det = analyse(a.balance, a.gabarit)
        print(rapport(det), file=sys.stderr)
        if det["statut"] != "ok":
            print("Balance illisible ou ambiguë : relancer avec --gabarit après avoir demandé à l'utilisateur.", file=sys.stderr)
            raise SystemExit(2)
        soldes = det["soldes"]
        entrees = fiscal_ge.entrees_depuis_soldes(soldes, a.exercice, a.date_cloture)
    elif a.resultat is not None and a.ca is not None:
        entrees = {"exercice": a.exercice, "date_cloture": a.date_cloture or f"{a.exercice}-12-31",
                   "resultat_avant_is": a.resultat, "ca": a.ca, "autres_produits": a.autres_produits}
    else:
        p.error("fournir --balance, ou --resultat et --ca")
    decisions = json.load(open(a.decisions, encoding="utf-8")) if a.decisions else None
    profil = json.load(open(a.profil, encoding="utf-8")) if a.profil else None
    res = fiscal_ge.calculer(entrees, decisions, soldes, libelles=det.get("libelles") if a.balance else None, profil=profil,
                             mouvements=det.get("mouvements") if a.balance else None)   # CMF versée lue dans la balance
    if a.xlsx:
        fiscal_ge.ecrire_xlsx(res, a.xlsx, a.entite, a.nif)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=2)); return

    t1, t2 = res["tf1"], res["tf2"]
    print(f"TF1 — Résultat fiscal {a.exercice}")
    print(f"  (1)  Résultat comptable avant impôt   {t1[1]:>20,.2f}")
    print(f"  (13) Total réintégrations             {t1[13]:>20,.2f}")
    for x in res["reintegrations_detail"]:
        print(f"         {x.get('compte', '')[:10]:10s} {x['ligne']:12s} {x['montant']:>18,.2f}  {x.get('article', '')}")
    print(f"  (20) Total déductions                 {t1[20]:>20,.2f}")
    print(f"  (22) Résultat fiscal                  {t1[22]:>20,.2f}")
    print(f"  (26) Résultat net après déficits      {t1[26]:>20,.2f}")
    print(f"\nTF2 — IS et Cuota Mínima Fiscal")
    arr = res["interpretations"].get("arrondi_base_is", True)
    print(f"  (3)  Bénéfice imposable               {t2[3]:>20,.2f}   "
          + (f"base arrondie {res['base_is_arrondie']:,.0f} (art. 75.1)" if arr
             else "base NON arrondie (interprétation d'entreprise ≠ art. 75.1)"))
    print(f"  (5)  IS {t2[4]:.0%}                            {t2[5]:>20,.2f}")
    print(f"  (14) CMF {t2[13]:.1%} × {t2[12]:,.0f}   {t2[14]:>20,.0f}")
    print(f"  (6)  CMF versée à déduire             {t2[6]:>20,.2f}")
    print(f"  (7)  IS À PAYER                       {t2[7]:>20,.2f}")
    en_attente = [x for x in res["propositions"] if x.get("statut") in ("proposée, non retenue", "en attente de réponse")]
    if en_attente:
        print("\nPropositions à soumettre à l'utilisateur (non appliquées) :")
        for x in en_attente:
            print(f"  - {x['compte']} « {x.get('libelle', '')} » {x['montant']:>16,.2f} -> {x['ligne']} ({x['article']}) "
                  f"[{x['statut']}] {x['motif']}")
    if res["questions"]:
        print("\nQuestions d'entrée (faits inconnus : à poser à l'utilisateur, la règle n'est pas appliquée sans réponse) :")
        for q in res["questions"]:
            ind = "; ".join(f"{i['compte']} « {i['libelle']} »" for i in q["indices"])
            print(f"  - [{q['fait']}] {q['question']}" + (f"  Indices : {ind}" if ind else ""))
    for o in res["obligations_annexes"]:
        print(f"\nObligation annexe : {o['objet']} = {o['taux']:.0%} × {o['base']:,.0f} = {o['montant']:,.0f} ({o['article']})")
    print("\nÉchéances :")
    for e in res["echeances"]:
        print(f"  - {e['objet']:28s} {e['date']:32s} {e['article']}")
    for w in res["avertissements"]:
        print("⚠ " + w)
    if a.xlsx:
        print(f"\nClasseur TF1/TF2 (formules vivantes) : {a.xlsx}")


if __name__ == "__main__":
    main()
