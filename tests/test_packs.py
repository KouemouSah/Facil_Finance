"""Format des packs pays : chaque règle de validation a sa contre-épreuve (une mutation, un rouge).

Les tests travaillent sur des COPIES des packs du dépôt, dans un dossier temporaire.
"""
from __future__ import annotations

import datetime as dt
import json
import shutil
from pathlib import Path

import pytest
import yaml
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from facil_moteur import packs

DEPOT_PACKS = Path(__file__).resolve().parents[1] / "packs"


@pytest.fixture
def racine(tmp_path: Path) -> Path:
    r = tmp_path / "packs"
    shutil.copytree(DEPOT_PACKS / "ohada", r / "ohada")
    shutil.copytree(DEPOT_PACKS / "cemac", r / "cemac")
    # Un pack pays minimal, fictif, pour les tests (pas de données réelles).
    cm = r / "CM" / "2025.1"
    (cm / "fiscal").mkdir(parents=True)
    (cm / "pack.yaml").write_text(yaml.safe_dump({
        "pays": "CM", "version": "2025.1", "valide_du": "2025-01-01", "valide_au": None, "monnaie": "XAF",
        "langues_liasse": ["fr", "en"], "systemes": ["SN", "SMT"], "herite_de": ["ohada/2017.1", "cemac/2025.1"],
        "statut": "brouillon", "validation": {"expert": None, "date": None, "liasses_reproduites": 0}}), encoding="utf-8")
    (cm / "fiscal" / "parametres.json").write_text(json.dumps({"parametres": {
        "is.taux_test": {"valeur": 0.3, "unite": "taux", "article": "art. test", "source": "texte de test"}}}), encoding="utf-8")
    (cm / "SOURCES.md").write_text("# test\n", encoding="utf-8")
    return r


@pytest.fixture
def cle():
    prive = Ed25519PrivateKey.generate()
    pem = prive.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    pub = prive.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
    return pem, {"test": pub}


def erreurs(racine: Path, rel: str, cles=None) -> set[str]:
    return {a.code for a in packs.valider(packs.charger(racine / rel), racine, cles or {}) if a.niveau == "erreur"}


def manifeste(racine: Path, rel: str, **modifs) -> None:
    f = racine / rel / "pack.yaml"
    m = yaml.safe_load(f.read_text(encoding="utf-8")); m.update(modifs)
    f.write_text(yaml.safe_dump(m, allow_unicode=True), encoding="utf-8")


# -- témoins : les packs du dépôt sont valides --------------------------------------------------
@pytest.mark.parametrize("rel", ["ohada/2017.1", "cemac/2025.1", "CM/2025.1"])
def test_temoin_packs_valides(racine, rel):
    assert erreurs(racine, rel) == set()


# -- contre-épreuves du manifeste -----------------------------------------------------------------
@pytest.mark.parametrize("modif,code", [
    ({"pays": "GA"}, "PACK-PAYS"),
    ({"version": "2026.1"}, "PACK-VERSION"),
    ({"version": "v1"}, "PACK-VERSION"),
    ({"monnaie": "EUR"}, "PACK-MONNAIE"),
    ({"monnaie": None}, "PACK-MONNAIE"),
    ({"langues_liasse": ["fr", "de"]}, "PACK-LANGUE"),
    ({"systemes": ["SN", "IFRS"]}, "PACK-SYSTEME"),
    ({"valide_du": "le 1er janvier"}, "PACK-VALIDITE"),
    ({"valide_au": "2024-12-31"}, "PACK-VALIDITE"),
    ({"statut": "en_test"}, "PACK-STATUT"),
    ({"statut": "retire"}, "PACK-RETRAIT"),
    ({"herite_de": ["cemac/2025.1"]}, "PACK-HERITAGE"),
    ({"herite_de": ["ohada/2017.1", "cemac/1999.1"]}, "PACK-HERITAGE"),
])
def test_manifeste_mutations(racine, modif, code):
    manifeste(racine, "CM/2025.1", **modif)
    assert code in erreurs(racine, "CM/2025.1")


