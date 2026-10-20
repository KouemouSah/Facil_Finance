"""Garde de confidentialité du dépôt PUBLIC : aucun nom de client, aucune coordonnée, aucun compte bancaire.

Deux contrôles :

1. **Nominatif.** La liste des noms confidentiels ne vit JAMAIS dans le dépôt. Le dépôt ne porte que leurs
   empreintes HMAC-SHA256 (`outils/confidentialite.empreintes`), calculées avec une clé secrète. Sans la clé,
   une empreinte ne permet pas de vérifier une hypothèse (« tel client figure-t-il dans la liste ? »).
   La clé vient de `FACIL_CLE_CONFIDENTIALITE` (secret GitHub en CI) ou de `~/.facil/cle_confidentialite`.
   Le texte est découpé en mots normalisés (minuscules, sans accents) ; chaque suite de mots de la longueur
   d'un nom est hachée et comparée.
2. **Générique.** Adresses de courriel, numéros IBAN et de téléphone, hors liste blanche publique.

Portée : les fichiers suivis par git (texte, et le contenu des .xlsx/.docx/.pptx/.pdf), ou un dossier donné
(site construit).

  garde_confidentialite.py                     contrôle le dépôt
  garde_confidentialite.py --dossier site      contrôle un dossier (site construit)
  garde_confidentialite.py --regenerer LISTE   recalcule les empreintes depuis une liste locale (hors dépôt)
  --exiger-cle                                 échec si la clé manque (CI sur les branches du dépôt)
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import os
import re
import subprocess
import sys
import unicodedata
import zipfile
from pathlib import Path

DEPOT = Path(__file__).resolve().parents[1]
EMPREINTES = DEPOT / "outils" / "confidentialite.empreintes"
CLE_LOCALE = Path.home() / ".facil" / "cle_confidentialite"

# Coordonnées PUBLIQUES de l'éditeur et adresses techniques : elles ont le droit de paraître.
AUTORISES = {"sah@emacsah.com", "emacsah@gmail.com", "noreply@anthropic.com", "noreply@github.com",
             "+33 6 99 33 12 30", "+33699331230"}
COURRIEL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[a-z]{2,}", re.I)
IBAN = re.compile(r"\b[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){3,7}\b")
TELEPHONE = re.compile(r"\+\d{3}[ .]?\d{2,3}[ .]?\d{2,3}[ .]?\d{2,3}")
TEXTE = {".py", ".md", ".json", ".yaml", ".yml", ".txt", ".csv", ".html", ".css", ".js", ".toml", ".cfg",
         ".ini", ".cmd", ".sh", ".ps1", ".mmd", ".svg", ".xml", ".jsonl"}
BUREAUTIQUE = {".xlsx", ".docx", ".pptx"}
# Bibliothèques tierces minifiées : leurs exemples (courriels, numéros) ne sont pas des données.
IGNORES = re.compile(r"(^|/)(mermaid\.min\.js|.*\.min\.js|search_index\.json)$|(^|/)assets/javascripts/")


def normaliser(t: str) -> list[str]:
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.findall(r"[a-z0-9]+", t)


def empreinte(cle: bytes, mots: list[str]) -> str:
    return hmac.new(cle, " ".join(mots).encode(), hashlib.sha256).hexdigest()


def charger_cle() -> bytes | None:
    v = os.environ.get("FACIL_CLE_CONFIDENTIALITE")
    if v:
        return v.strip().encode()
    if CLE_LOCALE.exists():
        return CLE_LOCALE.read_text(encoding="utf-8").strip().encode()
    return None


def charger_empreintes() -> dict[int, set[str]]:
    """{nombre de mots : empreintes}."""
    par_longueur: dict[int, set[str]] = {}
    if EMPREINTES.exists():
        for ligne in EMPREINTES.read_text(encoding="utf-8").splitlines():
            if ligne and not ligne.startswith("#"):
                n, h = ligne.split(":", 1)
                par_longueur.setdefault(int(n), set()).add(h)
    return par_longueur


def contenu(chemin: Path) -> str | None:
    ext = chemin.suffix.lower()
    try:
        if ext in TEXTE:
            return chemin.read_text(encoding="utf-8", errors="ignore")
        if ext in BUREAUTIQUE:
            with zipfile.ZipFile(chemin) as z:
                return "\n".join(z.read(n).decode("utf-8", "ignore") for n in z.namelist() if n.endswith(".xml"))
        if ext == ".pdf":
            import pymupdf  # facultatif : sans lui, les PDF ne sont pas lus (et le rapport le dit)
            return "\n".join(p.get_text() for p in pymupdf.open(chemin))
    except ImportError:
        return None
    except (OSError, zipfile.BadZipFile):
        return None
    return None


def fichiers_du_depot() -> list[Path]:
    sortie = subprocess.run(["git", "ls-files", "-z"], cwd=DEPOT, capture_output=True, check=True).stdout
    return [DEPOT / p for p in sortie.decode("utf-8").split("\0") if p]


def controler(fichiers: list[Path], cle: bytes | None, par_longueur: dict[int, set[str]], base: Path) -> list[str]:
    alertes = []
    for f in fichiers:
        rel = f.relative_to(base).as_posix()
        if IGNORES.search(rel) or not f.is_file():
            continue
        t = contenu(f)
        if t is None:
            continue
        if cle and par_longueur:
            mots = normaliser(t)
            for n, cibles in par_longueur.items():
                if any(empreinte(cle, mots[i:i + n]) in cibles for i in range(len(mots) - n + 1)):
                    alertes.append(f"{rel} : nom confidentiel ({n} mot(s))")
                    break
        for nom, rx in (("courriel", COURRIEL), ("IBAN", IBAN), ("téléphone", TELEPHONE)):
            trouves = [m for m in rx.findall(t) if m not in AUTORISES and m.replace(" ", "") not in AUTORISES]
            if trouves:
                alertes.append(f"{rel} : {len(trouves)} {nom}(s)")
    return alertes


def regenerer(liste: Path, cle: bytes) -> int:
    noms = [l.strip() for l in liste.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    lignes = sorted({f"{len(m)}:{empreinte(cle, m)}" for m in (normaliser(n) for n in noms) if m})
    EMPREINTES.write_text("# Empreintes HMAC-SHA256 des noms confidentiels (la liste et la clé restent hors dépôt).\n"
                          "# Régénérer : python outils/garde_confidentialite.py --regenerer <liste>\n"
                          + "\n".join(lignes) + "\n", encoding="utf-8")
    print(f"{len(lignes)} empreintes écrites dans {EMPREINTES.relative_to(DEPOT)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dossier", type=Path, help="contrôler ce dossier au lieu des fichiers suivis par git")
    p.add_argument("--regenerer", type=Path, metavar="LISTE")
    p.add_argument("--exiger-cle", action="store_true")
    a = p.parse_args(argv)

    cle = charger_cle()
    if a.regenerer:
        if not cle:
            print("clé absente : FACIL_CLE_CONFIDENTIALITE ou ~/.facil/cle_confidentialite")
            return 1
        return regenerer(a.regenerer, cle)

    par_longueur = charger_empreintes()
    if not cle:
        msg = "contrôle NOMINATIF NON JOUÉ : clé absente (seul le contrôle générique s'applique)"
        if a.exiger_cle:
            print("ÉCHEC — " + msg)
            return 1
        print("AVERTISSEMENT — " + msg)
    if a.dossier:
        base = a.dossier.resolve()
        fichiers = [p for p in base.rglob("*") if p.is_file()]
    else:
        base, fichiers = DEPOT, fichiers_du_depot()
    alertes = controler(fichiers, cle, par_longueur, base)
    for x in alertes:
        print("  " + x)
    nb = sum(len(v) for v in par_longueur.values())
    print(f"{len(fichiers)} fichiers contrôlés, {nb} empreintes, {len(alertes)} alerte(s)")
    return 1 if alertes else 0


if __name__ == "__main__":
    sys.exit(main())
