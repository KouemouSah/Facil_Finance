# -*- coding: utf-8 -*-
"""Génère les templates Excel du plugin compta-ohada (openpyxl).
Exécuter : python tools/build_templates.py
Idempotent : régénère les .xlsx dans les dossiers skills/<cycle>/templates/.
"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONEY = '#,##0'
PCT = '0.0%'
HDR = PatternFill("solid", fgColor="1F4E78")
HF = Font(bold=True, color="FFFFFF")
BF = Font(bold=True)
TITLE = Font(bold=True, size=13, color="1F4E78")
NOTE = Font(italic=True, color="808080", size=9)


def _p(*parts):
    return os.path.join(ROOT, "skills", *parts)


def _save(wb, cycle, filename):
    d = _p(cycle, "templates")
    os.makedirs(d, exist_ok=True)
    out = os.path.join(d, filename)
    wb.save(out)
    return out


def hdr_row(ws, row, labels, start=1):
    for j, l in enumerate(labels, start=start):
        c = ws.cell(row, j, l)
        c.fill = HDR; c.font = HF; c.alignment = Alignment(horizontal="center")


# ---------------- 1) Passage résultat comptable -> fiscal ----------------
def build_passage_fiscal():
    wb = Workbook(); ws = wb.active; ws.title = "Passage"
    ws["A1"] = "PASSAGE RÉSULTAT COMPTABLE → RÉSULTAT FISCAL (Ley 1/2024)"; ws["A1"].font = TITLE
    ws.merge_cells("A1:C1")
    ws["A3"] = "Résultat comptable (base)"; ws["A3"].font = BF
    ws["B3"] = 0; ws["B3"].number_format = MONEY

    ws["A5"] = "RÉINTÉGRATIONS (charges non déductibles)"; ws["A5"].font = BF
    hdr_row(ws, 6, ["Libellé", "Montant", "Article justificatif (Ley 1/2024)"])
    r1a, r1b = 7, 16
    for r in range(r1a, r1b + 1):
        ws.cell(r, 2).number_format = MONEY
    ws.cell(17, 1, "Total réintégrations").font = BF
    ws["B17"] = f"=SUM(B{r1a}:B{r1b})"; ws["B17"].number_format = MONEY; ws["B17"].font = BF

    ws["A19"] = "DÉDUCTIONS (justifiées par un article)"; ws["A19"].font = BF
    hdr_row(ws, 20, ["Libellé", "Montant", "Article justificatif (Ley 1/2024)"])
    r2a, r2b = 21, 30
    for r in range(r2a, r2b + 1):
        ws.cell(r, 2).number_format = MONEY
    ws.cell(31, 1, "Total déductions").font = BF
    ws["B31"] = f"=SUM(B{r2a}:B{r2b})"; ws["B31"].number_format = MONEY; ws["B31"].font = BF

    ws.cell(33, 1, "RÉSULTAT FISCAL").font = Font(bold=True, size=12)
    ws["B33"] = "=B3+B17-B31"; ws["B33"].number_format = MONEY; ws["B33"].font = Font(bold=True, size=12)
    ws.cell(35, 1, "Taux IS (à CITER — art. 75)").font = BF
    ws["B35"] = 0; ws["B35"].number_format = PCT
    ws.cell(36, 1, "IS estimé").font = BF
    ws["B36"] = "=ROUND(MAX(B33,0)*B35,2)"; ws["B36"].number_format = MONEY
    ws.cell(38, 1, "⚠ N'inscrire un taux qu'après l'avoir lu et cité dans la loi. À faire valider.").font = NOTE
    ws.column_dimensions["A"].width = 40; ws.column_dimensions["B"].width = 18; ws.column_dimensions["C"].width = 34
    out = _p("fiscalite-guinee-equatoriale", "templates", "passage-resultat-fiscal.xlsx")
    wb.save(out); return out


# ---------------- 2) SIG SYSCOHADA ----------------
def build_sig():
    wb = Workbook(); en = wb.active; en.title = "Entrees"
    en["A1"] = "ENTRÉES — Compte de résultat par nature (anonymisé)"; en["A1"].font = TITLE
    en.merge_cells("A1:B1")
    # (label, valeur exemple)
    lignes = [
        ("Chiffre d'affaires (70)", 2400),
        ("Marge commerciale (si négoce)", 0),
        ("Production de l'exercice (705/706/73/72)", 2400),
        ("Consommations intermédiaires (60/61/62/63)", 1700),
        ("Impôts et taxes (64)", 0),
        ("Charges de personnel (66)", 400),
        ("Autres produits d'exploitation (71/75/78/79)", 0),
        ("Autres charges d'exploitation (65/68)", 0),
        ("Produits financiers (77)", 0),
        ("Charges financières (67)", 0),
        ("Produits HAO (82/84/86/88)", 0),
        ("Charges HAO (81/83/85)", 0),
        ("Impôts sur le résultat (89)", 0),
    ]
    r = 3
    ref = {}
    for label, val in lignes:
        en.cell(r, 1, label).font = BF
        c = en.cell(r, 2, val); c.number_format = MONEY
        ref[label.split(" (")[0]] = f"Entrees!$B${r}"
        r += 1
    en.cell(r + 1, 1, "Valeurs d'exemple — à remplacer par vos agrégats.").font = NOTE
    en.column_dimensions["A"].width = 44; en.column_dimensions["B"].width = 16

    sig = wb.create_sheet("SIG")
    sig["A1"] = "SOLDES INTERMÉDIAIRES DE GESTION (SYSCOHADA révisé)"; sig["A1"].font = TITLE
    sig.merge_cells("A1:C1")
    hdr_row(sig, 3, ["Solde", "Montant", "% du CA"])
    CA = ref["Chiffre d'affaires"]
    mc = ref["Marge commerciale"]
    prod = ref["Production de l'exercice"]
    conso = ref["Consommations intermédiaires"]
    it = ref["Impôts et taxes"]
    cp = ref["Charges de personnel"]
    ap = ref["Autres produits d'exploitation"]
    ac = ref["Autres charges d'exploitation"]
    pf = ref["Produits financiers"]
    cf = ref["Charges financières"]
    ph = ref["Produits HAO"]
    ch = ref["Charges HAO"]
    ir = ref["Impôts sur le résultat"]
    cascade = [
        ("Marge commerciale", "=" + mc),
        ("Valeur ajoutée", "=" + mc + "+" + prod + "-" + conso),
        ("Excédent brut d'exploitation (EBE)", "=B5-" + it + "-" + cp),
        ("Résultat d'exploitation", "=B6+" + ap + "-" + ac),
        ("Résultat financier", "=" + pf + "-" + cf),
        ("Résultat des activités ordinaires (RAO)", "=B7+B8"),
        ("Résultat HAO", "=" + ph + "-" + ch),
        ("Résultat net", "=B9+B10-" + ir),
    ]
    row = 4
    for label, formula in cascade:
        sig.cell(row, 1, label).font = BF
        sig.cell(row, 2, formula).number_format = MONEY
        sig.cell(row, 3, f"=IF({CA}=0,\"\",B{row}/{CA})").number_format = PCT
        row += 1
    sig.cell(row + 1, 1, "Contrôle : Résultat net doit égaler le résultat du bilan.").font = NOTE
    sig.column_dimensions["A"].width = 40; sig.column_dimensions["B"].width = 16; sig.column_dimensions["C"].width = 10
    out = _p("etats-financiers-ohada", "templates", "sig-syscohada.xlsx")
    wb.save(out); return out


# ---------------- 3) Contrôles de balance ----------------
def build_controles_balance():
    wb = Workbook(); ba = wb.active; ba.title = "Balance"
    hdr_row(ba, 1, ["N° compte", "Libellé", "Débit", "Crédit", "Solde"])
    NB = 200
    for r in range(2, NB + 2):
        ba.cell(r, 3).number_format = MONEY
        ba.cell(r, 4).number_format = MONEY
        ba.cell(r, 5, f"=IF(AND(C{r}=\"\",D{r}=\"\"),\"\",N(C{r})-N(D{r}))").number_format = MONEY
    ba.column_dimensions["A"].width = 12; ba.column_dimensions["B"].width = 40
    for col in "CDE":
        ba.column_dimensions[col].width = 16

    co = wb.create_sheet("Controles")
    co["A1"] = "CONTRÔLES DE LA BALANCE"; co["A1"].font = TITLE; co.merge_cells("A1:B1")
    rows = [
        ("Total débit", f"=SUM(Balance!C2:C{NB+1})", MONEY),
        ("Total crédit", f"=SUM(Balance!D2:D{NB+1})", MONEY),
        ("Écart (débit - crédit)", "=B3-B4", MONEY),
        ("Équilibre", '=IF(ROUND(B5,2)=0,"OK","ÉCART")', None),
        ("Nb lignes renseignées", f"=COUNTA(Balance!A2:A{NB+1})", '0'),
    ]
    r = 3
    for label, formula, fmt in rows:
        co.cell(r, 1, label).font = BF
        c = co.cell(r, 2, formula)
        if fmt:
            c.number_format = fmt
        r += 1
    co.cell(r + 1, 1, "Soldes de sens anormal (fournisseur débiteur, client créditeur, amortissement au débit) :").font = NOTE
    co.cell(r + 2, 1, "à examiner via le skill (colonne Solde de l'onglet Balance).").font = NOTE
    co.column_dimensions["A"].width = 30; co.column_dimensions["B"].width = 20
    out = _p("excel-comptable", "templates", "controles-balance.xlsx")
    wb.save(out); return out


# ---------------- 4) Écritures de régularisation (clôture) ----------------
def build_ecritures_regularisation():
    wb = Workbook(); ws = wb.active; ws.title = "Journal"
    ws["A1"] = "ÉCRITURES DE RÉGULARISATION — CLÔTURE (SYSCOHADA)"; ws["A1"].font = TITLE
    ws.merge_cells("A1:D1")
    hdr_row(ws, 3, ["Compte", "Libellé", "Débit", "Crédit"])
    a, b = 4, 33
    for r in range(a, b + 1):
        ws.cell(r, 3).number_format = MONEY
        ws.cell(r, 4).number_format = MONEY
    # exemple : charge à payer électricité
    ws.cell(4, 1, "605"); ws.cell(4, 2, "Électricité déc. (facture non parvenue)"); ws.cell(4, 3, 1200000)
    ws.cell(5, 1, "408"); ws.cell(5, 2, "Fournisseurs, factures non parvenues"); ws.cell(5, 4, 1200000)
    ws.cell(b + 2, 2, "Total débit").font = BF
    ws.cell(b + 2, 3, f"=SUM(C{a}:C{b})").number_format = MONEY
    ws.cell(b + 3, 2, "Total crédit").font = BF
    ws.cell(b + 3, 4, f"=SUM(D{a}:D{b})").number_format = MONEY
    ws.cell(b + 4, 2, "Équilibre").font = BF
    ws.cell(b + 4, 3, f'=IF(ROUND(C{b+2}-D{b+3},2)=0,"OK","ÉCART")')
    ws.cell(b + 6, 1, "Exemple en lignes 4-5 (à remplacer). Comptes à confirmer ; TVA selon régime.").font = NOTE
    ws.column_dimensions["A"].width = 12; ws.column_dimensions["B"].width = 42
    ws.column_dimensions["C"].width = 16; ws.column_dimensions["D"].width = 16
    return _save(wb, "cloture-comptable-ohada", "ecritures-regularisation.xlsx")


# ---------------- 5) Situation de travaux (chantier) ----------------
def build_situation_travaux():
    wb = Workbook(); ws = wb.active; ws.title = "Decompte"
    ws["A1"] = "DÉCOMPTE — SITUATION DE TRAVAUX (BTP)"; ws["A1"].font = TITLE
    ws.merge_cells("A1:B1")
    def line(r, label, val=None, fmt=MONEY, bold=False):
        ws.cell(r, 1, label).font = BF if bold else Font()
        if val is not None:
            c = ws.cell(r, 2, val); c.number_format = fmt
    line(3, "Montant HT", 0)
    line(4, "Révision de prix", 0)
    line(5, "Montant HT révisé", None, bold=True); ws["B5"] = "=B3+B4"; ws["B5"].number_format = MONEY
    line(6, "Taux de TVA (à CITER — loi)", 0, PCT)
    line(7, "TVA", None); ws["B7"] = "=ROUND(B5*B6,2)"; ws["B7"].number_format = MONEY
    line(8, "Montant TTC", None, bold=True); ws["B8"] = "=B5+B7"; ws["B8"].number_format = MONEY
    line(9, "Taux de retenue de garantie (contrat)", 0, PCT)
    line(10, "Retenue de garantie", None); ws["B10"] = "=ROUND(B5*B9,2)"; ws["B10"].number_format = MONEY
    line(11, "Acompte à déduire", 0)
    line(12, "NET À PAYER", None, bold=True); ws["B12"] = "=B8-B10-B11"; ws["B12"].number_format = MONEY
    ws["A12"].font = Font(bold=True, size=12); ws["B12"].font = Font(bold=True, size=12)
    ws.cell(14, 1, "⚠ Taux de TVA à lire et citer dans ley_tributaria_2024.md. RG selon le marché.").font = NOTE
    ws.column_dimensions["A"].width = 38; ws.column_dimensions["B"].width = 18
    return _save(wb, "comptabilite-chantier-btp", "situation-travaux.xlsx")


# ---------------- 6) Avancement chantier ----------------
def build_avancement():
    wb = Workbook(); ws = wb.active; ws.title = "Avancement"
    ws["A1"] = "AVANCEMENT DE CHANTIER (méthode à l'avancement)"; ws["A1"].font = TITLE
    ws.merge_cells("A1:B1")
    ws.cell(3, 1, "Coûts engagés à date").font = BF; ws["B3"] = 0; ws["B3"].number_format = MONEY
    ws.cell(4, 1, "Coût total estimé").font = BF; ws["B4"] = 0; ws["B4"].number_format = MONEY
    ws.cell(5, 1, "Prix du marché").font = BF; ws["B5"] = 0; ws["B5"].number_format = MONEY
    ws.cell(7, 1, "% d'avancement").font = BF
    ws["B7"] = "=IF(B4=0,0,B3/B4)"; ws["B7"].number_format = PCT
    ws.cell(8, 1, "CA à reconnaître").font = BF
    ws["B8"] = "=ROUND(B5*B7,2)"; ws["B8"].number_format = MONEY
    ws.cell(9, 1, "Marge totale prévue").font = BF
    ws["B9"] = "=B5-B4"; ws["B9"].number_format = MONEY
    ws.cell(10, 1, "Marge reconnue à date").font = BF
    ws["B10"] = "=ROUND(B9*B7,2)"; ws["B10"].number_format = MONEY
    ws.cell(11, 1, "Provision perte à terminaison").font = BF
    ws["B11"] = "=IF(B9<0,ROUND(-B9*(1-B7),2),0)"; ws["B11"].number_format = MONEY
    ws.cell(13, 1, "Contrat déficitaire si marge totale prévue < 0 (provision immédiate de la part non courue).").font = NOTE
    ws.column_dimensions["A"].width = 34; ws.column_dimensions["B"].width = 18
    return _save(wb, "comptabilite-chantier-btp", "avancement-chantier.xlsx")


# ---------------- 7) Rapprochement bancaire (trésorerie) ----------------
def build_rapprochement():
    wb = Workbook(); ws = wb.active; ws.title = "Rapprochement"
    ws["A1"] = "ÉTAT DE RAPPROCHEMENT BANCAIRE (SYSCOHADA)"; ws["A1"].font = TITLE
    ws.merge_cells("A1:C1")
    ws.cell(3, 1, "Solde comptable (compte 52)").font = BF; ws["B3"] = 0; ws["B3"].number_format = MONEY
    ws.cell(4, 1, "Solde du relevé bancaire").font = BF; ws["B4"] = 0; ws["B4"].number_format = MONEY
    ws.cell(6, 1, "À AJOUTER au relevé (ex. virements en cours)").font = BF
    hdr_row(ws, 7, ["Libellé", "Montant"])
    aa, ab = 8, 13
    for r in range(aa, ab + 1):
        ws.cell(r, 2).number_format = MONEY
    ws.cell(14, 1, "À RETRANCHER du relevé (ex. chèques non débités, frais)").font = BF
    hdr_row(ws, 15, ["Libellé", "Montant"])
    ra, rb = 16, 21
    for r in range(ra, rb + 1):
        ws.cell(r, 2).number_format = MONEY
    ws.cell(23, 1, "Solde relevé ajusté").font = BF
    ws["B23"] = f"=B4+SUM(B{aa}:B{ab})-SUM(B{ra}:B{rb})"; ws["B23"].number_format = MONEY
    ws.cell(24, 1, "Écart (comptable - ajusté)").font = BF
    ws["B24"] = "=B3-B23"; ws["B24"].number_format = MONEY
    ws.cell(25, 1, "Contrôle").font = BF
    ws["B25"] = '=IF(ROUND(B24,2)=0,"OK","ÉCART")'
    ws.cell(27, 1, "Comptabiliser les frais/agios (631) ; investiguer les écarts anciens.").font = NOTE
    ws.column_dimensions["A"].width = 44; ws.column_dimensions["B"].width = 18
    return _save(wb, "tresorerie-rapprochement-bancaire", "rapprochement-bancaire.xlsx")


# ---------------- 8) Revue analytique (révision) ----------------
def build_revue_analytique():
    wb = Workbook(); ws = wb.active; ws.title = "Revue"
    ws["A1"] = "REVUE ANALYTIQUE — Variations N vs N-1 (SYSCOHADA)"; ws["A1"].font = TITLE
    ws.merge_cells("A1:G1")
    ws.cell(2, 1, "Seuil d'alerte (%)").font = BF
    ws["B2"] = 0.10; ws["B2"].number_format = PCT
    hdr_row(ws, 3, ["N° compte", "Libellé", "Solde N", "Solde N-1", "Variation", "Variation %", "Alerte"])
    a, b = 4, 53
    for r in range(a, b + 1):
        ws.cell(r, 3).number_format = MONEY
        ws.cell(r, 4).number_format = MONEY
        ws.cell(r, 5, f"=IF(AND(C{r}=\"\",D{r}=\"\"),\"\",N(C{r})-N(D{r}))").number_format = MONEY
        ws.cell(r, 6, f'=IF(OR(D{r}="",D{r}=0),"",(N(C{r})-N(D{r}))/ABS(D{r}))').number_format = PCT
        ws.cell(r, 7, f'=IF(F{r}="","",IF(ABS(F{r})>=$B$2,"À investiguer",""))')
    # exemple ligne 4
    ws.cell(4, 1, "605"); ws.cell(4, 2, "Autres achats"); ws.cell(4, 3, 45000000); ws.cell(4, 4, 30000000)
    ws.cell(b + 2, 1, "Exemple ligne 4 (605 : +50% > seuil → À investiguer). À remplacer par votre balance.").font = NOTE
    for col, w in zip("ABCDEFG", [12, 34, 15, 15, 15, 12, 14]):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A4"
    return _save(wb, "revision-comptes-ohada", "revue-analytique.xlsx")


# ---------------- 9) Ratios financiers (analyse) ----------------
def build_ratios():
    wb = Workbook(); en = wb.active; en.title = "Entrees"
    en["A1"] = "ENTRÉES — Agrégats (anonymisés)"; en["A1"].font = TITLE; en.merge_cells("A1:B1")
    items = [
        ("Actif circulant", 900), ("Stocks", 200), ("Créances", 400),
        ("Trésorerie actif", 100), ("Passif circulant", 600),
        ("Capitaux propres", 1200), ("Total passif", 3000),
        ("Dettes financières", 800), ("Chiffre d'affaires HT", 2400),
        ("Résultat net", 150), ("Créances clients TTC", 500),
        ("Dettes fournisseurs TTC", 300), ("Achats", 1400),
    ]
    ref = {}
    r = 3
    for label, val in items:
        en.cell(r, 1, label).font = BF
        en.cell(r, 2, val).number_format = MONEY
        ref[label] = f"Entrees!$B${r}"
        r += 1
    en.cell(r + 1, 1, "Valeurs d'exemple — à remplacer.").font = NOTE
    en.column_dimensions["A"].width = 30; en.column_dimensions["B"].width = 16

    ra = wb.create_sheet("Ratios")
    ra["A1"] = "RATIOS FINANCIERS (OHADA)"; ra["A1"].font = TITLE; ra.merge_cells("A1:B1")
    hdr_row(ra, 3, ["Ratio", "Valeur"])
    AC, ST, CR = ref["Actif circulant"], ref["Stocks"], ref["Créances"]
    PC, CP, TP = ref["Passif circulant"], ref["Capitaux propres"], ref["Total passif"]
    DF, CA, RN = ref["Dettes financières"], ref["Chiffre d'affaires HT"], ref["Résultat net"]
    CCT, DFT, ACH = ref["Créances clients TTC"], ref["Dettes fournisseurs TTC"], ref["Achats"]
    ratios = [
        ("Liquidité générale", f"=IF({PC}=0,\"n/d\",{AC}/{PC})", '0.00'),
        ("Liquidité réduite", f"=IF({PC}=0,\"n/d\",({AC}-{ST})/{PC})", '0.00'),
        ("Autonomie financière", f"=IF({TP}=0,\"n/d\",{CP}/{TP})", '0.00'),
        ("Endettement financier", f"=IF({CP}=0,\"n/d\",{DF}/{CP})", '0.00'),
        ("BFR", f"={ST}+{CR}-{PC}", MONEY),
        ("BFR en jours de CA", f"=IF({CA}=0,\"n/d\",({ST}+{CR}-{PC})*360/{CA})", '0.0'),
        ("Délai clients (jours)", f"=IF({CA}=0,\"n/d\",{CCT}*360/{CA})", '0.0'),
        ("Délai fournisseurs (jours)", f"=IF({ACH}=0,\"n/d\",{DFT}*360/{ACH})", '0.0'),
        ("Rentabilité financière", f"=IF({CP}=0,\"n/d\",{RN}/{CP})", PCT),
    ]
    row = 4
    for label, formula, fmt in ratios:
        ra.cell(row, 1, label).font = BF
        ra.cell(row, 2, formula).number_format = fmt
        row += 1
    ra.cell(row + 1, 1, "Interprétation par le comptable (repères sectoriels à valider).").font = NOTE
    ra.column_dimensions["A"].width = 30; ra.column_dimensions["B"].width = 16
    return _save(wb, "analyse-financiere-btp", "ratios.xlsx")


# ---------------- 10) Suivi des recommandations (audit) ----------------
def build_suivi_recommandations():
    wb = Workbook(); ws = wb.active; ws.title = "Suivi"
    ws["A1"] = "SUIVI DES RECOMMANDATIONS D'AUDIT"; ws["A1"].font = TITLE; ws.merge_cells("A1:F1")
    hdr_row(ws, 3, ["Recommandation", "Criticité", "Responsable", "Échéance", "Statut", "Commentaire"])
    a, b = 4, 33
    ws.column_dimensions["A"].width = 40
    for col, w in zip("BCDEF", [12, 16, 14, 14, 30]):
        ws.column_dimensions[col].width = w
    ws.cell(b + 2, 1, "Nb recommandations").font = BF
    ws.cell(b + 2, 2, f"=COUNTA(A{a}:A{b})")
    ws.cell(b + 3, 1, "Nb clôturées").font = BF
    ws.cell(b + 3, 2, f'=COUNTIF(E{a}:E{b},"Clôturée")')
    ws.cell(b + 4, 1, "Taux de mise en œuvre").font = BF
    ws.cell(b + 4, 2, f"=IF(B{b+2}=0,\"\",B{b+3}/B{b+2})").number_format = PCT
    ws.cell(b + 6, 1, "Statuts suggérés : À faire / En cours / Clôturée.").font = NOTE
    ws.freeze_panes = "A4"
    return _save(wb, "audit-controle-interne-ohada", "suivi-recommandations.xlsx")


# ---------------- 11) Registre d'immobilisations multi-biens ----------------
def build_registre_immobilisations():
    wb = Workbook(); ws = wb.active; ws.title = "Registre"
    ws["A1"] = "REGISTRE D'IMMOBILISATIONS — Exercice N ="; ws["A1"].font = TITLE
    ws.merge_cells("A1:B1")
    ws["C1"] = 2025; ws["C1"].font = Font(bold=True, size=13, color="C00000")
    heads = ["Désignation", "Catégorie", "Valeur origine", "Date service", "Durée",
             "Val. résiduelle", "Annuité", "Prorata1", "Année0",
             "Cumul N-1", "Dotation N", "Cumul N", "VNC N"]
    hdr_row(ws, 3, heads)
    a, b = 4, 43
    for r in range(a, b + 1):
        for col in (3, 6, 10, 11, 12, 13):
            ws.cell(r, col).number_format = MONEY
        ws.cell(r, 4).number_format = 'DD/MM/YYYY'
        ws.cell(r, 7).number_format = MONEY
        ws.cell(r, 8).number_format = '0.0000'
        # formules
        ws.cell(r, 7, f'=IF($E{r}=0,0,($C{r}-$F{r})/$E{r})')
        ws.cell(r, 8, f'=IF($D{r}="","",(360-((MONTH($D{r})-1)*30+(DAY($D{r})-1)))/360)')
        ws.cell(r, 9, f'=IF($D{r}="","",YEAR($D{r}))')
        ws.cell(r, 10, f'=IF($D{r}="","",ROUND($G{r}*MIN($E{r},MAX(0,(($C$1-1)-$I{r})+$H{r})),2))')
        ws.cell(r, 11, f'=IF($D{r}="","",ROUND($G{r}*MIN($E{r},MAX(0,($C$1-$I{r})+$H{r})),2)-$J{r})')
        ws.cell(r, 12, f'=IF($D{r}="","",$J{r}+$K{r})')
        ws.cell(r, 13, f'=IF($D{r}="","",$C{r}-$L{r})')
    # exemples
    ws.cell(4, 1, "Pelle hydraulique"); ws.cell(4, 2, "Matériel de transport"); ws.cell(4, 3, 120000000); ws.cell(4, 4, __import__("datetime").date(2023, 4, 15)); ws.cell(4, 5, 5)
    ws.cell(5, 1, "Camion benne"); ws.cell(5, 2, "Matériel de transport"); ws.cell(5, 3, 45000000); ws.cell(5, 4, __import__("datetime").date(2024, 7, 1)); ws.cell(5, 5, 4)
    # totaux + Note 3C
    t = b + 2
    ws.cell(t, 2, "TOTAL").font = BF
    for col, letter in ((3, "C"), (11, "K"), (12, "L"), (13, "M")):
        ws.cell(t, col, f"=SUM({letter}{a}:{letter}{b})").number_format = MONEY
        ws.cell(t, col).font = BF
    ws.cell(t + 2, 1, "Note 3C — par catégorie (saisir la catégorie) :").font = BF
    hdr_row(ws, t + 3, ["Catégorie", "Brut", "Amort. (Cumul N)", "VNC N", "Dotation N"])
    for i in range(6):
        rr = t + 4 + i
        cat_cell = f"A{rr}"
        ws.cell(rr, 2, f'=IF({cat_cell}="","",SUMIF($B${a}:$B${b},{cat_cell},$C${a}:$C${b}))').number_format = MONEY
        ws.cell(rr, 3, f'=IF({cat_cell}="","",SUMIF($B${a}:$B${b},{cat_cell},$L${a}:$L${b}))').number_format = MONEY
        ws.cell(rr, 4, f'=IF({cat_cell}="","",SUMIF($B${a}:$B${b},{cat_cell},$M${a}:$M${b}))').number_format = MONEY
        ws.cell(rr, 5, f'=IF({cat_cell}="","",SUMIF($B${a}:$B${b},{cat_cell},$K${a}:$K${b}))').number_format = MONEY
    ws.cell(t + 4, 1, "Matériel de transport"); ws.cell(t + 5, 1, "Matériel et outillage")
    ws.column_dimensions["A"].width = 26; ws.column_dimensions["B"].width = 20
    for col in "CFGJKLM":
        ws.column_dimensions[col].width = 15
    ws.freeze_panes = "A4"
    return _save(wb, "immobilisations-ohada", "registre-immobilisations.xlsx")


# ---------------- 12) Dossier de révision par cycle ----------------
def build_dossier_revision():
    wb = Workbook(); ba = wb.active; ba.title = "Balance"
    ba["A1"] = "BALANCE N / N-1 (à coller)"; ba["A1"].font = TITLE; ba.merge_cells("A1:D1")
    ba.cell(2, 1, "Seuil d'alerte (%)").font = BF; ba["E2"] = 0.10; ba["E2"].number_format = PCT
    hdr_row(ba, 3, ["Compte", "Libellé", "Solde N", "Solde N-1", "Cycle", "Variation", "Var %", "Alerte"])
    a, b = 4, 253
    for r in range(a, b + 1):
        ba.cell(r, 3).number_format = MONEY; ba.cell(r, 4).number_format = MONEY
        ba.cell(r, 5, (
            f'=IF($A{r}="","",'
            f'IF(LEFT($A{r},2)="40","Achats/Fournisseurs",'
            f'IF(LEFT($A{r},2)="41","Ventes/Clients",'
            f'IF(OR(LEFT($A{r},2)="42",LEFT($A{r},2)="43"),"Personnel",'
            f'IF(LEFT($A{r},2)="44","État/Fiscal",'
            f'IF(LEFT($A{r},1)="1","Capitaux",'
            f'IF(LEFT($A{r},1)="2","Immobilisations",'
            f'IF(LEFT($A{r},1)="3","Stocks",'
            f'IF(LEFT($A{r},1)="5","Trésorerie",'
            f'IF(LEFT($A{r},1)="6","Charges",'
            f'IF(LEFT($A{r},1)="7","Produits",'
            f'IF(LEFT($A{r},1)="8","HAO","Autres")))))))))))))'
        ))
        ba.cell(r, 6, f'=IF($A{r}="","",$C{r}-$D{r})').number_format = MONEY
        ba.cell(r, 7, f'=IF(OR($A{r}="",$D{r}=0),"",($C{r}-$D{r})/ABS($D{r}))').number_format = PCT
        ba.cell(r, 8, f'=IF($G{r}="","",IF(ABS($G{r})>=$E$2,"À investiguer",""))')
    # exemples
    ba.cell(4, 1, "602000"); ba.cell(4, 2, "Achats matières"); ba.cell(4, 3, 350000000); ba.cell(4, 4, 230000000)
    ba.cell(5, 1, "411000"); ba.cell(5, 2, "Clients"); ba.cell(5, 3, 250000000); ba.cell(5, 4, 180000000)
    ba.column_dimensions["A"].width = 12; ba.column_dimensions["B"].width = 30
    for col in "CDEFG":
        ba.column_dimensions[col].width = 15
    ba.freeze_panes = "A4"

    sy = wb.create_sheet("Synthese")
    sy["A1"] = "SYNTHÈSE PAR CYCLE (feuilles maîtresses)"; sy["A1"].font = TITLE; sy.merge_cells("A1:D1")
    hdr_row(sy, 3, ["Cycle", "Total N", "Total N-1", "Variation", "Var %"])
    cyc_list = ["Achats/Fournisseurs", "Ventes/Clients", "Personnel", "État/Fiscal", "Capitaux",
                "Immobilisations", "Stocks", "Trésorerie", "Charges", "Produits", "HAO", "Autres"]
    for i, c in enumerate(cyc_list):
        r = 4 + i
        sy.cell(r, 1, c)
        sy.cell(r, 2, f'=SUMIF(Balance!$E${a}:$E${b},$A{r},Balance!$C${a}:$C${b})').number_format = MONEY
        sy.cell(r, 3, f'=SUMIF(Balance!$E${a}:$E${b},$A{r},Balance!$D${a}:$D${b})').number_format = MONEY
        sy.cell(r, 4, f'=B{r}-C{r}').number_format = MONEY
        sy.cell(r, 5, f'=IF(C{r}=0,"",(B{r}-C{r})/ABS(C{r}))').number_format = PCT
    sy.column_dimensions["A"].width = 22
    for col in "BCDE":
        sy.column_dimensions[col].width = 16
    return _save(wb, "revision-comptes-ohada", "dossier-revision.xlsx")


if __name__ == "__main__":
    builders = (
        build_passage_fiscal, build_sig, build_controles_balance,        # Lot 1
        build_ecritures_regularisation, build_situation_travaux,          # Lot 2
        build_avancement, build_rapprochement,                            # Lot 2
        build_revue_analytique, build_ratios, build_suivi_recommandations,  # Lot 3
        build_registre_immobilisations, build_dossier_revision,           # Phase 6 (balance-driven)
    )
    for fn in builders:
        print("Généré :", os.path.relpath(fn(), ROOT))
