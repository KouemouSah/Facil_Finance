# -*- coding: utf-8 -*-
"""Garde du dossier de travail : une valeur mal transmise par Claude Desktop n'est jamais un chemin.

Incident du 16/10/2026 : l'extension installée recevait FACIL_DEF_RACINE = « ${DOCUMENTS}/Facil-DEF »
(variable non remplacée) ; le serveur tentait de créer ce dossier relatif → « Accès refusé ».
La garde vérifie le serveur (espace_def) ET la garde de lecture (garde_lecture) : mêmes réponses.

Lancer : python tests/test_racine.py      (code 0 = tout conforme)
"""
import importlib.util
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def charger(nom, chemin):
    spec = importlib.util.spec_from_file_location(nom, chemin)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


sys.path.insert(0, os.path.join(ROOT, "skills", "dsf-syscohada", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "lib"))
ed = charger("espace_def", os.path.join(ROOT, "skills", "dsf-syscohada", "scripts", "espace_def.py"))
gl = charger("garde_lecture", os.path.join(ROOT, "serveur", "garde_lecture.py"))

# Défaut : Documents\Facil-DEF, sauf Documents synchronisé par OneDrive → %USERPROFILE%\Facil-DEF (règle du 17/10/2026).
defaut = ed.dossier_par_defaut(ed.documents())
autre = os.path.join(os.path.expanduser("~"), "Mes dossiers DEF")
CAS = [
    ("variable ${DOCUMENTS} non remplacée (incident)", "${DOCUMENTS}/Facil-DEF", defaut),
    ("réglage utilisateur non remplacé", "${user_config.dossier_travail}", defaut),
    ("valeur vide", "", defaut),
    ("espaces seuls", "   ", defaut),
    ("variable Windows inconnue restée telle quelle", "%DOSSIER_INEXISTANT_FACIL%\\DEF", defaut),
    ("chemin réel choisi par l'utilisateur", autre, autre),
    ("chemin réel entre guillemets", f'"{autre}"', autre),
    ("variable Windows connue, développée", "%USERPROFILE%\\Mes dossiers DEF", autre),
]

resultats = []
for nom, valeur, attendu in CAS:
    os.environ["FACIL_DEF_RACINE"] = valeur
    a, b = ed.racine_defaut(), gl.racine()
    ok = os.path.normcase(a) == os.path.normcase(attendu) and os.path.normcase(b) == os.path.normcase(attendu)
    resultats.append(ok)
    print(f"{'ok   ' if ok else 'ÉCHEC'} {nom} → {a}" + ("" if ok else f" (garde : {b} ; attendu : {attendu})"))
os.environ.pop("FACIL_DEF_RACINE", None)
ok_doc = os.path.isabs(defaut) and "${" not in defaut
resultats.append(ok_doc)
print(f"{'ok   ' if ok_doc else 'ÉCHEC'} le dossier par défaut est un chemin absolu réel : {defaut}")
hors_cloud = not ed.est_synchronise(defaut)
resultats.append(hors_cloud)
print(f"{'ok   ' if hors_cloud else 'ÉCHEC'} le dossier par défaut n'est pas synchronisé dans le cloud (OneDrive)")
meme = os.path.normcase(gl.dossier_par_defaut(gl.documents())) == os.path.normcase(defaut)
resultats.append(meme)
print(f"{'ok   ' if meme else 'ÉCHEC'} le serveur et la garde de lecture désignent le même dossier")
print(f"{sum(resultats)}/{len(resultats)} contrôles conformes")
sys.exit(0 if all(resultats) else 1)
