# -*- coding: utf-8 -*-
"""Falsification de tests/test_confidentialite.py : chaque sabotage de la passerelle ou du hook, appliqué à une COPIE
de serveur/, doit faire échouer la garde.
Lancer : python tests/falsification_confidentialite.py   (code 0 = tous détectés)
"""
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C, H = "confidentialite.py", "garde_lecture.py"
MUT = [
    ("montants non masqués", C, "return MONTANT.sub(lambda m: m.group(0) if _annee(m.group(0)) else MASQUE, s)", "return s"),
    ("noms non remplacés", C, "                    s = re.sub(r\"(?<![A-Za-z0-9])\" + re.escape(forme)", "                    s = s or re.sub(r\"(?<![A-Za-z0-9])\" + re.escape(forme)"),
    ("chemin absolu laissé", C, 's = re.sub(re.escape(self.racine), "<Facil-DEF>", s, flags=re.I)', "s = s"),
    ("contrôle final désactivé (échec ouvert)", C, "        reste = self.fuites(f)\n", "        reste = []\n"),
    ("journal non écrit", C, "        self._journal(outil, f)\n        return f", "        return f"),
    ("tiers du TF5 non appris", C, "                self.coffre.pseudo(q[\"id\"].split(\".\", 1)[1], \"tiers\")", "                pass"),
    ("pseudonyme non rendu en entrée", C, "lambda m: self.t[\"vers_reel\"].get(m.group(0), m.group(0))", "lambda m: m.group(0)"),
    ("pseudonymes instables (coffre non sauvé)", C, "        os.replace(tmp, self.chemin)", "        os.remove(tmp)"),
    ("hook : chemin non normalisé (casse, ..)", H, "    return os.path.normcase(os.path.realpath(os.path.normpath(p)))", "    return p"),
    ("hook : commandes non examinées", H, "    if texte:\n", "    if False:\n"),
    ("hook : entrée illisible acceptée (échec ouvert)", H, "        refuse(\"appel illisible.\")", "        sys.exit(0)"),
    ("hook : refus par code 1 (non bloquant)", H, "    sys.exit(2)", "    sys.exit(1)"),
]


def main():
    aveugles = 0
    for nom, f, a, b in MUT:
        d = tempfile.mkdtemp()
        dst = os.path.join(d, "serveur")
        shutil.copytree(os.path.join(ROOT, "serveur"), dst, ignore=shutil.ignore_patterns("__pycache__"))
        p = os.path.join(dst, f)
        src = open(p, encoding="utf-8").read()
        assert src.count(a) == 1, f"motif introuvable ou multiple : {nom}"
        open(p, "w", encoding="utf-8").write(src.replace(a, b))
        cp = subprocess.run([sys.executable, os.path.join(ROOT, "tests", "test_confidentialite.py")], capture_output=True,
                            text=True, encoding="utf-8", env={**os.environ, "FACIL_SERVEUR": dst}, timeout=300)
        det = cp.returncode != 0
        aveugles += not det
        bilan = next((l.strip() for l in cp.stdout.splitlines() if "conformes" in l), "PLANTAGE : " + cp.stderr.strip()[-80:])
        print(f"  {nom:48s} {'détecté' if det else '!! NON DÉTECTÉ'}   {bilan}")
        shutil.rmtree(d, ignore_errors=True)
    sys.exit(1 if aveugles else 0)


if __name__ == "__main__":
    main()