def test_couche_inconnue(racine):
    shutil.copytree(racine / "CM", racine / "FR")
    manifeste(racine, "FR/2025.1", pays="FR")
    assert "PACK-COUCHE" in erreurs(racine, "FR/2025.1")


def test_valide_sans_expert_ni_preuves(racine):
    manifeste(racine, "CM/2025.1", statut="valide")
    e = erreurs(racine, "CM/2025.1")
    assert {"PACK-EXPERT", "PACK-PREUVE", "SIG-ABSENTE"} <= e


def test_publie_exige_30_liasses(racine):
    manifeste(racine, "CM/2025.1", statut="publie", validation={"expert": "X, ONECCA n° 0", "liasses_reproduites": 12})
    assert "PACK-PREUVE" in erreurs(racine, "CM/2025.1")


def test_sans_sources(racine):
    (racine / "CM/2025.1/SOURCES.md").unlink()
    assert "PACK-SOURCES" in erreurs(racine, "CM/2025.1")


# -- contre-épreuves des données ------------------------------------------------------------------
def ecrire(racine, rel, donnees):
    f = racine / "CM/2025.1" / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(donnees), encoding="utf-8")


@pytest.mark.parametrize("param,code", [
    ({"valeur": 0.3, "source": "LF"}, "FISC-ARTICLE"),
    ({"valeur": 0.3, "article": "art. 17"}, "FISC-SOURCE"),
    ({"valeur": 30, "unite": "taux", "article": "art. 17", "source": "LF"}, "FISC-TAUX"),
    ({"article": "art. 17", "source": "LF"}, "FISC-FORME"),
    ({"valeur": 0.3, "article": "a", "source": "LF", "url": "ftp://x"}, "FISC-SOURCE"),
])
def test_parametres_mutations(racine, param, code):
    ecrire(racine, "fiscal/parametres.json", {"parametres": {"x": param}})
    assert code in erreurs(racine, "CM/2025.1")


def test_compte_sur_deux_postes(racine):
    ecrire(racine, "correspondances/comptes.json", {"regles": [
        {"prefixe": "601", "sens": "tous", "ref": "RA"}, {"prefixe": "601", "sens": "tous", "ref": "RB"}]})
    assert "CPT-DOUBLON" in erreurs(racine, "CM/2025.1")


def test_compte_sans_poste_ni_exclusion(racine):
    ecrire(racine, "correspondances/comptes.json", {"regles": [{"prefixe": "9", "sens": "tous", "ref": None}]})
    assert "CPT-REF" in erreurs(racine, "CM/2025.1")
    ecrire(racine, "correspondances/comptes.json", {"regles": [{"prefixe": "9", "sens": "tous", "ref": None, "nature": "hors_etats"}]})
    assert "CPT-REF" not in erreurs(racine, "CM/2025.1")  # témoin : exclusion explicite admise


def test_controle_mal_forme(racine):
    ecrire(racine, "controles.json", {"controles": [{"id": "C1", "gravite": "fatal", "message": {"en": "x"}},
                                                    {"id": "C1", "gravite": "bloquant", "message": {"fr": "x"}}]})
    assert {"CTL-GRAVITE", "CTL-MESSAGE", "CTL-DOUBLON"} <= erreurs(racine, "CM/2025.1")


def test_json_illisible(racine):
    (racine / "CM/2025.1/controles.json").write_text("{pas du json", encoding="utf-8")
    assert "PACK-JSON" in erreurs(racine, "CM/2025.1")


