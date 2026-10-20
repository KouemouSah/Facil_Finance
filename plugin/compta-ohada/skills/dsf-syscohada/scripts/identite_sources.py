# -*- coding: utf-8 -*-
"""Identité de l'entité lue dans les SOURCES déposées, pour ne pas la redemander d'une année sur l'autre.

Deux sources, par ordre de préférence :
  1. une FICHE ENTITÉ (classeur, CSV ou texte « Champ : valeur ») déposée une fois — dans 01_sources, ou dans le
     dossier de l'entité ; la validation d'un exercice en écrit une (fiche_entite.json) pour l'exercice suivant ;
  2. la PAGE DE GARDE de la DEF précédente déposée (et sa fiche R1 / fiche d'identification).

Seuls les champs dont la POSITION est sans ambiguïté sont repris d'une DEF : libellé puis valeur sur la même ligne
(« DENOMINATION SOCIALE | X ») ou dans la même cellule (« ADRESSE COMPLETE : X »). L'activité, la forme juridique et
le dirigeant sont dans des cadres « valeur au-dessus du libellé » propres à chaque pays : on ne les devine pas, ils
restent demandés. Une valeur reprise reste une PROPOSITION : elle s'affiche dans le formulaire, avec son origine, et
toute saisie de l'utilisateur la remplace.
"""
import json
import os
import re
import unicodedata

CHAMPS_DEF = ("raison_sociale", "sigle", "adresse", "nif", "rccm")
CHAMPS_FICHE = CHAMPS_DEF + ("forme_juridique", "activite", "dirigeant")
FEUILLES_DEF = ("garde", "ficher1", "ficheidentification", "fichedepot")
NOMS_FICHE = ("fiche_entite", "identite", "fiche_identite")


def _norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return "".join(ch for ch in s.lower() if ch.isalnum())


def champ_du_libelle(lib):
    """Libellé (normalisé) -> clé d'identité, ou None. Listes fermées : un libellé inconnu n'est jamais deviné."""
    n = _norm(lib)
    if not n or len(n) > 60:
        return None
    if n.startswith(("denominationsociale", "raisonsociale", "razonsocial", "denominacionsocial")):
        return "raison_sociale"
    if n.startswith("sigleusuel") or n == "sigle":
        return "sigle"
    if n.startswith(("adressecomplete", "adressegeographique", "siegesocial", "direccion", "domicilio")) or n == "adresse":
        return "adresse"
    if ("identificationfiscal" in n or "immatriculationfiscal" in n or "identificationunique" in n
            or n in ("nif", "niu", "nifniu", "nnif", "nniu") or n.startswith("numerodecontribuable")):
        return "nif"
    if n == "rccm" or n.startswith("rccm"):
        return "rccm"
    if n.startswith(("formejuridique", "formajuridica")):
        return "forme_juridique"
    if n.startswith(("activiteprincipale", "actividadprincipal")) or n in ("activite", "actividad"):
        return "activite"
    if n.startswith(("dirigeant", "representantlegal", "signataire")):
        return "dirigeant"
    return None


def valeur_plausible(v):
    """Une valeur saisie, pas un gabarit vide, une date, une formule ou un autre libellé."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, float):
        if v != int(v):
            return None
        v = int(v)
    if isinstance(v, int):
        return str(v) if v > 0 else None
    if not isinstance(v, str):
        return None                                            # date, heure… : jamais une identité
    if v.strip().endswith(":") or v.strip().startswith("("):  # un autre libellé (« Exercice clos le : »), une consigne
        return None
    s = " ".join(v.split()).strip(" :")
    if len(s) < 2 or s.startswith("=") or champ_du_libelle(s) or _norm(s) in ("sommaire", "neant", "na"):
        return None
    if re.fullmatch(r"[xX.\-_ *]+", s) or re.search(r"a\s*compl[eé]ter|to\s*complete|xxx", s, re.I):
        return None
    return s


def _lignes(path):
    """[(feuille normalisée, [valeurs de la ligne])] pour classeurs, CSV et texte."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".txt":
        txt = open(path, encoding="utf-8-sig", errors="replace").read()
        return [("", [l]) for l in txt.splitlines()]
    if ext == ".json":
        return []
    from detection_balance import read_sheets
    return [(_norm(nom), list(r)) for nom, rows in read_sheets(path) for r in rows[:80]]


def extraire(lignes, champs):
    """Première valeur plausible de chaque champ : « libellé | valeur » (cellule suivante non vide de la ligne)
    ou « libellé : valeur » dans une seule cellule."""
    out = {}
    for _, row in lignes:
        cells = list(row)
        for i, c in enumerate(cells):
            if not isinstance(c, str) or not c.strip():
                continue
            lib, sep, reste = c.partition(":")
            cle = champ_du_libelle(lib)
            if not cle or cle not in champs or cle in out:
                continue
            v = valeur_plausible(reste) if sep else None
            if v is None:
                suiv = next((x for x in cells[i + 1:i + 9] if x not in (None, "") and str(x).strip()), None)
                v = valeur_plausible(suiv)
            if v:
                out[cle] = v
    return out


def depuis_def(path):
    """Identité lue sur la page de garde (et la fiche R1) d'une DEF déposée. {} si rien de sûr."""
    try:
        lignes = [x for x in _lignes(path) if any(f in x[0] for f in FEUILLES_DEF)]
    except Exception:                                          # noqa: BLE001 — une DEF illisible ne casse pas la génération
        return {}
    return extraire(lignes, CHAMPS_DEF)


def depuis_fiche(path):
    """Identité d'une fiche entité (json, txt « Champ : valeur », classeur ou CSV à deux colonnes)."""
    try:
        if path.lower().endswith(".json"):
            brut = json.load(open(path, encoding="utf-8"))
            src = brut.get("identite", brut) if isinstance(brut, dict) else {}
            return {k: str(v).strip() for k, v in src.items() if k in CHAMPS_FICHE and valeur_plausible(str(v))}
        return extraire(_lignes(path), CHAMPS_FICHE)
    except Exception:                                          # noqa: BLE001
        return {}


def est_fiche(path):
    """Un petit fichier qui porte au moins deux champs d'identité dont la raison sociale ou le NIF."""
    try:
        if os.path.getsize(path) > 200_000:
            return False
        f = depuis_fiche(path)
    except OSError:
        return False
    return len(f) >= 2 and bool({"raison_sociale", "nif"} & set(f))


def fiche_du_dossier_entite(dossier_entite):
    """(identité, chemin) de la fiche posée dans le dossier de l'ENTITÉ (valable pour tous ses exercices)."""
    for nom in NOMS_FICHE:
        for ext in (".json", ".xlsx", ".csv", ".txt"):
            p = os.path.join(dossier_entite, nom + ext)
            if os.path.isfile(p):
                f = depuis_fiche(p)
                if f:
                    return f, p
    return {}, None
