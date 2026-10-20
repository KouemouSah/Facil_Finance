# -*- coding: utf-8 -*-
"""Falsification de tests/test_fiscal_ge.py : une mutation par règle fiscale protégée,
appliquée à une COPIE du plugin ; la garde doit échouer sur un contrôle métier.
Lancer : python tests/falsification_fiscal.py   -> code 0 si toutes sont détectées.
"""
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join("lib", "fiscal_ge.py")
J = os.path.join("lib", "parametres_fiscaux_ge.json")
MUT = [
    ("taux d'IS faux (30 %)", J, '"is_taux": {"valeur": 0.25', '"is_taux": {"valeur": 0.30'),
    ("arrondi art. 75.1 oublié", F, "b = math.floor(imposable / pas) * pas if arr_base else imposable",
     "b = imposable"),
    ("CMF ignorée quand elle dépasse l'IS", F, "du = max(is_brut, cmf)", "du = is_brut"),
    ("délai de report des déficits faux (6 ans)", J, '"deficit_report_exercices": {"valeur": 5', '"deficit_report_exercices": {"valeur": 6'),
    ("« don » reconnu dans « abandon »", F, r're.search(r"\b" + re.escape(k)', r're.search("" + re.escape(k)'),
    ("écart d'interprétation passé sous silence", F, "    if abs(is_brut - is_strict) >= 0.01:",
     "    if False:"),
    ("profil ignoré (défauts forcés)", F, "interp[k] = decisions.get(k, pi.get(k, v[\"defaut\"]))",
     "interp[k] = v[\"defaut\"]"),
    ("questions d'entrée jamais posées", F,
     '        if faits.get(k) is not None or spec.get("portee", "tf2") != portee:\n            continue',
     "        continue"),
    ("propositions appliquées sans acceptation", F,
     'pris = acc == "toutes" and p["type"] == "reintegration" or p["compte"] in (acc if isinstance(acc, list) else [])',
     'pris = p["type"] != "information"'),
    ("versement de janvier compté pour l'exercice (art. 80.2 ignoré)", F,
     'elif date[5:7] == "01" and n not in annees', 'elif False and n not in annees'),
    ("IS passé en charge non détecté (structure des pièces ignorée)", F,
     "    out += is_en_charge_par_piece(gl_lignes, params, pieces_exclues, deja={p[\"compte\"] for p in out})\n", ""),
    ("majorations d'IS non déduites du principal", F,
     "        principal = round(min(credit_is - maj,", "        principal = round(min(credit_is,"),
    ("versements enregistrés dans la balance ignorés", F,
     "        if a.startswith(racines) and md:\n", "        if False:\n"),
]


def main():
    aveugles = 0
    for name, rel, a, b in MUT:
        d = tempfile.mkdtemp()
        dst = os.path.join(d, "compta-ohada")
        shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns("dist", "datas", "__pycache__"))
        path = os.path.join(dst, rel)
        src = open(path, encoding="utf-8").read()
        assert src.count(a) == 1, f"motif introuvable ou multiple : {name}"
        open(path, "w", encoding="utf-8").write(src.replace(a, b))
        cp = subprocess.run([sys.executable, os.path.join(dst, "tests", "test_fiscal_ge.py")],
                            capture_output=True, text=True, encoding="utf-8")
        detectee = cp.returncode != 0 and "ÉCHEC" in cp.stdout
        aveugles += not detectee
        bilan = next((l.strip() for l in cp.stdout.splitlines() if "conformes" in l), cp.stderr.strip()[-100:])
        print(f"  {name:45s} {'détectée' if detectee else '!! NON DÉTECTÉE'}   {bilan}")
        shutil.rmtree(d, ignore_errors=True)
    sys.exit(1 if aveugles else 0)


if __name__ == "__main__":
    main()
