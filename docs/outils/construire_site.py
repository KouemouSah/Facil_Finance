"""Construit le site de documentation du projet (hors ligne, ouvrable par double-clic).
Fichier fourni par le plugin doc-projet ; les paramètres du projet sont dans doc-projet.yml.

Étapes, chacune bloquante :
  1. assemble les sources dans .outils/staging : les pages de la documentation et les documents
     de référence tenus ailleurs (déclarés dans doc-projet.yml). On COPIE au moment de la
     construction ; les sources ne sont jamais dupliquées dans le dépôt ;
  2. garde de confidentialité : aucun nom confidentiel (liste tenue HORS du produit) ne doit
     paraître dans le site. Si le projet déclare une liste, son absence fait échouer (échec fermé) ;
  3. garde de parité : chaque page assemblée figure au menu, et chaque entrée du menu existe ;
  4. construction MkDocs en mode strict (lien cassé = échec) ;
  5. garde hors ligne : aucune page ne charge de script, de style ni d'image depuis Internet.

Usage :  .outils\\venv\\Scripts\\python.exe outils\\construire_site.py [--ouvrir]
Le raccourci « Ouvrir la documentation.cmd » enchaîne construction et ouverture.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # outils/calendrier.py

import yaml

RACINE = Path(__file__).resolve().parents[1]          # dossier de la documentation
DEPOT = RACINE.parent                                  # racine du dépôt du projet
OUTILS = RACINE / ".outils"
STAGING = OUTILS / "staging"
SITE = RACINE / "site"

# Paramètres du projet (écrits par /doc-projet à l'initialisation, modifiables à la main).
CONFIG = yaml.safe_load((RACINE / "doc-projet.yml").read_text(encoding="utf-8"))

# Documents de référence tenus hors de la documentation : publiés en lecture seule dans « Sources ».
SOURCES_EXTERNES = {rel: (RACINE / s["chemin"]).resolve() for rel, s in (CONFIG.get("sources_externes") or {}).items()}
ICONES_SOURCES = {rel: s.get("icone", "lucide/file") for rel, s in (CONFIG.get("sources_externes") or {}).items()}
_conf = CONFIG.get("confidentialite") or {}
NOMS_CONFIDENTIELS = (RACINE / _conf["liste"]).resolve() if _conf.get("liste") else None
EXCLUS = {".outils", "site", "outils", "theme", "mkdocs.yml", "doc-projet.yml", "Ouvrir la documentation.cmd"}


class EchecConstruction(Exception):
    pass


def assembler() -> list[str]:
    if STAGING.exists():
        shutil.rmtree(STAGING)
    STAGING.mkdir(parents=True)
    for element in RACINE.iterdir():
        if element.name in EXCLUS or element.name.startswith(".") or element.suffix in (".cmd", ".sh"):
            continue
        cible = STAGING / element.name
        if element.is_dir():
            # Les données sources (calendrier.yml…) servent à la construction, pas au site.
            shutil.copytree(element, cible, ignore=shutil.ignore_patterns("*.yml"))
        else:
            shutil.copy2(element, cible)
    for rel, src in SOURCES_EXTERNES.items():
        if not src.exists():
            raise EchecConstruction(f"source de référence absente : {src}")
        cible = STAGING / rel
        cible.parent.mkdir(parents=True, exist_ok=True)
        icone = ICONES_SOURCES.get(rel, "lucide/file")
        entete = (f"---\nicon: {icone}\n---\n\n"
                  f"!!! info \"Document source\"\n    Copie en lecture seule de `{src.relative_to(DEPOT)}`, "
                  f"reprise à chaque construction. Toute correction se fait dans l'original.\n\n")
        cible.write_text(entete + src.read_text(encoding="utf-8"), encoding="utf-8")
    return sorted(p.relative_to(STAGING).as_posix() for p in STAGING.rglob("*.md"))


def appliquer_calendrier(pages: list[str]) -> None:
    """Résout les marques {{cal:…}} depuis plans/calendrier.yml et refuse toute date de planning
    écrite à la main dans les pages planifiantes."""
    import calendrier as cal  # module voisin (outils/)
    source = RACINE / "plans" / "calendrier.yml"
    if not source.exists():
        return  # projet encore au cadrage : pas de calendrier
    try:
        c = cal.Calendrier(source, CONFIG.get("produit", "Projet"), CONFIG.get("couleurs"))
        planifiantes = {}
        for rel in pages:
            chemin = STAGING / rel
            texte = chemin.read_text(encoding="utf-8")
            if rel in cal.PAGES_PLANIFIANTES:
                planifiantes[rel] = texte
            if "{{cal:" in texte:
                chemin.write_text(c.appliquer(texte), encoding="utf-8")
        cal.verifier_dates_en_dur(planifiantes)
    except cal.ErreurCalendrier as e:
        raise EchecConstruction(f"calendrier — {e}") from None


def compter_indicateurs() -> dict[str, int]:
    """Les chiffres de la page d'accueil se DÉRIVENT des documents, jamais recopiés à la main."""
    # Chaque indicateur n'existe que si son document source existe ; un indicateur demandé par
    # l'accueil sans source fait échouer la construction (« indicateur inconnu »).
    sources = {
        "NB_EXIGENCES": ("prd.md", lambda t: len(set(re.findall(r"\bEX-[A-Z]+-\d+\b", t)))),
        "NB_RISQUES": ("registre-risques.md", lambda t: len(re.findall(r"^\| R\d+ \|", t, re.MULTILINE))),
        "NB_PAYS": ("plans/couverture-pays.md", lambda t: len(re.findall(r"^\| \d+ \| ", t, re.MULTILINE))),
        "NB_VERSIONS": ("plans/feuille-de-route.md", lambda t: len(re.findall(r"^\| \*\*V\d", t, re.MULTILINE))),
    }
    valeurs = {cle: f((RACINE / rel).read_text(encoding="utf-8"))
               for cle, (rel, f) in sources.items() if (RACINE / rel).exists()}
    if (RACINE / "adr").is_dir():
        valeurs["NB_ADR"] = len(list((RACINE / "adr").glob("[0-9][0-9][0-9][0-9]-*.md")))
    return valeurs


