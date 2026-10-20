"""Assemble le site GitHub Pages : portail (tableau de bord du projet), documentation, manuels.

  python outils/construire_portail.py --sortie _site

  _site/index.html          portail : indicateurs, avancement des jalons, accès à la documentation et aux manuels
  _site/documentation/      site MkDocs déjà construit par docs/outils/construire_site.py (docs/site)
  _site/manuels/            PDF du manuel, de la présentation et du flyer de Facil DEF (FR et ES)
  _site/donnees/tableau.json  données du tableau de bord

Les données viennent de l'API GitHub (jetons GITHUB_TOKEN et GITHUB_REPOSITORY en CI). Sans jeton, le portail se
construit quand même et le dit : il n'invente aucun chiffre.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import shutil
import sys
import urllib.request
from pathlib import Path

DEPOT = Path(__file__).resolve().parents[1]
ICONES = DEPOT / "docs" / "theme" / ".icons" / "lucide"
CONFIG_DOC = DEPOT / "docs" / "doc-projet.yml"

MANUELS = [  # (langue, titre, chemin relatif à manuel/livrable, icône)
    ("fr", "Manuel d'utilisation", "Manuel-utilisation-Facil-DEF.pdf", "book-open"),
    ("fr", "Présentation commerciale", "Presentation-commerciale-Facil-DEF.pdf", "presentation"),
    ("fr", "Flyer", "Flyer-Facil-DEF.pdf", "file-text"),
    ("es", "Manual de uso", "es/Manual-de-uso-Facil-DEF.pdf", "book-open"),
    ("es", "Presentación comercial", "es/Presentacion-comercial-Facil-DEF.pdf", "presentation"),
    ("es", "Folleto", "es/Folleto-Facil-DEF.pdf", "file-text"),
]


def icone(nom: str, classe: str = "ic") -> str:
    p = ICONES / f"{nom}.svg"
    if not p.exists():
        raise SystemExit(f"icône Lucide absente : {p} (ajouter le SVG à docs/theme/.icons/lucide)")
    corps = re.search(r"<svg[^>]*>(.*)</svg>", p.read_text(encoding="utf-8"), re.S).group(1)
    corps = re.sub(r"<!--.*?-->", "", corps, flags=re.S).strip()
    return (f'<svg class="{classe}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{corps}</svg>')


def api(chemin: str) -> list | dict | None:
    jeton, depot = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPOSITORY")
    if not (jeton and depot):
        return None
    req = urllib.request.Request(f"https://api.github.com/repos/{depot}/{chemin}",
                                 headers={"Authorization": f"Bearer {jeton}", "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except OSError as e:
        print(f"API GitHub indisponible pour {chemin} : {e}")
        return None


def donnees() -> dict:
    jalons = api("milestones?state=all&sort=due_on&direction=asc&per_page=50")
    ouverts = api("issues?state=open&per_page=100")
    fermes = api("issues?state=closed&per_page=100&sort=updated")
    if jalons is None:
        return {"disponible": False}
    tickets = [i for i in (ouverts or []) + (fermes or []) if "pull_request" not in i]
    return {
        "disponible": True,
        "jalons": [{"titre": j["title"], "echeance": (j.get("due_on") or "")[:10], "ouverts": j["open_issues"],
                    "fermes": j["closed_issues"], "etat": j["state"], "url": j["html_url"],
                    "description": (j.get("description") or "").split("\n")[0]} for j in jalons],
        "tickets_ouverts": sum(1 for i in tickets if i["state"] == "open"),
        "tickets_fermes": sum(1 for i in tickets if i["state"] == "closed"),
        "recents": [{"numero": i["number"], "titre": i["title"], "etat": i["state"], "url": i["html_url"]}
                    for i in sorted(tickets, key=lambda i: i["updated_at"], reverse=True)[:8]],
    }


def config_doc() -> dict:
    import yaml
    return yaml.safe_load(CONFIG_DOC.read_text(encoding="utf-8"))


def rendre(d: dict, cfg: dict, depot: str, manuels: list) -> str:
    e = html.escape
    c = cfg.get("couleurs", {})
    construit = dt.datetime.now(dt.timezone.utc).strftime("%d/%m/%Y %H:%M UTC")
    url_depot = f"https://github.com/{depot}" if depot else "#"

    if d.get("disponible"):
        total = d["tickets_ouverts"] + d["tickets_fermes"]
        part = round(100 * d["tickets_fermes"] / total) if total else 0
        jalons_actifs = [j for j in d["jalons"] if j["etat"] == "open"]
        indicateurs = [("list-checks", f"{d['tickets_ouverts']}", "tâches ouvertes"),
                       ("circle-check", f"{d['tickets_fermes']}", "tâches fermées"),
                       ("gauge", f"{part} %", "avancement global"),
                       ("milestone", f"{len(jalons_actifs)}", "jalons en cours")]
        lignes = []
        for j in d["jalons"]:
            n = j["ouverts"] + j["fermes"]
            p = round(100 * j["fermes"] / n) if n else 0
            lignes.append(
                f'<li class="jalon"><a href="{e(j["url"])}"><span class="jalon-titre">{e(j["titre"])}</span>'
                f'<span class="jalon-meta">{e(j["echeance"] and "échéance " + j["echeance"][8:10] + "/" + j["echeance"][5:7] + "/" + j["echeance"][:4])}'
                f' · {j["fermes"]}/{n} fermées</span></a>'
                f'<div class="barre" role="progressbar" aria-valuenow="{p}" aria-valuemin="0" aria-valuemax="100" '
                f'aria-label="{e(j["titre"])}"><span style="width:{p}%"></span></div></li>')
        bloc_jalons = "<ul class=\"jalons\">" + "".join(lignes) + "</ul>" if lignes else "<p>Aucun jalon.</p>"
        recents = "".join(f'<li><a href="{e(t["url"])}">{icone("circle-dot" if t["etat"] == "open" else "circle-check", "ic petit " + t["etat"])}'
                          f'<span>#{t["numero"]} {e(t["titre"])}</span></a></li>' for t in d["recents"])
    else:
        indicateurs = []
        bloc_jalons = ('<p class="note">Données du projet indisponibles dans cette construction (pas de jeton GitHub). '
                       f'Les jalons et les tâches se lisent sur <a href="{url_depot}/milestones">GitHub</a>.</p>')
        recents = ""

    cartes_ind = "".join(f'<div class="kpi">{icone(i)}<strong>{e(v)}</strong><span>{e(l)}</span></div>'
                         for i, v, l in indicateurs)
    cartes_man = "".join(
        f'<a class="carte" href="manuels/{e(p)}">{icone(i)}<span class="carte-titre">{e(t)}</span>'
        f'<span class="carte-texte">PDF · {"français" if lg == "fr" else "español"}</span></a>'
        for lg, t, p, i in manuels)

    acces = [
        ("documentation/index.html", "book-open", "Documentation projet", "Cadrage, exigences, architecture, décisions, plans de sprint."),
        ("documentation/architecture.html", "network", "Architecture cible", "Vues C4, déploiement, flux de la balance à la liasse."),
        ("documentation/plans/sprints.html", "calendar-range", "Plan de sprints", "Sprint en cours, tâches reportées, reprise."),
        ("documentation/facil-def.html", "file-check", "Facil DEF", "L'extension livrée : DSF de Guinée équatoriale, OCR, analyse financière."),
        (f"{url_depot}", "code-xml", "Code source", "Moteur, packs pays, extension, CI/CD."),
        (f"{url_depot}/issues", "list-checks", "Tâches", "Tickets par sprint, exigences, définition de « fait »."),
    ]
    cartes_acces = "".join(f'<a class="carte" href="{e(h)}">{icone(i)}<span class="carte-titre">{e(t)}</span>'
                           f'<span class="carte-texte">{e(x)}</span></a>' for h, i, t, x in acces)

    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Facil Finance</title>
<meta name="description" content="{e(cfg.get('resume', ''))}">
<link rel="icon" href="documentation/assets/icon.png">
<style>
:root {{ --vert:{c.get('principale', '#448403')}; --vert-fonce:{c.get('nuit', '#2e5a02')}; --encre:{c.get('encre', '#1f3c01')};
  --texte:#1f2a14; --doux:{c.get('texte_doux', '#66705c')}; --fond:#ffffff; --panneau:{c.get('panneau', '#f6f8f4')};
  --bordure:{c.get('bordure', '#e3e7df')}; --voile:{c.get('voile', '#f0f7e9')}; --rayon:12px; }}
@media (prefers-color-scheme: dark) {{ :root {{ --texte:{c.get('encre_claire', '#ebf3e2')}; --encre:{c.get('encre_claire', '#ebf3e2')};
  --doux:{c.get('texte_doux_sombre', '#adb6a5')}; --fond:{c.get('fond_sombre', '#12160d')}; --panneau:{c.get('panneau_sombre', '#171c12')};
  --bordure:{c.get('bordure_sombre', '#30362b')}; --voile:{c.get('voile_sombre', '#29351d')}; --vert:#9ccb5e; }} }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font:clamp(15px,1.4vw,16px)/1.55 Inter,"Segoe UI",system-ui,sans-serif; color:var(--texte); background:var(--fond); }}
a {{ color:inherit; }}
.ic {{ width:22px; height:22px; flex:none; color:var(--vert); }}
.ic.petit {{ width:16px; height:16px; }} .ic.closed {{ color:var(--doux); }}
header.bandeau {{ background:linear-gradient(135deg,#0e3416,#105c2c 60%,#1d6b31); color:#fff; padding:40px 16px 56px; }}
.cadre {{ max-width:1200px; margin:0 auto; padding:0 16px; }}
.bandeau img {{ height:40px; }}
.bandeau h1 {{ font-size:clamp(28px,4vw,44px); line-height:1.1; margin:18px 0 8px; }}
.bandeau p {{ max-width:760px; color:#dce8d2; margin:0; }}
.etiquette {{ display:inline-block; margin-top:16px; padding:4px 12px; border:1px solid rgba(156,203,94,.6); border-radius:999px;
  color:#9ccb5e; font-size:12px; letter-spacing:.12em; text-transform:uppercase; }}
main {{ margin-top:-28px; }}
section {{ margin:0 0 36px; }}
h2 {{ font-size:20px; margin:0 0 14px; color:var(--encre); }}
.kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:14px; }}
.kpi {{ background:var(--fond); border:1px solid var(--bordure); border-radius:var(--rayon); padding:16px; display:grid; gap:4px;
  box-shadow:0 6px 18px rgba(14,52,22,.08); }}
.kpi strong {{ font-size:28px; color:var(--encre); }} .kpi span {{ color:var(--doux); font-size:14px; }}
.grille {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:14px; }}
.carte {{ display:grid; gap:6px; padding:18px; min-height:44px; border:1px solid var(--bordure); border-radius:var(--rayon);
  background:var(--panneau); text-decoration:none; transition:border-color .15s, transform .15s; }}
.carte:hover, .carte:focus-visible {{ border-color:var(--vert); transform:translateY(-2px); }}
.carte-titre {{ font-weight:600; color:var(--encre); }} .carte-texte {{ color:var(--doux); font-size:14px; }}
.deux {{ display:grid; grid-template-columns:2fr 1fr; gap:24px; }}
@media (max-width:820px) {{ .deux {{ grid-template-columns:1fr; }} }}
.jalons {{ list-style:none; margin:0; padding:0; display:grid; gap:12px; }}
.jalon a {{ display:flex; justify-content:space-between; gap:12px; text-decoration:none; flex-wrap:wrap; }}
.jalon-titre {{ font-weight:600; }} .jalon-meta {{ color:var(--doux); font-size:14px; }}
.barre {{ height:8px; border-radius:999px; background:var(--voile); overflow:hidden; margin-top:6px; }}
.barre span {{ display:block; height:100%; background:var(--vert); }}
.recents {{ list-style:none; margin:0; padding:0; display:grid; gap:8px; }}
.recents a {{ display:flex; gap:8px; align-items:flex-start; text-decoration:none; }}
.note {{ color:var(--doux); background:var(--panneau); border:1px solid var(--bordure); border-radius:var(--rayon); padding:14px; }}
a:focus-visible {{ outline:3px solid var(--vert); outline-offset:2px; border-radius:6px; }}
footer {{ border-top:1px solid var(--bordure); color:var(--doux); font-size:14px; padding:20px 0 32px; }}
footer .cadre {{ display:flex; flex-wrap:wrap; gap:8px 24px; justify-content:space-between; }}
</style>
</head>
<body>
<header class="bandeau">
  <div class="cadre">
    <img src="documentation/assets/logo-blanc.png" alt="Facil">
    <h1>Facil Finance</h1>
    <p>{e(cfg.get('resume', ''))} De la balance à la liasse fiscale validée, calculée sur le poste ou le serveur du client, avec une trace de chaque chiffre.</p>
    <span class="etiquette">SYSCOHADA révisé · 17 États de l'OHADA · V1 le 30/11/2026</span>
  </div>
</header>
<main class="cadre">
  <section aria-label="Indicateurs"><div class="kpis">{cartes_ind}</div></section>
  <section><h2>Accès</h2><div class="grille">{cartes_acces}</div></section>
  <section class="deux">
    <div><h2>Avancement des jalons</h2>{bloc_jalons}</div>
    <div><h2>Tâches récentes</h2><ul class="recents">{recents or '<li class="note">—</li>'}</ul></div>
  </section>
  <section><h2>Facil DEF — manuels et supports</h2><div class="grille">{cartes_man}</div></section>
</main>
<footer>
  <div class="cadre">
    <span>© <span id="annee">{dt.date.today().year}</span> Emac SAH · Facil - AI Solutions Architect</span>
    <span>Construit le {construit}</span>
    <span><a href="{url_depot}/blob/develop/LICENSE">Licence propriétaire</a> · <a href="{url_depot}/blob/develop/SECURITY.md">Sécurité</a></span>
  </div>
</footer>
<script>document.getElementById("annee").textContent = new Date().getFullYear();</script>
</body>
</html>
"""


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--sortie", type=Path, default=DEPOT / "_site")
    p.add_argument("--site-doc", type=Path, default=DEPOT / "docs" / "site")
    a = p.parse_args()

    if not (a.site_doc / "index.html").exists():
        print(f"site de documentation absent ({a.site_doc}) : lancer d'abord docs/outils/construire_site.py")
        return 1
    if a.sortie.exists():
        shutil.rmtree(a.sortie)
    shutil.copytree(a.site_doc, a.sortie / "documentation")

    manuels = []
    for lg, titre, rel, ic in MANUELS:
        src = DEPOT / "manuel" / "livrable" / rel
        if src.exists():
            (a.sortie / "manuels" / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, a.sortie / "manuels" / rel)
            manuels.append((lg, titre, rel, ic))
        else:
            print(f"manuel absent, non publié : {rel}")

    d = donnees()
    (a.sortie / "donnees").mkdir(parents=True, exist_ok=True)
    (a.sortie / "donnees" / "tableau.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    page = rendre(d, config_doc(), os.environ.get("GITHUB_REPOSITORY", "KouemouSah/Facil_Finance"), manuels)
    (a.sortie / "index.html").write_text(page, encoding="utf-8")
    (a.sortie / ".nojekyll").write_text("", encoding="utf-8")
    print(f"portail construit : {a.sortie} ({len(manuels)} manuels, données GitHub "
          f"{'incluses' if d.get('disponible') else 'INDISPONIBLES'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
