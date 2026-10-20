# -*- coding: utf-8 -*-
"""TF3 (IVA annuelle), TF4 (salaires), TF5 (paiements aux tiers) de la DEF GE, depuis le GRAND LIVRE.

SOURCE UNIQUE : compta-ohada/lib/tf345_ge.py (copies synchronisées par tools/sync_lib.py).

Mêmes principes que fiscal_ge : taux et comptes lus dans parametres_fiscaux_ge.json (surchargeables par le
profil d'entreprise), interprétations chiffrées, faits inconnus = questions, rien ne bloque. Chaque montant
est TRAÇABLE jusqu'aux lignes du grand livre (onglet « Tracabilite » du classeur).

Limites déclarées :
- TF3 : la base imposable est RECONSTITUÉE depuis l'IVA facturée au taux général (art. 155.2). Des opérations
  au taux réduit ou à 0 % exigent la ventilation des déclarations mensuelles.
- TF4 : le grand livre porte la paie en TOTAUX : l'état NOMINATIF (art. 32) exige le fichier de paie.
- TF5 : montants IMPUTÉS en charges par code tiers (les paiements ne sont visibles que si les comptes
  fournisseurs sont détaillés) ; nom / adresse / NIF viennent d'un fichier des tiers, sinon une SUGGESTION
  de nom est tirée des libellés (à confirmer).
"""
import re
from collections import Counter, defaultdict

import fiscal_ge

MOIS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
        "Noviembre", "Diciembre"]
_MOTS_VIDES = set("""FACT FACTURE FACTURA FAC S SUR TVA IVA LOC LOYER LOCATION TRAVAUX TRAV SIT N DE DU DES LA LE LES
ET EN AU A POUR PAR SUIVANT REGL REGLT PAIE PAIEMENT PERS PERSONNEL MOIS DIVERS FR FRAIS HONO HONORAIRES
AVOIR REPARATION MAINT MAINTENANCE ACHAT ACHATS SERVICE SERVICES PRESTATION PRESTATIONS CAMION CAMIONS
SOUS TRAITANCE SOUS-TRAITANCE""".split())


def _comptes(params, profil):
    c = dict(params["comptes"])
    c.update((profil or {}).get("comptes", {}))
    return c


def _dans(compte, racines):
    return any((compte or "").startswith(r) for r in racines)


def _hors_cloture(gl, pieces_cloture):
    return [x for x in gl["lignes"] if x["piece"] not in pieces_cloture]