LIBELLES_ETAT = {"fait": "fait", "en_cours": "**en cours**", "a_venir": "à venir"}


def injecter_etat() -> None:
    """L'accueil affiche le produit et l'avancement des phases, lus dans doc-projet.yml."""
    accueil = STAGING / "index.md"
    texte = accueil.read_text(encoding="utf-8")
    phases = CONFIG.get("phases") or {}
    texte = texte.replace("{{PRODUIT}}", str(CONFIG.get("produit", ""))).replace("{{RESUME}}", str(CONFIG.get("resume", "")))
    texte = texte.replace("{{PHASE}}", str(CONFIG.get("phase", 1)))
    for n in range(1, 7):
        texte = texte.replace("{{ETAT_%d}}" % n, LIBELLES_ETAT.get(phases.get(n, "a_venir"), "à venir"))
    accueil.write_text(texte, encoding="utf-8")


def injecter_indicateurs() -> None:
    accueil = STAGING / "index.md"
    texte = accueil.read_text(encoding="utf-8")
    for cle, valeur in compter_indicateurs().items():
        if valeur == 0 and "{{" + cle + "}}" in texte:
            raise EchecConstruction(f"indicateur {cle} nul : le document source a changé de forme")
        texte = texte.replace("{{" + cle + "}}", str(valeur))
    if re.search(r"\{\{NB_[A-Z_]+\}\}", texte):
        raise EchecConstruction("indicateur inconnu dans index.md : " + re.search(r"\{\{NB_[A-Z_]+\}\}", texte).group(0))
    accueil.write_text(texte, encoding="utf-8")


