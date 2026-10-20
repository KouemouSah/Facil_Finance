# -*- coding: utf-8 -*-
"""Valide et empaquette le plugin compta-ohada.
Exécuter : python tools/package.py
- Valide plugin.json et le frontmatter de chaque SKILL.md (name == dossier, description présente).
- Régénère les templates (via build_templates).
- Produit dist/compta-ohada.zip (plugin complet) + dist/skills/<skill>.zip (import Team).
"""
import os
import re
import json
import shutil
import sys
import zipfile
import subprocess

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
EXCLUDE_DIRS = {"dist", "__pycache__"}
EXCLUDE_EXT = {".pyc"}


def fail(msg):
    print("  [ERREUR]", msg)
    return 1


def _liste_interdits():
    """La liste nomme les clients : elle vit HORS du plugin et hors du dépôt public. Ordre de recherche :
    FACIL_NOMS_CONFIDENTIELS, puis documentation/analyse/reference/ dans un dossier parent (C:\\DSF\\documentation sur le
    poste de l'éditeur, que le plugin soit atteint par C:\\DSF\\compta-ohada ou par le dépôt Facil_Finance)."""
    if os.environ.get("FACIL_NOMS_CONFIDENTIELS"):
        return os.environ["FACIL_NOMS_CONFIDENTIELS"]
    d = os.path.realpath(ROOT)
    while True:
        c = os.path.join(d, "documentation", "analyse", "reference", "noms_confidentiels.txt")
        if os.path.exists(c) or os.path.dirname(d) == d:
            return c
        d = os.path.dirname(d)


LISTE_INTERDITS = _liste_interdits()


def _plat(s):
    import unicodedata
    return unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()


def noms_interdits(liste_path=LISTE_INTERDITS, racine=ROOT):
    """Garde de confidentialité : aucune valeur de la liste d'exclusion (tenue HORS du plugin, puisqu'elle nomme le
    client) dans les fichiers texte ni dans les chaînes des classeurs du plugin. Retourne (fuites, liste | None)."""
    if not os.path.exists(liste_path):
        return [], None
    liste = [_plat(l.strip()) for l in open(liste_path, encoding="utf-8") if l.strip() and not l.startswith("#")]
    fuites = []
    for base, dirs, files in os.walk(racine):
        # runtime/ : Python officiel et roues tierces, reconstruits par l'outil (aucune donnée écrite par nous)
        dirs[:] = [d for d in dirs if d not in ("dist", "__pycache__", ".git", "runtime")]
        for f in files:
            p = os.path.join(base, f)
            if f.endswith((".py", ".md", ".json", ".txt", ".html", ".css", ".js", ".toml", ".yml", ".yaml")):
                texte = _plat(open(p, encoding="utf-8", errors="replace").read())
            elif f.endswith((".xlsx", ".xlsm")):
                import openpyxl
                wb = openpyxl.load_workbook(p)
                texte = _plat(" ".join([w.title for w in wb.worksheets] + [str(c.value) for w in wb.worksheets
                                        for row in w.iter_rows() for c in row if isinstance(c.value, str)]))
            else:
                continue
            fuites += [f"{os.path.relpath(p, racine)} : « {x} »" for x in liste if x and x in texte]
    return fuites, liste


def validate():
    issues = 0
    # plugin.json
    manifest = os.path.join(ROOT, ".claude-plugin", "plugin.json")
    try:
        with open(manifest, encoding="utf-8") as f:
            m = json.load(f)
        assert m.get("name") and m.get("version") and m.get("description")
        print(f"  plugin.json OK — {m['name']} v{m['version']}")
    except Exception as e:
        issues += fail(f"plugin.json invalide : {e}")

    # skills
    sk_dir = os.path.join(ROOT, "skills")
    skills = sorted(d for d in os.listdir(sk_dir) if os.path.isdir(os.path.join(sk_dir, d)))
    for s in skills:
        p = os.path.join(sk_dir, s, "SKILL.md")
        if not os.path.exists(p):
            issues += fail(f"{s} : SKILL.md manquant"); continue
        txt = open(p, encoding="utf-8").read()
        mobj = re.match(r"^---\s*\n(.*?)\n---", txt, re.S)
        if not mobj:
            issues += fail(f"{s} : frontmatter absent"); continue
        fm = mobj.group(1)
        name = re.search(r"^name:\s*(\S+)", fm, re.M)
        desc = re.search(r"^description:\s*", fm, re.M)
        if not name or name.group(1) != s:
            issues += fail(f"{s} : 'name' absent ou != dossier ({name.group(1) if name else '—'})")
        if not desc:
            issues += fail(f"{s} : 'description' absente")
    print(f"  {len(skills)} skills contrôlés")

    # inventaire
    cmds = [c for c in os.listdir(os.path.join(ROOT, "commands")) if c.endswith(".md")]
    tpls = []
    for root, _, files in os.walk(sk_dir):
        tpls += [f for f in files if f.endswith(".xlsx")]
    print(f"  {len(cmds)} commandes, {len(tpls)} templates Excel")
    return issues, skills