# --------------------------------------------------------------------------- TF3
def tf3(lignes, params, profil=None, decisions=None, soldes_balance=None):
    d, prof = decisions or {}, profil or {}
    interp, faits, justif = fiscal_ge.resoudre_profil(params, prof, d)
    c = _comptes(params, prof)
    taux = fiscal_ge.P(params, "iva_taux_general")
    par_piece = defaultdict(list)
    for x in lignes:
        par_piece[x["piece"]].append(x)
    # paiements au Trésor D'ABORD : pièce qui DÉBITE l'IVA collectée / due ET CRÉDITE la trésorerie.
    # Ces pièces sont exclues du calcul de l'IVA facturée (un reversement n'est pas une annulation de facture).
    paiements = []
    for p, ls in par_piece.items():
        tva = sum(x["debit"] for x in ls if _dans(x["compte"], c["iva_collectee"] + c["iva_due"]))
        if tva > 0 and any(_dans(x["compte"], c["tresorerie"]) and x["credit"] > 0 for x in ls):
            paiements.append({"date": ls[0]["date"], "piece": p, "montant": round(tva, 2), "carta_de_pago": ""})
    pieces_paiement = {p["piece"] for p in paiements}
    mois = {m: {"iva": 0.0, "ca": 0.0, "deductible": 0.0} for m in range(1, 13)}
    trace = []
    ca_racines = Counter()
    for x in lignes:
        m = int(x["date"][5:7])
        if x["piece"] in pieces_paiement:
            if _dans(x["compte"], c["iva_collectee"] + c["iva_due"]):
                trace.append(("TF3 paiement au Trésor", x))
            continue
        if _dans(x["compte"], c["iva_collectee"]):
            mois[m]["iva"] += x["credit"] - x["debit"]; trace.append(("TF3 IVA facturée", x))
        elif _dans(x["compte"], c["iva_deductible"]):
            mois[m]["deductible"] += x["debit"] - x["credit"]; trace.append(("TF3 IVA déductible", x))
        elif _dans(x["compte"], c["ca"]):
            mois[m]["ca"] += x["credit"] - x["debit"]
            ca_racines[x["compte"][:3]] += x["credit"] - x["debit"]
    nature = "venta_bienes" if sum(v for k, v in ca_racines.items() if k in ("701", "702", "703", "704")) > \
        sum(v for k, v in ca_racines.items() if k in ("705", "706", "707")) else "prestacion_servicios"
    avert, questions = [], []
    lignes_mois = []
    for m in range(1, 13):
        v = mois[m]
        base = round(v["iva"] / taux, 2)
        lignes_mois.append({"mois": m, "base": base, "iva": round(v["iva"], 2), "ca": round(v["ca"], 2),
                            "deductible": round(v["deductible"], 2)})
    # sur l'ANNÉE, en net : des mois négatifs (annulations de facturation) existent ; les ignorer gonflerait le montant
    ca_annuel = round(sum(x["ca"] for x in lignes_mois), 2)
    ca_sans_tva = max(round(ca_annuel - sum(x["base"] for x in lignes_mois), 2), 0.0)
    iva_tot = round(sum(x["iva"] for x in lignes_mois), 2)
    ded_tot = round(sum(x["deductible"] for x in lignes_mois), 2)
    exo_col = 0.0
    if ca_sans_tva >= 1:
        rep = faits.get("iva_ca_sans_tva")
        if rep is None:
            questions.append({"fait": "iva_ca_sans_tva", "article": params["faits"]["iva_ca_sans_tva"]["article"],
                              "question": params["faits"]["iva_ca_sans_tva"]["question"], "montant": round(ca_sans_tva, 2)})
            avert.append(f"QUESTION (art. 155) : {ca_sans_tva:,.0f} de chiffre d'affaires sans IVA facturée — exonéré, hors "
                         "champ ou à régulariser ? Sans réponse, rien n'est porté en « base exonerada ».")
        elif rep == "exonere":
            exo_col = ca_sans_tva
        elif rep == "a_regulariser":
            avert.append(f"CA déclaré « à régulariser » : IVA potentiellement due {ca_sans_tva * taux:,.0f} "
                         f"({taux:.0%} × {ca_sans_tva:,.0f}, art. 155.2).")
    if not paiements:
        avert.append("Aucun reversement d'IVA au Trésor identifié dans le grand livre (pièce débitant l'IVA collectée "
                     "ou due contre la trésorerie). Section « pagos » vide : fournir les cartas de pago si des paiements existent.")
    if soldes_balance:
        cum = sum(s for a, s in soldes_balance.items() if _dans(a, c["iva_collectee"] + c["iva_due"]))
        if cum < -1:
            avert.append(f"Solde créditeur CUMULÉ des comptes d'IVA collectée/due en fin d'exercice : {-cum:,.0f} "
                         "(IVA facturée non reversée, exercices antérieurs compris ?).")
    dans_paiements = interp["tf3_iva_deductible"] == "dans_paiements"
    pay_tot = round(sum(x["montant"] for x in paiements), 2)
    if dans_paiements:
        avert.append(f"INTERPRÉTATION D'ENTREPRISE (tf3_iva_deductible = dans_paiements) : {ded_tot:,.2f} d'IVA déductible "
                     "présentés dans la section « pagos », sans carta de pago. Lecture par défaut : ligne distincte (art. 156)."
                     + (f" Justification : {justif['tf3_iva_deductible']}" if justif.get("tf3_iva_deductible") else ""))
    l28 = pay_tot + (ded_tot if dans_paiements else 0.0)
    l15b = 0.0 if dans_paiements else ded_tot
    net = round(iva_tot - l15b - l28, 2)
    return {"mois": lignes_mois, "nature": nature, "taux": taux, "base_totale": round(sum(x["base"] for x in lignes_mois), 2),
            "iva_theorique": iva_tot, "iva_deductible": ded_tot, "ligne_15bis": l15b, "paiements": paiements,
            "ligne_28": round(l28, 2), "ligne_29": max(net, 0.0), "ligne_30": max(-net, 0.0), "base_exoneree": round(exo_col, 2),
            "ca_sans_iva": round(ca_sans_tva, 2), "ca_annuel": ca_annuel, "interpretation": interp["tf3_iva_deductible"],
            "avertissements": avert, "questions": questions, "trace": trace}


