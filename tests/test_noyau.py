"""Noyau du moteur : importable en paquet, et publié à l'identique dans le plugin (garde de parité)."""
from __future__ import annotations

import importlib
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

DEPOT = Path(__file__).resolve().parents[1]
PLUGIN = DEPOT.parent / "compta-ohada"
sys.path.insert(0, str(DEPOT / "outils"))
import publier_vers_plugin as pub  # noqa: E402


@pytest.mark.parametrize("module", ["detection_balance", "grand_livre", "formules_xl", "rendu_pdf"])
def test_import_en_paquet(module):
    m = importlib.import_module(f"facil_moteur.noyau.{module}")
    assert m.__name__ == f"facil_moteur.noyau.{module}"


def test_grand_livre_utilise_le_detecteur_du_paquet():
    gl = importlib.import_module("facil_moteur.noyau.grand_livre")
    db = importlib.import_module("facil_moteur.noyau.detection_balance")
    assert gl.parse_number is db.parse_number


def test_lecture_balance_minimale(tmp_path):
    db = importlib.import_module("facil_moteur.noyau.detection_balance")
    lignes = [["601000", "Achats", "1 234,50"], ["701000", "Ventes", "2 000,00"]]
    dec = db.guess_decimal(lignes)
    assert dec == ","                                                   # séparateur décimal deviné par vote
    assert db.parse_number("1 234,50", dec) == pytest.approx(1234.50)
    assert db.parse_number(1234.5, dec) == pytest.approx(1234.5)
    assert db.parse_number("Achats", dec) is None                      # un libellé n'est pas un montant


@pytest.mark.skipif(not PLUGIN.exists(), reason="plugin compta-ohada absent de ce poste")
def test_parite_avec_le_plugin():
    r = subprocess.run([sys.executable, str(DEPOT / "outils" / "publier_vers_plugin.py"), "--check"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout


@pytest.mark.skipif(not PLUGIN.exists(), reason="plugin compta-ohada absent de ce poste")
def test_contre_epreuve_parite(tmp_path):
    """Une copie modifiée dans le plugin doit faire rougir la garde."""
    faux = tmp_path / "plugin"
    for d in pub.DESTINATIONS.values():
        (faux / d).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PLUGIN / d, faux / d)
    assert pub.ecarts(faux) == []                                       # témoin
    cible = faux / pub.DESTINATIONS["grand_livre.py"]
    cible.write_text(cible.read_text(encoding="utf-8") + "\n# retouche locale\n", encoding="utf-8")
    assert any("grand_livre" in e for e in pub.ecarts(faux))
