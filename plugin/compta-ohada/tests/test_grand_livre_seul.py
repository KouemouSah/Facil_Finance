# -*- coding: utf-8 -*-
"""Garde de l'entrée « GRAND LIVRE SEUL » : la balance est reconstituée depuis le grand livre, puis sert au calcul.

Grand livre fictif (balance de test_def_modele.py), qui porte les pièges rencontrés sur un dossier réel :
  - reports à nouveau en lignes d'en-tête ET une écriture d'à-nouveau DATÉE (journal AN) -> ouvertures ;
  - un libellé « Report frais de mission » sur une écriture ordinaire -> mouvement, PAS une ouverture ;
  - un compte CENTRALISÉ (seulement des « Total du … au … ») -> ses totaux sont ses mouvements ;
  - une écriture de CLÔTURE (6-7 contre 13) -> exclue, sinon charges et produits seraient nuls.
Attendu : la balance reconstituée est IDENTIQUE, compte par compte, à la balance d'origine ; le dossier de travail
génère une DEF sur le grand livre seul ; un grand livre déséquilibré suspend le calcul (question bloquante).
Lancer : python tests/test_grand_livre_seul.py     (code 0 = conforme)
"""
import datetime
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
import espace_def as ed  # noqa: E402
import grand_livre  # noqa: E402
import test_def_modele as tdm  # noqa: E402

ok = []
D = datetime.datetime


def check(nom, cond, detail=""):
    ok.append(bool(cond))
    print(f"  {'OK   ' if cond else 'ÉCHEC'} {nom}" + ("" if cond else f"  — {str(detail)[:300]}"))


CLOTURE = {"70510000": (1_000_000, 0), "60400000": (0, 450_000), "68130000": (0, 70_000), "13100000": (0, 480_000)}


