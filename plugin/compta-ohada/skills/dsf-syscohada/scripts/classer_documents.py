# -*- coding: utf-8 -*-
"""Classifieur de documents DSF (mode adaptatif) — détecte le rôle des fichiers
fournis par l'utilisateur pour qu'il n'ait PAS à se conformer à un format figé.

Pour chaque fichier (CSV/XLSX), inspecte feuilles + en-têtes et devine son rôle :
  balance | grand_livre | registre_immobilisations | detail_tiers | modele_dsf | inconnu
(balance : reconnue par INVARIANTS comptables via detection_balance.py, même sans en-tête)
Puis résume la couverture des intrants DSF et ce qui manque encore.

IMPORTANT : la détection est une PROPOSITION à confirmer par l'utilisateur, pas une
vérité. En cas de doute -> demander. Le prédéfini (mapping, sources) reste la
référence ; ce mode l'enrichit, ne le remplace pas.

Usage :
  python classer_documents.py --fichiers a.xlsx b.csv c.xlsx
  python classer_documents.py --dossier "C:/.../mes_docs"
"""
import argparse
import csv
import datetime
import glob
import json
import os
import re
import sys
import unicodedata

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from detection_balance import analyse as analyse_balance, read_sheets  # noqa: E402


def _norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return "".join(ch for ch in s.lower() if ch.isalnum())


FIELDS = {
    "compte": ["compte", "numerocompte", "nocompte", "ncompte", "cpte", "codecompte", "comptegeneral"],
    "debit": ["debit", "dt", "mouvementdebit", "soldedebit"],
    "credit": ["credit", "ct", "avoir", "soldecredit"],
    "solde": ["solde", "soldefinal", "soldecompte", "balance", "montant", "solden", "solden1"],
    "valeur_brute": ["valeurorigine", "valeurbrute", "vo", "valeuracquisition", "cout", "prixdacquisition"],
    "date_service": ["dateservice", "datemiseenservice", "dateacquisition", "miseenservice"],
    "duree": ["duree", "dureeutilite", "dureeamortissement", "annees"],
    "designation": ["designation", "libelle", "intitule", "bien", "immobilisation"],
    "tiers": ["tiers", "client", "fournisseur", "numeroidentifiant", "raisonsociale", "nif"],
    "echeance": ["echeance", "echeancier", "echu", "nonechu", "delai", "moins1an", "plus1an"],
}
DSF_SHEET_KW = ["bilan", "resultat", "flux", "note", "dsf", "garde", "cf1", "cf2", "annexe"]


def _has(headers_norm, field):
    als = FIELDS[field]
    return any(hn and (hn in als or any(al in hn or (len(hn) >= 2 and hn in al) for al in als))
               for hn in headers_norm)


def _best_headers(rows):
    """Choisit la ligne d'en-tête la plus plausible (max de champs connus)."""
    best, best_sc = [], -1
    for row in rows[:15]:
        hs = [_norm(c) for c in row]
        sc = sum(1 for f in FIELDS if _has(hs, f))
        if sc > best_sc:
            best, best_sc = hs, sc
    return best


def inspect(path):
    """(noms de feuilles, en-têtes plausibles). Lit .xls/.xlsx/.csv via detection_balance."""
    sheets = read_sheets(path)
    headers = []
    for _, rows in sheets[:8]:
        headers += _best_headers(rows[:15])
    names = [n for n, _ in sheets] if os.path.splitext(path)[1].lower() != ".csv" else []
    return names, headers, sheets


def _ecritures_datees(sheets):
    """Part des lignes qui commencent par une DATE d'écriture (série Excel 2000-2040 ou jj/mm/aaaa)
    suivie d'un code journal ou d'une pièce : signature d'un grand livre ou d'un journal."""
    n = hits = 0
    for _, rows in sheets[:3]:
        for r in rows[:3000]:
            if not r or not str(r[0]).strip():
                continue
            n += 1
            v = r[0]
            # .xls rend un float, .xlsx un int pour la même date série : accepter les deux (pas bool)
            serie = isinstance(v, (int, float)) and not isinstance(v, bool) and 36526 <= v <= 51136
            # .xlsx à vraies dates : objet date / datetime, ou son texte ISO « 2025-06-30[ 00:00:00] »
            vraie = isinstance(v, (datetime.date, datetime.datetime)) or bool(re.match(r"^\d{4}-\d{2}-\d{2}", str(v).strip()))
            date = serie or vraie or bool(re.match(r"^\d{2}/\d{2}/\d{4}$", str(v).strip()))
            if date and len(r) > 2 and str(r[1]).strip() and str(r[2]).strip():
                hits += 1
    return hits / n if n else 0.0


