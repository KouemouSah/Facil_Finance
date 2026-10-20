# -*- coding: utf-8 -*-
"""Lecture d'un grand livre quelconque (xls/xlsx/csv) par la STRUCTURE de ses lignes.

SOURCE UNIQUE : compta-ohada/lib/grand_livre.py (copies synchronisées par tools/sync_lib.py).

Aucun nom de colonne n'est présupposé :
- ligne d'ÉCRITURE  : porte une DATE (série Excel 2000-2040, datetime, jj/mm/aaaa) dans ses 3 premières
  cellules, et au moins un montant ;
- EN-TÊTE de compte : première cellule = numéro de compte, pas de date -> compte courant (grand livre
  « par compte ») ; si les lignes portent elles-mêmes un compte, il prime (grand livre « à plat ») ;
- REPORT À NOUVEAU  : libellé « report / à nouveau / solde initial / saldo anterior » -> ouverture du compte ;
- DÉBIT / CRÉDIT    : paire de colonnes numériques EXCLUSIVES (une seule non nulle par ligne). Si plusieurs
  paires le sont (soldes progressifs), celle dont une autre paire est le SOLDE PROGRESSIF est retenue ;
- journal / pièce / libellé / tiers : par profil de contenu (codes courts répétés, identifiants, texte long,
  codes tiers du type F833).
Contrôle : ouverture + Σ(D - C) par compte, rapproché de la balance si elle est fournie.
"""
import datetime
import re
from collections import Counter, defaultdict

try:  # paquet facil_moteur (source unique)
    from .detection_balance import parse_number, read_sheets, split_account, guess_decimal
except ImportError:  # copie à plat publiée dans le plugin compta-ohada
    from detection_balance import parse_number, read_sheets, split_account, guess_decimal

_DATE_TXT = re.compile(r"^(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})$")
_OUVERTURE = re.compile(r"report|a[- ]?nouveau|solde initial|saldo anterior|apertura|opening", re.I)
_TIERS = re.compile(r"^[A-Z]{1,3}\d{2,7}[A-Z]?$")
_SYNTHESE = re.compile(r"^(total|totaux|solde|saldo|sous-total|cumul|compte de cumul)\b", re.I)
_PERIODE = re.compile(r"^(total|totaux|totales?)\s+(du|de|del)\b", re.I)          # « Total du <date> au <date> »
_ORIGINE = datetime.date(1899, 12, 30)


def as_date(v):
    if isinstance(v, datetime.datetime):
        return v.date()
    if isinstance(v, datetime.date):
        return v
    if isinstance(v, (int, float)) and not isinstance(v, bool) and 36526 <= v <= 51136:
        return _ORIGINE + datetime.timedelta(days=int(v))
    m = _DATE_TXT.match(str(v).strip())
    if m:
        try:
            return datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            return None
    return None


def lire(path):
    """{'lignes': [...], 'ouvertures': {compte: D-C}, 'detection': {...}} — meilleure feuille retenue."""
    best = None
    for nom, raw in read_sheets(path):
        r = _lire_grille(raw)
        r["detection"]["feuille"] = nom
        if best is None or len(r["lignes"]) > len(best["lignes"]):
            best = r
    return best


