# -*- coding: utf-8 -*-
"""RAPPORT PDF de la DEF (sortie du plugin), distinct de l'impression Excel de la liasse.

Principe : UN calcul, deux présentations. Le classeur officiel (def_modele) est RECALCULÉ par Excel, puis chaque
tableau est relu EN VALEURS et remis en page dans la présentation du rapport (celle de def_ge : bandeau, en-têtes
sur fond bleu, totaux, pied de page) — les chiffres du rapport sont donc, par construction, ceux du classeur.

Contenu (professionnel, pas une copie des 51 feuilles) :
  couverture (logo de l'entité) · sommaire paginé · identification · bilan actif / passif · compte de résultat · TFT ·
  toutes les notes APPLICABLES (lignes sans montant omises) · tableau d'applicabilité des notes (présentée, néant,
  à compléter par l'entité, non reprise) · TF1, réintégrations, TF2 à TF5.
Écartés, et dits dans le tableau d'applicabilité : intercalaires, bilan paysage (doublon de l'actif et du passif),
table des codes (note 36), grille d'analyse (remplacée), balance (annexe séparée, art. 79.2 : PDF à part).
"""
import datetime
import os
import re
import subprocess
import tempfile
import unicodedata

NUM = '#,##0;(#,##0);"–"'
BLEU, BLEU_CLAIR, GRIS, AMBRE = "1F3864", "D9E1F2", "F2F2F2", "FFF2CC"

T = {
    "fr": {"titre": "DÉCLARATION STATISTIQUE ET FISCALE (DEF)", "sous": "États financiers annuels SYSCOHADA révisé — Guinée équatoriale",
           "republique": "République de Guinée équatoriale — Ministère de l'Économie, des Finances et de la Planification — DGIC",
           "exercice": "Exercice clos le 31 décembre {ex}", "monnaie": "Système normal · Montants en XAF",
           "genere": "Document généré le {d} — à valider et signer par la direction et l'expert-comptable.",
           "a_completer": "à compléter", "nif": "NIF", "sommaire": "SOMMAIRE", "page": "Page", "section": "Rubrique",
           "ident": "IDENTIFICATION DE L'ENTITÉ", "rub": "Rubrique", "rens": "Renseignement",
           "applic": "NOTES ANNEXES — APPLICABILITÉ", "note": "Note", "intitule": "Intitulé", "statut": "Statut",
           "presentee": "présentée", "neant": "néant — aucun montant sur l'exercice ni sur le précédent",
           "entite": "à compléter par l'entité (données extra-comptables)", "non_reprise": "non reprise dans le rapport",
           "pied": "{s} — DEF {ex}", "entete_ex": "Exercice clos le 31/12/{ex}  ·  Montants en XAF",
           "etats": "ÉTATS FINANCIERS", "notes": "NOTES ANNEXES", "fiscal": "TABLEAUX FISCAUX (Guinée équatoriale)",
           "motifs": {"bilan paysage": "doublon du bilan actif et du bilan passif", "note 36": "table des codes (nomenclature, pas une donnée de l'entité)",
                      "grille": "remplacée par le présent tableau", "balance": "annexe séparée (art. 79.2) : fichier PDF distinct"},
           "champs": [("raison_sociale", "Dénomination sociale"), ("sigle", "Sigle usuel"), ("nif", "N° d'identification fiscale (NIF)"),
                      ("rccm", "RCCM"), ("forme_juridique", "Forme juridique"), ("activite", "Activité principale"),
                      ("adresse", "Adresse"), ("telephone", "Téléphone"), ("email", "Courriel"),
                      ("dirigeant", "Dirigeant / signataire des états financiers"), ("expert_comptable", "Expert-comptable")]},
    "es": {"titre": "DECLARACIÓN ESTADÍSTICA Y FISCAL (DEF)", "sous": "Estados financieros anuales SYSCOHADA revisado — Guinea Ecuatorial",
           "republique": "República de Guinea Ecuatorial — Ministerio de Hacienda, Economía y Planificación — DGIC",
           "exercice": "Ejercicio cerrado el 31 de diciembre de {ex}", "monnaie": "Sistema normal · Importes en XAF",
           "genere": "Documento generado el {d} — a validar y firmar por la dirección y el experto contable.",
           "a_completer": "a completar", "nif": "NIF", "sommaire": "ÍNDICE", "page": "Página", "section": "Apartado",
           "ident": "IDENTIFICACIÓN DE LA ENTIDAD", "rub": "Concepto", "rens": "Información",
           "applic": "NOTAS ANEXAS — APLICABILIDAD", "note": "Nota", "intitule": "Título", "statut": "Situación",
           "presentee": "presentada", "neant": "sin importe en el ejercicio ni en el anterior",
           "entite": "a completar por la entidad (datos extracontables)", "non_reprise": "no incluida en el informe",
           "pied": "{s} — DEF {ex}", "entete_ex": "Ejercicio cerrado el 31/12/{ex}  ·  Importes en XAF",
           "etats": "ESTADOS FINANCIEROS", "notes": "NOTAS ANEXAS", "fiscal": "CUADROS FISCALES (Guinea Ecuatorial)",
           "motifs": {"bilan paysage": "duplica el balance activo y el balance pasivo", "note 36": "tabla de códigos (nomenclatura, no un dato de la entidad)",
                      "grille": "sustituido por el presente cuadro", "balance": "anexo separado (art. 79.2): archivo PDF distinto"},
           "champs": [("raison_sociale", "Denominación social"), ("sigle", "Sigla"), ("nif", "Número de identificación fiscal (NIF)"),
                      ("rccm", "Registro mercantil"), ("forme_juridique", "Forma jurídica"), ("activite", "Actividad principal"),
                      ("adresse", "Dirección"), ("telephone", "Teléfono"), ("email", "Correo electrónico"),
                      ("dirigeant", "Director / firmante de los estados financieros"), ("expert_comptable", "Experto contable")]},
}
ETATS = ("bilan actif", "bilan passif", "compte resultat", "flux tresorerie")
FISCAUX = ("tf1", "reintegraciones", "tf2", "tf3", "tf4", "tf5")
ECARTES = {"french version": None, "statistiques et syntheses": None, "sommaire": None, "page garde": None,
           "bilan paysage": "bilan paysage", "note 36": "note 36", "grille d'analyse des notes": "grille"}
