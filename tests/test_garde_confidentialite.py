"""Garde de confidentialité éprouvée des DEUX côtés : elle attrape un nom planté et laisse passer un texte propre."""
import importlib.util
import zipfile
from pathlib import Path

import pytest

DEPOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("garde", DEPOT / "outils" / "garde_confidentialite.py")
garde = importlib.util.module_from_spec(spec)
spec.loader.exec_module(garde)

CLE = b"cle-de-test"


@pytest.fixture
def empreintes(tmp_path, monkeypatch):
    liste = tmp_path / "liste.txt"
    liste.write_text("# commentaire\nÉtablissements Zébulon Fictifs\nQWERTZ\n", encoding="utf-8")
    monkeypatch.setattr(garde, "EMPREINTES", tmp_path / "empreintes")
    monkeypatch.setattr(garde, "DEPOT", tmp_path)
    garde.regenerer(liste, CLE)
    return garde.charger_empreintes()


def ecrire(tmp_path, nom, texte):
    p = tmp_path / nom
    p.write_text(texte, encoding="utf-8")
    return p


def test_attrape_un_nom_plante_malgre_casse_et_accents(tmp_path, empreintes):
    f = ecrire(tmp_path, "a.md", "Client : ETABLISSEMENTS zebulon   FICTIFS, exercice 2025.")
    assert garde.controler([f], CLE, empreintes, tmp_path)


def test_attrape_un_nom_dans_un_classeur(tmp_path, empreintes):
    f = tmp_path / "c.xlsx"
    with zipfile.ZipFile(f, "w") as z:
        z.writestr("xl/sharedStrings.xml", "<sst><si><t>Qwertz SA</t></si></sst>")
    assert garde.controler([f], CLE, empreintes, tmp_path)


def test_laisse_passer_un_texte_propre(tmp_path, empreintes):
    f = ecrire(tmp_path, "b.md", "Établissements publics ; Zébulon seul ne suffit pas ; contact sah" + AROBASE + "emacsah.com")
    assert garde.controler([f], CLE, empreintes, tmp_path) == []


def test_sans_cle_le_controle_nominatif_ne_joue_pas(tmp_path, empreintes):
    f = ecrire(tmp_path, "a.md", "Etablissements Zebulon Fictifs")
    assert garde.controler([f], None, empreintes, tmp_path) == []


def test_une_autre_cle_ne_reconnait_pas_les_empreintes(tmp_path, empreintes):
    f = ecrire(tmp_path, "a.md", "Etablissements Zebulon Fictifs")
    assert garde.controler([f], b"autre-cle", empreintes, tmp_path) == []


# Échantillons ASSEMBLÉS à l'exécution : ce fichier ne doit pas porter lui-même ce que la garde attrape.
AROBASE, PLUS = chr(64), chr(43)


@pytest.mark.parametrize("texte", ["ecrire a jean.dupont" + AROBASE + "exemple.org",
                                   "IBAN " + "DE89" + " 3704 0044 0532 0130 00",   # IBAN d'exemple de la norme, fictif
                                   "tel " + PLUS + "240 222 12 34 56"])
def test_motifs_generiques(tmp_path, texte):
    f = ecrire(tmp_path, "g.md", texte)
    assert garde.controler([f], None, {}, tmp_path)


def test_bibliotheque_minifiee_ignoree(tmp_path):
    f = ecrire(tmp_path, "mermaid.min.js", "exemple" + AROBASE + "exemple.com")
    assert garde.controler([f], None, {}, tmp_path) == []