# --------------------------------------------------------------------------- TF4
def tf4(lignes, params, profil=None, libelles=None):
    prof = profil or {}
    c = _comptes(params, prof)
    libelles = libelles or {}
    mots = c.get("irpf_non_national_mots", [])
    cats = {"national": {"remunerations": 0.0, "irpf_retenu": 0.0, "irpf_reverse": 0.0, "cartas": [], "comptes_irpf": set()},
            "non_national": {"remunerations": 0.0, "irpf_retenu": 0.0, "irpf_reverse": 0.0, "cartas": [], "comptes_irpf": set()}}
    par_piece = defaultdict(list)
    for x in lignes:
        par_piece[x["piece"]].append(x)
    forces = prof.get("comptes_irpf", {})          # {"national": [...], "non_national": [...]} si le profil tranche

    def cat_irpf(compte):
        for k, lst in forces.items():
            if compte in lst:
                return k
        lib = fiscal_ge._norm(libelles.get(compte, ""))
        return "non_national" if any(re.search(r"\b" + re.escape(m), lib) for m in mots) else "national"

    trace = []
    for x in lignes:
        if _dans(x["compte"], c["salaires_national"]):
            cats["national"]["remunerations"] += x["debit"] - x["credit"]; trace.append(("TF4 rémunérations nationales", x))
        elif _dans(x["compte"], c["salaires_non_national"]):
            cats["non_national"]["remunerations"] += x["debit"] - x["credit"]; trace.append(("TF4 rémunérations non nationales", x))
        elif _dans(x["compte"], c["irpf"]):
            k = cat_irpf(x["compte"])
            cats[k]["comptes_irpf"].add(x["compte"])
            if x["credit"]:
                cats[k]["irpf_retenu"] += x["credit"]; trace.append((f"TF4 IRPF retenu ({k})", x))
            if x["debit"] and any(_dans(y["compte"], c["tresorerie"]) and y["credit"] > 0 for y in par_piece[x["piece"]]):
                cats[k]["irpf_reverse"] += x["debit"]; cats[k]["cartas"].append(x["piece"])
                trace.append((f"TF4 IRPF reversé ({k})", x))
    avert = [f"État NOMINATIF des salaires ({fiscal_ge.cite(params, 'etat_salaires')}) : nom, fonction, adresse, salaire "
             "imposable, avantages par salarié — le grand livre ne porte que des totaux : fournir le fichier de paie. "
             "TF4 ci-dessous : totaux par catégorie, rapprochables de la paie."]
    for k, v in cats.items():
        if v["irpf_retenu"] and not v["irpf_reverse"]:
            avert.append(f"IRPF {k.replace('_', ' ')} : {v['irpf_retenu']:,.0f} retenus, AUCUN reversement identifié "
                         "dans le grand livre (débit du compte d'IRPF contre la trésorerie).")
        v["comptes_irpf"] = sorted(v["comptes_irpf"])
        for f in ("remunerations", "irpf_retenu", "irpf_reverse"):
            v[f] = round(v[f], 2)
        v["difference"] = round(v["irpf_retenu"] - v["irpf_reverse"], 2)
    if len({a for v in cats.values() for a in v["comptes_irpf"]}) == 1:
        avert.append("Un seul compte d'IRPF : la ventilation nationaux / non nationaux de l'impôt n'est pas possible "
                     "(profil.comptes_irpf pour la préciser).")
    return {"categories": cats, "avertissements": avert, "trace": trace}


