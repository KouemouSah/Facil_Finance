# -*- coding: utf-8 -*-
"""Lecture locale d'une DEF scannée (ocr_def) — sur une DEF de test de VÉRITÉ CONNUE (tests/fabriquer_scan.py).

Ce qui est prouvé :
  1. les pages d'états sont trouvées, le bilan tourné de 90° est redressé, l'exercice est lu ;
  2. toutes les formules SYSCOHADA vérifiables sont justes, et — propriété centrale — TOUT MONTANT DÉCLARÉ PROUVÉ
     EST JUSTE (comparé à la vérité) ; la couverture des montants est mesurée ;
  3. cache par empreinte et lecture en arrière-plan ;
  4. génération : DEF N-1 scannée → lecture lancée et dite ; une fois lue, compte de résultat N-1 repris, question
     « DEF précédente » levée, montants non prouvés demandés (et seulement confirmés s'ils sont des montants).
Les deux DEF réelles numérisées (mise au point) ne sont pas versionnées : données client.
Lancer : python tests/test_ocr_def.py      (code 0 = conforme)
"""
import glob
import json
import os
import shutil
import sys
import tempfile
import time

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "skills", "dsf-syscohada", "scripts"))
import ocr_def  # noqa: E402

ok = []


def check(nom, cond, detail=""):
    ok.append(bool(cond))
    print(f"  {'OK   ' if cond else 'ÉCHEC'} {nom}" + ("" if cond else f"  — {str(detail)[:400]}"))


def attendre(pdf, cache, limite=1500):
    t0 = time.time()
    while time.time() - t0 < limite:
        st, r = ocr_def.etat(pdf, cache)
        if st in ("pret", "echec"):
            return st, r
        time.sleep(3)
    return "delai", None


