# -*- coding: utf-8 -*-
"""Contre-épreuves de test_formulaire_parcours.py : on remet, une à la fois, l'ANCIEN comportement
(celui de l'incident du 17/10/2026) ; le test doit alors échouer. Code 0 = chaque mutation détectée."""
import contextlib
import io
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MUTATIONS = {
    "lecture qui prend un fichier tenu pour vide": """
import espace_def as ed
def lire_json(p, defaut):
    try:
        return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return defaut
import json; ed.lire_json = lire_json
""",
    "écriture sans nouvel essai": """
import espace_def as ed, json, os
def ecrire_json(p, v):
    tmp = p + ".tmp"
    json.dump(v, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, p)
ed.ecrire_json = ecrire_json
""",
    "formulaire sans filet (page blanche)": """
import formulaire as fo
fo.Gestionnaire.do_POST = fo.Gestionnaire._post
fo.Gestionnaire.do_GET = fo.Gestionnaire._get
""",
    "politique de référent « no-referrer » (cause de l'incident)": """
import formulaire as fo
_envoyer = fo.Gestionnaire._envoyer
def envoyer(self, code, corps, type_="text/html; charset=utf-8", nonce=""):
    vrai = self.send_header
    self.send_header = lambda k, v: vrai(k, "no-referrer" if k == "Referrer-Policy" else v)
    try:
        return _envoyer(self, code, corps, type_, nonce)
    finally:
        self.send_header = vrai
fo.Gestionnaire._envoyer = envoyer
""",
    "dossier par défaut dans OneDrive": """
import espace_def as ed, os
ed.dossier_par_defaut = lambda docs: os.path.join(docs, "Facil-DEF")
""",
}

LANCEUR = """
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
ROOT = {root!r}
sys.path.insert(0, os.path.join(ROOT, "skills", "dsf-syscohada", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "serveur"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
{mutation}
import test_formulaire_parcours as t
sys.exit(t.main())
"""

detectees = 0
for nom, mutation in MUTATIONS.items():
    code = LANCEUR.format(root=ROOT, mutation=mutation)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=900)
    echecs = r.stdout.count("ÉCHEC")
    ok = r.returncode != 0 and echecs > 0
    detectees += ok
    print(f"{'détectée    ' if ok else 'NON DÉTECTÉE'} {nom} ({echecs} contrôle(s) en échec)")
print(f"{detectees}/{len(MUTATIONS)} mutations détectées")
sys.exit(0 if detectees == len(MUTATIONS) else 1)