def _lire_grille(raw):
    dec = guess_decimal(raw)
    entrees, ouvertures, courant, intitules, periodes = [], defaultdict(float), None, {}, []
    for i, r in enumerate(raw):
        cells = list(r)
        first = next((j for j, v in enumerate(cells) if str(v).strip()), None)
        if first is None:
            continue
        # lignes de synthèse (« Total compte au 31/12 », « Solde créditeur au … ») : datées, mais pas des écritures.
        # Exception retenue plus bas : « Total du <date> au <date> » d'un compte CENTRALISÉ (aucune écriture détaillée,
        # l'édition ne donne que des totaux de période) — ses débits / crédits sont alors les mouvements du compte.
        if any(isinstance(v, str) and _SYNTHESE.match(v.strip()) for v in cells[first:first + 3]):
            if courant and _PERIODE.match(str(cells[first]).strip()):
                periodes.append({"row": i, "cells": cells, "compte": courant})
            continue
        di = next((j for j in range(first, min(first + 3, len(cells))) if as_date(cells[j])), None)
        if di is not None:
            nums = []
            for j, v in enumerate(cells):
                if j == di or v in (None, "") or isinstance(v, bool):
                    continue
                if isinstance(v, (int, float)):
                    nums.append((j, float(v)))
                elif re.search(r"\d[\s .,]\d{3}|[.,]\d{2}\)?-?$", str(v)):   # montant saisi en texte
                    x = parse_number(v, dec)
                    if x is not None:
                        nums.append((j, x))
            if nums:
                entrees.append({"row": i, "cells": cells, "date": as_date(cells[di]), "di": di, "nums": dict(nums),
                                "compte": courant})
            continue
        acc = split_account(cells[first])
        if acc and len(acc[0]) >= 4:
            txt = next((str(v) for v in cells[first + 1:first + 3] if isinstance(v, str) and v.strip()), "")
            if not re.match(r"total|solde|saldo", txt.strip(), re.I):
                courant = acc[0]
                lib = (acc[1] if len(acc) > 1 and acc[1] else txt).strip()
                if lib and courant not in intitules:
                    intitules[courant] = lib              # intitulé du compte (en-tête) : sert aux réintégrations
            continue
        if isinstance(cells[first], str) and _OUVERTURE.search(cells[first]) and courant:
            vals = [parse_number(v, dec) for v in cells[first + 1:]]
            vals = [x for x in vals if x is not None]
            if len(vals) >= 2:
                ouvertures[courant] += vals[0] - vals[1]
    if not entrees:
        return {"lignes": [], "ouvertures": {}, "detection": {"statut": "illisible", "raison": "aucune ligne datée avec montant"}}

    # --- grand livre « à plat » : colonne portant un numéro de compte sur ≥ 90 % des lignes. Elle est
    #     retirée des montants (un compte saisi en nombre n'est pas un débit) et des colonnes de texte.
    col_compte = None
    for j in range(0, 8):
        vals = [e["cells"][j] for e in entrees if j < len(e["cells"]) and j != e["di"]]
        ok = [v for v in vals if split_account(v) and len(split_account(v)[0]) >= 4
              and not (isinstance(v, float) and not v.is_integer())]
        if vals and len(ok) >= 0.9 * len(entrees):
            col_compte = j
            break
    if col_compte is not None:
        for e in entrees:
            e["nums"].pop(col_compte, None)
            a = split_account(e["cells"][col_compte]) if col_compte < len(e["cells"]) else None
            if a:
                e["compte"] = a[0]

    # --- débit / crédit : paires exclusives ; solde progressif pour départager
    pres = Counter(j for e in entrees for j in e["nums"])
    cols = sorted(j for j, n in pres.items() if n >= 0.3 * len(entrees))
    val = lambda e, j: e["nums"].get(j, 0.0) or 0.0
    paires, paires_solde = [], []
    for a, b in zip(cols, cols[1:]):
        excl = sum(1 for e in entrees if not (val(e, a) and val(e, b))) / len(entrees)
        util = sum(1 for e in entrees if val(e, a) or val(e, b)) / len(entrees)
        if excl >= 0.9 and util >= 0.8:
            paires.append((a, b))            # candidat débit / crédit : presque chaque ligne porte un montant
        if excl >= 0.9 and util >= 0.3:
            paires_solde.append((a, b))      # candidat solde progressif : nul chaque fois qu'un compte est soldé
    if not paires:
        return {"lignes": [], "ouvertures": {}, "detection": {"statut": "illisible", "raison": f"aucune paire débit/crédit parmi {cols}"}}

    def progressif(dc, sp):
        ok = n = 0
        prev = {}
        for e in entrees:
            k = e["compte"]
            s = val(e, sp[0]) - val(e, sp[1])
            if k in prev:
                n += 1
                ok += abs(prev[k] + val(e, dc[0]) - val(e, dc[1]) - s) < 1
            prev[k] = s
        return ok / n if n else 0.0

    choix, preuve = paires[0], None
    for dc in paires:
        for sp in paires_solde:
            if sp != dc and sp[0] > dc[1]:
                p = progressif(dc, sp)
                if p >= 0.9 and (preuve is None or p > preuve):
                    choix, preuve = dc, p

    # --- colonnes de texte : journal / pièce / libellé / tiers
    texte = defaultdict(list)
    for e in entrees:
        for j, v in enumerate(e["cells"]):
            if isinstance(v, str) and v.strip() and j != e["di"] and j not in choix and j != col_compte:
                texte[j].append(v.strip())
    n = len(entrees)
    prof = {j: {"n": len(v), "distinct": len(set(v)), "long": sum(map(len, v)) / len(v),
                "tiers": sum(bool(_TIERS.match(x)) for x in v) / len(v)} for j, v in texte.items()}
    lib = max((j for j in prof if prof[j]["n"] >= 0.5 * n), key=lambda j: prof[j]["long"], default=None)
    piece = max((j for j in prof if j != lib and prof[j]["n"] >= 0.5 * n and prof[j]["tiers"] < 0.5),
                key=lambda j: prof[j]["distinct"], default=None)
    journal = min((j for j in prof if j not in (lib, piece) and prof[j]["n"] >= 0.5 * n and prof[j]["long"] <= 6
                   and prof[j]["distinct"] <= 60), default=None)
    tiers = max((j for j in prof if j not in (lib, piece, journal) and prof[j]["tiers"] >= 0.8),
                key=lambda j: prof[j]["n"], default=None)
    get = lambda e, j: (str(e["cells"][j]).strip() if j is not None and j < len(e["cells"]) else "")

    lignes = []
    for e in entrees:
        compte = e["compte"]
        lignes.append({"compte": compte, "date": e["date"].isoformat(), "journal": get(e, journal), "piece": get(e, piece),
                       "libelle": get(e, lib), "tiers": get(e, tiers), "debit": val(e, choix[0]), "credit": val(e, choix[1]),
                       "ligne_source": e["row"] + 1})
    sans_compte = [x for x in lignes if not x["compte"]]     # ex. en-tête d'édition (date d'impression + heure)
    lignes = [x for x in lignes if x["compte"]]
    # comptes CENTRALISÉS : aucune écriture détaillée, seulement des « Total du … au … » -> ces totaux sont les
    # mouvements (une ligne par période, pièce « CENTRALISATION ») ; un compte détaillé garde ses seules écritures
    detailles = {x["compte"] for x in lignes}
    centralises = defaultdict(int)
    for p in periodes:
        if p["compte"] in detailles:
            continue
        # mise en page propre à ces lignes : « Total du <date> au <date> [site] débit crédit [solde D solde C] » ->
        # les deux premiers montants APRÈS la seconde date (une date de série ressemble à un montant : on se fie à
        # la position, pas à la valeur)
        cells = p["cells"]
        dates = [j for j, v in enumerate(cells) if j > 0 and as_date(v)]
        if len(dates) < 2:
            continue
        montants = []
        for v in cells[dates[1] + 1:]:
            if isinstance(v, bool) or v in (None, ""):
                continue
            x = float(v) if isinstance(v, (int, float)) else parse_number(v, dec)
            if x is not None:
                montants.append(x)
        if len(montants) >= 2 and (montants[0] or montants[1]):
            lignes.append({"compte": p["compte"], "date": as_date(cells[dates[1]]).isoformat(), "journal": "",
                           "piece": "CENTRALISATION", "libelle": "Total de période (compte centralisé)", "tiers": "",
                           "debit": montants[0], "credit": montants[1], "ligne_source": p["row"] + 1})
            centralises[p["compte"]] += 1
    det = {"statut": "ok", "lignes": len(lignes),
           "colonnes": {"date": Counter(e["di"] for e in entrees).most_common(1)[0][0], "compte": col_compte,
                        "debit": choix[0], "credit": choix[1],
                        "journal": journal, "piece": piece, "libelle": lib, "tiers": tiers},
           "solde_progressif_verifie": preuve, "lignes_ecartees_sans_compte": [x["ligne_source"] for x in sans_compte],
           "comptes_centralises": dict(centralises)}
    return {"lignes": lignes, "ouvertures": dict(ouvertures), "intitules": intitules, "detection": det}