def main():
    print("== 0. Moteur OCR")
    check("moteur OCR local disponible (runtime du plugin)", ocr_def.disponible())
    if not ok[-1]:
        print("0/1 — le reste n'est pas vérifiable sans moteur")
        return 1
    print("== 0 bis. Signe « - » imprimé à part (style des DEF réelles : tiret collé au trait de la case)")
    import cv2
    import numpy as np

    def case(tiret, separateur):
        im = np.full((80, 420, 3), 255, np.uint8)
        cv2.line(im, (20, 0), (20, 79), (0, 0, 0), 3)                     # trait vertical de la case
        cv2.putText(im, "1 633 927 813", (150, 52), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
        if tiret:
            cv2.rectangle(im, (27, 37), (35, 41), (0, 0, 0), -1)          # 9 x 5 px, comme mesuré à 300 dpi
        if separateur:
            cv2.line(im, (20, 38), (419, 38), (0, 0, 0), 2)                # trait de séparation de ligne, mince
        return im
    check("tiret à part détecté (montant négatif)", ocr_def.signe_moins(case(True, False), 20, 150, 40, 30))
    check("pas de tiret : positif", not ocr_def.signe_moins(case(False, False), 20, 150, 40, 30))
    check("trait de séparation de ligne : PAS un signe moins", not ocr_def.signe_moins(case(False, True), 20, 150, 40, 30))
    import fabriquer_scan
    tmp = tempfile.mkdtemp()
    scan, verite, ex = fabriquer_scan.fabriquer(tmp)

    print("== 1-2. Lecture et preuve")
    r = ocr_def.lire(scan, journal=lambda m: None)
    check("pages d'états trouvées (bilan tourné de 90°, compte de résultat)", r["pages_etats"] == [1, 2], r["pages_etats"])
    check("exercice lu sur les dates de clôture", r["exercice"] == ex, (r["exercice"], ex))
    f = r["formules"]
    check("toutes les formules vérifiables sont justes (≥ 40 vérifiables)", f["justes"] == f["verifiables"] >= 40, f)
    faux, prouves_nz = [], 0
    for code, cols in r["etats"].items():
        vrais = {abs(x) for x in verite.get(code, [])}
        for ch, x in cols.items():
            if x["prouve"] and x["valeur"]:
                prouves_nz += 1
                if abs(x["valeur"]) not in vrais:
                    faux.append((code, ch, x["valeur"], sorted(vrais)))
    check(f"TOUT montant prouvé est juste ({prouves_nz} montants non nuls prouvés)", not faux and prouves_nz >= 40, faux[:5])
    # et un ZÉRO prouvé ne cache pas un montant : sur une ligne où la vérité porte un montant que rien n'a lu, aucune
    # case ne doit être « prouvée » à 0 (constaté : formule 0 = 0 + 0 sur des totaux non lus)
    zeros_faux = [c for c, cols in r["etats"].items()
                  if any(x["prouve"] and x["valeur"] == 0 for x in cols.values())
                  and any(abs(v) >= 1000 and abs(v) not in {abs(x["valeur"] or 0) for x in cols.values()}
                          for v in verite.get(c, []))]
    check("aucun zéro prouvé là où la vérité porte un montant non lu", not zeros_faux, zeros_faux)
    lus = {abs(x["valeur"]) for cols in r["etats"].values() for x in cols.values()}
    vrais_nz = [(c, v) for c, vs in verite.items() for v in vs if abs(v) >= 1000]
    couverts = sum(1 for _, v in vrais_nz if abs(v) in lus)
    check(f"couverture : ≥ 95 % des montants vrais retrouvés ({couverts}/{len(vrais_nz)})", couverts >= 0.95 * len(vrais_nz))
    negatifs = [(c, v) for c, vs in verite.items() for v in vs if v <= -1000 and c[0] in "RX"]
    signes = [(c, v) for c, v in negatifs if any(x["valeur"] == v for x in r["etats"].get(c, {}).values())]
    check(f"montants négatifs lus avec leur signe ({len(signes)}/{len(negatifs)})", negatifs and len(signes) == len(negatifs),
          [x for x in negatifs if x not in signes])

    print("== 3. Cache et lecture en arrière-plan")
    cache = os.path.join(tmp, "cache")
    check("lancement en arrière-plan", ocr_def.lancer_en_fond(scan, cache) == "lance")
    check("état « en cours » pendant la lecture", ocr_def.etat(scan, cache)[0] == "en_cours", ocr_def.etat(scan, cache))
    st, r2 = attendre(scan, cache)
    check("lecture terminée, résultat en cache, identique à la lecture directe",
          st == "pret" and r2["formules"] == r["formules"] and r2["montants"] == r["montants"], (st, r2 and r2.get("formules")))
    check("relancer une lecture prête ne relit rien", ocr_def.lancer_en_fond(scan, cache) == "pret")

    print("== 4. Génération : DEF de l'exercice précédent scannée")
    import test_reprise_validation as trv
    ed = trv.ed
    reel = ed.generer
    ed.generer = lambda d, **k: reel(d, **{**k, "pdf": False})
    d, _ = trv.balance_seule()
    man = ed.lire_json(os.path.join(d, "manifeste.json"), {})
    man["exercice"] = ex + 1                              # la DEF scannée (exercice ex) est la DEF N-1
    ed.ecrire_json(os.path.join(d, "manifeste.json"), man)
    shutil.copy(scan, os.path.join(d, "01_sources", "DEF_precedente_scannee.pdf"))
    g = ed.generer(d)
    q = {x["id"]: x for x in ed.lire_json(os.path.join(d, "04_questions", "questions.json"), [])}
    check("1re génération : lecture lancée et dite", g.get("lecture_scan", {}).get("code") == "en_cours", g.get("lecture_scan"))
    check("la question « DEF précédente » dit la lecture en cours",
          "en cours de lecture" in q.get("sources.def_precedente", {}).get("question", ""), q.get("sources.def_precedente"))
    st, _ = attendre(os.path.join(d, "01_sources", "DEF_precedente_scannee.pdf"), os.path.join(d, "04_questions", "travail", "ocr"))
    check("lecture en arrière-plan aboutie", st == "pret", st)
    g = ed.generer(d)
    ls = g.get("lecture_scan", {})
    q = {x["id"]: x for x in ed.lire_json(os.path.join(d, "04_questions", "questions.json"), [])}
    check("2e génération : DEF scannée lue et utilisée", ls.get("code") == "lue" and ls.get("montants_prouves", 0) >= 40, ls)
    check("question « DEF précédente » levée", "sources.def_precedente" not in q, list(q)[:4])
    a_verif = [k for k in q if k.startswith("scan.")]
    check("montants non prouvés demandés, un par case, avec la valeur lue proposée",
          len(a_verif) == ls.get("a_verifier") and all(q[k].get("proposition") is not None for k in a_verif), (len(a_verif), ls))
    import openpyxl
    v = ed.lire_json(os.path.join(d, "manifeste.json"), {})["versions"][-1]
    ctrl = next(os.path.join(d, x) for x in v["livrables"] if "controle" in x and x.endswith(".xlsx"))
    texte = " | ".join(str(c) for ws in openpyxl.load_workbook(ctrl).worksheets for row in ws.iter_rows(values_only=True)
                       for c in row if c is not None)
    check("rapport de contrôle : source du compte de résultat N-1 = la DEF scannée, montants prouvés comptés",
          f"DEF {ex} scannée" in texte and "prouvé(s) par les formules" in texte, texte[-500:])
    check("contrôle croisé : bilan N-1 du scan = ouvertures de la balance", "Bilan N-1 de la DEF scannée = ouvertures" in texte)
    if a_verif:
        k = a_verif[0]
        try:
            ed.repondre(d, k, "environ un million", canal="formulaire")
            refus = False
        except SystemExit:
            refus = True
        check("une réponse qui n'est pas un montant est refusée", refus)
        ed.repondre(d, k, q[k]["proposition"], canal="formulaire")
        g = ed.generer(d)
        check("montant confirmé : utilisé, et compté comme confirmé", g["lecture_scan"].get("confirmes") == 1, g["lecture_scan"])
    print("== 5. Un scan qui n'est pas une DEF")
    import pymupdf
    d2, _ = trv.balance_seule()
    doc = pymupdf.open()
    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 200, 280), 0)
    pix.clear_with(255)
    doc.new_page().insert_image(pymupdf.Rect(0, 0, 595, 842), pixmap=pix)    # une page blanche numérisée
    p2 = os.path.join(d2, "01_sources", "facture_scannee.pdf")
    doc.save(p2)
    ed.generer(d2)
    attendre(p2, os.path.join(d2, "04_questions", "travail", "ocr"))
    g = ed.generer(d2)
    q = {x["id"]: x for x in ed.lire_json(os.path.join(d2, "04_questions", "questions.json"), [])}
    check("aucun état trouvé : dit, et la question « DEF précédente » RESTE posée",
          g.get("lecture_scan", {}).get("code") == "pas_un_etat" and "aucun bilan" in q.get("sources.def_precedente", {}).get("question", ""),
          (g.get("lecture_scan"), q.get("sources.def_precedente", {}).get("question")))
    print(f"{sum(ok)}/{len(ok)} contrôles conformes")
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
