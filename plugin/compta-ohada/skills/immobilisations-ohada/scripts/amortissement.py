#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moteur de calcul de plan d'amortissement — SYSCOHADA révisé.

PRINCIPE : moteur PARAMÉTRIQUE. Aucune durée, aucun taux, aucun coefficient
n'est codé en dur. TOUT est fourni en entrée par l'utilisateur, d'après la
politique d'amortissement de l'entreprise. Pour le dégressif, le coefficient
est un paramètre (à justifier par la réglementation applicable, jamais deviné).

Méthodes : 'lineaire' ou 'degressif'.
Prorata temporis la 1re année : base 360 jours (mois de 30 jours) par défaut,
ou 'mois' (prorata au mois entier), au choix.

Usage CLI :
  python amortissement.py --valeur 12000000 --date-service 2024-04-15 \
      --duree 5 --methode lineaire --exercice-debut 01-01
  python amortissement.py --valeur 12000000 --date-service 2024-04-15 \
      --duree 5 --methode degressif --coef 2 --prorata mois --json

Sortie : tableau année par année (base | dotation | cumul | VNC) + JSON optionnel.
"""
import argparse
import json
import sys
from datetime import date

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def _prorata_premiere_annee(date_service, fin_exercice, mode):
    """Fraction d'année amortissable sur le 1er exercice (0 < f <= 1)."""
    if mode == "mois":
        mois_restants = (fin_exercice.month - date_service.month) + 1
        # si mise en service le 15, le mois compte entier (convention mois entier)
        return max(0, min(12, mois_restants)) / 12.0
    # base 360 : mois de 30 jours
    jours_ecoules = (date_service.month - 1) * 30 + (date_service.day - 1)
    jours_restants = 360 - jours_ecoules
    return max(0.0, min(360.0, jours_restants)) / 360.0


def plan_amortissement(valeur_origine, date_service, duree_annees,
                       methode="lineaire", valeur_residuelle=0.0,
                       coef_degressif=None, prorata="jours",
                       mois_debut_exercice=1, jour_debut_exercice=1):
    """Retourne la liste des lignes du plan.

    Paramètres (TOUS fournis, aucun défaut normatif) :
      valeur_origine      : base amortissable brute (VO)
      date_service        : datetime.date de mise en service
      duree_annees        : durée d'utilité en années (politique entreprise)
      methode             : 'lineaire' | 'degressif'
      valeur_residuelle   : valeur résiduelle éventuelle
      coef_degressif      : coefficient (obligatoire si degressif) — paramètre réglementaire fourni
      prorata             : 'jours' (base 360) | 'mois'
    """
    base_amortissable = valeur_origine - valeur_residuelle
    if base_amortissable < 0:
        raise ValueError("Valeur résiduelle > valeur d'origine.")
    if methode == "degressif" and not coef_degressif:
        raise ValueError("Le mode dégressif exige --coef (coefficient fourni, non deviné).")

    annee0 = date_service.year
    fin_ex0 = date(annee0, mois_debut_exercice, jour_debut_exercice)
    # fin de l'exercice de mise en service (approx. 12 mois - simplifiée calendaire)
    fin_ex0 = date(annee0, 12, 31) if (mois_debut_exercice == 1) else fin_ex0
    frac0 = _prorata_premiere_annee(date_service, fin_ex0, prorata)

    lignes = []
    vnc = valeur_origine
    cumul = 0.0
    taux_lin = 1.0 / duree_annees
    taux_deg = (coef_degressif or 0) / duree_annees

    # nb d'exercices touchés = duree + 1 (à cause du prorata) au maximum
    for i in range(duree_annees + 1):
        base_nette = vnc - valeur_residuelle
        if base_nette <= 0.009:
            break
        if methode == "lineaire":
            dotation_pleine = base_amortissable * taux_lin
        else:  # degressif avec bascule en linéaire sur la durée résiduelle
            annees_restantes = duree_annees - i
            dot_deg = base_nette * taux_deg
            dot_lin_res = base_nette / annees_restantes if annees_restantes > 0 else base_nette
            dotation_pleine = max(dot_deg, dot_lin_res)
        # prorata la 1re année
        dotation = dotation_pleine * frac0 if i == 0 else dotation_pleine
        # ne pas dépasser la base restante
        dotation = min(dotation, base_nette)
        dotation = round(dotation, 2)
        cumul = round(cumul + dotation, 2)
        vnc = round(valeur_origine - cumul, 2)
        lignes.append({
            "exercice": annee0 + i,
            "base": round(base_amortissable if methode == "lineaire" else base_nette, 2),
            "dotation": dotation,
            "cumul": cumul,
            "vnc": vnc,
            "prorata": round(frac0, 4) if i == 0 else 1.0,
        })
    return lignes


def _print_table(lignes):
    print(f"{'Exercice':>9} | {'Dotation':>15} | {'Cumul':>15} | {'VNC':>15} | prorata")
    print("-" * 72)
    for l in lignes:
        print(f"{l['exercice']:>9} | {l['dotation']:>15,.2f} | {l['cumul']:>15,.2f} | "
              f"{l['vnc']:>15,.2f} | {l['prorata']}")
    if lignes:
        print("-" * 72)
        print(f"Total dotations : {sum(l['dotation'] for l in lignes):,.2f}  |  VNC finale : {lignes[-1]['vnc']:,.2f}")


def main():
    p = argparse.ArgumentParser(description="Plan d'amortissement SYSCOHADA (paramétrique).")
    p.add_argument("--valeur", type=float, required=True, help="Valeur d'origine (VO)")
    p.add_argument("--date-service", required=True, help="Date de mise en service AAAA-MM-JJ")
    p.add_argument("--duree", type=int, required=True, help="Durée d'utilité en années (politique entreprise)")
    p.add_argument("--methode", choices=["lineaire", "degressif"], default="lineaire")
    p.add_argument("--residuelle", type=float, default=0.0, help="Valeur résiduelle")
    p.add_argument("--coef", type=float, default=None, help="Coefficient dégressif (fourni, réglementaire)")
    p.add_argument("--prorata", choices=["jours", "mois"], default="jours")
    p.add_argument("--json", action="store_true", help="Sortie JSON")
    a = p.parse_args()
    y, m, d = map(int, a.date_service.split("-"))
    lignes = plan_amortissement(a.valeur, date(y, m, d), a.duree, a.methode,
                                a.residuelle, a.coef, a.prorata)
    if a.json:
        print(json.dumps(lignes, ensure_ascii=False, indent=2))
    else:
        _print_table(lignes)


if __name__ == "__main__":
    main()