def ecrire_gl(path, desequilibre=False):
    """Grand livre « par compte » : chaque ligne d'une écriture figure dans la section de SON compte."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["GRAND LIVRE GENERAL - EXERCICE 2025"])
    ws.append(["Date", "Journal", "Pièce", "Libellé", "Débit", "Crédit"])
    n = 0
    for a, (o, md, mk) in list(tdm.B.items()) + [("13100000", (0, 0, 0))]:
        ws.append([a, tdm.LIB.get(a, "RESULTAT NET")])
        if a in CLOTURE:                                       # écriture de CLÔTURE : 6-7 contre 13, même pièce
            dd, cc = CLOTURE[a]
            ws.append([D(2025, 12, 31), "CLO", "CLO-001", "Clôture des comptes de gestion", dd, cc])
        if a == "12100000":                                    # à-nouveau passé en écriture DATÉE (journal AN)
            # libellé NEUTRE : seul le code journal « AN » dit que c'est une ouverture
            ws.append([D(2025, 1, 1), "AN", "AN-001", "Reprise des soldes 2024", o, 0])
        elif o:
            ws.append(["Report à nouveau", max(o, 0), max(-o, 0)])
        if a == "40110000":                                    # compte CENTRALISÉ : seulement des totaux de période
            ws.append(["Total du", D(2025, 1, 1), "au", D(2025, 6, 30), 150_000, 200_000, 0, 150_000])
            ws.append(["Total du", D(2025, 7, 1), "au", D(2025, 12, 31), 250_000, 250_000, 0, 150_000])
            continue
        if a == "52110000":                                    # « report » dans un libellé ordinaire : un mouvement
            ws.append([D(2025, 3, 2), "BQ", f"P{n}", "Report frais de mission", 100_000, 0])
            md -= 100_000
            n += 1
        if md:
            ws.append([D(2025, 6, 30), "OD", f"P{n}", f"Mouvement {tdm.LIB[a]}", md, 0])
            n += 1
        if mk:
            ws.append([D(2025, 6, 30), "OD", f"P{n}", f"Mouvement {tdm.LIB[a]}", 0, mk])
            n += 1
        ws.append([f"Total compte {a}", None, None, None, None, None])
    if desequilibre:                                           # une écriture sans contrepartie : grand livre incomplet
        ws.append([D(2025, 12, 30), "OD", "ORPH-1", "Écriture orpheline", 5, 0])
    wb.save(path)


def main():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "grand_livre.xlsx")
    ecrire_gl(p)
    print("== Balance reconstituée depuis le grand livre")
    gl = grand_livre.lire(p)
    lignes, ctrl = grand_livre.balance_reconstituee(gl)
    rec = {a: (o, md, mc) for a, _, o, md, mc in lignes}
    check("balance équilibrée (ouvertures et mouvements)", ctrl["equilibree"], ctrl)
    ecarts = {a: (rec.get(a), v) for a, v in tdm.B.items() if tuple(round(x) for x in rec.get(a, (0, 0, 0))) != v}
    check("IDENTIQUE à la balance d'origine, compte par compte (ouverture, débit, crédit)", not ecarts, ecarts)
    check("à-nouveau daté (journal AN) compté en OUVERTURE", rec.get("12100000", (0,))[0] == 200_000, rec.get("12100000"))
    check("« Report frais de mission » compté en MOUVEMENT", rec.get("52110000", (0, 0))[1] == 1_000_000, rec.get("52110000"))
    check("compte centralisé repris par ses totaux de période", rec.get("40110000", (0, 0, 0))[1:] == (400_000, 450_000)
          and gl["detection"].get("comptes_centralises", {}).get("40110000") == 2, (rec.get("40110000"), gl["detection"].get("comptes_centralises")))
    check("écriture de clôture exclue (produits et charges non soldés)", "CLO-001" in ctrl["pieces_de_cloture_exclues"]
          and rec.get("70510000", (0, 0, 0))[2] == 1_000_000, (ctrl["pieces_de_cloture_exclues"], rec.get("70510000")))
    check("intitulés des comptes repris des en-têtes", all(x[1] for x in lignes if x[0] in tdm.LIB), [x[:2] for x in lignes][:4])

    print("== Dossier de travail : grand livre SEUL")
    e = ed.init(tempfile.mkdtemp(), "ENTITE GL SA", 2025)
    ecrire_gl(os.path.join(e, "01_sources", "gl_2025.xlsx"))
    inv = {x["fichier"]: x["role"] for x in ed.inventaire(e, "ENTITE GL SA")}
    check("fichier reconnu comme grand livre (par son contenu)", inv.get("gl_2025.xlsx") == "grand_livre", inv)
    r = ed.generer(e, pdf=False)
    check("DEF générée sur le grand livre seul (balance reconstituée, contrôlée)", r.get("statut") == "projet"
          and r["sources"]["balance"] == "reconstituée depuis le grand livre" and r["balance_reconstituee"]["equilibree"], r)
    print("== Grand livre déséquilibré : calcul suspendu")
    f = ed.init(tempfile.mkdtemp(), "ENTITE GL KO", 2025)
    ecrire_gl(os.path.join(f, "01_sources", "gl_2025.xlsx"), desequilibre=True)
    r2 = ed.generer(f, pdf=False)
    check("question bloquante « grand livre déséquilibré », rien de calculé", r2.get("statut") == "bloque_avant_calcul"
          and any(q["id"] == "sources.grand_livre" for q in r2.get("questions", [])), r2)
    print("== Ni balance ni grand livre")
    g = ed.init(tempfile.mkdtemp(), "ENTITE VIDE", 2025)
    r3 = ed.generer(g, pdf=False)
    check("une seule question : déposer la balance OU le grand livre", r3.get("statut") == "bloque_avant_calcul"
          and [q["id"] for q in r3["questions"]] == ["sources.balance"] and "grand livre" in r3["questions"][0]["question"], r3)
    print(f"\n{sum(ok)}/{len(ok)} contrôles conformes")
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
