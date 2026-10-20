# -*- coding: utf-8 -*-
"""Falsification de tests/test_def_modele.py : une mutation par règle protégée du générateur « modèle officiel »,
appliquée à une COPIE du plugin ; la garde doit échouer sur un contrôle métier (pas planter).
Lancer : python tests/falsification_def_modele.py   -> code 0 si toutes sont détectées.
"""
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = os.path.join("skills", "dsf-syscohada", "scripts", "def_modele.py")
MUT = [
    ("montant N du modèle recopié au lieu d'être calculé", G,
     "        val = self.valeur(mws, t, r, c, role, ex, ref_cols, v)\n",
     "        val = v\n"),
    ("identité du modèle laissée en page de garde", G,
     "                if t == \"page garde\":\n                    out.value = None\n",
     "                if t == \"page garde\":\n                    out.value = v\n"),
    ("N-1 lu dans la mauvaise colonne du modèle", G,
     "        g = mws.cell(r, c - 1).value\n        return g if num(g) else None",
     "        return v"),
    ("sens de présentation ignoré (passif en négatif)", G,
     "    return round(-tot if ref[0] == \"R\" else tot, 2)",
     "    return round(-tot, 2)"),
    ("total : une ligne oubliée", G,
     "            cands[\"lignes\"] = [(x, 1) for x in data_rows]",
     "            cands[\"lignes\"] = [(x, 1) for x in data_rows[:-1]]"),
    ("libellé « = … » laissé en formule", G,
     "                out.data_type = \"s\"\n",
     "                pass\n"),
    ("version espagnole non traduite", G,
     "        return self.i18n.get(lang, {}).get(s.strip(), s)",
     "        return s"),
    ("modèle pro : lignes nulles non masquées", G,
     "                    ws.row_dimensions[r].hidden = True\n",
     "                    pass\n"),
    ("brouillon hors zone d'impression recopié", G,           # zone utilisée au lieu de la zone d'impression
     "        pa = mws.print_area\n", "        pa = None\n"),
    ("logo posé sur toutes les feuilles du classeur", G,
     'if t == "page garde" and self.a.logo and os.path.exists(self.a.logo):', "if self.a.logo and os.path.exists(self.a.logo):"),
    ("rapport : second tableau d'une note perdu (commentaire ignoré)", os.path.join("skills", "dsf-syscohada", "scripts", "rapport_def.py"),
     "        if est_commentaire(ws, r, c0, c1):\n            courant[3] = r - 1", "        if False:\n            courant[3] = r - 1"),
    ("logo absent de la couverture du rapport", os.path.join("skills", "dsf-syscohada", "scripts", "def_ge.py"),
     "    if logo and os.path.exists(logo):", "    if False:"),
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
        cp = subprocess.run([sys.executable, os.path.join(dst, "tests", "test_def_modele.py")],
                            capture_output=True, text=True, encoding="utf-8")
        detectee = cp.returncode != 0 and "ÉCHEC" in cp.stdout
        aveugles += not detectee
        bilan = next((l.strip() for l in cp.stdout.splitlines() if "conformes" in l), "PLANTAGE : " + cp.stderr.strip()[-90:])
        print(f"  {name:52s} {'détectée' if detectee else '!! NON DÉTECTÉE'}   {bilan}")
        shutil.rmtree(d, ignore_errors=True)
    sys.exit(1 if aveugles else 0)


if __name__ == "__main__":
    main()