ICONES = RACINE / "theme" / ".icons" / "lucide"


def incruster_icones(pages: list[str]) -> None:
    """:lucide-nom: devient l'icône SVG elle-même, y compris dans les blocs HTML (que l'extension
    emoji ne traite pas). Une icône absente fait échouer la construction."""
    motif = re.compile(r":lucide-([a-z0-9-]+):")
    for rel in pages:
        chemin = STAGING / rel
        texte = chemin.read_text(encoding="utf-8")
        if ":lucide-" not in texte:
            continue

        def svg(m: re.Match) -> str:
            fichier = ICONES / f"{m.group(1)}.svg"
            if not fichier.exists():
                raise EchecConstruction(f"{rel} : icône Lucide absente « {m.group(1)} »")
            contenu = fichier.read_text(encoding="utf-8").replace("<svg ", '<svg aria-hidden="true" ', 1)
            return f'<span class="twemoji">{contenu}</span>'

        chemin.write_text(motif.sub(svg, texte), encoding="utf-8")


def garde_confidentialite(pages: list[str]) -> None:
    if NOMS_CONFIDENTIELS is None:
        if _conf.get("obligatoire"):
            raise EchecConstruction("doc-projet.yml exige une liste de noms confidentiels (confidentialite.liste) : aucune n'est déclarée")
        return  # projet sans données de tiers déclarées : rien à protéger
    if not NOMS_CONFIDENTIELS.exists() and os.environ.get("DOC_CONFIDENTIALITE_DELEGUEE"):
        # Ajout Facil_Finance (dépôt public, CI) : la liste n'existe que sur le poste de l'éditeur. La délégation est
        # NOMMÉE (la garde qui prend le relais), annoncée, et cette garde est exigée juste après sur le site construit.
        print(f"garde nominative déléguée à {os.environ['DOC_CONFIDENTIALITE_DELEGUEE']} (liste absente de ce poste)")
        return
    if not NOMS_CONFIDENTIELS.exists():
        raise EchecConstruction(f"liste des noms confidentiels introuvable ({NOMS_CONFIDENTIELS}) : "
                                "construction refusée (échec fermé)")
    noms = [l.strip() for l in NOMS_CONFIDENTIELS.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.lstrip().startswith("#")]
    motifs = [re.compile(re.escape(n), re.IGNORECASE) for n in noms]
    fuites = []
    for rel in pages:
        texte = (STAGING / rel).read_text(encoding="utf-8")
        for motif in motifs:
            if motif.search(texte):
                fuites.append(f"{rel} : un nom confidentiel ({len(motif.pattern)} caractères)")
    if fuites:
        # Le nom lui-même n'est jamais affiché : le journal de construction peut être partagé.
        raise EchecConstruction("nom de client dans le site :\n  " + "\n  ".join(fuites))


def garde_parite_menu(pages: list[str]) -> None:
    config = (RACINE / "mkdocs.yml").read_text(encoding="utf-8")
    bloc_nav = config.split("\nnav:", 1)[1]
    # Seules les CIBLES comptent : « Libellé: cible.md » ou « - cible.md » en fin de ligne
    # (un libellé comme « Document projet (projet.md) » ne doit pas être pris pour une page).
    au_menu = {m.group(1) for ligne in bloc_nav.splitlines()
               if (m := re.search(r"(?:^\s*-\s*|:\s+)([\w./-]+\.md)\s*$", ligne))}
    assemblees = set(pages)
    hors_menu = sorted(assemblees - au_menu)
    sans_page = sorted(au_menu - assemblees)
    erreurs = [f"page absente du menu : {p}" for p in hors_menu] + \
              [f"entrée de menu sans page : {p}" for p in sans_page]
    if erreurs:
        raise EchecConstruction("menu et pages divergent :\n  " + "\n  ".join(erreurs))


