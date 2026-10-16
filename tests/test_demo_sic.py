"""Démonstration du pack Cameroun sur une DSF réelle publiée : Société Immobilière du Cameroun (SIC), exercice 2025.

Source : DSF SYSCOHADA révisé (système normal) de la SIC, exercice clos le 31/12/2025, publiée par la Direction
générale du budget (document public) — corpus : datas/liasses-officielles/Cameroun/CM_exemple_DGB_SIC_DSF_2025.pdf.
Montants relevés par outils/lire_dsf_pdf.py (pages 10, 11, 70 et 71 du PDF).

Ce que la démonstration prouve : les paramètres fiscaux du pack (taux, seuil, CAC, minimum) redonnent l'impôt
déposé AU FRANC PRÈS, et les contrôles OHADA tiennent sur les états publiés. Elle ne prouve PAS la production
de la liasse depuis une balance : la balance de la SIC n'est pas publique.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

from facil_moteur import packs

PUBLIE = {  # montants N de la DSF déposée
    "CA_XB": 5_022_768_363, "XG": 1_529_138_674, "XI": 878_503_091, "CJ": 878_503_091, "RS": 650_635_583,
    "actif_net_total": 170_386_323_674, "passif_total_DZ": 170_386_323_674,
    "TA": 0, "TB": 1_640_448_856, "TC": 3_131_511_773, "TD": 250_807_734,
    "reintegrations": 258_356_861, "deductions": 90_689_636, "benefice_fiscal": 1_696_805_899,
    "is_principal": 509_041_770, "minimum": 100_455_367, "impot_exercice_avec_cac": 559_945_947,
    "rappel_impots_anterieurs": 90_689_636, "acomptes": 470_845_908, "net_a_payer": 89_100_039,
}


@pytest.fixture(scope="module")
def p():
    racine = Path(__file__).resolve().parents[1] / "packs"
    r = packs.resoudre(racine, packs.en_vigueur(racine, "CM", dt.date(2025, 12, 31), atelier=True))
    return {k: v["valeur"] for k, v in r.parametres.items()}


def arrondi(x: float) -> int:
    return int(x + 0.5)


def impot_sur_les_societes(p, benefice_fiscal, ca):
    taux = p["is.taux_reduit"] if ca <= p["is.seuil_ca_taux_reduit"] else p["is.taux_normal"]
    principal = arrondi(benefice_fiscal * taux)
    minimum = arrondi(ca * p["minimum_perception.taux"])
    retenu = max(principal, minimum)
    return principal, minimum, retenu + arrondi(retenu * p["cac.taux"])


def test_controles_ohada_sur_les_etats_publies():
    d = PUBLIE
    assert d["XI"] == d["CJ"]                                              # OHADA-RESULTAT
    assert d["actif_net_total"] == d["passif_total_DZ"]                    # OHADA-BILAN-EQUILIBRE
    assert d["TA"] + d["TB"] + d["TC"] + d["TD"] == d["CA_XB"]             # XB = A + B + C + D
    assert d["XG"] + 0 + 0 - d["RS"] == d["XI"]                            # XI = XG + XH + RQ + RS (XH = RQ = 0)


def test_resultat_fiscal():
    d = PUBLIE
    assert d["XG"] + d["reintegrations"] - d["deductions"] == d["benefice_fiscal"]


def test_impot_reproduit_au_franc_pres(p):
    d = PUBLIE
    principal, minimum, impot = impot_sur_les_societes(p, d["benefice_fiscal"], d["CA_XB"])
    assert principal == d["is_principal"]                 # 30 % : CA au-dessus du seuil de 3 milliards
    assert minimum == d["minimum"]                        # 2 % du CA DE L'EXERCICE
    assert impot == d["impot_exercice_avec_cac"]          # max(IS, minimum) + 10 % de CAC
    assert impot + d["rappel_impots_anterieurs"] == d["RS"]
    assert impot - d["acomptes"] == d["net_a_payer"]


@pytest.mark.parametrize("cle,delta", [("is.taux_normal", 0.01), ("cac.taux", 0.01), ("minimum_perception.taux", 0.03),
                                       ("is.seuil_ca_taux_reduit", 3_000_000_000)])
def test_contre_epreuve_un_parametre_faux_se_voit(p, cle, delta):
    """Un paramètre faux dans le pack (taux, CAC, minimum, seuil) ne reproduit plus la DSF déposée.
    LIMITE : chez la SIC le minimum (100 M) est inférieur à l'IS (509 M) ; un taux de minimum faux ne change donc
    pas l'impôt final, seulement la ligne « minimum proportionnel ». Le cas où le minimum L'EMPORTE reste à
    éprouver sur une DSF déficitaire ou peu bénéficiaire (tâche du plan)."""
    faux = dict(p); faux[cle] = p[cle] + delta
    obtenu = impot_sur_les_societes(faux, PUBLIE["benefice_fiscal"], PUBLIE["CA_XB"])
    attendu = (PUBLIE["is_principal"], PUBLIE["minimum"], PUBLIE["impot_exercice_avec_cac"])
    assert obtenu != attendu
