# -*- coding: utf-8 -*-
"""Falsification de test_formulaire.py : chaque sabotage de serveur/formulaire.py doit faire ÉCHOUER la garde.

Lancer : python tests/falsification_formulaire.py     (code 0 = tous les sabotages détectés)
"""
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "serveur", "formulaire.py")

SABOTAGES = [
    ("jeton ignoré", "return secrets.compare_digest(str(jeton or \"\"), self.server.jeton)", "return True"),
    ("Host non contrôlé", "if hote not in (\"127.0.0.1\", \"localhost\"):", "if False:"),
    ("Origin non contrôlée", "if origine and urllib.parse.urlparse(origine).hostname not in", "if False and origine not in"),
    ("témoin sans SameSite", "HttpOnly; SameSite=Strict; Path=/", "HttpOnly; Path=/"),
    ("année écrite en dur", "annee = datetime.date.today().year", "annee = 2025"),
    ("inactivité non tenue par le serveur", "if t - self.derniere > self.inactivite and not self.occupe():", "if False:"),
    ("durée absolue absente", "if t - self.debut > self.duree_max:", "if False:"),
    ("seuil décalé (>= au lieu de >, puis +1 s)", "if t - self.derniere > self.inactivite and", "if t - self.derniere > self.inactivite + 1 and"),
    ("requête refusée prolonge la session", "    def _entree(self, params):\n", "    def _entree(self, params):\n        self.server.derniere = time.time()\n"),
    ("battement ressuscite", "            self.server.fermer(motif)\n            return False", "            return True"),
    ("réponse enregistrée sans contrôle", "                    ed.repondre(d, k, val)", "                    ed.ecrire_json(os.path.join(d, '04_questions', 'reponses.json'), {**ed.lire_json(os.path.join(d, '04_questions', 'reponses.json'), {}), k: val})"),
    ("pas de veille", "                if motif:\n                    srv.fermer(motif)", "                pass"),
    ("défaut d'inactivité allongé", "INACTIVITE = 15 * 60", "INACTIVITE = 30 * 60"),
    ("étapes surchargées (toutes les questions sur une page)", "TAILLE = 6 ", "TAILLE = 60 "),
    ("« Suivant » n'avance pas", "(1 if aller == 'suivant' else", "(0 if aller == 'suivant' else"),
    ("boutons des dossiers côte à côte", ".pile {{ display:flex; flex-direction:column;", ".pile {{ display:flex; flex-direction:row;"),
    ("identité découpée en deux étapes", 'UNE_ETAPE = ("Identité de l\'entité", ', "UNE_ETAPE = ("),
    ("chemin d'accès remis sur les boutons", '{_ic("dossier")}{lab}</button>',
     '{_ic("dossier")}{lab} {html.escape(os.path.join(d, q))}</button>'),
    ("écoute sur toutes les interfaces", "super().__init__((\"127.0.0.1\", 0), Gestionnaire)", "super().__init__((\"0.0.0.0\", 0), Gestionnaire)"),
]


def main():
    texte = open(SOURCE, encoding="utf-8").read()
    rates = []
    for nom, avant, apres in SABOTAGES:
        if avant not in texte:
            print(f"  ?     {nom} : motif introuvable (sabotage obsolète)")
            rates.append(nom)
            continue
        tmp = tempfile.mkdtemp()
        shutil.copy(os.path.join(ROOT, "serveur", "facil_logo.png"), tmp)
        open(os.path.join(tmp, "formulaire.py"), "w", encoding="utf-8").write(texte.replace(avant, apres, 1))
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tests", "test_formulaire.py")], capture_output=True,
                           text=True, encoding="utf-8", env={**os.environ, "FACIL_FORMULAIRE": tmp}, timeout=600)
        detecte = r.returncode != 0
        print(f"  {'DÉTECTÉ' if detecte else 'RATÉ   '} {nom}")
        if not detecte:
            rates.append(nom)
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{len(SABOTAGES) - len(rates)}/{len(SABOTAGES)} sabotages détectés")
    return 0 if not rates else 1


if __name__ == "__main__":
    sys.exit(main())
