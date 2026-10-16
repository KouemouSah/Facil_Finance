"""Guinée équatoriale convertie au format pack : mêmes paramètres, mêmes calculs, au franc près.

Référence : le plugin compta-ohada v0.10.0 (lib/parametres_fiscaux_ge.json et lib/fiscal_ge.py), dont la DEF
reproduit une DEF déposée réelle (3 952 cellules identiques). Si le pack redonne les mêmes paramètres et que
le calcul fiscal donne les mêmes montants, la conversion n'a rien changé.
"""
from __future__ import annotations

import copy
import datetime as dt
import importlib.util
import json
from pathlib import Path

import pytest

from facil_moteur import adaptateurs, packs

DEPOT = Path(__file__).resolve().parents[1]
PLUGIN = DEPOT.parent / "compta-ohada"
pytestmark = pytest.mark.skipif(not PLUGIN.exists(), reason="plugin compta-ohada (référence) absent de ce poste")


@pytest.fixture(scope="module")
def origine() -> dict:
    return json.loads((PLUGIN / "lib" / "parametres_fiscaux_ge.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def depuis_pack() -> dict:
    racine = DEPOT / "packs"
    r = packs.resoudre(racine, packs.en_vigueur(racine, "GQ", dt.date(2025, 12, 31), atelier=True))
    return adaptateurs.parametres_fiscaux(r, garder_tracabilite=False)


@pytest.fixture(scope="module")
def fiscal_ge():
    spec = importlib.util.spec_from_file_location("fiscal_ge_reference", PLUGIN / "lib" / "fiscal_ge.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def test_parametres_identiques_cle_par_cle(origine, depuis_pack):
    assert depuis_pack == origine


def test_aucun_taux_sans_article(depuis_pack):
    assert all(str(v.get("article", "")).strip() for v in depuis_pack["parametres"].values())


# Balances types (soldes débit − crédit) : bénéfice, perte, petit bénéfice sous le minimum, dons au-delà du plafond.
CAS = {
    "benefice": {"701": -500_000_000, "601": 200_000_000, "661": 80_000_000, "641": 10_000_000, "521": 190_000_000},
    "perte": {"701": -100_000_000, "601": 150_000_000, "661": 40_000_000, "521": -90_000_000},
    "minimum": {"701": -800_000_000, "601": 790_000_000, "661": 5_000_000, "521": 5_000_000},
    "dons": {"701": -300_000_000, "601": 100_000_000, "6581": 9_000_000, "658": 3_000_000, "521": 188_000_000},
}


def _sans_volatile(x):
    """Les sorties portent parfois des dates de calcul : on compare le fond."""
    return json.loads(json.dumps(x, default=str, sort_keys=True))


@pytest.mark.parametrize("cas", sorted(CAS))
def test_calcul_fiscal_identique_au_franc_pres(fiscal_ge, origine, depuis_pack, cas):
    soldes = CAS[cas]
    entrees = fiscal_ge.entrees_depuis_soldes(soldes, 2025)
    a = fiscal_ge.calculer(copy.deepcopy(entrees), soldes=dict(soldes), params=copy.deepcopy(origine))
    b = fiscal_ge.calculer(copy.deepcopy(entrees), soldes=dict(soldes), params=copy.deepcopy(depuis_pack))
    assert _sans_volatile(a) == _sans_volatile(b)


def test_contre_epreuve_un_taux_change_se_voit(fiscal_ge, origine, depuis_pack):
    """Si le pack portait un autre taux d'IS, le calcul le montrerait (le test ci-dessus n'est pas aveugle)."""
    falsifie = copy.deepcopy(depuis_pack)
    falsifie["parametres"]["is_taux"]["valeur"] = round(falsifie["parametres"]["is_taux"]["valeur"] + 0.05, 4)
    soldes = CAS["benefice"]
    entrees = fiscal_ge.entrees_depuis_soldes(soldes, 2025)
    a = fiscal_ge.calculer(copy.deepcopy(entrees), soldes=dict(soldes), params=copy.deepcopy(origine))
    b = fiscal_ge.calculer(copy.deepcopy(entrees), soldes=dict(soldes), params=falsifie)
    assert _sans_volatile(a) != _sans_volatile(b)
