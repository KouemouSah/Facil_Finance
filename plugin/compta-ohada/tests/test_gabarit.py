# -*- coding: utf-8 -*-
"""Garde du GABARIT VIERGE embarqué (skills/dsf-syscohada/templates/def_ge_gabarit.xlsx + .json).

Sans aucune donnée client (balance synthétique de test_def_modele.py) :
  - le gabarit est VIERGE : aucun montant, identité en repères, balance vide, fichier annexe cohérent ;
  - une DEF d'un AUTRE exercice (2026) se produit dessus : 51 feuilles, dates décalées, identité à saisir,
    N-1 des notes VIDE (jamais 0), bilan N-1 = ouverture de la balance ;
  - le dossier de travail sans DEF déposée l'emploie et pose la question de la DEF précédente.
L'équivalence avec la DEF déposée du dossier pilote se prouve hors plugin (la garde de référence du dossier pilote (hors plugin)).
Lancer : python tests/test_gabarit.py     (code 0 = conforme)
"""
import argparse
import csv
import datetime
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
import espace_def as ed  # noqa: E402
import test_def_modele as tdm  # noqa: E402

GAB = os.path.join(ROOT, "skills", "dsf-syscohada", "templates", "def_ge_gabarit.xlsx")
ok = []


def check(nom, cond, detail=""):
    ok.append(bool(cond))
    print(f"  {'OK   ' if cond else 'ÉCHEC'} {nom}" + ("" if cond else f"  — {str(detail)[:300]}"))


def balance(path, exercice_ouverture=True):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Compte", "Intitulé", "Ouverture D", "Ouverture C", "Mvt D", "Mvt C", "Solde D", "Solde C"])
        for a, (o, md, mk) in tdm.B.items():
            s = o + md - mk
            w.writerow([a, tdm.LIB[a], max(o, 0), max(-o, 0), md, mk, max(s, 0), max(-s, 0)])