EXTRA = ("fiche r1", "fiche r2", "fiche r3", "note 27b", "note 35")
# lignes d'en-tête des tableaux fiscaux (modèle GE) : ils n'ont ni REF ni liste de comptes pour les situer
ENTETES_TF = {"tf1": (8, 8), "tf2": (8, 8), "tf3": (8, 9), "tf4": (9, 10), "tf5": (7, 7), "reintegraciones": (2, 2)}


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", s).strip()


def num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def recalculer(xlsx):
    """Valeurs des formules du classeur, SANS Excel : évaluateur du plugin (formules_xl), prouvé contre Excel par
    la garde d'équivalence. Si une formule sortait de son périmètre, Excel prend le relais quand il est présent ;
    sinon les cellules concernées restent vides et c'est signalé."""
    import formules_xl
    out = os.path.join(tempfile.mkdtemp(), "valeurs.xlsx")
    r = formules_xl.evaluer_classeur(xlsx, out)
    if r["non_supportees"]:
        xe = recalculer_par_excel(xlsx)
        if xe:
            return xe
        print(f"AVERTISSEMENT : {len(r['non_supportees'])} formule(s) hors périmètre de l'évaluateur, laissées vides : "
              + "; ".join(r["non_supportees"][:3]))
    return out


def recalculer_par_excel(xlsx):
    """Recalcule le classeur par Excel et l'enregistre à côté (valeurs des formules disponibles à la lecture)."""
    out = os.path.join(tempfile.mkdtemp(), "recalc.xlsx")
    ps = (f"$x=New-Object -ComObject Excel.Application;$x.Visible=$false;$x.DisplayAlerts=$false;"
          f"try{{$w=$x.Workbooks.Open('{os.path.abspath(xlsx)}');$x.CalculateFull();$w.SaveAs('{out}',51);$w.Close($false);'OK'}}"
          f"finally{{$x.Quit()}}")
    try:
        cp = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=900)
        return out if "OK" in cp.stdout and os.path.exists(out) else None
    except (OSError, subprocess.TimeoutExpired):
        return None


