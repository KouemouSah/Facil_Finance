# -*- coding: utf-8 -*-
"""Génération de la DEF (Declaración Estadística y Fiscal = DSF) — Guinée équatoriale, système normal SYSCOHADA.

Assemble, dans UN classeur présentable et imprimable, tout ce que le plugin sait calculer :
  Couverture · Sommaire · Identification · Bilan actif · Bilan passif · Compte de résultat · TFT ·
  Note 3 (immobilisations) · Notes de détail · TF1 · TF2 · TF3 · TF4 · TF5 · [annexe interne] Contrôles & couverture
puis exporte deux PDF : la DEF, et le rapport de contrôle (interne, jamais joint au dépôt).

Sources : balance (obligatoire), grand livre (TF3-TF5), DEF précédente (colonne N-1, TFT), profil d'entreprise
(identité, interprétations, faits), décisions fiscales. Rien ne bloque : ce qui manque est déclaré dans
« Contrôles & couverture » et marqué « à compléter » dans la DEF.

Usage :
  python def_ge.py --balance B.xls --exercice 2025 --profil p.json [--decisions d.json] [--grand-livre GL.xls]
                   [--def-precedente DEF.xlsx --colonne-precedente N|N-1] [--tiers t.xlsx] --sortie DEF.xlsx [--pdf]
"""
import argparse
import datetime
import json
import os
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import agreger_balance_dsf as agr  # noqa: E402
import fiscal_ge  # noqa: E402
from detection_balance import analyse  # noqa: E402

TFT_LIGNES = [
    ("ZA", "Trésorerie nette au 1er janvier (trésorerie actif N-1 − trésorerie passif N-1)", "A", "total"),
    (None, "Flux de trésorerie provenant des activités opérationnelles", None, "section"),
    ("FA", "Capacité d'autofinancement globale (CAFG)", None, "base"),
    ("FB", "− Variation de l'actif circulant HAO", None, "base"),
    ("FC", "− Variation des stocks", None, "base"),
    ("FD", "− Variation des créances et emplois assimilés", None, "base"),
    ("FE", "+ Variation du passif circulant", None, "base"),
    ("ZB", "Flux de trésorerie provenant des activités opérationnelles (somme FA à FE)", "B", "total"),
    (None, "Flux de trésorerie provenant des activités d'investissement", None, "section"),
    ("FF", "− Décaissements liés aux acquisitions d'immobilisations incorporelles", None, "base"),
    ("FG", "− Décaissements liés aux acquisitions d'immobilisations corporelles", None, "base"),
    ("FH", "− Décaissements liés aux acquisitions d'immobilisations financières", None, "base"),
    ("FI", "+ Encaissements liés aux cessions d'immobilisations incorporelles et corporelles", None, "base"),
    ("FJ", "+ Encaissements liés aux cessions d'immobilisations financières", None, "base"),
    ("ZC", "Flux de trésorerie provenant des activités d'investissement (somme FF à FJ)", "C", "total"),
    (None, "Flux de trésorerie provenant du financement par les capitaux propres", None, "section"),
    ("FK", "+ Augmentations de capital par apports nouveaux", None, "base"),
    ("FL", "+ Subventions d'investissement reçues", None, "base"),
    ("FM", "− Prélèvements sur le capital", None, "base"),
    ("FN", "− Distributions de dividendes", None, "base"),
    ("ZD", "Flux de trésorerie provenant des capitaux propres (somme FK à FN)", "D", "total"),
    (None, "Trésorerie provenant du financement par les capitaux étrangers", None, "section"),
    ("FO", "+ Emprunts", None, "base"),
    ("FP", "+ Autres dettes financières", None, "base"),
    ("FQ", "− Remboursements des emprunts et autres dettes financières", None, "base"),
    ("ZE", "Flux de trésorerie provenant des capitaux étrangers (somme FO à FQ)", "E", "total"),
    ("ZF", "Flux de trésorerie provenant des activités de financement (D + E)", "F", "total"),
    ("ZG", "VARIATION DE LA TRÉSORERIE NETTE DE LA PÉRIODE (B + C + F)", "G", "total"),
    ("ZH", "Trésorerie nette au 31 décembre (G + A)", "H", "total"),
]


# --------------------------------------------------------------------------- lecture d'une DEF antérieure (N-1)
def lire_def_ge(path, colonne="N-1"):
    """Postes {REF: montant} d'une DEF au format GE (feuilles bilan / compte de résultat avec colonnes REF).
    colonne « N » : exercice de cette DEF ; « N-1 » : sa colonne comparative. Repérage par les codes REF,
    pas par des adresses de cellules."""
    import openpyxl
    import re as _re
    wb = openpyxl.load_workbook(path, data_only=True)
    out = {}
    est_ref = lambda v: isinstance(v, str) and len(v.strip()) == 2 and v.strip().isupper() and v.strip().isalpha()

    def annee(v):
        if isinstance(v, (datetime.date, datetime.datetime)):
            return v.year
        m = _re.search(r"(19|20)\d{2}", str(v or ""))
        return int(m.group(0)) if m else None

    def par_entetes(ws):
        """Colonnes « NET » de l'en-tête, datées par la cellule au-dessus : N = année la plus récente."""
        rows = list(ws.iter_rows(max_row=12))
        refs = sorted({c.column for r in rows for c in r if isinstance(c.value, str) and c.value.strip().upper() == "REF"})
        nets = {}

        def date_au_dessus(col, row):
            """Date de l'en-tête au-dessus de la colonne ; une cellule FUSIONNÉE ne porte sa valeur qu'à gauche :
            on remonte la ligne vers la gauche jusqu'à la première cellule non vide (sans franchir une colonne REF)."""
            for k in range(row - 2, -1, -1):
                for cc in range(col, 0, -1):
                    if cc in refs:
                        break
                    v = rows[k][cc - 1].value if cc - 1 < len(rows[k]) else None
                    if v not in (None, ""):
                        if annee(v):
                            return annee(v)
                        break
            return None

        for r in rows:
            for c in r:
                if isinstance(c.value, str) and c.value.strip().upper() == "NET":
                    an = date_au_dessus(c.column, c.row)
                    if an:
                        nets[c.column] = an
        if not refs or len(nets) < 2:
            return False
        bornes = refs + [10 ** 6]
        for i, rc in enumerate(refs):
            cols = {c: an for c, an in nets.items() if bornes[i] < c < bornes[i + 1]}
            if len(cols) < 2:
                continue
            col_n = max(cols, key=lambda c: (cols[c], c))
            col_n1 = min(cols, key=lambda c: (cols[c], -c))
            col = col_n1 if colonne == "N-1" else col_n
            for row in ws.iter_rows(min_row=1):
                ref = row[rc - 1].value if rc - 1 < len(row) else None
                val = row[col - 1].value if col - 1 < len(row) else None
                if est_ref(ref) and isinstance(val, (int, float)) and not isinstance(val, bool) and ref.strip() not in out:
                    out[ref.strip()] = val
        return True

    def scan(ws):
        if par_entetes(ws):
            return
        for row in ws.iter_rows():
            cells = list(row)
            for i, c in enumerate(cells):
                v = c.value
                if isinstance(v, str) and len(v.strip()) == 2 and v.strip().isupper() and v.strip().isalpha():
                    ref = v.strip()
                    nums = []
                    for d in cells[i + 1:]:
                        if isinstance(d.value, str) and len(d.value.strip()) == 2 and d.value.strip().isupper() and d.value.strip().isalpha():
                            break                              # début du bloc suivant (passif sur la même ligne)
                        if isinstance(d.value, (int, float)) and not isinstance(d.value, bool):
                            nums.append(d.value)
                    if len(nums) >= 2 and ref not in out:
                        out[ref] = nums[-1] if colonne == "N-1" else nums[-2]
    noms = [n for n in wb.sheetnames if "paysage" in n.lower()] or [n for n in wb.sheetnames if "bilan" in n.lower()]
    for n in noms[:1] + [n for n in wb.sheetnames if "sultat" in n.lower()][:1]:
        scan(wb[n])
    return out


