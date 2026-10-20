# -*- coding: utf-8 -*-
"""Garde du MODÈLE SYSCOHADA SYSTÈME NORMAL (skills/dsf-syscohada/scripts/def_sn.py), sans donnée client.

Balance synthétique (test_def_modele.py) + subvention d'investissement (note 15A, propre au SN) :
  - états : bilan ÉQUILIBRÉ au total du moteur (actif = passif = BZ), résultat du CR = XI, formule officielle du total
    général corrigée si elle oublie l'écart de conversion ;
  - notes : chaque note retombe sur son poste ; la 15A (absente du format GE) est produite ; 3A = brut du bilan ;
  - liasse ADAPTÉE : moins de 74 feuilles, annexes camerounaises retirées, tableaux fiscaux GE ajoutés, chaque note
    omise dite dans la grille ; en-têtes : exercice et durée ; page de garde : mentions de la GE ;
  - toutes les formules du formulaire évaluées ; dossier de travail : SN par défaut, format GE au choix.
Lancer : python tests/test_sn.py     (code 0 = conforme)
"""
import argparse
import contextlib
import csv
import io
import json
import os
import sys
import tempfile
import warnings

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "dsf-syscohada", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import openpyxl  # noqa: E402
import def_modele as dm  # noqa: E402
import def_sn  # noqa: E402
import espace_def as ed  # noqa: E402
import formules_xl  # noqa: E402
import test_def_modele as tdm  # noqa: E402

GAB = os.path.join(ROOT, "skills", "dsf-syscohada", "templates", "def_ge_gabarit.xlsx")
ok = []


def check(nom, cond, detail=""):
    ok.append(bool(cond))
    print(f"  {'OK   ' if cond else 'ÉCHEC'} {nom}" + ("" if cond else f"  — {str(detail)[:300]}"))


def balance(path):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Compte", "Intitulé", "Ouverture D", "Ouverture C", "Mvt D", "Mvt C", "Solde D", "Solde C"])
        # + subvention d'investissement (note 15A, propre au SN) et écart de conversion PASSIF (479) : la formule
        # officielle du total général l'oublie — la correction du plugin doit se voir dans l'équilibre du bilan
        lignes = list(tdm.B.items()) + [("14110000", (-300_000, 0, 0)), ("47900000", (-5_000, 0, 0))]
        for a, (o, md, mk) in lignes:
            o = o + 305_000 if a == "52110000" else o            # subvention encaissée, contrepartie de l'écart
            s = o + md - mk
            lib = {"14110000": "SUBVENTION D'EQUIPEMENT ETAT", "47900000": "ECARTS DE CONVERSION PASSIF"}.get(a) or tdm.LIB[a]
            w.writerow([a, lib, max(o, 0), max(-o, 0), md, mk, max(s, 0), max(-s, 0)])


def cellule_totale(ws, texte, col):
    for r in range(1, ws.max_row + 1):
        for c in (1, 2, 9):
            if def_sn.plat(ws.cell(r, c).value).startswith(texte):
                return ws.cell(r, col).value
    return None


