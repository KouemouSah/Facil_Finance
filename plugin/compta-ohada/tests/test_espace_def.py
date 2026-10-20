# -*- coding: utf-8 -*-
"""Garde du DOSSIER DE TRAVAIL (skills/dsf-syscohada/scripts/espace_def.py) : automatique d'abord, questions ensuite.

Données : la balance et le modèle construits à la main de test_def_modele.py (autre entité, exercice 2024 -> N-1).
Sans Excel ni PDF (--sans-pdf) : on garde la mécanique (sources, versions, questions, réponses, validation, traces).
Lancer : python tests/test_espace_def.py     (code 0 = conforme)
"""
import csv
import json
import os
import shutil
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "dsf-syscohada", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import espace_def as ed  # noqa: E402
import test_def_modele as tdm  # noqa: E402

ok = []


def check(nom, cond, detail=""):
    ok.append(bool(cond))
    print(f"  {'OK   ' if cond else 'ÉCHEC'} {nom}" + ("" if cond else f"  — {detail}"))


def main():
    racine = tempfile.mkdtemp()
    print("== Création du dossier de travail")
    d = ed.init(racine, "ENTITE TEST SA", 2025)
    # cette garde éprouve la mécanique du dossier sur le FORMAT GE (le modèle SYSCOHADA a sa garde : test_sn.py)
    ed.repondre(d, "interp.modele_def", "ge")
    check("arborescence 01_sources / 02_xls / 03_pdf / 04_questions + LISEZMOI + manifeste",
          all(os.path.isdir(os.path.join(d, s)) for s in ed.SOUS) and os.path.exists(os.path.join(d, "LISEZMOI.txt"))
          and os.path.exists(os.path.join(d, "manifeste.json")))
    print("== Sans balance : arrêt AVANT le calcul, une seule question bloquante")
    try:
        r = ed.generer(d, pdf=False)
    except Exception as e:                      # un plantage est un échec du contrôle, pas une preuve
        r = {"erreur": repr(e)}
    check("statut bloque_avant_calcul, question sources.balance", r.get("statut") == "bloque_avant_calcul"
          and r["questions"][0]["id"] == "sources.balance", r)
    print("== Dépôt des sources : reconnaissance par le contenu, logo par le nom")
    src = os.path.join(d, "01_sources")
    with open(os.path.join(src, "export_compta.csv"), "w", encoding="utf-8", newline="") as f:     # nom neutre
        w = csv.writer(f, delimiter=";")
        w.writerow(["Compte", "Intitulé", "Ouverture D", "Ouverture C", "Mvt D", "Mvt C", "Solde D", "Solde C"])
        for a, (o, md, mk) in tdm.B.items():
            s = o + md - mk
            w.writerow([a, tdm.LIB[a], max(o, 0), max(-o, 0), md, mk, max(s, 0), max(-s, 0)])
    tdm.modele(os.path.join(src, "reference.xlsx"))
    from PIL import Image
    for nom in ("logo_entite_test.png", "logo_editeur.png", "photo_reunion.jpg"):
        Image.new("RGB", (60, 30), (10, 20, 30)).save(os.path.join(src, nom))
    inv = {x["fichier"]: x["role"] for x in ed.inventaire(d, "ENTITE TEST SA")}
    check("balance reconnue par son contenu (nom neutre)", inv.get("export_compta.csv") == "balance", inv)
    check("DEF de référence reconnue", inv.get("reference.xlsx") == "modele_dsf", inv)
    check("photo ignorée (pas un logo)", inv.get("photo_reunion.jpg") == "image", inv)
    check("exercice du modèle détecté (2024 -> colonne N)", ed.exercice_du_modele(os.path.join(src, "reference.xlsx")) == 2024)
    print("== Lancement automatique : version PROJET, questions consolidées")
    r = ed.generer(d, pdf=False)
    check("logo de l'entité choisi, logo de l'éditeur écarté", r["sources"]["logo"] == "logo_entite_test.png"
          and "logo_editeur.png" in r["sources_ignorees"], r["sources"])
    check("v1 projet", r["statut"] == "projet" and r["version"] == 1, r)
    check("classeurs dans 02_xls, nommés _projet", all(p.startswith("02_xls") and "_projet" in p for p in r["livrables"]), r["livrables"])
    qs = json.load(open(os.path.join(d, "04_questions", "questions.json"), encoding="utf-8"))
    ids = {q["id"] for q in qs}
    check("identité demandée (obligatoire), interprétations facultatives",
          "identite.raison_sociale" in ids and any(q["id"].startswith("interp.") and not q["obligatoire"] for q in qs), sorted(ids)[:6])
    check("sortie sans aucune donnée comptable (soldes absents)", "150000" not in json.dumps(r) and "150 000" not in json.dumps(r))
    print("== Réponses : contrôlées, puis réinjectées")
    try:
        ed.repondre(d, "interp.base_cmf", "n'importe quoi")
        refus = False
    except SystemExit:
        refus = True
    check("réponse hors choix refusée", refus)
    v = ed.valider(d, "Comptable")
    check("validation refusée tant que des questions obligatoires sont ouvertes", v["statut"] == "refuse", v)
    ed.repondre(d, "identite.raison_sociale", "ENTITE TEST SA")
    for q in qs:
        if q["obligatoire"] and q["id"] != "identite.raison_sociale":
            ed.repondre(d, q["id"], q["options"][0] if q["options"] else "valeur test")
    v = ed.valider(d, "Comptable Test")
    check("validation acceptée : version définitive", v.get("statut") == "definitive" and v.get("version") == 2, v)
    check("livrables définitifs sans « _projet »", v.get("livrables") and all("_projet" not in p for p in v["livrables"]), v.get("livrables"))
    import openpyxl
    x = next(p for p in v["livrables"] if p.endswith("_FR.xlsx"))
    pg = openpyxl.load_workbook(os.path.join(d, x))["page garde"]
    check("identité saisie reprise en page de garde du classeur", pg["D13"].value == "ENTITE TEST SA", pg["D13"].value)
    man = json.load(open(os.path.join(d, "manifeste.json"), encoding="utf-8"))
    check("manifeste : 2 versions, empreintes des sources, validé par", len(man["versions"]) == 2
          and all(len(s["sha256"]) == 64 for s in man["versions"][-1]["sources"]) and man["versions"][-1]["valide_par"] == "Comptable Test")
    check("versions jamais écrasées (fichiers v1 toujours présents)",
          all(os.path.exists(os.path.join(d, p)) for p in man["versions"][0]["livrables"]))
    shutil.rmtree(racine, ignore_errors=True)
    print(f"\n{sum(ok)}/{len(ok)} contrôles conformes")
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