def ecrire_charte() -> None:
    """Couleurs de la charte (doc-projet.yml) → variables CSS lues par extra.css."""
    c = CONFIG.get("couleurs") or {}
    clair = {"--facil-vert": "decor", "--facil-vert-fonce": "principale", "--facil-vert-nuit": "nuit",
             "--facil-vert-clair": "claire", "--facil-vert-voile": "voile", "--facil-vert-pale": "pale",
             "--facil-encre": "encre", "--facil-zebre": "zebre", "--facil-panneau": "panneau",
             "--facil-bordure": "bordure", "--facil-texte-doux": "texte_doux",
             "--facil-fond-sombre": "fond_sombre", "--facil-encre-claire": "encre_claire"}
    sombre = {"--facil-vert-voile": "voile_sombre", "--facil-zebre": "zebre_sombre",
              "--facil-panneau": "panneau_sombre", "--facil-bordure": "bordure_sombre",
              "--facil-texte-doux": "texte_doux_sombre"}
    def bloc(selecteur, table):
        lignes = [f"  {var}: {c[cle]};" for var, cle in table.items() if c.get(cle)]
        return f"{selecteur} {{\n" + "\n".join(lignes) + "\n}\n" if lignes else ""
    css = ("/* Généré depuis doc-projet.yml à chaque construction : ne pas modifier ici. */\n"
           + bloc(":root", clair) + bloc('[data-md-color-scheme="slate"]', sombre))
    (STAGING / "assets" / "charte.css").write_text(css, encoding="utf-8")