_JOURNAL_AN = re.compile(r"^(a\s*n|ran|ano|anx|an\d*|report)$", re.I)
# libellé d'à-nouveau : il COMMENCE par la formule (« report frais de mission » n'en est pas un)
_LIB_AN = re.compile(r"^\s*(report\s+[àa]\s+nouveau|[àa][- ]?nouveaux?\b|solde\s+(initial|d.ouverture)|saldo\s+anterior|apertura)", re.I)


def balance_reconstituee(gl):
    """Balance APRÈS INVENTAIRE, AVANT CLÔTURE reconstituée depuis le grand livre seul :
    [(compte, intitulé, ouverture D-C, mouvements débit, mouvements crédit)] + contrôles.
      - ouverture = reports à nouveau (lignes d'en-tête) + écritures d'à-nouveaux datées (journal AN/RAN… ou libellé
        « report / à nouveau ») : ce sont des soldes d'ouverture, pas des mouvements de l'exercice ;
      - l'écriture de CLÔTURE (solde des comptes 6-8 contre le 13) est exclue, sinon charges et produits seraient nuls ;
      - contrôle d'équilibre : Σ ouvertures = 0 et Σ débits = Σ crédits (à 1 près)."""
    cloture = set(pieces_de_cloture(gl))
    ouv = defaultdict(float, gl["ouvertures"])
    md, mc = defaultdict(float), defaultdict(float)
    n_an = 0
    for x in gl["lignes"]:
        if x["piece"] and x["piece"] in cloture:
            continue
        if _JOURNAL_AN.match(x["journal"] or "") or _LIB_AN.match(x["libelle"] or ""):
            ouv[x["compte"]] += x["debit"] - x["credit"]
            n_an += 1
            continue
        md[x["compte"]] += x["debit"]
        mc[x["compte"]] += x["credit"]
    comptes = sorted(set(ouv) | set(md) | set(mc))
    lignes = [(a, (gl.get("intitules") or {}).get(a, ""), round(ouv[a], 2), round(md[a], 2), round(mc[a], 2)) for a in comptes]
    controles = {"ecritures_a_nouveau_datees": n_an, "pieces_de_cloture_exclues": sorted(cloture),
                 "ecart_ouverture": round(sum(ouv.values()), 2), "ecart_mouvements": round(sum(md.values()) - sum(mc.values()), 2),
                 "comptes": len(comptes), "intitules_trouves": sum(1 for x in lignes if x[1])}
    controles["equilibree"] = abs(controles["ecart_ouverture"]) < 1 and abs(controles["ecart_mouvements"]) < 1
    return lignes, controles


