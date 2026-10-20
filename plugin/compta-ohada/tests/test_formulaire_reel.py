# -*- coding: utf-8 -*-
"""Parcours navigateur sur les QUESTIONS RÉELLES de l'installation qui a bogué (16/10/2026).

Jeu : tests/donnees_questions_reelles_2025.json — tiré du journal des sorties (déjà pseudonymisé :
aucun nom, aucun montant). Étapes réelles : Sources (choix unique), Identité, Faits (oui/non),
Réintégrations TF1 (accepter/refuser), puis les interprétations facultatives du dossier de test.

Lancer : python tests/test_formulaire_reel.py      (code 0 = conforme)
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import test_formulaire as tf  # noqa: E402
import test_formulaire_parcours as tp  # noqa: E402

ed, fo, requete = tf.ed, tf.fo, tf.requete
ok = []


def check(nom, cond, detail=""):
    ok.append(bool(cond))
    print(f"  {'OK   ' if cond else 'ÉCHEC'} {nom}" + ("" if cond else f"  — {str(detail)[:400]}"))


def main():
    reel = ed.generer
    ed.generer = lambda d, **k: reel(d, **{**k, "pdf": False})
    d = tf.preparer()
    # Questions réelles (obligatoires) + les facultatives du dossier de test (interprétations).
    reelles = json.load(open(os.path.join(ROOT, "tests", "donnees_questions_reelles_2025.json"), encoding="utf-8"))
    p_q = os.path.join(d, "04_questions", "questions.json")
    facultatives = [q for q in ed.lire_json(p_q, []) if not q.get("obligatoire")]
    ed.ecrire_json(p_q, reelles + facultatives)
    ed.ecrire_json(os.path.join(d, "04_questions", "reponses.json"), {})

    url = fo.demarrer(d, navigateur=False)
    srv = fo._SERVEURS[d][0]
    ck = {"Cookie": f"facil_t={srv.jeton}"}
    etapes = fo._etapes(fo._questions(d))
    print(f"== {len(etapes)} étapes : " + " · ".join(e["court"] for e in etapes))
    for k in range(len(etapes) - 1):
        s, _, page = requete(url.split("?")[0] + f"?e={k}", entetes=ck)
        titre = (re.search(r'<h2 id="titre-etape">(.*?)</h2>', page) or [None, "?"])[1]
        corps = tp.envoi_navigateur(page, k)
        s, h, retour = requete(url, "POST", "/repondre", corps, ck)
        check(f"étape {k + 1} « {titre} » → étape {k + 2}", s == 303 and h.get("Location") == f"/?e={k + 1}",
              (s, h.get("Location"), retour[-300:]))
        reponses = ed.lire_json(os.path.join(d, "04_questions", "reponses.json"), {})
        ids = [q["id"] for q in etapes[k]["questions"] if q["obligatoire"]]
        check(f"étape {k + 1} : ses réponses obligatoires sont enregistrées", all(i in reponses for i in ids),
              [i for i in ids if i not in reponses])
    s, _, page = requete(url.split("?")[0] + "?e=v", entetes=ck)
    ouvertes = [q["id"] for q in fo._questions(d) if q["obligatoire"] and not q.get("reponse")]
    check("validation : aucune question obligatoire ouverte", not ouvertes, ouvertes)
    bouton = re.search(r'<form method="post" action="/valider">.*?</form>', page, re.S)
    check("validation : bouton actif", bouton and "disabled" not in bouton.group(0),
          bouton.group(0)[:200] if bouton else "absent")
    print(f"{sum(ok)}/{len(ok)} contrôles conformes")
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