TITRES_TF = {
    "tf1": ("TF1 — DÉTERMINATION DU RÉSULTAT FISCAL", "TF1 — DETERMINACIÓN DEL RESULTADO FISCAL"),
    "reintegraciones": ("RÉINTÉGRATIONS — DÉTAIL PAR COMPTE", "REINTEGRACIONES — DETALLE POR CUENTA"),
    "tf2": ("TF2 — IMPÔT SUR LES SOCIÉTÉS ET CUOTA MÍNIMA FISCAL", "TF2 — IMPUESTO SOBRE SOCIEDADES Y CUOTA MÍNIMA FISCAL"),
    "tf3": ("TF3 — IVA : DÉCLARATION ANNUELLE", "TF3 — IVA: DECLARACIÓN ANUAL"),
    "tf4": ("TF4 — TRAITEMENTS ET SALAIRES, RÉGULARISATION DE L'IRPF", "TF4 — SUELDOS Y SALARIOS, REGULARIZACIÓN DEL IRPF"),
    "tf5": ("TF5 — PAIEMENTS À DES TIERS (comptes 62, 63 et 66)", "TF5 — PAGOS A TERCEROS (cuentas 62, 63 y 66)"),
}
# TF1 : le libellé de la section (« I. Résultat… ») partage la ligne des en-têtes « Perte / Bénéfice » : en-têtes posés
ENTETES_NOMMES = {"tf1": {"fr": {1: "Rubrique", 6: "Ligne", 7: "Perte", 8: "Bénéfice"},
                          "es": {1: "Concepto", 6: "Línea", 7: "Pérdida", 8: "Beneficio"}},
                  "tf2": {"fr": {1: "Rubrique", 5: "Ligne", 6: "Montant"}, "es": {1: "Concepto", 5: "Línea", 6: "Importe"}}}
ENTETES_TF["tf1"] = (8, 7)                                   # aucune ligne d'en-tête : la ligne 8 est une ligne de données


def est_commentaire(ws, r, c0, c1):
    return any(isinstance(ws.cell(r, c).value, str) and norm(ws.cell(r, c).value).startswith(("commentaire", "comentario"))
               for c in range(c0, min(c0 + 3, c1) + 1))


def est_donnee(ws, r, c0, c1):
    """Ligne de données : un montant, ou une liste de comptes / une REF dans les premières colonnes."""
    for c in range(c0, c1 + 1):
        v = ws.cell(r, c).value
        if num(v):
            return True
        if c <= c0 + 1 and isinstance(v, str) and re.match(r"^[A-Z]{2}(\s+\d|$)", v.strip()):
            return True
    return False


