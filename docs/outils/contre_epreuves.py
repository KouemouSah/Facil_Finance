"""Contre-épreuves des gardes de construire_site.py : chaque mutation doit faire échouer la garde.
À rejouer après toute modification de construire_site.py ou calendrier.py (fourni par doc-projet)."""
import importlib.util
import sys
import tempfile
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
spec = importlib.util.spec_from_file_location("cs", ICI / "construire_site.py")
cs = importlib.util.module_from_spec(spec); spec.loader.exec_module(cs)
import calendrier as cal  # noqa: E402
import yaml  # noqa: E402

resultats = []


def doit_echouer(nom, fn, erreur=None):
    erreur = erreur or cs.EchecConstruction
    try:
        fn(); resultats.append((nom, "NON DÉTECTÉ"))
    except erreur:
        resultats.append((nom, "détecté"))


def temoin(nom, fn, erreur=None):
    erreur = erreur or cs.EchecConstruction
    try:
        fn(); resultats.append((nom, "passe"))
    except erreur as e:
        resultats.append((nom, f"ÉCHEC {e}"))


pages = cs.assembler()
cs.injecter_etat()  # même ordre que la construction : la garde voit les pages complètes
page_test = next(p for p in pages if p != "index.md") if len(pages) > 1 else "index.md"

# 1-2. Confidentialité : un mot présent dans le site (le nom du produit) ajouté à une liste de test ; liste absente.
produit = str(cs.CONFIG.get("produit", "Projet"))
tmp = Path(tempfile.mkdtemp()) / "noms.txt"; tmp.write_text(f"# test\n{produit}\n", encoding="utf-8")
orig = cs.NOMS_CONFIDENTIELS
cs.NOMS_CONFIDENTIELS = tmp; doit_echouer("nom confidentiel présent", lambda: cs.garde_confidentialite(pages))
cs.NOMS_CONFIDENTIELS = tmp.with_name("absent.txt"); doit_echouer("liste déclarée mais absente (échec fermé)", lambda: cs.garde_confidentialite(pages))
cs.NOMS_CONFIDENTIELS = orig
temoin("témoin : confidentialité du projet", lambda: cs.garde_confidentialite(pages))

# 3-4. Parité menu / pages.
(cs.STAGING / "orpheline.md").write_text("# x", encoding="utf-8")
doit_echouer("page hors menu", lambda: cs.garde_parite_menu(pages + ["orpheline.md"]))
doit_echouer("entrée de menu sans page", lambda: cs.garde_parite_menu([p for p in pages if p != "index.md"]))

# 5-6. Hors ligne : ressource distante injectée dans une page construite.
cible = cs.SITE / "index.html"
if cible.exists():
    sauve = cible.read_text(encoding="utf-8")
    cible.write_text(sauve.replace("</head>", '<script src="https://exemple.invalid/x.js"></script></head>'), encoding="utf-8")
    doit_echouer("script distant", cs.garde_hors_ligne)
    cible.write_text(sauve.replace("</head>", '<link rel="stylesheet" href="//exemple.invalid/x.css"></head>'), encoding="utf-8")
    doit_echouer("style distant sans protocole", cs.garde_hors_ligne)
    cible.write_text(sauve, encoding="utf-8")
    temoin("témoin : site réel hors ligne", cs.garde_hors_ligne)

# 7. Icône absente.
pages = cs.assembler()
(cs.STAGING / page_test).write_text("# x :lucide-icone-qui-n-existe-pas:", encoding="utf-8")
doit_echouer("icône absente", lambda: cs.incruster_icones(pages))

# 8. Indicateur inconnu dans l'accueil.
pages = cs.assembler()
accueil = cs.STAGING / "index.md"
accueil.write_text(accueil.read_text(encoding="utf-8") + "\n{{NB_INCONNU}}\n", encoding="utf-8")
doit_echouer("indicateur inconnu", cs.injecter_indicateurs)

# 9. Gantt : « : » dans un libellé.
doit_echouer("Gantt : « : » dans un libellé", lambda: cs.verifier_gantt("t", "gantt\n    dateFormat YYYY-MM-DD\n    section A\n    A : B :a1, 2026-01-05, 2026-01-09"))
temoin("témoin : Gantt correct", lambda: cs.verifier_gantt("t", "gantt\n    dateFormat YYYY-MM-DD\n    section A\n    A — B :a1, 2026-01-05, 2026-01-09"))

# 10-15. Calendrier (si le projet en a un).
src = cs.RACINE / "plans" / "calendrier.yml"
doit_echouer("date de planning écrite à la main", lambda: cal.verifier_dates_en_dur({"plans/roadmap.md": "Livraison le 30/11 au plus tard"}), cal.ErreurCalendrier)
doit_echouer("trimestre écrit à la main", lambda: cal.verifier_dates_en_dur({"tdr.md": "Disponible au T2 2027"}), cal.ErreurCalendrier)
temoin("témoin : ligne de statut datée", lambda: cal.verifier_dates_en_dur({"tdr.md": '<span class="statut">x</span> · 15/10/2026'}), cal.ErreurCalendrier)
if src.exists():
    def avec(modif):
        d = yaml.safe_load(src.read_text(encoding="utf-8")); modif(d)
        p = Path(tempfile.mkdtemp()) / "cal.yml"; p.write_text(yaml.safe_dump(d, allow_unicode=True), encoding="utf-8")
        return lambda: cal.Calendrier(p)
    doit_echouer("marque inconnue", lambda: cal.Calendrier(src).appliquer("{{cal:jalon:inexistant}}"), cal.ErreurCalendrier)
    doit_echouer("tâche hors de son étape", avec(lambda d: d["etapes"][0]["taches"][0].update(fin="2099-01-01")), cal.ErreurCalendrier)
    doit_echouer("« : » dans une tâche", avec(lambda d: d["etapes"][0]["taches"][0].update(libelle="A : B")), cal.ErreurCalendrier)

for n, r in resultats:
    print(f"{r:14} {n}")
ok = all(r in ("détecté", "passe") for _, r in resultats)
print("RÉSULTAT :", f"{sum(r in ('détecté', 'passe') for _, r in resultats)}/{len(resultats)}")
sys.exit(0 if ok else 1)
