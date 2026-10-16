"""Adaptateurs : rendent aux calculs du moteur les données d'un pack résolu, dans le format qu'ils attendent.

Transitoire : tant que les calculs fiscaux nationaux vivent encore dans le plugin compta-ohada
(fiscal_ge.py, tf345_ge.py), ils reçoivent leurs paramètres d'ici, et non plus d'un fichier du plugin.
"""
from __future__ import annotations

from .packs import PackResolu

# Champs ajoutés par le format du pack (traçabilité) : sans effet sur les calculs.
CHAMPS_DE_TRACABILITE = ("source", "url", "consulte_le")


def parametres_fiscaux(r: PackResolu, garder_tracabilite: bool = True) -> dict:
    """Le dictionnaire { _meta, parametres, interpretations, comptes, faits, propositions… } d'un pays."""
    params = {}
    for cle, v in r.parametres.items():
        params[cle] = dict(v) if garder_tracabilite else {k: x for k, x in v.items() if k not in CHAMPS_DE_TRACABILITE}
    return {**r.fiscal, "parametres": params}