def main():
    d = tempfile.mkdtemp()
    bal = os.path.join(d, "balance.csv")
    balance(bal)
    a = argparse.Namespace(modele=GAB, balance=bal, grand_livre=None, exercice=2025, profil=None, decisions=None,
                           colonne_precedente="N", logo=None, langues="fr", pdf=False, pdf_excel=False, pro=False,
                           sortie=os.path.join(d, "DEF"), gabarit=True, structure=GAB[:-5] + ".json", sn=True)
    with contextlib.redirect_stdout(io.StringIO()):
        out = dm.produire(a)
    g = out["gen"]
    sn = g.liasse_sn
    ev = openpyxl.load_workbook(sn["evalue"], data_only=True)
    noms = [w.title for w in ev.worksheets]
    codes = {def_sn.code(n) for n in noms}
    print("== États")
    bp = next(w for w in ev.worksheets if def_sn.code(w.title) == "bilan paysage")
    actif, passif = cellule_totale(bp, "total general", 6), cellule_totale(bp, "total general", 11)
    bz = g.D["pN"].get("BZ")
    check("bilan ÉQUILIBRÉ au total du moteur (actif = passif = BZ)",
          dm.num(actif) and dm.num(passif) and abs(actif - bz) < 1 and abs(passif - bz) < 1, (actif, passif, bz))
    brut_bilan = cellule_totale(bp, "total general", 4)
    brut_moteur = sum(v.get("brut", 0) for r, v in g.D["agg"]["par_ref"].items()
                      if g.D["postes"].get(r, {}).get("etat") == "actif" and not g.D["postes"].get(r, {}).get("total"))
    check("bilan : total BRUT = brut du moteur (la colonne brut est écrite, pas seulement le net)",
          dm.num(brut_bilan) and abs(brut_bilan - brut_moteur) < 1, (brut_bilan, brut_moteur))
    dv = g.D["pN"].get("DV") or g.D["pN"].get("DY")
    check("écart de conversion passif présent et compté (formule du total général corrigée)",
          dm.num(dv) and abs(dv) >= 1 and any("CORRIGÉE" in c[0] for c in sn["controles"]), dv)
    cr = next(w for w in ev.worksheets if def_sn.code(w.title) == "compte de resultat")
    xi = cellule_totale(cr, "resultat net", 5)
    check("résultat du compte de résultat = résultat du moteur (XI)", dm.num(xi) and abs(xi - g.D["pN"]["XI"]) < 1,
          (xi, g.D["pN"].get("XI")))
    print("== Notes")
    ko = [c for c in sn["controles"] if not c[1]]
    check("chaque note retombe sur son poste ; aucun contrôle en écart", not ko, ko[:3])
    check("note 15A (subventions, absente du format GE) produite", "note 15a" in codes)
    n15 = next((w for w in ev.worksheets if def_sn.code(w.title) == "note 15a"), None)
    etat = next((n15.cell(r, 3).value for r in range(8, 20) if def_sn.plat(n15.cell(r, 1).value) == "etat"), None) if n15 else None
    check("15A : subvention de l'État (1411) sur sa ligne", dm.num(etat) and abs(etat - 300_000) < 1, etat)
    n3a = next(w for w in ev.worksheets if def_sn.code(w.title) == "note 3a")
    t3a = cellule_totale(n3a, "total general", 10)
    brut = sum(g.D["agg"]["par_ref"].get(r, {}).get("brut", 0) for r in ("AD", "AI", "AP", "AQ"))
    check("note 3A : total clôture = immobilisations brutes du bilan", dm.num(t3a) and abs(t3a - brut) < 1, (t3a, brut))
    print("== Liasse adaptée aux données")
    check("moins de feuilles que le formulaire complet (74)", len(noms) < 74, len(noms))
    check("annexes fiscales camerounaises retirées (CF1, CF2, C1/C2)",
          not any(def_sn.CAMEROUN.match(def_sn.plat(n)) for n in noms), [n for n in noms if def_sn.CAMEROUN.match(def_sn.plat(n))])
    check("tableaux fiscaux GE ajoutés (TF1 à TF5, réintégrations) et balance générale",
          {"tf1", "tf2", "tf3", "tf4", "tf5"} <= codes and any(c.startswith("reintegra") for c in codes)
          and any(c.startswith("balance genera") for c in codes), sorted(codes)[-8:])
    gr = next(w for w in ev.worksheets if def_sn.code(w.title).startswith("grille"))
    marques = [c.value for row in gr.iter_rows() for c in row if isinstance(c.value, str)
               and c.value.startswith(("néant", "non applicable", "aucune information", "annexe fiscale"))]
    omises_notes = [t for t, m in sn["omises"] if not m.startswith("annexe fiscale")]
    check("chaque note omise est dite dans la grille d'analyse des notes", marques and len(omises_notes) > 0, len(marques))
    brut_wb = openpyxl.load_workbook(sn["xlsx"])
    pg = next(w for w in brut_wb.worksheets if def_sn.code(w.title) == "page de garde")
    texte = " ".join(str(c.value) for row in pg.iter_rows() for c in row if c.value)
    check("page de garde : mentions de la Guinée équatoriale, plus aucune du Cameroun",
          "GUINÉE ÉQUATORIALE" in texte and "CAMEROUN" not in texte.upper(), texte[:120])
    entete = str(bp.cell(4, 1).value) + str(bp.cell(5, 1).value)
    check("en-têtes : exercice et durée écrits", "31-12-2025" in entete and "Durée (en mois) : 12" in entete, entete)
    check("toutes les formules du formulaire évaluées par le moteur",
          any(c[0].startswith("Formules") and c[1] for c in sn["controles"]))
    print("== Dossier de travail : SYSCOHADA par défaut, format GE au choix")
    e = ed.init(tempfile.mkdtemp(), "ENTITE SN SA", 2025)
    balance(os.path.join(e, "01_sources", "balance.csv"))
    with contextlib.redirect_stdout(io.StringIO()):
        r = ed.generer(e, pdf=False)
    check("par défaut : liasse SYSCOHADA (FR) livrée, classeur FR au format GE retiré",
          any("SYSCOHADA" in p for p in r["livrables"]) and not any(p.endswith("v1_FR_projet.xlsx") for p in r["livrables"]),
          r["livrables"])
    ed.repondre(e, "identite.raison_sociale", "ENTITE SN SA")
    ed.repondre(e, "identite.nif", "NIF-SN-001")
    with contextlib.redirect_stdout(io.StringIO()):
        r1 = ed.generer(e, pdf=False)
    xs = next(os.path.join(e, p) for p in r1["livrables"] if "SYSCOHADA" in p)
    wsn = openpyxl.load_workbook(xs)
    tete = " ".join(str(wsn[n].cell(k, 1).value) for n in wsn.sheetnames[9:12] for k in (4, 5))
    pgs = next(w for w in wsn.worksheets if def_sn.code(w.title) == "page de garde")
    txt = " ".join(str(c.value) for row in pgs.iter_rows() for c in row if c.value)
    check("identité saisie réinjectée : en-têtes et page de garde de la liasse SYSCOHADA",
          "ENTITE SN SA" in tete and "NIF-SN-001" in tete and "ENTITE SN SA" in txt, tete[:160])
    ed.repondre(e, "interp.modele_def", "ge")
    with contextlib.redirect_stdout(io.StringIO()):
        r2 = ed.generer(e, pdf=False)
    check("choix « format GE » : classeurs FR / ES au format GE, pas de SYSCOHADA",
          not any("SYSCOHADA" in p for p in r2["livrables"]) and any(p.endswith("v3_FR_projet.xlsx") for p in r2["livrables"]),
          r2["livrables"])
    print(f"\n{sum(ok)}/{len(ok)} contrôles conformes")
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
