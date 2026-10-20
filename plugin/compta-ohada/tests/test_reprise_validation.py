# -*- coding: utf-8 -*-
"""0.11.0 — DEF précédente, identité reprise des sources, mode « préparer et valider ».

Incident du 16/10/2026 (machine du porteur) : la DEF précédente, déposée APRÈS la génération, restait invisible ; la
question « DEF précédente » n'offrait que « premier exercice » et bloquait la validation. Ce test prouve :
  1. deux réponses possibles à la question, chacune acceptée ;
  2. une DEF déposée après la génération est signalée (formulaire : bandeau, validation désactivée ; moteur : refus
     motivé), et la régénération la lit — la question disparaît, l'identité de sa page de garde est reprise ;
  3. une DEF d'un autre exercice est écartée, dite, jamais utilisée en silence ;
  4. une fiche entité déposée donne l'identité (liste fermée respectée) ; la saisie de l'utilisateur l'emporte ;
  5. la validation trace chaque réponse (origine, date) et le valideur au rapport de contrôle, et pose la fiche de
     l'entité, reprise par l'exercice suivant ;
  6. l'identité reprise est pseudonymisée par la passerelle ; un gabarit vide ne donne aucune identité.
Lancer : python tests/test_reprise_validation.py      (code 0 = conforme)
"""
import json
import os
import shutil
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import test_formulaire as tf  # noqa: E402

ed, fo, requete = tf.ed, tf.fo, tf.requete
import identite_sources as ids  # noqa: E402

ok = []


def check(nom, cond, detail=""):
    ok.append(bool(cond))
    print(f"  {'OK   ' if cond else 'ÉCHEC'} {nom}" + ("" if cond else f"  — {str(detail)[:400]}"))


def qs_de(d):
    return {q["id"]: q for q in fo._questions(d)}


def repondre_tout(d, canal):
    """Répond à chaque question obligatoire ouverte, comme le ferait l'utilisateur."""
    for q in fo._questions(d):
        if not q["obligatoire"] or q.get("reponse"):
            continue
        v = ("refuser" if "refuser" in q["options"] else "non" if "non" in q["options"] else q["options"][-1]) \
            if q.get("options") else "inconnu"
        ed.repondre(d, q["id"], v, canal=canal)


def balance_seule():
    d = ed.init(tempfile.mkdtemp(), "ENTITE TEST SA", 2025)
    src = os.path.join(d, "01_sources")
    tmp = tf.preparer()                                   # balance + DEF de test, prises au dossier préparé
    shutil.copy(os.path.join(tmp, "01_sources", "balance.csv"), src)
    return d, os.path.join(tmp, "01_sources", "reference.xlsx")


