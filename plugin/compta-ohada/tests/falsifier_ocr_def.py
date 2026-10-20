# -*- coding: utf-8 -*-
"""Contre-épreuves de test_ocr_def.py : chaque mutation remet un défaut RENCONTRÉ pendant la mise au point sur les
DEF réelles numérisées ; le test doit alors échouer. Code 0 = chaque mutation détectée."""
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MUTATIONS = {
    "« - » imprimé à part non détecté (soldes négatifs lus positifs)": """
import ocr_def
ocr_def.signe_moins = lambda *a, **k: False
""",
    "page jamais redressée (bilan numérisé tourné de 90°)": """
import ocr_def, numpy as np
def orienter(img):
    T = ocr_def.jetons(ocr_def._ocr()(img)[0])
    return 0, np.ascontiguousarray(img), T
ocr_def.orienter = orienter
""",
    "ordre officiel des lignes faux (XG placé après les lignes HAO)": """
import ocr_def
s = ocr_def.SEQUENCES[2]
s.remove("XG"); s.insert(s.index("XH"), "XG")
""",
    "scan de 2 pages (états seuls) non reconnu": """
import espace_def
_r = espace_def.role_pdf
def role_pdf(p):
    import pymupdf
    return ("inconnu", 0) if pymupdf.open(p).page_count < 3 else _r(p)
espace_def.role_pdf = role_pdf
""",
    "scan sans état qui lève la question « DEF précédente »": """
import espace_def
_n = espace_def.n1_depuis_scan
def n1(d, inv, N, rep):
    a, b, info = _n(d, inv, N, rep)
    if info and info.get("code") == "pas_un_etat":
        info = dict(info, code="lue")
    return a, b, info
espace_def.n1_depuis_scan = n1
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
import test_ocr_def as t
sys.exit(t.main())
"""

filtre = os.environ.get("FACIL_MUTATION", "")          # rejouer une seule mutation (chaque passe dure ~20 min)
MUTATIONS = {k: v for k, v in MUTATIONS.items() if filtre.lower() in k.lower()}
detectees = 0
for nom, mutation in MUTATIONS.items():
    r = subprocess.run([sys.executable, "-c", LANCEUR.format(root=ROOT, mutation=mutation)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=7200)
    echecs = r.stdout.count("ÉCHEC")
    ok = r.returncode != 0 and echecs > 0
    detectees += ok
    print(f"{'détectée    ' if ok else 'NON DÉTECTÉE'} {nom} ({echecs} contrôle(s) en échec)"
          + ("" if ok or echecs else f" — {r.stderr.strip()[-300:]}"), flush=True)
print(f"{detectees}/{len(MUTATIONS)} mutations détectées")
sys.exit(0 if detectees == len(MUTATIONS) else 1)
