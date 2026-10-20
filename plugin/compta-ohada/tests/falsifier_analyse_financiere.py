# -*- coding: utf-8 -*-
"""Contre-épreuves de test_analyse_financiere.py : chaque mutation remet un défaut plausible ; le test doit échouer."""
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MUTATIONS = {
    "ratio calculé sur une base négative (constaté : personnel / valeur ajoutée < 0)": """
import analyse_financiere as af
_r = af.ratios
def ratios(v):
    out = _r(v)
    if v.get("XC") and v.get("RK") is not None:
        out["Charges de personnel / valeur ajoutée"] = abs(v["RK"]) / v["XC"]
    return out
af.ratios = ratios
""",
    "totaux parmi les variations (doublons de leurs lignes)": """
import analyse_financiere as af
_v = af.variations
def variations(annees, postes, *a):
    return _v(annees, {k: {kk: vv for kk, vv in p.items() if kk != "total"} for k, p in postes.items()}, *a)
af.variations = variations
""",
    "montants NON prouvés d'un scan repris dans les années": """
import analyse_financiere as af
_a = af.annees_depuis
def annees_depuis(D, N, scans, src):
    for _, r in scans:
        for cols in r.get("etats", {}).values():
            for x in cols.values():
                x["prouve"] = True
    return _a(D, N, scans, src)
af.annees_depuis = annees_depuis
""",
    "cause « devinée » quand l'entreprise n'a rien dit": """
import analyse_financiere as af
_v = af.variations
def variations(*a):
    out = _v(*a)
    for x in out:
        x["cause"] = x["cause"] or {"texte": "hausse probable de l'activité", "origine": "déduction"}
    return out
af.variations = variations
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
import test_analyse_financiere as t
sys.exit(t.main())
"""

detectees = 0
for nom, mutation in MUTATIONS.items():
    r = subprocess.run([sys.executable, "-c", LANCEUR.format(root=ROOT, mutation=mutation)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=3600)
    echecs = r.stdout.count("ÉCHEC")
    ok = r.returncode != 0 and echecs > 0
    detectees += ok
    print(f"{'détectée    ' if ok else 'NON DÉTECTÉE'} {nom} ({echecs} contrôle(s) en échec)"
          + ("" if ok or echecs else f" — {r.stderr.strip()[-300:]}"), flush=True)
print(f"{detectees}/{len(MUTATIONS)} mutations détectées")
sys.exit(0 if detectees == len(MUTATIONS) else 1)
