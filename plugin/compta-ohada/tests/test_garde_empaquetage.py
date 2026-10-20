# -*- coding: utf-8 -*-
"""Garde de la GARDE D'EMPAQUETAGE (tools/package.py : noms_interdits) : un nom de client glissé dans un fichier texte
ou dans un classeur du plugin est trouvé ; accents et casse n'y changent rien ; dist/ est ignoré ; le plugin réel est
propre (si la liste d'exclusion, tenue hors plugin, est présente sur ce poste).
Lancer : python tests/test_garde_empaquetage.py     (code 0 = conforme)
"""
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import package  # noqa: E402

ok = []


def check(nom, cond, detail=""):
    ok.append(bool(cond))
    print(f"  {'OK   ' if cond else 'ÉCHEC'} {nom}" + ("" if cond else f"  — {detail}"))


def main():
    d = tempfile.mkdtemp()
    liste = os.path.join(d, "liste.txt")
    open(liste, "w", encoding="utf-8").write("# commentaire\nCLIENT PILOTE\nNIF-9999X\n")
    plug = os.path.join(d, "plugin")
    os.makedirs(os.path.join(plug, "skills"))
    os.makedirs(os.path.join(plug, "dist"))
    open(os.path.join(plug, "skills", "a.md"), "w", encoding="utf-8").write("Validé sur le dossier pilote.\n")
    f, l = package.noms_interdits(liste, plug)
    check("plugin propre : aucune fuite, liste lue (commentaires ignorés)", f == [] and len(l) == 2, (f, l))
    open(os.path.join(plug, "skills", "b.py"), "w", encoding="utf-8").write("# exemple : Client Pilote\n")
    open(os.path.join(plug, "dist", "c.md"), "w", encoding="utf-8").write("CLIENT PILOTE\n")
    f, _ = package.noms_interdits(liste, plug)
    check("nom dans un .py trouvé (casse ignorée), dist/ ignoré", len(f) == 1 and "b.py" in f[0], f)
    import openpyxl
    wb = openpyxl.Workbook()
    wb.active["C5"] = "nif-9999x"
    wb.save(os.path.join(plug, "skills", "gabarit.xlsx"))
    f, _ = package.noms_interdits(liste, plug)
    check("valeur dans un CLASSEUR trouvée", any("gabarit.xlsx" in x for x in f), f)
    f, l = package.noms_interdits(os.path.join(d, "absente.txt"), plug)
    check("liste absente : contrôle déclaré NON JOUÉ (None), pas « propre »", l is None)
    if os.path.exists(package.LISTE_INTERDITS):
        f, l = package.noms_interdits()
        check(f"plugin réel propre ({len(l)} valeurs interdites contrôlées)", f == [], f[:5])
    else:
        print("  (liste d'exclusion absente de ce poste : contrôle du plugin réel non joué)")
    print(f"\n{sum(ok)}/{len(ok)} contrôles conformes")
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