def extraire(ws, meta, t, lang="fr"):
    """Tableaux d'une feuille recalculée. Une feuille peut en porter PLUSIEURS, séparés par un bloc « Commentaire »
    (note 12 : écarts de conversion PUIS transferts de charges). Retourne [(titre, [(col, en-tête)], lignes)],
    lignes = [(style, [valeurs], [formats], n° de ligne)]. Le texte des commentaires n'est pas repris."""
    c0, c1, r1 = meta["c0"], meta["c1"], meta["r1"]
    h0, h1 = ENTETES_TF.get(t, (meta["h0"], meta["h1"]))
    fus = {}
    for rg in ws.merged_cells.ranges:
        v = ws.cell(rg.min_row, rg.min_col).value
        for r in range(rg.min_row, rg.max_row + 1):
            for c in range(rg.min_col, rg.max_col + 1):
                fus[(r, c)] = v
    titre = ""
    for r in range(1, h0):
        for c in range(c0, c1 + 1):
            v = ws.cell(r, c).value
            if isinstance(v, str) and len(v.strip()) > len(titre) and not re.match(r"^\d{2}/\d{2}/\d{4}$", v.strip()) \
                    and norm(v) not in ("sommaire", "indice") and not v.startswith("="):
                titre = v.strip()
    # segments : [début des en-têtes, fin des en-têtes, début des données, fin des données, titre]
    segments, r = [], h1 + 1
    courant = [h0, h1, h1 + 1, None, titre]
    while r <= r1:
        if est_commentaire(ws, r, c0, c1):
            courant[3] = r - 1
            segments.append(courant)
            # sauter le texte du commentaire jusqu'au titre du tableau suivant (ligne de texte suivie d'en-têtes)
            k = r + 1
            while k <= r1 and not est_donnee(ws, k, c0, c1):
                k += 1
            if k > r1:
                courant = None
                break
            textes = [x for x in range(r + 1, k) if any(isinstance(ws.cell(x, c).value, str) and ws.cell(x, c).value.strip()
                                                        for c in range(c0, c1 + 1))]
            sous_titre = ""
            if textes:                              # titre = premier texte en majuscules du bloc, en-têtes = les suivants
                cand = [x for x in textes if any(isinstance(ws.cell(x, c).value, str) and ws.cell(x, c).value.isupper()
                                                 and len(ws.cell(x, c).value) > 8 for c in range(c0, c1 + 1))]
                t_row = cand[-1] if cand else None
                if t_row:
                    sous_titre = next(ws.cell(t_row, c).value for c in range(c0, c1 + 1)
                                      if isinstance(ws.cell(t_row, c).value, str) and ws.cell(t_row, c).value.isupper())
                ent = [x for x in textes if t_row is None or x > t_row]
            else:
                ent = []
            courant = [ent[0] if ent else k, ent[-1] if ent else k - 1, k, None, sous_titre]
            r = k
            continue
        r += 1
    if courant:
        courant[3] = r1
        segments.append(courant)
    tables = []
    for e0, e1, d0, d1, ttl in segments:
        rows = range(d0, d1 + 1)
        cols = [c for c in range(c0, c1 + 1) if not ws.column_dimensions[ws.cell(1, c).column_letter].hidden
                and any(ws.cell(x, c).value not in (None, "") for x in rows)]
        nommes = ENTETES_NOMMES.get(t, {}).get(lang, {})
        entetes = []
        for c in cols:
            parts = []
            for x in range(e0, e1 + 1):
                v = fus.get((x, c), ws.cell(x, c).value)
                if isinstance(v, datetime.datetime):
                    v = v.strftime("%d/%m/%Y")
                if v not in (None, "") and str(v).strip() not in parts:
                    parts.append(str(v).strip())
            entetes.append((c, nommes.get(c) or " ".join(parts)))   # en-tête posé (TF1, TF2) prioritaire
        lignes = []
        for x in rows:
            vals = [ws.cell(x, c).value for c in cols]
            if all(v in (None, "") for v in vals):
                continue
            nums = [v for v in vals if num(v)]
            style = "total" if x in meta.get("totaux", []) else ("section" if not nums else "base")
            lignes.append((style, vals, [ws.cell(x, c).number_format for c in cols], x))
        tables.append((ttl, entetes, lignes))
    return tables


def utile(tables, texte=False):
    """Une note s'imprime si elle porte un montant non nul ; une note de TEXTE (note 2) si elle porte du texte."""
    if texte:
        return any(isinstance(v, str) and len(v.strip()) > 3 for _, _, ls in tables for _, vals, _, _ in ls for v in vals)
    return any(num(v) and abs(v) >= 0.5 for _, _, ls in tables for _, vals, _, _ in ls for v in vals)