def soldes(gl, exclure_pieces=()):
    s = defaultdict(float, gl["ouvertures"])
    for x in gl["lignes"]:
        if x["piece"] not in exclure_pieces:
            s[x["compte"]] += x["debit"] - x["credit"]
    return dict(s)


def rapprocher(gl, soldes_balance, exclure_pieces=()):
    """Comptes dont ouverture + mouvements du grand livre ≠ solde de la balance (versions différentes, etc.)."""
    g = soldes(gl, exclure_pieces)
    ecarts = {a: round(g.get(a, 0.0) - soldes_balance.get(a, 0.0), 2) for a in (set(g) | set(soldes_balance)) if a}
    return {a: e for a, e in sorted(ecarts.items()) if abs(e) >= 1}


def pieces_de_cloture(gl):
    """Pièces qui soldent les comptes de gestion (classes 6-8) : à exclure pour retrouver les charges."""
    par = defaultdict(list)
    for x in gl["lignes"]:
        par[x["piece"]].append(x)
    out = []
    for p, ls in par.items():
        # une pièce qui solde au moins 3 comptes de gestion CONTRE le résultat (13) : écriture de clôture
        # (seuil bas : une petite entité n'a que quelques comptes ; une affectation 13 -> 11/12 n'a pas de gestion)
        g = [x for x in ls if (x["compte"] or "")[:1] in "678"]
        if len(g) >= 3 and any((x["compte"] or "").startswith("13") for x in ls):
            out.append(p)
    return out