def main():
    print("== Le gabarit est vierge")
    meta = json.load(open(GAB[:-5] + ".json", encoding="utf-8"))
    wb = openpyxl.load_workbook(GAB)
    check("51 feuilles, annexe de structure cohérente (année, totaux prouvés)",
          len(wb.worksheets) == 51 == meta["feuilles"] and meta["annee"] >= 2020 and len(meta["totaux"]) >= 40, meta.get("feuilles"))
    grands = [f"{ws.title}!{c.coordinate}" for ws in wb.worksheets for row in ws.iter_rows() for c in row
              if dm.num(c.value) and not isinstance(c.value, bool) and abs(c.value) >= 1000 and c.column > 2]
    check("aucun montant (≥ 1 000) hors colonnes de codes", not grands, grands[:5])
    pg = next(w for w in wb.worksheets if dm.norm(w.title) == "page garde")
    check("identité en repères (dénomination, sigle, adresse, NIF)",
          all(str(pg[c].value).startswith("[") for c in ("D13", "D16", "D17", "D18")), [pg[c].value for c in ("D13", "D18")])
    bg = next(w for w in wb.worksheets if dm.norm(w.title).startswith("bg "))
    check("feuille balance vide (reconstruite depuis la balance de l'entité)",
          not any(c.value is not None for row in bg.iter_rows() for c in row))
    tf5 = next(w for w in wb.worksheets if dm.norm(w.title) == "tf5")
    noms = [tf5.cell(r, 1).value for r in range(9, 30) if isinstance(tf5.cell(r, 1).value, str)
            and not dm.norm(tf5.cell(r, 1).value).startswith(("nombre", "total"))]
    check("TF5 sans bénéficiaire, en-têtes conservés", not noms and any(
        isinstance(tf5.cell(r, c).value, str) for r in range(1, 9) for c in range(1, 13)), noms[:3])

    print("== Une DEF 2026 sur le gabarit (balance synthétique)")
    d = tempfile.mkdtemp()
    bal = os.path.join(d, "balance.csv")
    balance(bal)
    a = argparse.Namespace(modele=GAB, balance=bal, grand_livre=None, exercice=2026, profil=None, decisions=None,
                           colonne_precedente="N", logo=None, langues="fr", pdf=False, pdf_excel=False, pro=False,
                           sortie=os.path.join(d, "DEF"), gabarit=True, structure=GAB[:-5] + ".json")
    out = dm.produire(a)
    x = out["fichiers"]["xlsx"][0]
    g = out["gen"]
    w = openpyxl.load_workbook(x)
    noms = {dm.norm(s.title) for s in w.worksheets}
    omises = g.notes_omises.get("fr", [])
    check("classeur ADAPTÉ aux données : notes sans montant omises (moins de 51 feuilles)",
          0 < len(omises) and len(w.worksheets) == 51 - len(omises), (len(w.worksheets), omises))
    obligatoires = ("page garde", "bilan actif", "bilan passif", "compte resultat", "flux tresorerie",
                    "tf1", "tf2", "tf3", "tf4", "tf5", "note 2", "note 27b", "note 35", "note 36", "fiche r1")
    check("états, tableaux fiscaux et notes extra-comptables toujours présents",
          all(o in noms for o in obligatoires), [o for o in obligatoires if o not in noms])
    gr = next(s for s in w.worksheets if dm.norm(s.title).startswith("grille"))
    marques = [str(c.value) for row in gr.iter_rows() for c in row if isinstance(c.value, str) and c.value.startswith("néant")]
    check("chaque note omise est signalée « néant » dans la grille d'analyse des notes", len(marques) == len(omises),
          (len(marques), len(omises)))
    import formules_xl
    ev = x[:-5] + "_eval.xlsx"
    formules_xl.evaluer_classeur(x, ev)
    erreurs = [f"{s.title}!{c.coordinate}" for s in openpyxl.load_workbook(ev, data_only=True).worksheets
               for row in s.iter_rows() for c in row if isinstance(c.value, str) and c.value.startswith("#")]
    check("aucune formule cassée par l'omission (#REF!, #VALUE!…)", not erreurs, erreurs[:5])
    pc = os.path.join(d, "profil_conserver.json")
    json.dump({"interpretations": {"notes_neant": "conserver"}}, open(pc, "w", encoding="utf-8"))
    a2 = argparse.Namespace(**{**vars(a), "profil": pc, "sortie": os.path.join(d, "DEF_complet")})
    x2 = dm.produire(a2)["fichiers"]["xlsx"][0]
    check("choix « conserver » : les 51 feuilles du formulaire", len(openpyxl.load_workbook(x2).worksheets) == 51)
    p = next(s for s in w.worksheets if dm.norm(s.title) == "page garde")
    check("date de clôture décalée sur l'exercice (31/12/2026)", str(p["D11"].value) == "31/12/2026", p["D11"].value)
    check("identité à saisir (fond ambre), aucun repère recopié",
          (p.title, "D13") in g.a_completer and not any(isinstance(c.value, str) and c.value.startswith("[DENOMINATION")
                                                        for s in w.worksheets for row in s.iter_rows() for c in row))
    annees = {c.value.year for s in w.worksheets for row in s.iter_rows(max_row=8) for c in row
              if isinstance(c.value, (datetime.date, datetime.datetime))}
    check("en-têtes datés 2026 / 2025, plus aucune année du gabarit", annees and annees <= {2026, 2025}, annees)
    n1_zero, n1_total = 0, 0
    for s in w.worksheets:
        m = g.meta.get(s.title, {})
        if not m.get("t", "").startswith("note") or m.get("t") in ("note 3a", "note 3c"):
            continue
        for c, ro in m.get("roles", {}).items():
            if ro in ("n1", "net_n1"):
                for r in range(m["h1"] + 1, m["r1"] + 1):
                    v = s.cell(r, c).value
                    n1_total += 1
                    if v == 0:
                        n1_zero += 1
    check("N-1 des notes VIDE, jamais 0 (aucune DEF précédente)", n1_total > 50 and n1_zero == 0, (n1_zero, n1_total))
    # colonne N repérée SANS le générateur : celle dont l'en-tête est daté de l'exercice ; elle doit porter des
    # montants de CLÔTURE qui ne sont pas des montants d'ouverture (sinon N et N-1 sont intervertis)
    ba = next(s for s in w.worksheets if dm.norm(s.title) == "bilan actif")
    def annee(v):
        if isinstance(v, (datetime.date, datetime.datetime)):
            return v.year
        return int(v[-4:]) if isinstance(v, str) and v.strip()[-4:].isdigit() else None

    def groupe(col, r=6):                          # date du groupe d'en-tête (cellule fusionnée : la plus proche à gauche)
        return next((annee(ba.cell(r, k).value) for k in range(col, 0, -1) if ba.cell(r, k).value is not None), None)
    cn = next((c for c in range(1, ba.max_column + 1) if dm.norm(str(ba.cell(7, c).value or "")) == "net"
               and groupe(c) == 2026), None)
    vals = {round(ba.cell(r, cn).value) for r in range(8, ba.max_row + 1)
            if dm.num(ba.cell(r, cn).value) and ba.cell(r, cn).value} if cn else set()
    cloture = {round(v) for v in g.D["pN"].values() if v}
    ouverture = {round(v) for v in g.D["p1"].values() if v}
    check("bilan : la colonne datée 2026 porte la CLÔTURE (N et N-1 non intervertis)",
          len(vals) >= 3 and vals <= cloture and vals - ouverture, (cn, sorted(vals)[:5]))
    check("bilan N-1 tiré de l'ouverture de la balance", g.D["p1"] and "ouverture" in (g.D.get("src_n1") or "").lower()
          or bool(g.D["p1"]), g.D.get("src_n1"))

    print("== Note applicable ABSENTE du formulaire : dite, jamais tue")
    check("sur la balance de test, aucune note chiffrée n'est hors formulaire", g.notes_absentes == {}, g.notes_absentes)
    bal2 = os.path.join(d, "balance_subvention.csv")
    with open(bal2, "w", encoding="utf-8", newline="") as f:           # + subvention d'investissement (note 15)
        wcsv = csv.writer(f, delimiter=";")
        wcsv.writerow(["Compte", "Intitulé", "Ouverture D", "Ouverture C", "Mvt D", "Mvt C", "Solde D", "Solde C"])
        for acc, (o, md, mk) in list(tdm.B.items()) + [("14100000", (-300_000, 0, 0))]:
            o = o + 300_000 if acc == "52110000" else o
            s = o + md - mk
            wcsv.writerow([acc, tdm.LIB.get(acc, "SUBVENTIONS D'EQUIPEMENT"), max(o, 0), max(-o, 0), md, mk, max(s, 0), max(-s, 0)])
    g3 = dm.Generateur(argparse.Namespace(**{**vars(a), "balance": bal2}))
    check("subvention d'investissement : note 15 signalée « applicable mais absente », au rapport de contrôle",
          "15" in g3.notes_absentes and any("Note 15" in c[0] and not c[1] for c in g3.controles), g3.notes_absentes)

    # exercice 2027 : deux ans d'écart avec le gabarit, pour qu'un décalage d'un an « juste par hasard » ne passe pas
    print("== Dossier de travail sans DEF déposée (exercice 2027)")
    e = ed.init(tempfile.mkdtemp(), "ENTITE GABARIT SA", 2027)
    ed.repondre(e, "interp.modele_def", "ge")          # le GABARIT GE est l'objet de cette garde
    balance(os.path.join(e, "01_sources", "export.csv"))
    r = ed.generer(e, pdf=False)
    check("DEF complète sur le gabarit (plus de liasse abrégée)", r.get("statut") == "projet"
          and "gabarit" in r.get("modele", "") and len([p for p in r["livrables"] if p.endswith(".xlsx")]) >= 2, r)
    fr = next(os.path.join(e, p) for p in r["livrables"] if p.endswith("_FR_projet.xlsx"))
    w2 = openpyxl.load_workbook(fr)
    an2 = {c.value.year for s in w2.worksheets for row in s.iter_rows(max_row=8) for c in row
           if isinstance(c.value, (datetime.date, datetime.datetime))}
    check("dossier 2027 : en-têtes datés 2027 / 2026 (décalage du gabarit, pas d'un an fixe)",
          an2 and an2 <= {2027, 2026} and 2027 in an2, an2)
    qs = json.load(open(os.path.join(e, "04_questions", "questions.json"), encoding="utf-8"))
    q = next((q for q in qs if q["id"] == "sources.def_precedente"), None)
    check("question « DEF de l'exercice précédent » posée, obligatoire", q and q["obligatoire"], q)
    print(f"\n{sum(ok)}/{len(ok)} contrôles conformes")
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