# --------------------------------------------------------------------------- TF5
def _tokens_ordonnes(lib):
    """Mots candidats d'un libellé, dans leur ORDRE D'APPARITION (liste, pas ensemble : déterminisme)."""
    vus, out = set(), []
    for t in re.findall(r"[A-Z][A-Z0-9&'.-]{2,}", lib.upper()):
        if t not in _MOTS_VIDES and not re.match(r"^\d", t) and t not in vus:
            vus.add(t); out.append(t)
    return out


def _tokens(lib):
    return set(_tokens_ordonnes(lib))


def _suggestion_nom(libs, bruit=frozenset()):
    """Mots présents dans ≥ 60 % des libellés d'un tiers, hors mots vides et hors BRUIT (mots communs à de
    nombreux tiers : codes de chantier, de site, de mois…). DÉTERMINISTE : ordre d'apparition dans le premier
    libellé qui les porte — jamais l'ordre d'itération d'un ensemble (variable d'une exécution à l'autre)."""
    listes = [[t for t in _tokens_ordonnes(l) if t not in bruit] for l in libs]
    if not listes:
        return ""
    cpt = Counter(t for lst in listes for t in lst)
    seuil = max(1, int(0.6 * len(listes)))
    ordre = []
    for lst in listes:
        for t in lst:
            if cpt[t] >= seuil and t not in ordre:
                ordre.append(t)
    return " ".join(ordre[:3])


def tf5(lignes, params, profil=None, libelles=None, tiers_ref=None):
    prof = profil or {}
    c = _comptes(params, prof)
    libelles, tiers_ref = libelles or {}, tiers_ref or {}
    par_piece = defaultdict(list)
    for x in lignes:
        par_piece[x["piece"]].append(x)
    agg = defaultdict(lambda: {"ht": 0.0, "iva": 0.0, "comptes": Counter(), "libs": [], "pieces": set(), "lignes": []})
    sans = defaultdict(lambda: {"ht": 0.0, "n": 0})
    for x in lignes:
        if not _dans(x["compte"], c["tf5"]):
            continue
        if not x["tiers"]:
            s = sans[x["compte"]]; s["ht"] += x["debit"] - x["credit"]; s["n"] += 1
            continue
        a = agg[x["tiers"]]
        a["ht"] += x["debit"] - x["credit"]
        a["comptes"][x["compte"]] += x["debit"] - x["credit"]
        a["libs"].append(x["libelle"]); a["lignes"].append(x)
        if x["piece"] not in a["pieces"]:
            a["pieces"].add(x["piece"])
            a["iva"] += sum(y["debit"] - y["credit"] for y in par_piece[x["piece"]] if _dans(y["compte"], c["iva_deductible"]))
    rows, trace = [], []
    df = Counter(t for a in agg.values() for t in set().union(*(_tokens(l) for l in a["libs"])))
    bruit = frozenset(t for t, n in df.items() if n > max(2, 0.15 * len(agg)))
    for code, a in agg.items():
        compte_dom = a["comptes"].most_common(1)[0][0]
        ref = tiers_ref.get(code, {})
        rows.append({"code": code, "nom": ref.get("nom", ""),
                     "nom_suggere": "" if ref.get("nom") else _suggestion_nom(a["libs"], bruit),
                     "adresse": ref.get("adresse", ""), "nif": ref.get("nif", ""),
                     "nature": libelles.get(compte_dom, compte_dom), "compte_principal": compte_dom,
                     "ht": round(a["ht"], 2), "iva": round(a["iva"], 2), "ttc": round(a["ht"] + a["iva"], 2),
                     "nb_lignes": len(a["lignes"])})
        trace += [(f"TF5 {code}", x) for x in a["lignes"]]
    rows.sort(key=lambda r: -r["ht"])
    sans_rows = [{"compte": k, "nature": libelles.get(k, k), "ht": round(v["ht"], 2), "nb_lignes": v["n"]}
                 for k, v in sorted(sans.items(), key=lambda kv: -kv[1]["ht"]) if abs(v["ht"]) >= 1]
    avert = []
    manquants = [r["code"] for r in rows if not (r["nom"] and r["nif"])]
    if manquants:
        avert.append(f"{len(manquants)} bénéficiaire(s) sans nom ou NIF confirmé ({fiscal_ge.cite(params, 'etat_paiements_tiers')} : "
                     "nom, adresse exacte, NIF obligatoires) : fournir le fichier des tiers. Noms « suggérés » tirés des "
                     "libellés : à CONFIRMER, jamais à déposer tels quels.")
    tot_sans = sum(r["ht"] for r in sans_rows)
    if tot_sans >= 1:
        avert.append(f"{tot_sans:,.0f} de charges déclarables sans code tiers ({sum(r['nb_lignes'] for r in sans_rows)} lignes) : "
                     f"bénéficiaires à identifier — une somme non déclarée ou mal identifiée est traitée comme revenu occulte "
                     f"({fiscal_ge.cite(params, 'tiers_non_declares')}).")
    avert.append("Montants IMPUTÉS en charges (HT) ; « importe pagado » exige les règlements, visibles seulement si les "
                 "comptes fournisseurs sont détaillés par tiers dans le grand livre.")
    return {"lignes": rows, "sans_tiers": sans_rows, "total_ht": round(sum(r["ht"] for r in rows), 2),
            "total_sans_tiers": round(tot_sans, 2), "avertissements": avert, "trace": trace}


