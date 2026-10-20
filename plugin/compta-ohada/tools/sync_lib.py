# -*- coding: utf-8 -*-
"""Synchronise les modules partagés de lib/ vers les skills qui les utilisent.

Chaque skill est zippé SEUL (import Team) : il doit embarquer sa copie. La source unique
reste lib/ ; les copies ne s'éditent jamais.

  python tools/sync_lib.py           copie lib/ -> skills
  python tools/sync_lib.py --check   code 1 si une copie diverge (appelé par package.py)
"""
import filecmp
import os
import shutil
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# module partagé -> skills consommateurs (dossier scripts/)
PARTAGES = {
    "detection_balance.py": ["dsf-syscohada", "revision-comptes-ohada", "fiscalite-guinee-equatoriale"],
    "fiscal_ge.py": ["dsf-syscohada", "fiscalite-guinee-equatoriale"],
    "parametres_fiscaux_ge.json": ["dsf-syscohada", "fiscalite-guinee-equatoriale"],
    "grand_livre.py": ["dsf-syscohada", "fiscalite-guinee-equatoriale"],
    "tf345_ge.py": ["dsf-syscohada", "fiscalite-guinee-equatoriale"],
    "rendu_pdf.py": ["dsf-syscohada", "redaction-comptable-pro"],
}


MARQUE = "compta-ohada/lib/"   # toute copie légitime porte cette mention (docstring / _meta)


def _est_une_copie(path):
    """Un fichier existant n'est écrasé QUE s'il est lui-même une copie de lib/ (porte la MARQUE).
    Incident du 2026-09-28 : un script de skill homonyme d'un module de lib/ a été écrasé."""
    try:
        with open(path, encoding="utf-8") as f:
            return MARQUE in f.read(4000)
    except (OSError, UnicodeDecodeError):
        return False


def main(check):
    ecarts = 0
    for mod, skills in PARTAGES.items():
        src = os.path.join(ROOT, "lib", mod)
        if not _est_une_copie(src):
            print(f"  [REFUS] lib/{mod} ne porte pas la mention « {MARQUE} » : ajouter la marque de source unique.")
            return 1
        for s in skills:
            dst = os.path.join(ROOT, "skills", s, "scripts", mod)
            if os.path.exists(dst) and not _est_une_copie(dst):
                print(f"  [COLLISION] skills/{s}/scripts/{mod} existe et N'EST PAS une copie de lib/ : "
                      "renommer l'un des deux. Rien n'est écrasé.")
                return 1
            same = os.path.exists(dst) and filecmp.cmp(src, dst, shallow=False)
            if check:
                if not same:
                    print(f"  [DIVERGENCE] skills/{s}/scripts/{mod} ≠ lib/{mod} — lancer tools/sync_lib.py")
                    ecarts += 1
            elif not same:
                shutil.copyfile(src, dst)
                print(f"  copié : lib/{mod} -> skills/{s}/scripts/{mod}")
    if check and not ecarts:
        print("  modules partagés : copies conformes à lib/")
    return 1 if ecarts else 0


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
