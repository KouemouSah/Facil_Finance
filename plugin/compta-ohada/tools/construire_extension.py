# -*- coding: utf-8 -*-
"""Construit l'extension Claude Desktop (MCP Bundle, .mcpb) du serveur « facil-def ».

Assemble dans dist/extension/ le strict nécessaire au serveur (manifeste, icône, serveur/, moteur de la DEF :
skills/dsf-syscohada/scripts et references), fait valider le manifeste par l'outil officiel puis l'empaquette :
    dist/facil-def.mcpb
Prérequis : Node.js (npx) pour l'outil officiel @anthropic-ai/mcpb. Sans lui : rien n'est produit, c'est signalé.
Usage : python tools/construire_extension.py
"""
import json
import os
import shutil
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
STAGE = os.path.join(DIST, "extension")
IGNORER = shutil.ignore_patterns("__pycache__", "*.pyc", "*.tmp", "~$*")


def npx():
    return shutil.which("npx.cmd") or shutil.which("npx")


def main():
    man = json.load(open(os.path.join(ROOT, "extension", "manifest.json"), encoding="utf-8"))
    plugin = json.load(open(os.path.join(ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8"))
    if man["version"] != plugin["version"]:
        print(f"ÉCHEC : version de l'extension ({man['version']}) ≠ version du plugin ({plugin['version']})")
        return 1
    n = npx()
    if not n:
        print("NON PRODUIT : Node.js (npx) absent — l'outil officiel mcpb est requis pour valider et empaqueter.")
        return 2
    shutil.rmtree(STAGE, ignore_errors=True)
    os.makedirs(STAGE)
    shutil.copy(os.path.join(ROOT, "extension", "manifest.json"), STAGE)
    shutil.copy(os.path.join(ROOT, "extension", "icon.png"), STAGE)
    shutil.copytree(os.path.join(ROOT, "serveur"), os.path.join(STAGE, "serveur"), ignore=IGNORER)
    rt = os.path.join(ROOT, "runtime")                  # Python embarqué : l'utilisateur n'installe rien
    if not os.path.exists(os.path.join(rt, "python.exe")):
        print("ÉCHEC : runtime embarqué absent — python tools/construire_runtime.py")
        return 1
    shutil.copytree(rt, os.path.join(STAGE, "runtime"), ignore=IGNORER)
    for sous in ("scripts", "references", "templates"):   # templates : le gabarit officiel (DEF sans DEF déposée)
        shutil.copytree(os.path.join(ROOT, "skills", "dsf-syscohada", sous),
                        os.path.join(STAGE, "skills", "dsf-syscohada", sous), ignore=IGNORER)
    v = subprocess.run([n, "-y", "@anthropic-ai/mcpb", "validate", os.path.join(STAGE, "manifest.json")],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if "passes" not in v.stdout + v.stderr:
        print("ÉCHEC validation du manifeste :\n" + v.stdout + v.stderr)
        return 1
    sortie = os.path.join(DIST, "facil-def.mcpb")
    if os.path.exists(sortie):
        os.remove(sortie)
    p = subprocess.run([n, "-y", "@anthropic-ai/mcpb", "pack", STAGE, sortie], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if not os.path.exists(sortie):
        print("ÉCHEC empaquetage :\n" + p.stdout + p.stderr)
        return 1
    print(f"  → {os.path.relpath(sortie, ROOT)} ({os.path.getsize(sortie) // 1024} Ko) — extension Claude Desktop validée")
    return 0


if __name__ == "__main__":
    sys.exit(main())
