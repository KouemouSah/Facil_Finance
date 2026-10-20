# -*- coding: utf-8 -*-
"""TF3 (IVA), TF4 (salaires), TF5 (paiements aux tiers) de la DEF GE, depuis le GRAND LIVRE.

  python calcul_tf345_ge.py --grand-livre GL.xls --exercice 2025 [--balance B.xls] [--profil p.json]
                            [--decisions d.json] [--tiers tiers.xlsx] [--xlsx TF345.xlsx] [--json]

--balance  : libellés des comptes (nature TF5, catégories IRPF), rapprochement grand livre / balance,
             soldes cumulés d'IVA.
--tiers    : fichier des tiers (code, nom, adresse, NIF) -> TF5 complet ; sans lui, noms SUGGÉRÉS.
--profil   : interprétations (ex. tf3_iva_deductible), faits (ex. iva_ca_sans_tva), comptes.
Rien ne bloque : questions et hypothèses sont listées ; le classeur trace chaque montant jusqu'à la ligne
source du grand livre. (Moteur : tf345_ge.py, copie synchronisée de lib/.)
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
import grand_livre  # noqa: E402
import tf345_ge  # noqa: E402
from detection_balance import analyse  # noqa: E402


def main():
    p = argparse.ArgumentParser(description="TF3/TF4/TF5 GE depuis le grand livre.")
    p.add_argument("--grand-livre", required=True)
    p.add_argument("--exercice", type=int, required=True)
    p.add_argument("--balance")
    p.add_argument("--profil")
    p.add_argument("--decisions")
    p.add_argument("--tiers")
    p.add_argument("--xlsx")
    p.add_argument("--entite", default="")
    p.add_argument("--nif", default="")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    gl = grand_livre.lire(a.grand_livre)
    det = gl["detection"]
    print(f"[grand livre] {det.get('lignes')} lignes — colonnes {det.get('colonnes')} — solde progressif vérifié "
          f"{det.get('solde_progressif_verifie')}", file=sys.stderr)
    if det.get("statut") != "ok":
        print(f"Grand livre illisible : {det.get('raison')}", file=sys.stderr)
        raise SystemExit(2)
    hors = [x for x in gl["lignes"] if not x["date"].startswith(str(a.exercice))]
    if hors:
        print(f"⚠ {len(hors)} ligne(s) datée(s) hors de l'exercice {a.exercice}", file=sys.stderr)
    libelles, soldes_b = {}, None
    if a.balance:
        b = analyse(a.balance)
        libelles, soldes_b = b.get("libelles", {}), b["soldes"]
        ec = grand_livre.rapprocher(gl, soldes_b, grand_livre.pieces_de_cloture(gl))
        if ec:
            print(f"⚠ Grand livre et balance diffèrent sur {len(ec)} compte(s) (versions différentes ? comptes collectifs "
                  f"non détaillés ?) : {dict(list(ec.items())[:6])}", file=sys.stderr)
    profil = json.load(open(a.profil, encoding="utf-8")) if a.profil else None
    dec = json.load(open(a.decisions, encoding="utf-8")) if a.decisions else None
    tiers = tf345_ge.lire_tiers(a.tiers) if a.tiers else None
    res = tf345_ge.calculer(gl, profil=profil, decisions=dec, libelles=libelles, soldes_balance=soldes_b, tiers_ref=tiers)
    if a.xlsx:
        tf345_ge.ecrire_xlsx(res, a.xlsx, entite=a.entite, identifiant=a.nif)
    if a.json:
        out = dict(res)
        for t in ("tf3", "tf4", "tf5"):
            out[t] = {k: v for k, v in res[t].items() if k != "trace"}
        print(json.dumps(out, ensure_ascii=False, indent=2, default=list))
        return
    r3, r4, r5 = res["tf3"], res["tf4"], res["tf5"]
    print(f"TF3 — IVA {a.exercice} ({r3['nature']}, taux {r3['taux']:.0%})")
    print(f"  base reconstituée {r3['base_totale']:>18,.2f} | IVA théorique (15) {r3['iva_theorique']:>16,.2f}")
    print(f"  IVA déductible {r3['iva_deductible']:>16,.2f} | paiements au Trésor (28) {r3['ligne_28']:>16,.2f} "
          f"| à payer (29) {r3['ligne_29']:>16,.2f} | crédit (30) {r3['ligne_30']:,.2f}")
    print("TF4 — salaires (totaux par catégorie)")
    for k, v in r4["categories"].items():
        print(f"  {k:13s} rémunérations {v['remunerations']:>18,.2f} | IRPF retenu {v['irpf_retenu']:>16,.2f} "
              f"| reversé {v['irpf_reverse']:>14,.2f} | différence {v['difference']:>16,.2f}")
    print(f"TF5 — {len(r5['lignes'])} bénéficiaires par code tiers : {r5['total_ht']:,.2f} HT | sans code tiers : "
          f"{r5['total_sans_tiers']:,.2f}")
    for x in r5["lignes"][:10]:
        print(f"  {x['code']:7s} {(x['nom'] or '≈ ' + x['nom_suggere'])[:28]:28s} {x['nature'][:28]:28s} {x['ht']:>16,.2f}")
    for w in res["avertissements"]:
        print("⚠ " + w)
    if a.xlsx:
        print(f"\nClasseur TF3/TF4/TF5 (formules vivantes + traçabilité) : {a.xlsx}")


if __name__ == "__main__":
    main()