def calculer(gl, params=None, profil=None, decisions=None, libelles=None, soldes_balance=None, tiers_ref=None, pieces_cloture=None):
    import grand_livre
    params = params or fiscal_ge.load_params()
    cl = pieces_cloture if pieces_cloture is not None else grand_livre.pieces_de_cloture(gl)
    lignes = _hors_cloture(gl, cl)
    r3 = tf3(lignes, params, profil, decisions, soldes_balance)
    r4 = tf4(lignes, params, profil, libelles)
    r5 = tf5(lignes, params, profil, libelles, tiers_ref)
    return {"tf3": r3, "tf4": r4, "tf5": r5, "pieces_cloture_exclues": cl,
            "avertissements": r3["avertissements"] + r4["avertissements"] + r5["avertissements"],
            "questions": r3["questions"]}


def lire_tiers(path):
    """Fichier des tiers (xls/xlsx/csv) : colonnes reconnues par NOM (code, nom, adresse, NIF) — référentiel."""
    from detection_balance import read_sheets, norm
    alias = {"code": ["code", "codetiers", "tiers", "compte", "id"], "nom": ["nom", "raisonsociale", "nombre", "denomination", "name"],
             "adresse": ["adresse", "direccion", "address", "ville"], "nif": ["nif", "numeroidentificationfiscale", "taxid"]}
    out = {}
    for _, rows in read_sheets(path):
        for i, r in enumerate(rows[:10]):
            h = [norm(x) for x in r]
            idx = {k: next((j for j, x in enumerate(h) if x in al), None) for k, al in alias.items()}
            if idx["code"] is not None and idx["nom"] is not None:
                for rr in rows[i + 1:]:
                    code = str(rr[idx["code"]]).strip() if idx["code"] < len(rr) else ""
                    if code:
                        out[code] = {k: (str(rr[j]).strip() if j is not None and j < len(rr) else "") for k, j in idx.items()}
                return out
    return out