def main():
    reel = ed.generer
    ed.generer = lambda d, **k: reel(d, **{**k, "pdf": False})

    print("== 1. Sans DEF précédente : deux réponses, aucune ne bloque")
    d, ref = balance_seule()
    ed.generer(d)
    q = qs_de(d).get("sources.def_precedente")
    check("question posée, obligatoire, avec DEUX réponses", q and q["obligatoire"]
          and q["options"] == ["premier exercice", "DEF précédente indisponible"], q and q["options"])
    ed.repondre(d, "sources.def_precedente", "DEF précédente indisponible", canal="formulaire")
    check("« DEF précédente indisponible » acceptée", qs_de(d)["sources.def_precedente"]["reponse"] == "DEF précédente indisponible")
    check("sources inchangées depuis la v1 : rien à signaler", ed.sources_modifiees(d) == {}, ed.sources_modifiees(d))

    print("== 2. DEF déposée APRÈS la génération (l'incident)")
    shutil.copy(ref, os.path.join(d, "01_sources", "DEF_2025_deposee.xlsx"))
    m = ed.sources_modifiees(d)
    check("nouvelle DEF signalée, avec son rôle", m and m["ajoutes"] == [{"fichier": "DEF_2025_deposee.xlsx", "role": "modele_dsf"}], m)
    r = ed.valider(d, "Valideur Test")
    check("validation REFUSÉE tant que la DEF n'est pas lue, motif dit", r["statut"] == "refuse" and "régénérez" in r["raison"]
          and "DEF_2025_deposee.xlsx" in r["raison"], r)
    url = fo.demarrer(d, navigateur=False)
    srv = fo._SERVEURS[d][0]
    ck = {"Cookie": f"facil_t={srv.jeton}"}
    s, _, page = requete(url.split("?")[0] + "?e=v", entetes=ck)
    check("formulaire : bandeau « nouveaux fichiers » avec bouton Régénérer",
          "Nouveaux fichiers dans 01_sources" in page and "DEF_2025_deposee.xlsx" in page and 'action="/regenerer"' in page)
    import re
    bouton = re.search(r'<form method="post" action="/valider">.*?</form>', page, re.S)
    check("formulaire : bouton Valider désactivé, raison dite", bouton and "disabled" in bouton.group(0)
          and "Régénérez d’abord" in bouton.group(0), bouton.group(0)[-300:] if bouton else "absent")
    s, h, _ = requete(url, "POST", "/regenerer", {"t": srv.jeton}, ck)
    tf.attendre(srv)
    qs = qs_de(d)
    check("après régénération : la question « DEF précédente » a disparu", "sources.def_precedente" not in qs, list(qs)[:5])
    check("identité reprise de la page de garde, avec son origine", qs.get("identite.raison_sociale", {}).get("reponse") == "ANCIENNE SA"
          and "DEF précédente déposée (DEF_2025_deposee.xlsx)" in qs["identite.raison_sociale"].get("origine", ""),
          qs.get("identite.raison_sociale"))
    check("nom différent du dossier : avertissement dans l'origine", "vérifiez" in qs["identite.raison_sociale"].get("origine", ""))
    adr = qs.get("identite.adresse", {})
    check("NIF repris aussi ; adresse (absente de la page de garde) toujours demandée, vide",
          qs.get("identite.nif", {}).get("reponse") == "NIF-OLD" and adr.get("obligatoire") and not adr.get("reponse"),
          [qs.get("identite.nif"), adr])
    s, _, page = requete(url.split("?")[0] + "?e=v", entetes=ck)
    check("bandeau disparu après régénération", "Nouveaux fichiers dans 01_sources" not in page)
    check("formulaire : la reprise s'affiche avec sa valeur et son origine",
          'value="ANCIENNE SA"' in requete(url.split("?")[0] + "?e=0", entetes=ck)[2] or
          'value="ANCIENNE SA"' in requete(url.split("?")[0] + "?e=1", entetes=ck)[2])

    print("== 3. Saisie de l'utilisateur prioritaire sur la reprise")
    ed.repondre(d, "identite.raison_sociale", "ENTITE TEST SA", canal="conversation")
    ed.generer(d)
    q = qs_de(d).get("identite.raison_sociale")
    check("la saisie remplace la reprise (plus d'origine « reprise »)", q is None or (q["reponse"] == "ENTITE TEST SA" and not q.get("origine")), q)

    print("== 4. Validation : traçabilité, valideur, fiche de l'entité")
    repondre_tout(d, "formulaire")
    r = ed.valider(d, "Valideur Test")
    check("version définitive produite", r.get("statut") == "definitive", {k: r.get(k) for k in ("statut", "raison")})
    man = ed.lire_json(os.path.join(d, "manifeste.json"), {})
    v = man["versions"][-1]
    check("manifeste : valideur et date de validation", v["valide_par"] == "Valideur Test" and v.get("valide_le"), v.get("valide_le"))
    check("manifeste : inventaire complet de 01_sources", {x["fichier"] for x in v.get("inventaire", [])} ==
          {"balance.csv", "DEF_2025_deposee.xlsx"}, v.get("inventaire"))
    import openpyxl
    ctrl = next(os.path.join(d, x) for x in v["livrables"] if "controle" in x and x.endswith(".xlsx"))
    texte = " | ".join(str(c) for ws in openpyxl.load_workbook(ctrl).worksheets for row in ws.iter_rows(values_only=True)
                       for c in row if c is not None)
    check("rapport de contrôle : validée par + date", "Validée par" in texte and "Valideur Test" in texte and "Validée le" in texte)
    check("rapport de contrôle : réponses appliquées avec leur origine et leur date",
          "Réponses appliquées" in texte and "saisie au formulaire, le " in texte
          and "ENTITE TEST SA — réponse donnée dans la conversation, le " in texte, texte[-600:])
    fiche = os.path.join(os.path.dirname(d), "fiche_entite.json")
    fj = ed.lire_json(fiche, {})
    check("fiche de l'entité posée pour l'exercice suivant", fj.get("identite", {}).get("raison_sociale") == "ENTITE TEST SA"
          and "Valideur Test" in fj.get("source", ""), fj)

    print("== 5. Exercice suivant : identité reprise de la fiche de l'entité")
    d2 = ed.init(os.path.dirname(os.path.dirname(d)), "ENTITE TEST SA", 2026)
    shutil.copy(os.path.join(d, "01_sources", "balance.csv"), os.path.join(d2, "01_sources"))
    ed.generer(d2)
    q = qs_de(d2).get("identite.raison_sociale")
    check("2026 : raison sociale reprise de la fiche de l'entité", q and q["reponse"] == "ENTITE TEST SA"
          and "fiche de l'entité" in q.get("origine", ""), q)

    print("== 6. DEF d'un autre exercice : écartée et dite")
    d3 = ed.init(tempfile.mkdtemp(), "ENTITE TEST SA", 2027)
    shutil.copy(os.path.join(d, "01_sources", "balance.csv"), os.path.join(d3, "01_sources"))
    shutil.copy(ref, os.path.join(d3, "01_sources", "DEF_ancienne.xlsx"))         # porte l'exercice 2024
    g = ed.generer(d3)
    q = qs_de(d3).get("sources.def_precedente")
    check("DEF 2024 pour 2027 : écartée, motif au résultat", g.get("modele_ecarte", {}).get("fichier") == "DEF_ancienne.xlsx"
          and "2024" in g["modele_ecarte"]["motif"], g.get("modele_ecarte"))
    check("la question nomme le fichier écarté et le motif, deux réponses", q and "DEF_ancienne.xlsx" in q["question"]
          and "2024" in q["question"] and len(q["options"]) == 2, q and q["question"])
    check("et son identité n'est pas reprise", not qs_de(d3).get("identite.raison_sociale", {}).get("origine"))
    okx, _, motif = ed.modele_utilisable("C:/x/DEF.xls", 2025)
    check("DEF au format .xls : écartée avec le geste à faire (enregistrer en .xlsx)", not okx and ".xlsx" in motif, motif)

    print("== 7. Fiche entité déposée dans 01_sources")
    d4, _ = balance_seule()
    with open(os.path.join(d4, "01_sources", "fiche_entite.txt"), "w", encoding="utf-8") as f:
        f.write("Raison sociale : BETA SARL\nNIF : 123456789\nAdresse : Rue 1, Bata\nForme juridique : sarl\n"
                "Activité principale : Négoce\nDirigeant : M. Test\n")
    with open(os.path.join(d4, "01_sources", "notes.txt"), "w", encoding="utf-8") as f:
        f.write("Penser à relancer le comptable.\n")
    inv = {x["fichier"]: x["role"] for x in ed.inventaire(d4, "ENTITE TEST SA")}
    check("fiche reconnue par son contenu ; un texte quelconque ne l'est pas",
          inv.get("fiche_entite.txt") == "fiche_entite" and inv.get("notes.txt") != "fiche_entite", inv)
    ed.generer(d4)
    qs = qs_de(d4)
    check("identité complète reprise de la fiche", all(qs.get(f"identite.{k}", {}).get("reponse") for k in
                                                      ("raison_sociale", "nif", "adresse", "activite", "dirigeant")),
          {k: qs.get(f"identite.{k}", {}).get("reponse") for k in ("raison_sociale", "nif", "adresse")})
    check("forme juridique ramenée à la liste fermée (« sarl » → « SARL »)", qs.get("identite.forme_juridique", {}).get("reponse") == "SARL")
    d5 = ed.init(tempfile.mkdtemp(), "GAMMA SA", 2025)
    with open(os.path.join(d5, "01_sources", "identite.txt"), "w", encoding="utf-8") as f:
        f.write("Raison sociale : GAMMA SA\nForme juridique : Coopérative agricole\n")
    val, orig = ed.identite_reprise(d5, ed.inventaire(d5, "GAMMA SA"), None)
    check("forme hors liste fermée : non reprise (elle reste demandée)", val.get("raison_sociale") == "GAMMA SA"
          and "forme_juridique" not in val, val)

    print("== 8. Aucune fausse identité ; confidentialité")
    gab = os.path.join(ROOT, "skills", "dsf-syscohada", "templates", "def_ge_gabarit.xlsx")
    check("gabarit officiel vide : aucune identité lue (ni libellé pris pour valeur)", ids.depuis_def(gab) == {}, ids.depuis_def(gab))
    check("« Exercice clos le : » n'est jamais une valeur", ids.valeur_plausible("Exercice clos le:") is None
          and ids.valeur_plausible("(ou nom et prénoms de l'exploitant)") is None and ids.valeur_plausible("BETA SARL") == "BETA SARL")
    sys.path.insert(0, os.path.join(ROOT, "serveur"))
    import confidentialite as conf
    racine = os.path.dirname(os.path.dirname(d4))
    P = conf.Passerelle(racine)
    P.apprendre_racine()
    sortie = json.dumps(P.sortie("test", {"texte": "BETA SARL, NIF 123456789, dirigeant M. Test"}), ensure_ascii=False)
    check("identité REPRISE pseudonymisée en sortie (raison sociale, NIF, dirigeant)",
          "BETA SARL" not in sortie and "123456789" not in sortie and "M. Test" not in sortie, sortie)

    print("== 9. DEF précédente en PDF (cas réel : DEF imprimées puis numérisées)")
    import pymupdf
    d6, _ = balance_seule()
    scan = pymupdf.open()
    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 60, 80), 0)
    pix.clear_with(200)
    for _ in range(4):                                     # images seules, aucune couche texte : un scan
        scan.new_page().insert_image(pymupdf.Rect(20, 20, 400, 600), pixmap=pix)
    scan.save(os.path.join(d6, "01_sources", "DEF_2024_scannee.pdf"))
    texte = pymupdf.open()
    pg = texte.new_page()
    pg.insert_text((50, 60), "ETATS FINANCIERS - BILAN ACTIF - COMPTE DE RESULTAT - exercice 2024")
    for i in range(40):                                    # une DEF porte des montants
        pg.insert_text((50, 80 + i * 18), f"Poste {i}    {1000 + i} 250 000    {900 + i} 125 500")
    guide = pymupdf.open()
    guide.new_page().insert_text((50, 80), "Guide : remplir le BILAN ACTIF et le COMPTE DE RESULTAT des ETATS FINANCIERS")
    p_guide = os.path.join(tempfile.mkdtemp(), "guide.pdf")
    guide.save(p_guide)
    p_txt = os.path.join(tempfile.mkdtemp(), "def.pdf")
    texte.save(p_txt)
    autre = pymupdf.open()
    autre.new_page().insert_text((50, 80), "Facture n. 12 - prestation de conseil")
    p_autre = os.path.join(tempfile.mkdtemp(), "facture.pdf")
    autre.save(p_autre)
    check("PDF scanné reconnu comme tel ; PDF texte de DEF reconnu ; autre PDF inconnu",
          ed.role_pdf(os.path.join(d6, "01_sources", "DEF_2024_scannee.pdf"))[0] == "pdf_scanne"
          and ed.role_pdf(p_txt)[0] == "def_pdf" and ed.role_pdf(p_autre)[0] == "inconnu"
          and ed.role_pdf(p_guide)[0] == "inconnu",
          [ed.role_pdf(x)[0] for x in (os.path.join(d6, "01_sources", "DEF_2024_scannee.pdf"), p_txt, p_autre)])
    g = ed.generer(d6)
    q = qs_de(d6).get("sources.def_precedente")
    check("scan : jamais ignoré en silence — la question le nomme et dit quoi faire",
          # depuis 0.12.0 : lecture OCR locale lancée (sinon, sans moteur OCR : « déposez la version .xlsx »)
          q and "DEF_2024_scannee.pdf" in q["question"] and "scann" in q["question"]
          and (".xlsx" in q["question"] or "en cours de lecture" in q["question"])
          and len(q["options"]) == 2 and g.get("def_pdf", {}).get("nature") == "pdf_scanne"
          and "DEF_2024_scannee.pdf" not in g.get("sources_ignorees", []), q and q["question"])

    print(f"{sum(ok)}/{len(ok)} contrôles conformes")
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