def construire() -> None:
    maintenant = dt.datetime.now().strftime("%d/%m/%Y à %H:%M")
    config = (RACINE / "mkdocs.yml").read_text(encoding="utf-8")
    config = config.replace("{{DATE}}", maintenant).replace("{{ANNEE}}", str(dt.date.today().year))
    for cle in ("produit", "sous_titre", "editeur", "version_doc", "langue"):
        config = config.replace("{{" + cle.upper() + "}}", str(CONFIG.get(cle, "")))
    config = config.replace("{{CONFIDENTIEL}}", "true" if CONFIG.get("confidentiel") else "false")
    # Liens du pied de page : seulement vers les pages qui existent (un lien mort fait douter du reste).
    demandes = CONFIG.get("liens_pied") or [{"titre": "Accueil", "page": "index.md"}]
    liens = [{"titre": l["titre"], "page": l["page"].replace(".md", ".html")}
             for l in demandes if (STAGING / l["page"]).exists()]
    config = config.replace("{{LIENS_PIED}}", json.dumps(liens, ensure_ascii=False))
    config = config.replace("docs_dir: .outils/staging", "docs_dir: staging")
    # Marque de version sur nos styles et scripts : un lecteur ne garde jamais l'ancien habillage en cache.
    marque = dt.datetime.now().strftime("%Y%m%d%H%M%S")
    for fichier in ("assets/charte.css", "assets/extra.css", "assets/extra.js"):
        config = config.replace(f"  - {fichier}\n", f"  - {fichier}?v={marque}\n")
    config = config.replace("custom_dir: theme", f"custom_dir: {(RACINE / 'theme').as_posix()}")
    config = config.replace("site_dir: site", f"site_dir: {SITE.as_posix()}")
    genere = OUTILS / "mkdocs.genere.yml"
    genere.write_text(config, encoding="utf-8")
    r = subprocess.run([sys.executable, "-m", "mkdocs", "build", "--strict", "--clean", "-q", "-f", str(genere)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise EchecConstruction("MkDocs (mode strict) :\n" + (r.stderr or r.stdout)[-4000:])


SHIM_DISTANT = "https://unpkg.com/iframe-worker/shim"


def localiser_ressources() -> None:
    """Le module « offline » de Material charge son script de recherche depuis unpkg : on le sert
    depuis assets/ (copie téléchargée une fois, versionnée avec la documentation)."""
    for page in SITE.rglob("*.html"):
        texte = page.read_text(encoding="utf-8")
        if SHIM_DISTANT in texte:
            profondeur = len(page.relative_to(SITE).parts) - 1
            local = "../" * profondeur + "assets/iframe-worker-shim.js"
            page.write_text(texte.replace(SHIM_DISTANT, local), encoding="utf-8")


_DIAGRAMME = re.compile(r'<pre class="mermaid"><code>(.*?)</code></pre>', re.DOTALL)


_MOTS_GANTT = ("gantt", "title", "dateformat", "axisformat", "tickinterval", "excludes", "includes",
               "todaymarker", "section", "%%", "weekday", "displaymode")


def verifier_gantt(page: str, source: str) -> None:
    """Mermaid lit le premier « : » d'une tâche comme séparateur : un deux-points dans le libellé
    casse tout le diagramme, sans erreur à la construction. Chaque tâche a donc exactement un « : »."""
    lignes = [l.strip() for l in source.splitlines() if l.strip()]
    if not lignes or not any(l.lower() == "gantt" for l in lignes):
        return
    for ligne in lignes:
        if ligne.lower().startswith(_MOTS_GANTT):
            continue
        if ligne.count(":") != 1:
            raise EchecConstruction(f"{page} : tâche de Gantt avec {ligne.count(':')} « : » — {ligne[:70]}")


def envelopper_diagrammes() -> int:
    """Chaque diagramme Mermaid devient agrandissable : on garde sa source à côté de lui
    (Material la remplace par un rendu inaccessible au script), et on ajoute un vrai bouton
    « Agrandir » pour le clavier. Le script assets/extra.js ouvre le grand format."""
    total = 0
    for page in SITE.rglob("*.html"):
        texte = page.read_text(encoding="utf-8")
        if '<pre class="mermaid">' not in texte:
            continue

        def remplacer(m: re.Match) -> str:
            source = html.unescape(m.group(1))
            if "</script" in source.lower():
                raise EchecConstruction(f"{page.name} : un diagramme contient « </script »")
            verifier_gantt(page.name, source)
            return (f'<figure class="diagramme">{m.group(0)}'
                    f'<script type="text/plain" class="diagramme__source">{source}</script>'
                    '<figcaption class="diagramme__legende">'
                    '<button type="button" class="diagramme__agrandir">Agrandir le diagramme</button>'
                    '</figcaption></figure>')

        texte, n = _DIAGRAMME.subn(remplacer, texte)
        total += n
        page.write_text(texte, encoding="utf-8")
    return total


def garde_hors_ligne() -> None:
    """Aucun script, style ni police chargé depuis Internet : le site est confidentiel et hors ligne.
    Les liens cliquables vers des sources externes (<a href>) restent permis."""
    motif = re.compile(r"<(?:script|link|img)\b[^>]*\b(?:src|href)=\"(?:https?:)?//", re.IGNORECASE)
    fautifs = sorted(p.relative_to(SITE).as_posix() for p in SITE.rglob("*.html")
                     if motif.search(p.read_text(encoding="utf-8", errors="replace")))
    if fautifs:
        raise EchecConstruction("ressource externe chargée par : " + ", ".join(fautifs[:10]))


def main() -> int:
    try:
        pages = assembler()
        appliquer_calendrier(pages)
        injecter_etat()
        injecter_indicateurs()
        incruster_icones(pages)
        garde_confidentialite(pages)
        garde_parite_menu(pages)
        ecrire_charte()
        construire()
        localiser_ressources()
        diagrammes = envelopper_diagrammes()
        garde_hors_ligne()
    except EchecConstruction as e:
        print(f"ÉCHEC — {e}", file=sys.stderr)
        return 1
    index = SITE / "index.html"
    print(f"Site construit : {len(pages)} pages, {diagrammes} diagrammes agrandissables → {index}")
    if "--ouvrir" in sys.argv:
        webbrowser.open(index.as_uri())
    return 0


if __name__ == "__main__":
    sys.exit(main())