# --------------------------------------------------------------------------- calculs
def _virements(lignes, cle_plus, cle_moins, total_virement, cle_vir):
    """Répartit un montant de VIREMENTS de poste à poste : sorties = diminutions des postes ; entrées imputées
    d'abord aux postes aux plus fortes augmentations (heuristique déclarée : un virement est en général bien
    plus gros que les opérations courantes). Les augmentations et diminutions restantes sont les vraies."""
    reste_out = total_virement
    for L in lignes.values():                              # sorties
        s = min(L[cle_moins], reste_out); L[cle_moins] -= s; L[cle_vir] -= s; reste_out -= s
    reste_in = total_virement
    for L in sorted(lignes.values(), key=lambda x: -x[cle_plus]):   # entrées
        e = min(L[cle_plus], reste_in); L[cle_plus] -= e; L[cle_vir] += e; reste_in -= e


def note3(det, regles, postes, pN):
    """Immobilisations par poste : brut (ouverture, acquisitions, virements, cessions, clôture) et
    amortissements (ouverture, dotations, virements, reprises/sorties, clôture) — depuis les mouvements.
    Une contre-passation NÉGATIVE est reclassée du côté opposé. Sans cession au compte de résultat
    (TN = RO = 0), les diminutions sont des VIREMENTS ; la dotation réelle est calée sur les comptes 681/687."""
    ouv, mv, sol = det.get("soldes_ouverture") or {}, det.get("mouvements") or {}, det["soldes"]
    lignes = {}
    for a in sol:
        r = agr.match_rule(a, regles)
        if not r or r.get("nature") not in ("actif", "amort") or r["ref"] not in postes or postes[r["ref"]].get("note") not in ("3", "4"):
            continue
        L = lignes.setdefault(r["ref"], {k: 0.0 for k in ("b_ouv", "b_aug", "b_vir", "b_dim", "b_clo",
                                                            "a_ouv", "a_dot", "a_vir", "a_rep", "a_clo")})
        md, mk = mv.get(a, (0.0, 0.0))
        deb, cre = max(md, 0) + max(-mk, 0), max(mk, 0) + max(-md, 0)
        if r["nature"] == "actif":
            L["b_ouv"] += ouv.get(a, 0.0); L["b_aug"] += deb; L["b_dim"] += cre; L["b_clo"] += sol[a]
        else:
            L["a_ouv"] += -ouv.get(a, 0.0); L["a_dot"] += cre; L["a_rep"] += deb; L["a_clo"] += -sol[a]
    cessions = abs(pN.get("TN", 0)) >= 1 or abs(pN.get("RO", 0)) >= 1
    heuristique = False
    if not cessions and lignes:
        t_brut = min(sum(L["b_aug"] for L in lignes.values()), sum(L["b_dim"] for L in lignes.values()))
        if t_brut >= 1:
            _virements(lignes, "b_aug", "b_dim", t_brut, "b_vir"); heuristique = True
    dot_reelle = sum(s for a, s in sol.items() if a.startswith(("681", "687")))
    t_amort = min(max(sum(L["a_dot"] for L in lignes.values()) - dot_reelle, 0.0), sum(L["a_rep"] for L in lignes.values()))
    if not cessions and t_amort >= 1:
        _virements(lignes, "a_dot", "a_rep", t_amort, "a_vir"); heuristique = True
    return {k: {kk: round(vv, 2) for kk, vv in v.items()} for k, v in lignes.items()}, bool(mv), heuristique


def tft(pN, p1, det, regles, n3):
    """Tableau des flux de trésorerie (SYSCOHADA révisé) — méthode indirecte, depuis N, N-1 et les mouvements.
    Toujours RÉCONCILIÉ : ZH calculé est comparé à la trésorerie nette du bilan N ; l'écart est affiché, jamais absorbé."""
    g = lambda d, k: (d.get(k) or 0.0)
    v = {}
    v["ZA"] = g(p1, "BT") - g(p1, "DT")
    v["FA"] = g(pN, "XI") - g(pN, "RL") - g(pN, "RN") - g(pN, "TJ") - g(pN, "TL") - g(pN, "TN") - g(pN, "RO")
    v["FB"] = -(g(pN, "BA") - g(p1, "BA"))
    v["FC"] = -(g(pN, "BB") - g(p1, "BB"))
    # écarts de conversion (latents, sans trésorerie) : rattachés aux créances (BU) et aux dettes (DV)
    v["FD"] = -((g(pN, "BG") + g(pN, "BU")) - (g(p1, "BG") + g(p1, "BU")))
    v["FE"] = (g(pN, "DP") + g(pN, "DV")) - (g(p1, "DP") + g(p1, "DV"))
    v["ZB"] = sum(v[k] for k in ("FA", "FB", "FC", "FD", "FE"))
    # acquisitions RÉELLES : la note 3 a déjà isolé les virements de poste à poste (sans flux de trésorerie)
    aug = lambda refs: sum(n3.get(r, {}).get("b_aug", 0.0) for r in refs)
    incorp, corp = ["AE", "AF", "AG", "AH"], ["AJ", "AK", "AL", "AM", "AN", "AP"]
    v["FF"], v["FG"] = -aug(incorp), -aug(corp)
    v["FH"] = -aug(["AR", "AS"])
    v["FI"] = g(pN, "TN")
    v["FJ"] = sum(n3.get(r, {}).get("b_dim", 0.0) for r in ("AR", "AS"))
    v["ZC"] = sum(v[k] for k in ("FF", "FG", "FH", "FI", "FJ"))
    mv = det.get("mouvements") or {}
    cred = lambda p: sum(max(m[1], 0) for a, m in mv.items() if a.startswith(p))
    debi = lambda p: sum(max(m[0], 0) for a, m in mv.items() if a.startswith(p))
    v["FK"] = cred("101") + cred("102") + cred("103") - debi("109")
    v["FL"] = cred("14")
    v["FM"] = 0.0
    e = lambda d: sum(g(d, k) for k in ("CD", "CE", "CF", "CG", "CH", "CJ"))
    v["FN"] = -(e(p1) + g(pN, "XI") - e(pN))                         # dividendes = variation non expliquée par le résultat
    v["ZD"] = sum(v[k] for k in ("FK", "FL", "FM", "FN"))
    v["FO"] = cred("16") + cred("17")
    v["FP"] = cred("18")
    v["FQ"] = -(debi("16") + debi("17") + debi("18"))
    v["ZE"] = sum(v[k] for k in ("FO", "FP", "FQ"))
    v["ZF"] = v["ZD"] + v["ZE"]
    v["ZG"] = v["ZB"] + v["ZC"] + v["ZF"]
    v["ZH"] = v["ZA"] + v["ZG"]
    bilan = g(pN, "BT") - g(pN, "DT")
    v = {k: round(x, 2) for k, x in v.items()}
    return v, round(bilan, 2), round(bilan - v["ZH"], 2)