# --------------------------------------------------------------------------- Excel (formules vivantes)
def ecrire_xlsx(res, path, params=None, entite="", identifiant=""):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    params = params or fiscal_ge.load_params()
    saisie, gras = PatternFill("solid", fgColor="FFF2CC"), Font(bold=True)
    wb = Workbook()
    wp = wb.active; wp.title = "Parametros"
    wp.append(["Paramètre", "Valeur", "Article (Ley 1/2024)", "Texte"])
    rowp = {}
    for k in ("iva_taux_general", "iva_deduction", "etat_salaires", "etat_paiements_tiers", "tiers_non_declares"):
        v = params["parametres"][k]
        wp.append([k, v["valeur"], v["article"], v["texte"]]); rowp[k] = wp.max_row
    T = f"Parametros!$B${rowp['iva_taux_general']}"

    # ---- TF3
    r3 = res["tf3"]
    ws = wb.create_sheet("TF3")
    ws.append(["Designación entidad:", entite, "", "Número de identificación", identifiant])
    ws.append(["IMPUESTO SOBRE EL VALOR AÑADIDO (IVA) — DECLARACIÓN ANUAL / IVA — DÉCLARATION ANNUELLE"])
    col = {"prestacion_servicios": "D", "venta_bienes": "E"}[r3["nature"]]
    ws.append(["Mes", "Línea", "Explotaciones", "Prestación de servicios", "Venta de bienes", "Auto-consumo", "Base exonerada",
               "IVA facturada (contrôle)", "IVA deducible (info)"])
    r0 = ws.max_row + 1
    for x in r3["mois"]:
        row = [MOIS[x["mois"] - 1], x["mois"], None, None, None, None, None, x["iva"], x["deductible"]]
        ws.append(row)
        rr = ws.max_row
        ws[f"{col}{rr}"] = f"=ROUND(H{rr}/{T},2)"                     # base reconstituée depuis l'IVA facturée
        ws[f"H{rr}"].fill = saisie
    rN = ws.max_row
    ws.append(["TOTAL", 13] + [f"=SUM({c}{r0}:{c}{rN})" for c in "CDEFGHI"])
    rT = ws.max_row
    ws[f"G{rT}"] = r3["base_exoneree"] or 0; ws[f"G{rT}"].fill = saisie
    ws.append(["Tasa a aplicar / Taux (art. 155.2)", 14, None, f"={T}"])
    ws.append(["IVA teórico / IVA théorique", 15, None, f"=ROUND(SUM(C{rT}:F{rT})*{T},2)"])
    r15 = ws.max_row
    ws.append(["IVA soportado deducible / IVA déductible (art. 156) — ligne ajoutée, absente du modèle du dossier pilote", "15 bis", None,
               r3["ligne_15bis"]])
    r15b = ws.max_row; ws[f"D{r15b}"].fill = saisie
    ws.append(["PAGOS HECHOS DURANTE EL EJERCICIO / PAIEMENTS AU TRÉSOR", "", "Fecha", "Nº Carta de pago / pièce", "Importe"])
    rp0 = ws.max_row + 1
    pays = list(r3["paiements"])
    if r3["interpretation"] == "dans_paiements":
        pays.append({"date": "", "piece": "IVA déductible (présentation d'entreprise)", "montant": r3["iva_deductible"]})
    for i, p in enumerate(pays[:12]):
        ws.append([f"Período {i + 1}", 16 + i, p["date"], p.get("carta_de_pago") or p["piece"], p["montant"]])
    for i in range(len(pays[:12]), 12):
        ws.append([f"Período {i + 1}", 16 + i, None, None, 0])
    rp1 = ws.max_row
    ws.append(["Total pagos realizados", 28, None, None, f"=SUM(E{rp0}:E{rp1})"])
    r28 = ws.max_row
    ws.append(["Diferencia del IVA a pagar (15 - 15 bis - 28)", 29, None, None, f"=MAX(D{r15}-D{r15b}-E{r28},0)"])
    ws.append(["Crédito de impuesto (28 + 15 bis - 15)", 30, None, None, f"=MAX(E{r28}+D{r15b}-D{r15},0)"])
    ws.column_dimensions["A"].width = 60
    for c in "CDEFGHI":
        ws.column_dimensions[c].width = 20

    # ---- TF4
    r4 = res["tf4"]
    w4 = wb.create_sheet("TF4")
    w4.append(["DECLARACIÓN ANUAL DE SUELDOS Y SALARIOS — totaux par catégorie (état nominatif : fichier de paie, art. 32)"])
    w4.append(["Categoría / Catégorie", "Remuneraciones (661/662)", "Ventajas en naturaleza", "Impuesto a pagar (I) = IRPF retenu",
               "I.R.P.F. pagado (II)", "Diferencia (I) - (II)", "Cartas de pago", "Comptes IRPF"])
    for k, lab in (("national", "PERSONAL NACIONAL / LOCAL"), ("non_national", "PERSONAL NO NACIONAL / EXPATRIADO")):
        v = r4["categories"][k]
        w4.append([lab, v["remunerations"], None, v["irpf_retenu"], v["irpf_reverse"], None, ", ".join(v["cartas"]),
                   ", ".join(v["comptes_irpf"])])
        rr = w4.max_row
        w4[f"F{rr}"] = f"=D{rr}-E{rr}"
    w4.append(["TOTALES", "=SUM(B3:B4)", "=SUM(C3:C4)", "=SUM(D3:D4)", "=SUM(E3:E4)", "=SUM(F3:F4)"])
    w4.append([]); w4.append(["Salariés (nominatif) : à compléter depuis le fichier de paie — nom, fonction, adresse, "
                              "salaire imposable, avantages, indemnités (art. 32.1)."])
    w4.column_dimensions["A"].width = 38
    for c in "BCDEFGH":
        w4.column_dimensions[c].width = 22

    # ---- TF5
    r5 = res["tf5"]
    w5 = wb.create_sheet("TF5")
    w5.append(["DETALLE DE PAGOS REALIZADOS A TERCEROS (62, 63, 667) — art. 27.2"])
    w5.append(["Código tercero", "Nombre del beneficiario", "Nom SUGGÉRÉ (libellés, à confirmer)", "Dirección", "N.I.F.",
               "Naturaleza", "Importe sin impuesto (HT)", "Impuesto (IVA)", "Total (TTC)"])
    for x in r5["lignes"]:
        w5.append([x["code"], x["nom"], x["nom_suggere"], x["adresse"], x["nif"], x["nature"], x["ht"], x["iva"], None])
        rr = w5.max_row
        w5[f"I{rr}"] = f"=G{rr}+H{rr}"
        for c in "BDE":
            if not w5[f"{c}{rr}"].value:
                w5[f"{c}{rr}"].fill = saisie
    last = w5.max_row
    w5.append(["TOTAL bénéficiaires identifiés par code", "", "", "", "", "", f"=SUM(G3:G{last})", f"=SUM(H3:H{last})", f"=SUM(I3:I{last})"])
    w5.append([]); w5.append(["SANS CODE TIERS — bénéficiaires à identifier (art. 27.4)"])
    s0 = w5.max_row + 1
    for x in r5["sans_tiers"]:
        w5.append([x["compte"], "", "", "", "", x["nature"], x["ht"], None, None, f"{x['nb_lignes']} lignes"])
    if r5["sans_tiers"]:
        w5.append(["TOTAL sans code tiers", "", "", "", "", "", f"=SUM(G{s0}:G{w5.max_row})"])
    for c, wdt in zip("ABCDEFGHI", (14, 30, 30, 26, 16, 34, 20, 18, 20)):
        w5.column_dimensions[c].width = wdt

    # ---- traçabilité et avertissements
    wt = wb.create_sheet("Tracabilite")
    wt.append(["Rubrique", "Compte", "Date", "Journal", "Pièce", "Libellé", "Tiers", "Débit", "Crédit", "Ligne du grand livre"])
    for rub, x in r3["trace"] + r4["trace"] + r5["trace"]:
        wt.append([rub, x["compte"], x["date"], x["journal"], x["piece"], x["libelle"], x["tiers"], x["debit"], x["credit"],
                   x["ligne_source"]])
    wa = wb.create_sheet("Avertissements")
    wa.append(["Avertissement / hypothèse / question"])
    for a in res["avertissements"]:
        wa.append([a])
    wa.column_dimensions["A"].width = 140
    wb.save(path)
    return path