def classify(path):
    sheets, headers, grids = inspect(path)
    sn = [_norm(s) for s in sheets]
    dsf_hits = sum(1 for kw in DSF_SHEET_KW if any(kw in s for s in sn))
    scores = {}
    # un modèle DSF contient souvent une feuille « balance » : il doit l'emporter (4 > 3)
    scores["modele_dsf"] = 4 if (len(sheets) >= 5 and dsf_hits >= 2) else (2 if dsf_hits >= 2 else 0)
    # balance : d'abord par INVARIANTS comptables (marche sans en-tête), sinon par en-têtes
    try:
        det = analyse_balance(path)
        par_invariants = det["statut"] != "illisible" and det["confiance"] >= 0.9 and abs(det["equilibre"]) < 1
    except (SystemExit, Exception):
        par_invariants = False
    par_entetes = _has(headers, "compte") and (_has(headers, "solde") or (_has(headers, "debit") and _has(headers, "credit")))
    # Repli par en-têtes (2) conservé : une balance PARTIELLE ou déséquilibrée reste une balance,
    # à signaler, pas un fichier « inconnu ». Le grand livre, qui porte aussi « Débit / Crédit /
    # Solde », l'emporte par sa signature propre (écritures datées) : 3 > 2.
    scores["balance"] = 3 if par_invariants else (2 if par_entetes else 0)
    scores["grand_livre"] = 3 if (not par_invariants and _ecritures_datees(grids) >= 0.3) else 0
    scores["registre_immobilisations"] = 2 if (_has(headers, "valeur_brute") and (_has(headers, "date_service") or _has(headers, "duree"))) else 0
    scores["detail_tiers"] = 2 if (_has(headers, "tiers") and (_has(headers, "solde") or _has(headers, "echeance"))) else 0
    role = max(scores, key=scores.get)
    if scores[role] == 0:
        role = "inconnu"
    return {"fichier": os.path.basename(path), "role": role, "confiance": scores.get(role, 0),
            "nb_feuilles": len(sheets), "scores": scores}


def main():
    p = argparse.ArgumentParser(description="Classifieur de documents DSF (adaptatif).")
    p.add_argument("--fichiers", nargs="*", default=[])
    p.add_argument("--dossier", default=None)
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    files = list(a.fichiers)
    if a.dossier:
        for ext in ("*.xls", "*.xlsx", "*.xlsm", "*.csv"):
            files += glob.glob(os.path.join(a.dossier, ext))
    if not files:
        raise SystemExit("Fournir --fichiers ou --dossier.")
    results = [classify(f) for f in files]
    # couverture des intrants DSF
    trouves = {r["role"] for r in results}
    besoins = {
        "Balance (squelette)": "balance",
        "Registre immobilisations (Note 3)": "registre_immobilisations",
        "Détail tiers (Notes 7/17)": "detail_tiers",
        "Modèle DSF": "modele_dsf",
        "Grand livre (pièce jointe, art. 79.2 e Ley 1/2024)": "grand_livre",
    }
    if a.json:
        print(json.dumps({"documents": results,
                          "couverture": {k: (v in trouves) for k, v in besoins.items()}},
                         ensure_ascii=False, indent=2))
        return
    print("== Rôles détectés (à CONFIRMER par l'utilisateur) ==")
    for r in results:
        print(f"  {r['fichier'][:40]:40s} -> {r['role']:26s} (confiance {r['confiance']}, {r['nb_feuilles']} feuilles)")
    print("\n== Couverture des intrants DSF ==")
    for lbl, role in besoins.items():
        print(f"  [{'x' if role in trouves else ' '}] {lbl}")
    manque_fichier = [lbl for lbl, role in besoins.items() if role not in trouves]
    print("\nNon couvert par fichier (à fournir ou via intake) : "
          + (", ".join(manque_fichier) if manque_fichier else "aucun"))
    print("Rappel : extra-comptable (R1-R3, effectifs, engagements) et retraitements "
          "= intake/jugement ; cell-map = propre au modèle. Confirmer chaque rôle deviné.")


if __name__ == "__main__":
    main()