def construire(gen, lang, xr, logo, sortie_pdf):
    """Construit le rapport (classeur temporaire) puis l'exporte en PDF ; retourne le mode d'export ou None."""
    import openpyxl
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.worksheet.page import PageMargins
    import def_ge

    L = T[lang]
    D = gen.D
    ex = gen.a.exercice
    I = D.get("identite") or {}
    nom, sigle = I.get("raison_sociale") or L["a_completer"].upper(), I.get("sigle") or ""
    src = openpyxl.load_workbook(xr, data_only=True)
    fill = lambda c: PatternFill("solid", fgColor=c)
    fin = Side(style="thin", color="8EA9DB")
    wb = Workbook()
    feuilles = []

    def mise_en_page(ws, titre, paysage=False, titres=None):
        ws.page_setup.paperSize = ws.PAPERSIZE_A4
        ws.page_setup.orientation = "landscape" if paysage else "portrait"
        ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.page_margins = PageMargins(left=0.45, right=0.45, top=0.6, bottom=0.6, header=0.25, footer=0.25)
        ws.print_options.horizontalCentered = True
        if titres:
            ws.print_title_rows = titres
        ws.oddFooter.left.text = L["pied"].format(s=sigle or nom, ex=ex)
        ws.oddFooter.center.text = f"{L['page']} &P / &N"
        ws.oddFooter.right.text = titre[:60]
        for part in (ws.oddFooter.left, ws.oddFooter.center, ws.oddFooter.right):
            part.size, part.color = 8, "595959"
        ws.sheet_view.showGridLines = False

    def bandeau(ws, titre, sous=""):
        ws.append([nom]); ws.cell(1, 1).font = Font(name="Calibri", size=11, bold=True, color=BLEU)
        ws.append([f"{L['nif']} : {I.get('nif') or L['a_completer']}   ·   " + L["entete_ex"].format(ex=ex)])
        ws.cell(2, 1).font = Font(name="Calibri", size=10, italic=True, color="595959")
        ws.append([titre]); ws.cell(3, 1).data_type = "s"; ws.cell(3, 1).font = Font(name="Calibri", size=14, bold=True, color=BLEU)
        ws.append([sous]); ws.cell(4, 1).font = Font(name="Calibri", size=9, italic=True, color="595959")
        ws.append([])

    def entetes_ligne(ws, textes, largeurs):
        ws.append(textes)
        r = ws.max_row
        for j in range(1, len(textes) + 1):
            c = ws.cell(r, j)
            if isinstance(c.value, str) and c.value.lstrip().startswith("="):
                c.data_type = "s"
            c.font, c.fill = Font(name="Calibri", size=9, bold=True, color="FFFFFF"), fill(BLEU)
            c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.row_dimensions[r].height = 30 if max(len(t or "") for t in textes) < 40 else 44
        for j, w in enumerate(largeurs, 1):
            ws.column_dimensions[ws.cell(1, j).column_letter].width = w
        return r

    def style(ws, r, n, kind, formats=None):
        for j in range(1, n + 1):
            c = ws.cell(r, j)
            if isinstance(c.value, str) and c.value.lstrip().startswith("="):
                c.data_type = "s"                           # libellé « = CAPACITE… » : texte, jamais une formule
            c.font = Font(name="Calibri", size=9, bold=kind in ("total", "section"))
            if kind == "section":
                c.fill = fill(BLEU_CLAIR)
            elif kind == "total":
                c.fill, c.border = fill(GRIS), Border(top=fin)
            else:
                c.border = Border(bottom=Side(style="hair", color="BFBFBF"))
            if num(c.value):
                f = (formats or [None] * n)[j - 1] or ""
                c.number_format = "0.0%" if "%" in f else NUM
                c.alignment = Alignment(horizontal="right")
            elif isinstance(c.value, str):
                c.alignment = Alignment(wrap_text=True, vertical="center")

    # ---------------- couverture
    ws = wb.active
    ws.title = "Couverture"
    feuilles.append(ws.title)
    ws.column_dimensions["A"].width, ws.column_dimensions["B"].width = 4, 92
    lignes = [("", None), (L["republique"], Font(name="Calibri", size=10, italic=True, color="595959")), ("", None), ("", None),
              (L["titre"], Font(name="Calibri", size=22, bold=True, color=BLEU)), (L["sous"], Font(name="Calibri", size=12, color=BLEU)),
              ("", None), (L["exercice"].format(ex=ex), Font(name="Calibri", size=14, bold=True)),
              (L["monnaie"], Font(name="Calibri", size=10, italic=True, color="595959")), ("", None), ("", None),
              (nom, Font(name="Calibri", size=18, bold=True)), (sigle, Font(name="Calibri", size=12, color="595959")), ("", None)]
    for t_, f in lignes:
        ws.append(["", t_])
        if f:
            ws.cell(ws.max_row, 2).font = f
    for k, lab in L["champs"][2:8]:
        ws.append(["", f"{lab} :  {I.get(k) or L['a_completer']}"])
        ws.cell(ws.max_row, 2).font = Font(name="Calibri", size=10, color="000000" if I.get(k) else "C00000")
    ws.append([]); ws.append(["", L["genere"].format(d=datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))])
    ws.cell(ws.max_row, 2).font = Font(name="Calibri", size=9, italic=True, color="595959")
    for r in range(1, ws.max_row + 1):
        ws.cell(r, 2).alignment = Alignment(horizontal="center", wrap_text=True)
    if logo and os.path.exists(logo):
        from openpyxl.drawing.image import Image
        from openpyxl.drawing.spreadsheet_drawing import AnchorMarker, OneCellAnchor
        from openpyxl.drawing.xdr import XDRPositiveSize2D
        from openpyxl.utils.units import pixels_to_EMU
        im = Image(logo)
        h = 110
        w = int(im.width * h / im.height)
        im.anchor = OneCellAnchor(_from=AnchorMarker(col=1, row=0, colOff=pixels_to_EMU(max((92 * 7 + 5 - w) // 2, 0)), rowOff=pixels_to_EMU(8)),
                                  ext=XDRPositiveSize2D(pixels_to_EMU(w), pixels_to_EMU(h)))
        ws.add_image(im)
        ws.row_dimensions[1].height = (h + 16) * 0.75
    mise_en_page(ws, "Couverture")

    # ---------------- sommaire (paginé au second passage)
    som = wb.create_sheet("Sommaire")
    feuilles.append(som.title)

    # ---------------- identification
    ws = wb.create_sheet("Identification")
    feuilles.append(ws.title)
    bandeau(ws, L["ident"])
    entetes_ligne(ws, [L["rub"], L["rens"]], [48, 70])
    for k, lab in L["champs"]:
        ws.append([lab, I.get(k) or L["a_completer"]])
        style(ws, ws.max_row, 2, "base")
        if not I.get(k):
            ws.cell(ws.max_row, 2).fill = fill(AMBRE)
    mise_en_page(ws, L["ident"])

    # ---------------- tableaux tirés du classeur recalculé
    noms_src = {norm(m.title): gen.noms[m.title] for m in gen.modele.worksheets}
    ordre = [m.title for m in gen.modele.worksheets]
    applic, sommaire = [], [("", L["ident"], "Identification")]
    compteur = {}

    def rendre_tableau(t, titre_src):
        wsrc = src[gen.noms[titre_src]]
        meta = gen.meta[wsrc.title]
        tables = extraire(wsrc, meta, t, lang)
        titre = tables[0][0] if tables else ""
        if t in TITRES_TF:
            titre = TITRES_TF[t][0 if lang == "fr" else 1]
        elif titre.rstrip().endswith(":"):                 # « BILAN ACTIF AU : » -> date de clôture
            titre = f"{titre.rstrip()} 31/12/{ex}"
        nom_f = re.sub(r"[\[\]\*\?/\\:]", "", wsrc.title)[:31]
        ws = wb.create_sheet(nom_f)
        feuilles.append(nom_f)
        bandeau(ws, titre or wsrc.title.upper())
        paysage, r_ent0 = False, None
        for i, (ttl, cols, lignes) in enumerate(tables):
            if t.startswith("note") and t != "note 2":
                # titre de section = texte en MAJUSCULES ; une ligne en minuscules sans montant est une ligne vide du modèle
                titre_sec = lambda x: any(isinstance(v, str) and v.strip().isupper() for v in x[1])
                lignes = [x for x in lignes if (x[0] == "section" and titre_sec(x)) or any(num(v) and abs(v) >= 0.5 for v in x[1])]
                garde = []                             # une section sans ligne chiffrée derrière elle ne s'imprime pas
                for k, x in enumerate(lignes):
                    if x[0] == "section" and (k + 1 >= len(lignes) or lignes[k + 1][0] == "section"):
                        continue
                    garde.append(x)
                lignes = garde
                if not lignes:
                    continue
            if i > 0:
                ws.append([])
                if ttl:
                    ws.append([ttl])
                    ws.cell(ws.max_row, 1).font = Font(name="Calibri", size=11, bold=True, color=BLEU)
                if not ttl and not any(h for _, h in cols):   # simple rappel sous le tableau (TF2 : IS à payer) : pas de bandeau vide
                    for kind, vals, fmts, _ in lignes:
                        ws.append(vals)
                        style(ws, ws.max_row, len(cols), "total", fmts)
                    continue
            larg = []
            for j, (c, h) in enumerate(cols):
                txt = [x[1][j] for x in lignes]
                if any(isinstance(v, str) and len(v) > 18 for v in txt):
                    larg.append(46)
                elif any(isinstance(v, str) for v in txt) and not any(num(v) for v in txt):
                    larg.append(16)
                else:
                    larg.append(17)
            if i == 0 or all((ws.column_dimensions[ws.cell(1, j + 1).column_letter].width or 0) < w for j, w in enumerate(larg)):
                pass
            r_ent = entetes_ligne(ws, [h for _, h in cols], [max(w, ws.column_dimensions[ws.cell(1, j + 1).column_letter].width or 0)
                                                               if i > 0 else w for j, w in enumerate(larg)])
            r_ent0 = r_ent0 or r_ent
            for kind, vals, fmts, _ in lignes:
                if t in ETATS and kind == "section":       # sous-lignes des états (« (1) dont… ») : discrètes, pas des titres
                    kind = "base"
                ws.append(vals)
                style(ws, ws.max_row, len(cols), kind, fmts)
                for j, v in enumerate(vals, 1):   # listes de comptes (« BI 411-4112… ») : discrètes
                    if isinstance(v, str) and re.match(r"^[A-Z]{2}\s+\d", v):
                        ws.cell(ws.max_row, j).font = Font(name="Calibri", size=7.5, color="7F7F7F")
            paysage = paysage or sum(larg) > 120
        mise_en_page(ws, titre or wsrc.title, paysage=paysage, titres=f"{r_ent0}:{r_ent0}" if r_ent0 and len(tables) == 1 else None)
        if t in ETATS or ws.max_row <= 70:                 # un état (bilan, CR, TFT) ou une note courte : UNE page
            ws.page_setup.fitToHeight = 1
        return nom_f, titre

    for grp, lab in ((ETATS, L["etats"]), (None, L["notes"]), (FISCAUX, L["fiscal"])):
        for titre_src in ordre:
            t = norm(titre_src)
            if t.startswith("bg ") or t in ECARTES and ECARTES[t] is None:
                continue
            if grp is ETATS and t not in ETATS or grp is FISCAUX and t not in FISCAUX:
                continue
            if grp is None and not t.startswith("note"):
                continue
            nnote = titre_src.split(" ", 1)[1] if t.startswith("note") else titre_src
            if t in ECARTES:
                applic.append((nnote, gen.noms[titre_src], L["non_reprise"] + " — " + L["motifs"][ECARTES[t]]))
                continue
            if t in EXTRA:
                applic.append((nnote, gen.noms[titre_src], L["entite"]))
                continue
            wsrc = src[gen.noms[titre_src]]
            tables_src = extraire(wsrc, gen.meta[wsrc.title], t, lang)
            if grp is None and not utile(tables_src, texte=(t == "note 2")):
                applic.append((nnote, gen.noms[titre_src], L["neant"]))
                continue
            nom_f, titre = rendre_tableau(t, titre_src)
            sommaire.append((lab, titre or nom_f, nom_f))
            if grp is None:
                applic.append((nnote, titre or nom_f, L["presentee"] + " — {p:" + nom_f + "}"))
        if grp is None:
            ws = wb.create_sheet("Applicabilite")
            feuilles.append(ws.title)
            bandeau(ws, L["applic"])
            r_ent = entetes_ligne(ws, [L["note"], L["intitule"], L["statut"]], [10, 60, 52])
            ws._applic = (r_ent, list(applic))
            sommaire.append((lab, L["applic"], "Applicabilite"))
            mise_en_page(ws, L["applic"], titres=f"{r_ent}:{r_ent}")

    def ecrire_sommaire(pages):
        idx = wb.sheetnames.index("Sommaire")             # feuille recréée à chaque passage (jamais de reliquat)
        del wb["Sommaire"]
        som = wb.create_sheet("Sommaire", idx)
        bandeau(som, L["sommaire"])
        entetes_ligne(som, [L["section"], L["intitule"], L["page"]], [30, 72, 10])
        for grp, titre, f in sommaire:
            som.append([grp, titre, pages.get(f, "")])
            style(som, som.max_row, 3, "base")
        mise_en_page(som, L["sommaire"])
        wa = wb["Applicabilite"]
        r_ent, lst = wa._applic
        for i, (n, titre, statut) in enumerate(lst):
            m = re.search(r"\{p:(.+)\}", statut)
            if m:
                statut = statut.replace(m.group(0), f"{L['page'].lower()} {pages.get(m.group(1), '')}")
            r = r_ent + 1 + i
            for j, v in enumerate((n, titre, statut), 1):
                wa.cell(r, j).value = v
            style(wa, r, 3, "base")
            if L["entite"] in statut:
                wa.cell(r, 3).fill = fill(AMBRE)

    tmp = os.path.join(tempfile.mkdtemp(), "rapport.xlsx")
    ecrire_sommaire({})
    wb.save(tmp)
    mode = def_ge.exporter_pdf(tmp, sortie_pdf, feuilles)
    if not mode:
        return None
    try:                                                   # second passage : numéros de page réels au sommaire
        try:
            import pymupdf as fitz            # nom actuel de PyMuPDF
        except ImportError:
            import fitz                       # ancien nom (versions < 1.24.3)
        doc = fitz.open(sortie_pdf)
        pages = {}
        for i, p in enumerate(doc):
            bas = unicodedata.normalize("NFKC", p.get_text("text", clip=fitz.Rect(0, p.rect.height - 40, p.rect.width, p.rect.height)))
            for f in feuilles:
                titre_pied = next((ws_.oddFooter.right.text for ws_ in wb.worksheets if ws_.title == f), f)
                if f not in pages and titre_pied and unicodedata.normalize("NFKC", titre_pied)[:25] in bas:
                    pages[f] = i + 1
        doc.close()
        ecrire_sommaire(pages)
        wb.save(tmp)
        mode = def_ge.exporter_pdf(tmp, sortie_pdf, feuilles) or mode
    except Exception:
        pass
    return mode