def _zip_dir(zf, src_dir, arc_prefix):
    for root, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if os.path.splitext(f)[1] in EXCLUDE_EXT:
                continue
            full = os.path.join(root, f)
            arc = os.path.join(arc_prefix, os.path.relpath(full, src_dir))
            zf.write(full, arc)


def package(skills):
    os.makedirs(os.path.join(DIST, "skills"), exist_ok=True)
    # plugin complet
    full = os.path.join(DIST, "compta-ohada.zip")
    with zipfile.ZipFile(full, "w", zipfile.ZIP_DEFLATED) as zf:
        _zip_dir(zf, ROOT, "compta-ohada")
    print(f"  → {os.path.relpath(full, ROOT)} ({os.path.getsize(full)//1024} Ko)")
    # skills individuels (import Team)
    for s in skills:
        dest = os.path.join(DIST, "skills", s + ".zip")
        with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
            _zip_dir(zf, os.path.join(ROOT, "skills", s), s)
    print(f"  → dist/skills/*.zip ({len(skills)} skills)")


if __name__ == "__main__":
    print("== Régénération des templates ==")
    # subprocess.run avec une liste d'arguments (pas de shell) : pas d'injection possible.
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build_templates.py")],
                   check=True, stdout=subprocess.DEVNULL)
    print("== Modules partagés (lib/ -> skills) ==")
    if subprocess.run([sys.executable, os.path.join(ROOT, "tools", "sync_lib.py"), "--check"]).returncode:
        print("\nREFUSÉ : copie divergente. Lancer `python tools/sync_lib.py`, puis relancer.")
        sys.exit(1)
    print("== Documentation dérivée ==")
    if subprocess.run([sys.executable, os.path.join(ROOT, "tools", "gen_mapping_md.py"), "--check"]).returncode:
        print("\nREFUSÉ : mapping-comptes-dsf.md diverge du JSON. Lancer `python tools/gen_mapping_md.py`.")
        sys.exit(1)
    print("== Runtime Python embarqué (rien à installer chez l'utilisateur) ==")
    if subprocess.run([sys.executable, os.path.join(ROOT, "tools", "construire_runtime.py")]).returncode:
        print("\nREFUSÉ : runtime embarqué non construit ; le plugin exigerait un Python installé.")
        sys.exit(1)
    print("== Confidentialité : aucune donnée d'un client dans le plugin ==")
    fuites, liste = noms_interdits()
    if liste is None:
        print(f"  liste d'exclusion ABSENTE ({LISTE_INTERDITS}) : contrôle NON JOUÉ")
    else:
        print(f"  {len(liste)} valeurs interdites contrôlées dans les fichiers texte et les classeurs du plugin")
    if fuites:
        for f in fuites[:15]:
            print("   ", f)
        print("\nREFUSÉ : le plugin contient des données d'un client ; rien n'est empaqueté.")
        sys.exit(1)
    print("== Tests ==")
    for t in sorted(os.listdir(os.path.join(ROOT, "tests"))):
        if t.startswith("test_") and t.endswith(".py"):
            cp = subprocess.run([sys.executable, os.path.join(ROOT, "tests", t)],
                                capture_output=True, text=True, encoding="utf-8")
            bilan = next((l for l in cp.stdout.splitlines() if "conformes" in l), "")
            print(f"  {t} : {'OK' if cp.returncode == 0 else 'ÉCHEC'} {bilan.strip()}")
            if cp.returncode:
                print(cp.stdout[-1500:])
                print("\nREFUSÉ : un test échoue ; rien n'est empaqueté.")
                sys.exit(1)
    print("== Validation ==")
    issues, skills = validate()
    claude = shutil.which("claude.cmd") or shutil.which("claude")
    if claude:                                            # validateur OFFICIEL de Claude Code (plugin + place de marché)
        cp = subprocess.run([claude, "plugin", "validate", "--strict", ROOT], capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
        print(f"  validation officielle Claude Code (--strict) : {'OK' if cp.returncode == 0 else 'ÉCHEC'}")
        if cp.returncode:
            print(cp.stdout[-1500:] + cp.stderr[-500:])
            issues += 1
    else:
        print("  validation officielle Claude Code : NON JOUÉE (CLI « claude » absente)")
    print("== Packaging ==")
    package(skills)
    print("== Extension Claude Desktop ==")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "construire_extension.py")])
    if r.returncode == 1:
        issues += 1
    if issues:
        print(f"\nTERMINÉ AVEC {issues} PROBLÈME(S).")
        sys.exit(1)
    print("\nOK — plugin validé et empaqueté.")
