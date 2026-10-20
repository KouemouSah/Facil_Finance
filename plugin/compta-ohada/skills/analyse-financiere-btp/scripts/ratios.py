#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ratios financiers (OHADA) — moteur paramétrique.

Aucune norme sectorielle en dur : le script CALCULE les ratios à partir des
agrégats fournis. L'INTERPRÉTATION (bon/mauvais) reste au comptable, avec des
repères à valider. Les données manquantes sont signalées, pas inventées.

Entrées : un JSON d'agrégats (via --data '{"...": ...}' ou --file agregats.json).
Clés reconnues (toutes optionnelles ; un ratio n'est calculé que si ses
composants sont fournis) :
  actif_circulant, stocks, creances, tresorerie_actif, passif_circulant,
  capitaux_propres, total_passif, dettes_financieres, ca_ht, achats,
  creances_clients_ttc, dettes_fournisseurs_ttc, resultat_net, ebe

Usage :
  python ratios.py --file agregats.json
  python ratios.py --data '{"actif_circulant":900,"passif_circulant":600,"stocks":200}'
"""
import argparse
import json
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def _safe_div(n, d):
    return None if (d in (None, 0)) else n / d


def calcul_ratios(x):
    """x = dict d'agrégats. Retourne {ratio: valeur ou 'donnée manquante'}."""
    R = {}

    def put(nom, num_keys, calc, jours=False):
        if all(k in x and x[k] is not None for k in num_keys):
            v = calc()
            R[nom] = round(v, 2) if v is not None else "n/d (division par 0)"
        else:
            manquants = [k for k in num_keys if k not in x or x[k] is None]
            R[nom] = "donnée manquante: " + ", ".join(manquants)

    put("liquidite_generale", ["actif_circulant", "passif_circulant"],
        lambda: _safe_div(x["actif_circulant"], x["passif_circulant"]))
    put("liquidite_reduite", ["actif_circulant", "stocks", "passif_circulant"],
        lambda: _safe_div(x["actif_circulant"] - x["stocks"], x["passif_circulant"]))
    put("autonomie_financiere", ["capitaux_propres", "total_passif"],
        lambda: _safe_div(x["capitaux_propres"], x["total_passif"]))
    put("endettement_financier", ["dettes_financieres", "capitaux_propres"],
        lambda: _safe_div(x["dettes_financieres"], x["capitaux_propres"]))
    put("bfr", ["stocks", "creances", "passif_circulant"],
        lambda: (x["stocks"] + x["creances"] - x["passif_circulant"]))
    put("bfr_jours_ca", ["stocks", "creances", "passif_circulant", "ca_ht"],
        lambda: _safe_div((x["stocks"] + x["creances"] - x["passif_circulant"]) * 360.0, x["ca_ht"]))
    put("delai_clients_jours", ["creances_clients_ttc", "ca_ht"],
        lambda: _safe_div(x["creances_clients_ttc"] * 360.0, x["ca_ht"]))
    put("delai_fournisseurs_jours", ["dettes_fournisseurs_ttc", "achats"],
        lambda: _safe_div(x["dettes_fournisseurs_ttc"] * 360.0, x["achats"]))
    put("rentabilite_financiere", ["resultat_net", "capitaux_propres"],
        lambda: _safe_div(x["resultat_net"], x["capitaux_propres"]))
    put("marge_ebe", ["ebe", "ca_ht"],
        lambda: _safe_div(x["ebe"], x["ca_ht"]))
    return R


def main():
    p = argparse.ArgumentParser(description="Ratios financiers OHADA (paramétrique).")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--data", help="Agrégats en JSON inline")
    g.add_argument("--file", help="Fichier JSON d'agrégats")
    a = p.parse_args()
    x = json.loads(a.data) if a.data else json.load(open(a.file, encoding="utf-8"))
    R = calcul_ratios(x)
    print(json.dumps(R, ensure_ascii=False, indent=2))
    print("\nInterprétation à réaliser par le comptable (repères sectoriels à valider).")


if __name__ == "__main__":
    main()
