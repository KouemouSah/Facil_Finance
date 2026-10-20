# -*- coding: utf-8 -*-
"""Lance le formulaire sur un dossier de test aux QUESTIONS RÉELLES et le garde ouvert, pour un essai dans
un vrai navigateur (Chromium piloté). Écrit l'URL dans le fichier passé en argument. Ctrl+C pour arrêter."""
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import test_formulaire as tf  # noqa: E402

ed, fo = tf.ed, tf.fo
reel = ed.generer
ed.generer = lambda d, **k: reel(d, **{**k, "pdf": False})
d = tf.preparer()
p_q = os.path.join(d, "04_questions", "questions.json")
reelles = json.load(open(os.path.join(ROOT, "tests", "donnees_questions_reelles_2025.json"), encoding="utf-8"))
ed.ecrire_json(p_q, reelles + [q for q in ed.lire_json(p_q, []) if not q.get("obligatoire")])
ed.ecrire_json(os.path.join(d, "04_questions", "reponses.json"), {})
url = fo.demarrer(d, navigateur=False)
open(sys.argv[1], "w", encoding="utf-8").write(json.dumps({"url": url, "dossier": d}))
print("formulaire prêt :", url, flush=True)
while True:
    time.sleep(1)