def calculer(a):
    profil = json.load(open(a.profil, encoding="utf-8")) if a.profil else {}
    decisions = json.load(open(a.decisions, encoding="utf-8")) if a.decisions else None
    det = analyse(a.balance, a.gabarit)
    if det["statut"] != "ok":
        raise SystemExit(f"Balance {det['statut']} : {det.get('raison') or det.get('rivaux')} — relancer avec --gabarit.")
    mapping = agr.load_mapping(agr.DEFAULT_MAPPING)
    regles, postes = mapping
    lib = det.get("libelles", {})
    # 1) fiscalité (TF1/TF2) -> impôt dû ; CMF versée lue dans les fichiers (grand livre, sinon mouvements de la balance)
    gl = None
    if a.grand_livre:
        import grand_livre
        gl = grand_livre.lire(a.grand_livre)
        if gl["detection"].get("statut") != "ok":
            gl = None
    fisc = fiscal_ge.calculer(fiscal_ge.entrees_depuis_soldes(det["soldes"], a.exercice), decisions, det["soldes"],
                              libelles=lib, profil=profil, mouvements=det.get("mouvements"),
                              gl_lignes=gl["lignes"] if gl else None,
                              pieces_exclues=grand_livre.pieces_de_cloture(gl) if gl else ())
    impot = fisc["impot_du"]
    # 2) bilan / CR, IS intégré s'il n'est pas comptabilisé
    bal, info_is = agr.avec_impot(sorted(det["soldes"].items()), impot)
    agg = agr.aggregate(bal, mapping, profil)
    pN = {k: v["montant"] for k, v in agg["par_ref"].items()}
    # 3) N-1 — l'agrégation des soldes d'OUVERTURE est gardée (agg1) : elle sert aussi aux lignes N-1 des notes de
    #    bilan (modèle SYSCOHADA : même règle ligne -> comptes qu'en N, appliquée à l'ouverture)
    agg1 = agr.aggregate(sorted(det["soldes_ouverture"].items()), mapping, profil) if det.get("soldes_ouverture") else None
    # N-1 lu sur une DEF SCANNÉE (ocr_def) : montants prouvés par les formules ou confirmés par l'utilisateur
    n1x = getattr(a, "n1_externe", None) or None
    if a.def_precedente:
        p1 = lire_def_ge(a.def_precedente, a.colonne_precedente)
        src_n1 = f"DEF précédente ({os.path.basename(a.def_precedente)}, colonne {a.colonne_precedente})"
    elif agg1 or n1x:
        # le bilan N-1 vient d'abord des ouvertures de la balance (comptable, exact) ; le scan apporte le compte de
        # résultat N-1, que la balance ne contient pas, et le bilan seulement à défaut d'ouvertures
        p1 = {k: v["montant"] for k, v in agg1["par_ref"].items() if v["etat"] in ("actif", "passif")} if agg1 else {}
        src_n1 = "soldes d'ouverture de la balance (bilan)" if agg1 else ""
        if n1x:
            p1.update({k: v for k, v in n1x["valeurs"].items() if k[0] in "RTX" or not agg1})
            src_n1 = "; ".join(x for x in (src_n1, f"{'compte de résultat' if agg1 else 'bilan et compte de résultat'} "
                                                     f"N-1 : {n1x['source']}") if x)
        else:
            src_n1 += " seulement ; compte de résultat N-1 inconnu"
    else:
        p1, src_n1 = {}, "aucune (colonne N-1 vide)"
    # 4) notes, TFT
    n3, n3_mvts, n3_vir = note3(det, regles, postes, pN)
    flux, treso_bilan, ecart_tft = tft(pN, p1, det, regles, n3) if p1 else ({}, None, None)
    # 5) TF3-TF5
    tf345, gl_det = None, None
    if a.grand_livre:
        import grand_livre
        import tf345_ge
        gl = gl or grand_livre.lire(a.grand_livre)
        gl_det = gl["detection"]
        if gl_det.get("statut") == "ok":
            tiers = tf345_ge.lire_tiers(a.tiers) if a.tiers else None
            tf345 = tf345_ge.calculer(gl, profil=profil, decisions=decisions, libelles=lib, soldes_balance=det["soldes"], tiers_ref=tiers)
    # 6) contrôles
    ctrl = []

    def c(nom, ok, detail=""):
        ctrl.append({"controle": nom, "ok": bool(ok), "detail": detail})

    c("Balance équilibrée (Σ soldes = 0)", abs(det["equilibre"]) < 1, f"{det['equilibre']:,.2f}")
    c("Total actif = total passif", agg["controles"]["actif_egal_passif"]["ok"],
      f"actif {pN['BZ']:,.2f} / passif {pN['DZ']:,.2f}")
    c("Résultat du bilan (CJ) = résultat du compte de résultat (XI)", abs(pN["CJ"] - pN["XI"]) < 1, f"{pN['CJ']:,.2f} / {pN['XI']:,.2f}")
    c("Impôt du compte de résultat (RS) = impôt dû selon TF2", abs(-pN["RS"] - impot) < 1, f"RS {pN['RS']:,.2f} / TF2 {impot:,.2f}")
    if flux:
        c("TFT réconcilié : trésorerie de clôture calculée = bilan", abs(ecart_tft) < 1,
          f"ZH {flux['ZH']:,.2f} / bilan {treso_bilan:,.2f} / écart {ecart_tft:,.2f}")
    for ref, L in n3.items():
        if abs(L["b_clo"] - (agg["par_ref"][ref].get("brut", 0))) >= 1:
            c(f"Note 3 {ref} : brut de clôture = bilan", False, f"{L['b_clo']:,.2f} / {agg['par_ref'][ref].get('brut', 0):,.2f}")
    c("Note 3 : bruts de clôture = bilan (tous postes)", all(abs(L["b_clo"] - agg["par_ref"][r].get("brut", 0)) < 1 for r, L in n3.items()))
    c("Note 3 : ouverture + mouvements = clôture (brut et amortissements)",
      all(abs(L["b_ouv"] + L["b_aug"] + L["b_vir"] - L["b_dim"] - L["b_clo"]) < 1 and
          abs(L["a_ouv"] + L["a_dot"] + L["a_vir"] - L["a_rep"] - L["a_clo"]) < 1 for L in n3.values()))
    dot_n3 = sum(L["a_dot"] for L in n3.values())
    dot_cr = sum(s for a2, s in det["soldes"].items() if a2.startswith(("681", "687")))
    c("Note 3 : dotations = dotations aux amortissements du compte de résultat (681/687)", abs(dot_n3 - dot_cr) < 1,
      f"note 3 {dot_n3:,.2f} / compte de résultat {dot_cr:,.2f}")
    neg = {r: round(v["montant"], 2) for r, v in agg["par_ref"].items() if v["etat"] == "actif" and "total" not in postes[r] and v["montant"] <= -0.5}
    c("Aucune valeur nette négative à l'actif", not neg, f"{neg} — amortissements supérieurs au brut (arrondis dans les comptes) : à régulariser" if neg else "")
    c("Aucun compte non rattaché à un poste", agg["nb_non_mappes"] == 0, str([x["compte"] for x in agg["non_mappes"][:8]]))
    if n1x and agg1:
        # contrôle CROISÉ : le bilan de la DEF scannée (clôture N-1) doit être l'ouverture de la balance N
        ecarts = {r: (round(v), round(agg1["par_ref"][r]["montant"])) for r, v in n1x["valeurs"].items()
                  if r[0] in "ABCD" and r in agg1["par_ref"] and abs(abs(v) - abs(agg1["par_ref"][r]["montant"])) >= 1}
        c("Bilan N-1 de la DEF scannée = ouvertures de la balance", not ecarts,
          ("écarts (scan / balance) : " + "; ".join(f"{r} {a_:,} / {b_:,}" for r, (a_, b_) in list(ecarts.items())[:8]))
          if ecarts else f"{sum(1 for r in n1x['valeurs'] if r[0] in 'ABCD')} postes concordants")
    ident = profil.get("identite", {})
    manquants = [k for k in ("raison_sociale", "nif", "adresse", "activite", "forme_juridique", "dirigeant") if not ident.get(k)]
    couverture = [
        ("Couverture, sommaire, identification", "produit" if not manquants else "partiel", f"à compléter : {', '.join(manquants)}" if manquants else ""),
        ("Bilan actif / passif (N, N-1)", "produit", f"N-1 : {src_n1}"),
        ("Compte de résultat (N, N-1)", "produit", "" if a.def_precedente else f"N-1 : {n1x['source']}" if n1x
         else "N-1 du compte de résultat inconnu sans DEF précédente"),
        ("Tableau des flux de trésorerie", "produit" if flux else "non produit", "réconcilié" if flux and abs(ecart_tft) < 1 else ("écart affiché" if flux else "N-1 requis")),
        ("Note 3 — immobilisations", "produit" if n3_mvts else "partiel",
         ("virements de poste à poste isolés (imputation des entrées aux plus fortes augmentations : à confirmer)" if n3_vir
          else "mouvements tirés de la balance") if n3_mvts else "balance sans mouvements"),
        ("Notes de détail (4 à 30) : composition par compte", "produit", "échéanciers (< 1 an / > 1 an) non ventilés"),
        ("TF1 / TF2 — résultat fiscal, IS, CMF", "produit", ""),
        ("TF3 / TF4 / TF5", "produit" if tf345 else "non produit", "" if tf345 else "grand livre requis (--grand-livre)"),
        ("TF4 nominatif (art. 32)", "non produit", "fichier de paie requis"),
        ("TF5 identité des tiers (art. 27.2)", "partiel" if tf345 else "non produit", "fichier des tiers requis pour nom / NIF / adresse"),
        ("Fiches R2 / R3, notes 27B, 31, 34-36 (statistiques, effectifs, 5 derniers exercices)", "non produit", "données extra-comptables"),
        ("Version espagnole des libellés de postes", "non produit", "en-têtes bilingues seulement"),
    ]
    avert = [info_is["message"]] + agg["avertissements"] + fisc["avertissements"] + (tf345["avertissements"] if tf345 else [])
    return {"exercice": a.exercice, "identite": ident, "postes": postes, "agg": agg, "agg1": agg1, "pN": pN, "p1": p1, "src_n1": src_n1,
            "n3": n3, "tft": flux, "tft_bilan": treso_bilan, "tft_ecart": ecart_tft, "fisc": fisc, "tf345": tf345,
            "info_is": info_is, "libelles": lib, "controles": ctrl, "couverture": couverture, "avertissements": avert,
            "genere_le": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"), "detection": {k: det[k] for k in ("gabarit", "confiance", "feuilles")}}


# --------------------------------------------------------------------------- présentation
def ecrire_xlsx(D, path, logo=None):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.worksheet.pagebreak import Break
    from openpyxl.worksheet.page import PageMargins

    BLEU, BLEU_CLAIR, GRIS, AMBRE = "1F3864", "D9E1F2", "F2F2F2", "FFF2CC"
    NUM = '#,##0;(#,##0);"–"'
    fin = Side(style="thin", color="8EA9DB")
    f_titre = Font(name="Calibri", size=15, bold=True, color=BLEU)
    f_sous = Font(name="Calibri", size=10, italic=True, color="595959")
    f_ent = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    f_b = Font(name="Calibri", size=10, bold=True)
    f_n = Font(name="Calibri", size=10)
    fill = lambda c: PatternFill("solid", fgColor=c)
    I = D["identite"]
    nom, sigle, ex = I.get("raison_sociale", "ENTITÉ À COMPLÉTER"), I.get("sigle", ""), D["exercice"]
    wb = Workbook()
    feuilles_def = []

    def mise_en_page(ws, titre, paysage=False, titres_lignes=None):
        ws.page_setup.paperSize = ws.PAPERSIZE_A4
        ws.page_setup.orientation = "landscape" if paysage else "portrait"
        ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.page_margins = PageMargins(left=0.45, right=0.45, top=0.6, bottom=0.6, header=0.25, footer=0.25)
        ws.print_options.horizontalCentered = True
        if titres_lignes:
            ws.print_title_rows = titres_lignes
        ws.oddFooter.left.text = f"{sigle or nom} — DEF {ex}"
        ws.oddFooter.center.text = "Page &P / &N"
        ws.oddFooter.right.text = titre
        for part in (ws.oddFooter.left, ws.oddFooter.center, ws.oddFooter.right):
            part.size, part.color = 8, "595959"
        ws.sheet_view.showGridLines = False

    def entete(ws, titre_fr, titre_es, cols, largeurs):
        ws.append([nom]); ws.cell(1, 1).font = Font(name="Calibri", size=11, bold=True, color=BLEU)
        ws.append([f"NIF : {I.get('nif', 'à compléter')}   ·   Exercice clos le 31/12/{ex}   ·   Montants en {I.get('monnaie', 'XAF')}"])
        ws.cell(2, 1).font = f_sous
        ws.append([titre_fr]); ws.cell(3, 1).font = f_titre
        ws.append([titre_es]); ws.cell(4, 1).font = f_sous
        ws.append([])
        ws.append(cols)
        for j in range(1, len(cols) + 1):
            c = ws.cell(6, j)
            c.font, c.fill = f_ent, fill(BLEU)
            c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.row_dimensions[6].height = 30
        for j, w in enumerate(largeurs, 1):
            ws.column_dimensions[chr(64 + j)].width = w
        ws.freeze_panes = "A7"

    def style_ligne(ws, r, ncol, kind):
        for j in range(1, ncol + 1):
            c = ws.cell(r, j)
            c.font = f_b if kind in ("total", "grand", "section") else f_n
            if kind == "section":
                c.fill = fill(BLEU_CLAIR)
            elif kind == "total":
                c.fill, c.border = fill(GRIS), Border(top=fin)
            elif kind == "grand":
                c.fill, c.border = fill(BLEU_CLAIR), Border(top=Side(style="thin", color=BLEU), bottom=Side(style="double", color=BLEU))
            if isinstance(c.value, (int, float)) or (isinstance(c.value, str) and c.value.startswith("=")):
                c.number_format = NUM
        ws.cell(r, 1).alignment = Alignment(horizontal="center")

    # ---------------- Couverture
    ws = wb.active; ws.title = "Couverture"; feuilles_def.append(ws.title)
    ws.column_dimensions["A"].width, ws.column_dimensions["B"].width = 4, 92
    lignes = [("", None), ("REPÚBLICA DE GUINEA ECUATORIAL — République de Guinée équatoriale", f_sous),
              ("Ministerio de Hacienda, Economía y Planificación — DGIC", f_sous), ("", None), ("", None),
              ("DECLARACIÓN ESTADÍSTICA Y FISCAL (DEF)", Font(name="Calibri", size=22, bold=True, color=BLEU)),
              ("Déclaration statistique et fiscale — États financiers annuels SYSCOHADA révisé", Font(name="Calibri", size=13, color=BLEU)),
              ("", None), (f"Exercice clos le 31 décembre {ex}", Font(name="Calibri", size=14, bold=True)),
              (I.get("systeme", "Système normal (SYSCOHADA révisé)") + f"  ·  Montants en {I.get('monnaie', 'XAF')}", f_sous),
              ("", None), ("", None), (nom, Font(name="Calibri", size=18, bold=True)),
              (f"{sigle}", Font(name="Calibri", size=12, color="595959")), ("", None)]
    for t, f in lignes:
        ws.append(["", t])
        if f:
            ws.cell(ws.max_row, 2).font = f
    for k, lab in (("nif", "NIF / Número de identificación fiscal"), ("rccm", "RCCM"), ("activite", "Activité principale"),
                   ("adresse", "Adresse"), ("telephone", "Téléphone")):
        ws.append(["", f"{lab} :  {I.get(k) or 'à compléter'}"])
        ws.cell(ws.max_row, 2).font = f_n if I.get(k) else Font(name="Calibri", size=10, color="C00000")
    ws.append([]); ws.append(["", f"Document généré le {D['genere_le']} — à valider et signer par la direction et l'expert-comptable."])
    ws.cell(ws.max_row, 2).font = f_sous
    for r in range(1, ws.max_row + 1):
        ws.cell(r, 2).alignment = Alignment(horizontal="center")
    if logo and os.path.exists(logo):                     # logo de l'ENTITÉ : couverture du rapport uniquement
        from openpyxl.drawing.image import Image
        from openpyxl.drawing.spreadsheet_drawing import AnchorMarker, OneCellAnchor
        from openpyxl.drawing.xdr import XDRPositiveSize2D
        from openpyxl.utils.units import pixels_to_EMU
        im = Image(logo)
        h = 110
        w = int(im.width * h / im.height)
        larg_b = int(92 * 7 + 5)                          # largeur de la colonne B en pixels (92 caractères)
        im.anchor = OneCellAnchor(_from=AnchorMarker(col=1, row=0, colOff=pixels_to_EMU(max((larg_b - w) // 2, 0)),
                                                     rowOff=pixels_to_EMU(8)),
                                  ext=XDRPositiveSize2D(pixels_to_EMU(w), pixels_to_EMU(h)))
        ws.add_image(im)
        ws.row_dimensions[1].height = (h + 16) * 0.75
    mise_en_page(ws, "Couverture")

    # ---------------- Sommaire
    ws = wb.create_sheet("Sommaire"); feuilles_def.append(ws.title)
    entete(ws, "SOMMAIRE", "Índice", ["N°", "État / Tableau", "Feuille"], [8, 70, 24])
    sommaire = [("Identification de l'entité", "Identification"), ("Bilan — actif", "Bilan actif"), ("Bilan — passif", "Bilan passif"),
                ("Compte de résultat", "Compte de résultat"), ("Tableau des flux de trésorerie", "TFT"),
                ("Note 3 — Immobilisations", "Note 3"), ("Notes de détail (composition des postes)", "Notes"),
                ("TF1 — Détermination du résultat fiscal", "TF1"), ("TF2 — Impôt sur les sociétés et Cuota Mínima", "TF2")]
    if D["tf345"]:
        sommaire += [("TF3 — IVA, déclaration annuelle", "TF3"), ("TF4 — Salaires (totaux)", "TF4"), ("TF5 — Paiements aux tiers", "TF5")]
    for i, (t, f) in enumerate(sommaire, 1):
        ws.append([i, t, f]); style_ligne(ws, ws.max_row, 3, "base")
    mise_en_page(ws, "Sommaire")

    # ---------------- Identification (fiche R1 simplifiée)
    ws = wb.create_sheet("Identification"); feuilles_def.append(ws.title)
    entete(ws, "IDENTIFICATION DE L'ENTITÉ (fiche R1)", "Identificación de la entidad", ["Code", "Rubrique", "Renseignement"], [8, 42, 60])
    champs = [("ZA", "Exercice comptable", f"du 01/01/{ex} au 31/12/{ex} (12 mois)"), ("ZB", "Dénomination sociale", I.get("raison_sociale")),
              ("ZC", "Sigle usuel", I.get("sigle")), ("ZD", "N° d'identification fiscale (NIF)", I.get("nif")), ("ZE", "RCCM", I.get("rccm")),
              ("ZF", "Forme juridique", I.get("forme_juridique")), ("ZG", "Activité principale", I.get("activite")),
              ("ZH", "Code activité", I.get("code_activite")), ("ZI", "Adresse", I.get("adresse")), ("ZJ", "Ville", I.get("ville")),
              ("ZK", "Téléphone", I.get("telephone")), ("ZL", "Courriel", I.get("email")),
              ("ZM", "Dirigeant / signataire des états financiers", I.get("dirigeant")),
              ("ZN", "Expert-comptable / commissaire aux comptes", I.get("expert_comptable"))]
    for code, lab, val in champs:
        ws.append([code, lab, val or "à compléter"])
        style_ligne(ws, ws.max_row, 3, "base")
        if not val:
            ws.cell(ws.max_row, 3).fill = fill(AMBRE)
    if I.get("banques"):
        ws.append([]); ws.append(["", "Domiciliations bancaires", ""]); style_ligne(ws, ws.max_row, 3, "section")
        for b, n in I["banques"]:
            ws.append(["", b, n]); style_ligne(ws, ws.max_row, 3, "base")
    mise_en_page(ws, "Identification")

    postes, agg, pN, p1 = D["postes"], D["agg"]["par_ref"], D["pN"], D["p1"]

    def etat(nom_feuille, titre_fr, titre_es, etat_nom, actif=False):
        ws = wb.create_sheet(nom_feuille); feuilles_def.append(nom_feuille)
        if actif:
            entete(ws, titre_fr, titre_es, ["REF", "ACTIF", "Note", "Brut N", "Amort. & dépréc. N", "Net N", "Net N-1"], [7, 52, 7, 18, 18, 18, 18])
        else:
            entete(ws, titre_fr, titre_es, ["REF", "LIBELLÉ" if etat_nom == "resultat" else "PASSIF", "Note", "Exercice N", "Exercice N-1"],
                   [7, 60, 8, 20, 20])
        row_of, totaux = {}, []
        for ref, p in postes.items():                  # 1er passage : toutes les lignes
            if p["etat"] != etat_nom:
                continue
            v = agg[ref]
            if actif:
                ws.append([ref, p["libelle"], p.get("note", ""), None, None, None, p1.get(ref)])
                r = ws.max_row
                if "total" not in p:
                    ws[f"D{r}"], ws[f"E{r}"] = v.get("brut", 0), v.get("amort", 0)
                    ws[f"F{r}"] = f"=D{r}-E{r}"
            else:
                ws.append([ref, p["libelle"], p.get("note", ""), None if "total" in p else v["montant"], p1.get(ref)])
                r = ws.max_row
            row_of[ref] = r
            if "total" in p:
                totaux.append((ref, r, p["total"]))
        for ref, r, parts in totaux:                   # 2e passage : formules (un total peut précéder ses composantes)
            for col in ("DEF" if actif else "D"):
                ws[f"{col}{r}"] = "=" + "+".join(f"{col}{row_of[x]}" for x in parts)
        ncol = 7 if actif else 5
        for ref, r in row_of.items():
            est_total = "total" in postes[ref]
            style_ligne(ws, r, ncol, "grand" if ref in ("BZ", "DZ", "XI") else ("total" if est_total else "base"))
        return ws, row_of

    ws, _ = etat("Bilan actif", "BILAN — ACTIF", "Balance de situación — Activo", "actif", actif=True)
    mise_en_page(ws, "Bilan actif", titres_lignes="6:6")
    ws, _ = etat("Bilan passif", "BILAN — PASSIF", "Balance de situación — Pasivo", "passif")
    mise_en_page(ws, "Bilan passif", titres_lignes="6:6")
    ws, _ = etat("Compte de résultat", "COMPTE DE RÉSULTAT", "Cuenta de resultados (produits +, charges −)", "resultat")
    mise_en_page(ws, "Compte de résultat", titres_lignes="6:6")

    # ---------------- TFT
    ws = wb.create_sheet("TFT"); feuilles_def.append("TFT")
    entete(ws, "TABLEAU DES FLUX DE TRÉSORERIE", "Estado de flujos de efectivo (método indirecto)", ["REF", "LIBELLÉ", "", "Exercice N"], [7, 78, 5, 20])
    t = D["tft"] or {}
    rows = {}
    for ref, lab, lettre, kind in TFT_LIGNES:
        ws.append([ref or "", lab, lettre or "", t.get(ref) if ref else None])
        r = ws.max_row
        if ref:
            rows[ref] = r
        style_ligne(ws, r, 4, "grand" if ref == "ZH" else ("total" if kind == "total" else kind))
    sums = {"ZB": ["FA", "FB", "FC", "FD", "FE"], "ZC": ["FF", "FG", "FH", "FI", "FJ"], "ZD": ["FK", "FL", "FM", "FN"],
            "ZE": ["FO", "FP", "FQ"], "ZF": ["ZD", "ZE"], "ZG": ["ZB", "ZC", "ZF"], "ZH": ["ZG", "ZA"]}
    if t:
        for k, parts in sums.items():
            ws[f"D{rows[k]}"] = "=" + "+".join(f"D{rows[p]}" for p in parts)
            ws[f"D{rows[k]}"].number_format = NUM
        ws.append([]); ws.append(["", "Contrôle : trésorerie nette du bilan N (BT − DT)", "", D["tft_bilan"]])
        style_ligne(ws, ws.max_row, 4, "base")
        ws.append(["", "Écart de réconciliation (doit être nul)", "", f"=D{ws.max_row}-D{rows['ZH']}"])
        style_ligne(ws, ws.max_row, 4, "total")
    else:
        ws.append(["", "Non produit : la colonne N-1 est nécessaire (DEF précédente ou balance avec soldes d'ouverture).", "", None])
    mise_en_page(ws, "TFT", titres_lignes="6:6")

    # ---------------- Note 3
    ws = wb.create_sheet("Note 3"); feuilles_def.append("Note 3")
    entete(ws, "NOTE 3 — IMMOBILISATIONS : MOUVEMENTS DE L'EXERCICE", "Nota 3 — Inmovilizado",
           ["REF", "Rubrique", "Brut ouverture", "Acquisitions", "Virements ±", "Cessions / sorties", "Brut clôture",
            "Amort. ouverture", "Dotations", "Virements ±", "Reprises / sorties", "Amort. clôture", "Valeur nette"],
           [6, 36, 16, 14, 14, 14, 16, 16, 14, 14, 14, 16, 15])
    for j, w in enumerate([6, 36, 16, 14, 14, 14, 16, 16, 14, 14, 14, 16, 15], 1):
        ws.column_dimensions[chr(64 + j)].width = w
    first = ws.max_row + 1
    for ref, p in postes.items():
        if ref in D["n3"]:
            L = D["n3"][ref]
            ws.append([ref, p["libelle"], L["b_ouv"], L["b_aug"], L["b_vir"], L["b_dim"], None,
                       L["a_ouv"], L["a_dot"], L["a_vir"], L["a_rep"], None, None])
            r = ws.max_row
            ws[f"G{r}"], ws[f"L{r}"], ws[f"M{r}"] = f"=C{r}+D{r}+E{r}-F{r}", f"=H{r}+I{r}+J{r}-K{r}", f"=G{r}-L{r}"
            style_ligne(ws, r, 13, "base")
    last = ws.max_row
    ws.append(["", "TOTAL"] + [f"=SUM({c}{first}:{c}{last})" for c in "CDEFGHIJKLM"]); style_ligne(ws, ws.max_row, 13, "grand")
    ws.append([]); ws.append(["", "Mouvements tirés de la balance ; une contre-passation négative est reclassée du côté opposé. Sans cession au compte "
                              "de résultat, les diminutions sont des virements de poste à poste (sans flux) ; les dotations sont calées sur les comptes 681/687."])
    ws.cell(ws.max_row, 2).font = f_sous
    mise_en_page(ws, "Note 3", paysage=True, titres_lignes="6:6")

    # ---------------- Notes de détail
    ws = wb.create_sheet("Notes"); feuilles_def.append("Notes")
    entete(ws, "NOTES ANNEXES — COMPOSITION DES POSTES PAR COMPTE", "Notas — composición de las partidas",
           ["REF", "Compte — libellé", "Colonne", "Exercice N"], [7, 70, 16, 20])
    par_note = {}
    for compte, ref, col, val in D["agg"]["detail"]:
        n = postes.get(ref, {}).get("note")
        if n and n not in ("3",):
            par_note.setdefault(n, []).append((ref, compte, col, val))
    cle = lambda n: (int("".join(ch for ch in n if ch.isdigit()) or 0), n)
    for n in sorted(par_note, key=cle):
        if ws.max_row > 7:
            ws.append([])                      # les notes s'enchaînent (pas une page presque vide par note)
        ws.append(["", f"NOTE {n}", "", None]); style_ligne(ws, ws.max_row, 4, "section")
        for ref in sorted({x[0] for x in par_note[n]}, key=lambda r: list(postes).index(r)):
            items = [x for x in par_note[n] if x[0] == ref]
            ws.append([ref, postes[ref]["libelle"], "", None]); style_ligne(ws, ws.max_row, 4, "total")
            r0 = ws.max_row
            for _, compte, col, val in sorted(items, key=lambda x: x[1]):
                if abs(val) < 0.5:
                    continue
                ws.append(["", f"   {compte} — {D['libelles'].get(compte, '')}", {"brut": "", "amort": "amort. / dépréc.", "montant": ""}[col],
                           -val if col == "amort" else val])
                style_ligne(ws, ws.max_row, 4, "base")
            r1 = ws.max_row
            ws[f"D{r0}"] = f"=SUM(D{r0 + 1}:D{r1})" if r1 > r0 else 0
            ws[f"D{r0}"].number_format = NUM
    mise_en_page(ws, "Notes", titres_lignes="6:6")

    # ---------------- TF1 / TF2
    f1, f2 = D["fisc"]["tf1"], D["fisc"]["tf2"]
    ws = wb.create_sheet("TF1"); feuilles_def.append("TF1")
    entete(ws, "TF1 — DÉTERMINATION DU RÉSULTAT FISCAL", "Determinación del resultado fiscal", ["Ligne", "Rubrique", "Montant"], [8, 78, 22])
    rr = {}
    for n, lab in [(1, "I. Résultat comptable avant impôt / Resultado contable antes de impuesto")] + \
            [(v[0], f"   {v[2]} / {v[1]}") for v in fiscal_ge.TF1_REINT.values()] + [(13, "TOTAL RÉINTÉGRATIONS")] + \
            [(v[0], f"   {v[2]} / {v[1]}") for v in fiscal_ge.TF1_DEDUC.values()] + [(20, "TOTAL DÉDUCTIONS"),
            (22, "IV. RÉSULTAT FISCAL / Resultado neto fiscal"), (24, "V. Déficits antérieurs imputés (art. 73)"), (26, "VI. RÉSULTAT NET FISCAL")]:
        ws.append([n, lab, f1.get(n, 0)]); rr[n] = ws.max_row
        style_ligne(ws, ws.max_row, 3, "grand" if n in (22, 26) else ("total" if n in (1, 13, 20) else "base"))
    ws[f"C{rr[13]}"] = "=" + "+".join(f"C{rr[v[0]]}" for v in fiscal_ge.TF1_REINT.values())
    ws[f"C{rr[20]}"] = "=" + "+".join(f"C{rr[v[0]]}" for v in fiscal_ge.TF1_DEDUC.values())
    ws[f"C{rr[22]}"], ws[f"C{rr[26]}"] = f"=C{rr[1]}+C{rr[13]}-C{rr[20]}", f"=C{rr[22]}-C{rr[24]}"
    for n in (13, 20, 22, 26):
        ws[f"C{rr[n]}"].number_format = NUM
    ws.append([]); ws.append(["", "Détail des réintégrations", ""]); style_ligne(ws, ws.max_row, 3, "section")
    for x in D["fisc"]["reintegrations_detail"]:
        ws.append(["", f"   {x.get('compte', '')} {x.get('libelle', '')} — {x.get('article', '')}", x["montant"]]); style_ligne(ws, ws.max_row, 3, "base")
    mise_en_page(ws, "TF1", titres_lignes="6:6")

    ws = wb.create_sheet("TF2"); feuilles_def.append("TF2")
    entete(ws, "TF2 — IMPÔT SUR LES SOCIÉTÉS ET CUOTA MÍNIMA FISCAL", "Impuesto sobre sociedades y cuota mínima fiscal",
           ["Ligne", "Rubrique", "Montant"], [8, 78, 22])
    it = D["fisc"]["interpretations"]
    for n, lab in [(1, "Bénéfice fiscal"), (2, "Bénéfice exonéré"), (3, "Bénéfice imposable"), (4, "Taux de l'IS (art. 75.2)"),
                   (5, "Impôt sur les sociétés" + ("" if it.get("arrondi_base_is", True) else " — base non arrondie (choix de l'entreprise)")),
                   (6, "Cuota Mínima versée, à déduire (art. 80.2 / 80.3)"), (7, "IMPÔT SUR LES SOCIÉTÉS À PAYER"),
                   (10, "Chiffre d'affaires (comptes 70)"), (11, "Autres produits retenus"), (12, "Base de la Cuota Mínima"),
                   (13, "Taux de la Cuota Mínima (art. 75.3)"), (14, "CUOTA MÍNIMA FISCAL")]:
        ws.append([n, lab, f2.get(n, 0)])
        style_ligne(ws, ws.max_row, 3, "grand" if n in (7, 14) else "base")
        if n in (4, 13):
            ws.cell(ws.max_row, 3).number_format = "0.0%"
    mise_en_page(ws, "TF2", titres_lignes="6:6")

    # ---------------- TF3 / TF4 / TF5
    if D["tf345"]:
        r3, r4, r5 = D["tf345"]["tf3"], D["tf345"]["tf4"], D["tf345"]["tf5"]
        mois = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        ws = wb.create_sheet("TF3"); feuilles_def.append("TF3")
        entete(ws, "TF3 — IVA : DÉCLARATION ANNUELLE", "Impuesto sobre el valor añadido — declaración anual",
               ["Mois", "Base imposable (reconstituée)", "IVA facturée", "IVA déductible", "Chiffre d'affaires"], [14, 26, 22, 22, 22])
        first = ws.max_row + 1
        for x in r3["mois"]:
            ws.append([mois[x["mois"] - 1], x["base"], x["iva"], x["deductible"], x["ca"]]); style_ligne(ws, ws.max_row, 5, "base")
        last = ws.max_row
        ws.append(["TOTAL"] + [f"=SUM({c}{first}:{c}{last})" for c in "BCDE"]); style_ligne(ws, ws.max_row, 5, "total")
        ws.append([])
        l28 = ("(28) « Pagos » : IVA déductible présentée ici (choix de l'entreprise, art. 156)" if r3["interpretation"] == "dans_paiements"
               else "(28) Paiements au Trésor (reversements identifiés)")
        for lab, val in [("(14) Taux appliqué (art. 155.2)", r3["taux"]), ("(15) IVA théorique", r3["iva_theorique"]),
                         ("(15 bis) IVA déductible (art. 156)", r3["ligne_15bis"]), (l28, r3["ligne_28"]),
                         ("(29) IVA restant à payer", r3["ligne_29"]), ("(30) Crédit d'IVA", r3["ligne_30"])]:
            ws.append([lab, None, None, None, val])        # libellé sur A:D (fusionné), montant en E
            r = ws.max_row
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
            style_ligne(ws, r, 5, "grand" if "(29)" in lab else "base")
            ws.cell(r, 1).alignment = Alignment(horizontal="left")
            if "Taux" in lab:
                ws.cell(r, 5).number_format = "0.0%"
        mise_en_page(ws, "TF3", titres_lignes="6:6")
        ws = wb.create_sheet("TF4"); feuilles_def.append("TF4")
        entete(ws, "TF4 — SALAIRES : TOTAUX PAR CATÉGORIE", "Sueldos y salarios (état nominatif : fichier de paie, art. 32)",
               ["Catégorie", "Rémunérations", "IRPF retenu (I)", "IRPF reversé (II)", "Différence (I − II)"], [34, 20, 20, 20, 20])
        for k, lab in (("national", "Personnel national (local)"), ("non_national", "Personnel non national (expatrié)")):
            v = r4["categories"][k]
            ws.append([lab, v["remunerations"], v["irpf_retenu"], v["irpf_reverse"], f"=C{ws.max_row + 1}-D{ws.max_row + 1}"])
            style_ligne(ws, ws.max_row, 5, "base")
            ws.cell(ws.max_row, 1).alignment = Alignment(horizontal="left")
        ws.append(["TOTAL"] + [f"=SUM({c}7:{c}8)" for c in "BCDE"]); style_ligne(ws, ws.max_row, 5, "grand")
        mise_en_page(ws, "TF4", titres_lignes="6:6")
        ws = wb.create_sheet("TF5"); feuilles_def.append("TF5")
        retenu = D.get("tf5_retenu")          # liste arrêtée ailleurs (TF5 hybride du modèle) : le rapport montre LA MÊME
        entete(ws, "TF5 — PAIEMENTS À DES TIERS (comptes 62, 63, 667)", "Detalle de pagos realizados a terceros (art. 27)",
               ["Code tiers", "Bénéficiaire", "NIF", "Nature", "Montant payé" if retenu else "Montant HT", "IVA", "Total"],
               [11, 34, 16, 30, 18, 16, 18])
        first = ws.max_row + 1
        for x in retenu or r5["lignes"]:
            ws.append([x.get("code", ""), x.get("nom") or "à compléter", x.get("nif") or "à compléter", x.get("nature", ""),
                       x.get("ht"), x.get("iva") or 0, f"=E{ws.max_row + 1}+F{ws.max_row + 1}"])
            style_ligne(ws, ws.max_row, 7, "base")
            for col in ("B", "C"):
                if ws[f"{col}{ws.max_row}"].value == "à compléter":
                    ws[f"{col}{ws.max_row}"].fill = fill(AMBRE)
        last = ws.max_row
        ws.append(["TOTAL", "", "", ""] + [f"=SUM({c}{first}:{c}{last})" for c in "EFG"]); style_ligne(ws, ws.max_row, 7, "total")
        if r5["sans_tiers"] and not retenu:
            ws.append(["", "Charges sans code tiers (bénéficiaires à identifier)", "", "", r5["total_sans_tiers"], None, None])
            style_ligne(ws, ws.max_row, 7, "base")
        mise_en_page(ws, "TF5", paysage=True, titres_lignes="6:6")

    # ---------------- Contrôles & couverture (annexe INTERNE, jamais jointe au dépôt)
    ws = wb.create_sheet("Controles")
    entete(ws, "CONTRÔLES ET COUVERTURE — annexe interne (ne pas déposer)", "Controles internos y cobertura",
           ["", "Contrôle / élément", "Statut", "Détail"], [4, 62, 14, 70])
    ws.append(["", "CONTRÔLES DE COHÉRENCE", "", ""]); style_ligne(ws, ws.max_row, 4, "section")
    for x in D["controles"]:
        ws.append(["", x["controle"], "OK" if x["ok"] else "ÉCART", x["detail"]]); style_ligne(ws, ws.max_row, 4, "base")
        ws.cell(ws.max_row, 3).font = Font(name="Calibri", size=10, bold=True, color="00803C" if x["ok"] else "C00000")
    ws.append([]); ws.append(["", "COUVERTURE DE LA DEF", "", ""]); style_ligne(ws, ws.max_row, 4, "section")
    for el, st, det in D["couverture"]:
        ws.append(["", el, st, det]); style_ligne(ws, ws.max_row, 4, "base")
        ws.cell(ws.max_row, 3).fill = fill({"produit": "E2EFDA", "partiel": AMBRE}.get(st, "F8CBAD"))
    ws.append([]); ws.append(["", "AVERTISSEMENTS, HYPOTHÈSES ET QUESTIONS", "", ""]); style_ligne(ws, ws.max_row, 4, "section")
    for w in D["avertissements"]:
        ws.append(["", w, "", ""]); ws.cell(ws.max_row, 2).alignment = Alignment(wrap_text=True, vertical="top")
        ws.merge_cells(start_row=ws.max_row, start_column=2, end_row=ws.max_row, end_column=4)
        ws.row_dimensions[ws.max_row].height = 15 * (1 + len(w) // 140)
    mise_en_page(ws, "Contrôles (interne)", paysage=True)
    wb.save(path)
    return feuilles_def


def exporter_pdf(xlsx, pdf, feuilles):
    """Export PDF des SEULES feuilles demandées, via Excel (COM) : les autres sont masquées EN MÉMOIRE, le
    classeur n'est jamais enregistré. À défaut d'Excel : LibreOffice (toutes les feuilles), sinon message."""
    if os.environ.get("FACIL_PDF", "").lower() == "natif":
        import rendu_pdf
        return "natif" if rendu_pdf.classeur_vers_pdf(xlsx, pdf, feuilles) else None
    liste = ",".join("'" + f.replace("'", "''") + "'" for f in feuilles)
    ps = rf"""
$x = New-Object -ComObject Excel.Application; $x.Visible = $false; $x.DisplayAlerts = $false
try {{ $wb = $x.Workbooks.Open('{os.path.abspath(xlsx)}', 0, $true); $garder = @({liste})
  foreach ($s in $wb.Worksheets) {{ if ($garder -notcontains $s.Name) {{ $s.Visible = 0 }} }}
  $wb.ExportAsFixedFormat(0, '{os.path.abspath(pdf)}', 0, $true, $false); $wb.Close($false); 'OK'
}} finally {{ $x.Quit() }}
"""
    try:
        cp = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=300)
        if "OK" in cp.stdout and os.path.exists(pdf):
            return "excel"
    except (OSError, subprocess.TimeoutExpired):
        pass
    try:                                                  # sans Excel : rendu natif (PyMuPDF), sur toute machine
        import rendu_pdf
        if rendu_pdf.classeur_vers_pdf(xlsx, pdf, feuilles):
            return "natif"
    except Exception:
        pass
    for soffice in ("soffice", r"C:\Program Files\LibreOffice\program\soffice.exe"):
        try:
            subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", os.path.dirname(os.path.abspath(pdf)), xlsx],
                           capture_output=True, timeout=300)
            gen = os.path.splitext(os.path.abspath(xlsx))[0] + ".pdf"
            if os.path.exists(gen):
                os.replace(gen, pdf)
                return "libreoffice (toutes les feuilles)"
        except (OSError, subprocess.TimeoutExpired):
            continue
    return None


def main():
    p = argparse.ArgumentParser(description="Génère la DEF complète (classeur + PDF).")
    p.add_argument("--balance", required=True)
    p.add_argument("--exercice", type=int, required=True)
    p.add_argument("--profil")
    p.add_argument("--decisions")
    p.add_argument("--grand-livre")
    p.add_argument("--tiers")
    p.add_argument("--def-precedente")
    p.add_argument("--colonne-precedente", choices=["N", "N-1"], default="N")
    p.add_argument("--gabarit", default=None)
    p.add_argument("--sortie", required=True)
    p.add_argument("--pdf", action="store_true")
    p.add_argument("--logo", help="logo de l'entité : posé sur la couverture du rapport, nulle part ailleurs")
    a = p.parse_args()
    D = calculer(a)
    feuilles = ecrire_xlsx(D, a.sortie, a.logo)
    print(f"DEF {a.exercice} : {a.sortie}  ({len(feuilles)} feuilles de DEF + annexe interne « Controles »)")
    for x in D["controles"]:
        print(f"  {'OK   ' if x['ok'] else 'ÉCART'} {x['controle']}  {x['detail']}")
    print("Couverture :")
    for el, st, det in D["couverture"]:
        print(f"  [{st:11s}] {el}" + (f" — {det}" if det else ""))
    if a.pdf:
        base = os.path.splitext(a.sortie)[0]
        m1 = exporter_pdf(a.sortie, base + ".pdf", feuilles)
        m2 = exporter_pdf(a.sortie, base + "_controles.pdf", ["Controles"])
        print(f"PDF DEF : {base + '.pdf' if m1 else 'NON PRODUIT (ni Excel ni LibreOffice)'}  [{m1}]")
        print(f"PDF contrôles (interne) : {base + '_controles.pdf' if m2 else 'NON PRODUIT'}")


if __name__ == "__main__":
    main()