# -- signature ------------------------------------------------------------------------------------
def test_signature_temoin_puis_mutations(racine, cle):
    pem, publiques = cle
    d = racine / "CM/2025.1"
    packs.signer(d, pem, "test")
    assert erreurs(racine, "CM/2025.1", publiques) == set()                       # témoin
    f = d / "fiscal/parametres.json"; original = f.read_text(encoding="utf-8")
    f.write_text(original.replace("0.3", "0.25"), encoding="utf-8")
    assert "SIG-FICHIER-MODIFIE" in erreurs(racine, "CM/2025.1", publiques)        # un taux retouché
    f.write_text(original, encoding="utf-8")
    (d / "ajout.json").write_text("{}", encoding="utf-8")
    assert "SIG-FICHIER-AJOUTE" in erreurs(racine, "CM/2025.1", publiques)
    (d / "ajout.json").unlink(); (d / "SOURCES.md").rename(d / "SOURCES.bak")
    e = erreurs(racine, "CM/2025.1", publiques)
    assert "SIG-FICHIER-RETIRE" in e
    (d / "SOURCES.bak").rename(d / "SOURCES.md")
    assert "SIG-CLE-INCONNUE" in erreurs(racine, "CM/2025.1", {"autre": publiques["test"]})
    sig = json.loads((d / "SIGNATURE").read_text(encoding="utf-8"))
    sig["empreintes"]["SOURCES.md"] = "0" * 64                                     # empreinte falsifiée
    (d / "SIGNATURE").write_text(json.dumps(sig), encoding="utf-8")
    assert {"SIG-INVALIDE", "SIG-FICHIER-MODIFIE"} <= erreurs(racine, "CM/2025.1", publiques)


def test_signature_obligatoire_hors_atelier(racine):
    manifeste(racine, "CM/2025.1", statut="valide", validation={"expert": "X", "liasses_reproduites": 10})
    assert "SIG-ABSENTE" in erreurs(racine, "CM/2025.1")


# -- résolution -----------------------------------------------------------------------------------
def test_en_vigueur_et_atelier(racine):
    with pytest.raises(LookupError):
        packs.en_vigueur(racine, "CM", dt.date(2025, 12, 31))                       # brouillon : refusé hors atelier
    assert packs.en_vigueur(racine, "CM", dt.date(2025, 12, 31), atelier=True).ident == "CM/2025.1"
    with pytest.raises(LookupError):
        packs.en_vigueur(racine, "CM", dt.date(2024, 12, 31), atelier=True)        # avant la validité
    with pytest.raises(ValueError):
        packs.en_vigueur(racine, "FR", dt.date(2025, 12, 31))                       # pas un État OHADA


def test_en_vigueur_choisit_la_plus_recente(racine):
    shutil.copytree(racine / "CM/2025.1", racine / "CM/2026.1")
    manifeste(racine, "CM/2026.1", version="2026.1", valide_du="2026-01-01")
    manifeste(racine, "CM/2025.1", valide_au="2025-12-31")
    assert packs.en_vigueur(racine, "CM", dt.date(2025, 12, 31), atelier=True).ident == "CM/2025.1"
    assert packs.en_vigueur(racine, "CM", dt.date(2026, 12, 31), atelier=True).ident == "CM/2026.1"


def test_resolution_couches_et_surcharges(racine):
    ecrire(racine, "correspondances/comptes.json", {"regles": [{"prefixe": "601", "sens": "tous", "ref": "RZ", "libelle": "surcharge de test"}]})
    r = packs.resoudre(racine, packs.charger(racine / "CM/2025.1"))
    assert r.versions == ["ohada/2017.1", "cemac/2025.1", "CM/2025.1"]
    assert "is.taux_test" in r.parametres and len(r.postes) == 99
    assert any(el.startswith("compte:('601'") and apres == "CM/2025.1" for el, _, apres in r.surcharges)
    assert packs.poste_du_compte(r, "6011")["ref"] == "RZ"                          # la couche pays prime


def test_poste_plus_long_prefixe_et_sens(racine):
    r = packs.resoudre(racine, packs.charger(racine / "CM/2025.1"))
    assert packs.poste_du_compte(r, "4091", "debiteur")["ref"] == "BH"
    assert packs.poste_du_compte(r, "4091", "crediteur")["ref"] == "DJ"
    assert packs.poste_du_compte(r, "9011")["nature"] == "hors_etats"
