# -*- coding: utf-8 -*-
"""Contre-épreuves de test_reprise_validation.py : on remet, une à la fois, l'ANCIEN comportement (ou un défaut
plausible) ; le test doit alors échouer. Code 0 = chaque mutation détectée."""
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MUTATIONS = {
    "question « DEF précédente » à une seule réponse (l'incident)": """
import espace_def as ed
ed.OPTIONS_DEF_PRECEDENTE = ("premier exercice",)
""",
    "validation sans contrôle des sources déposées après la génération": """
import espace_def as ed
ed.sources_modifiees = lambda d: {}
""",
    "aucune identité reprise des sources": """
import espace_def as ed
ed.identite_reprise = lambda d, inv, mod: ({}, {})
""",
    "un libellé pris pour une valeur (« Exercice clos le : »)": """
import identite_sources as ids
_v = ids.valeur_plausible
ids.valeur_plausible = lambda v: (" ".join(v.split()).strip(" :") or None) if isinstance(v, str) else _v(v)
""",
    "réponses appliquées absentes du rapport de contrôle": """
import espace_def as ed
ed.trace_reponses = lambda *a: []
""",
    "formulaire sans bandeau ni blocage de la validation": """
import formulaire as fo
fo._modif_sources = lambda d: {}
""",
    "PDF de DEF ignoré en silence (avant 0.11.1)": """
import espace_def as ed
ed.role_pdf = lambda p: ("inconnu", 0)
""",
    "DEF d'un autre exercice utilisée en silence": """
import espace_def as ed
_m = ed.modele_utilisable
ed.modele_utilisable = lambda p, N: (True, ed.exercice_du_modele(p), "") if p.lower().endswith(".xlsx") else _m(p, N)
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
import test_reprise_validation as t
sys.exit(t.main())
"""

detectees = 0
for nom, mutation in MUTATIONS.items():
    r = subprocess.run([sys.executable, "-c", LANCEUR.format(root=ROOT, mutation=mutation)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=1800)
    echecs = r.stdout.count("ÉCHEC")
    ok = r.returncode != 0 and echecs > 0
    detectees += ok
    print(f"{'détectée    ' if ok else 'NON DÉTECTÉE'} {nom} ({echecs} contrôle(s) en échec)"
          + ("" if ok or echecs else f" — {r.stderr.strip()[-300:]}"))
print(f"{detectees}/{len(MUTATIONS)} mutations détectées")
sys.exit(0 if detectees == len(MUTATIONS) else 1)
