# -*- coding: utf-8 -*-
"""Lanceur du serveur MCP « facil-def » — bibliothèque standard uniquement.

Au premier démarrage, crée un environnement Python ISOLÉ propre au plugin et y installe serveur/requirements.txt :
aucune dépendance n'est installée dans le Python de l'utilisateur (un conflit de versions y casserait ses autres
outils). Réinstalle seulement si requirements.txt change (empreinte). Puis lance le serveur dans cet environnement.

La sortie standard est RÉSERVÉE au protocole MCP : tout message du lanceur va sur la sortie d'erreur ou dans le
journal d'installation.

Usage :
  python lancer.py               démarre le serveur (appelé par Claude via .mcp.json)
  python lancer.py --installer   prépare seulement l'environnement (à faire une fois après installation du plugin)
  python lancer.py --verifier    dit si l'environnement est prêt
"""
import hashlib
import os
import subprocess
import sys
import venv

ICI = os.path.dirname(os.path.abspath(__file__))
REQ = os.path.join(ICI, "requirements.txt")


def base():
    if os.name == "nt":
        return os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "Facil-DEF")
    return os.path.join(os.path.expanduser("~"), ".local", "share", "facil-def")


def dossier_env():
    return os.environ.get("FACIL_DEF_VENV") or os.path.join(base(), "venv")


def python_env():
    d = dossier_env()
    return os.path.join(d, "Scripts", "python.exe") if os.name == "nt" else os.path.join(d, "bin", "python")


def empreinte():
    return hashlib.sha256(open(REQ, "rb").read()).hexdigest()


def pret():
    marque = os.path.join(dossier_env(), "facil_def_requirements.sha256")
    return os.path.exists(python_env()) and os.path.exists(marque) and open(marque).read().strip() == empreinte()


def installer(bavard=False):
    d = dossier_env()
    os.makedirs(os.path.dirname(d), exist_ok=True)
    journal = os.path.join(os.path.dirname(d), "installation.log")
    dire = (lambda m: print(m, file=sys.stderr)) if not bavard else (lambda m: print(m, file=sys.stderr, flush=True))
    if not os.path.exists(python_env()):
        dire(f"Création de l'environnement isolé : {d}")
        venv.EnvBuilder(with_pip=True, clear=False).create(d)
    dire("Installation des dépendances (première fois : 1 à 3 minutes)…")
    with open(journal, "a", encoding="utf-8") as j:
        cp = subprocess.run([python_env(), "-m", "pip", "install", "--disable-pip-version-check", "-r", REQ],
                            stdout=j, stderr=subprocess.STDOUT)
    if cp.returncode != 0:
        dire(f"ÉCHEC de l'installation — voir {journal}")
        return False
    open(os.path.join(d, "facil_def_requirements.sha256"), "w").write(empreinte())
    dire("Environnement prêt.")
    return True


def main():
    if "--verifier" in sys.argv:
        print("pret" if pret() else "a_installer", file=sys.stderr)
        sys.exit(0 if pret() else 1)
    if "--installer" in sys.argv:
        sys.exit(0 if installer(bavard=True) else 1)
    if not pret() and not installer():
        sys.exit(1)
    # le serveur hérite de l'entrée et de la sortie standard : c'est le canal MCP
    sys.exit(subprocess.call([python_env(), os.path.join(ICI, "mcp_def.py")]))


if __name__ == "__main__":
    main()
