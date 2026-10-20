# -*- coding: utf-8 -*-
"""Hook PreToolUse du plugin (Claude Code) : Claude ne LIT ni n'ÉCRIT le dossier de travail Facil-DEF par ses outils
généraux (Read, Grep, Glob, Bash, PowerShell, Notebook*, Edit, Write). Les données comptables n'y sont accessibles
qu'au travers du serveur MCP facil-def, dont chaque sortie passe par la passerelle de confidentialité.

Protocole des hooks : l'appel arrive en JSON sur l'entrée standard ; le code 2 REFUSE l'outil (le message d'erreur
standard est rendu à Claude) ; le code 0 laisse faire. Entrée illisible : refus par prudence (échec fermé).
Bibliothèque standard seulement : le hook doit tourner partout où le plugin tourne.
Limite DÉCLARÉE : une commande qui construit le chemin par morceaux (variables, concaténations) peut échapper à
l'analyse textuelle ; le hook ferme la voie ordinaire, pas une intention délibérée de contournement.
"""
import json
import os
import re
import sys

CHAMPS_CHEMIN = ("file_path", "path", "notebook_path", "pattern_path")
CHAMPS_TEXTE = ("command", "pattern", "glob")


def documents():
    if os.name == "nt":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders") as k:
                return os.path.expandvars(winreg.QueryValueEx(k, "Personal")[0])
        except OSError:
            pass
    return os.path.join(os.path.expanduser("~"), "Documents")


def racine_configuree(valeur):
    """Même règle que espace_def.racine_configuree : une variable non remplacée (« ${…} »)
    ou une valeur vide n'est jamais un chemin."""
    v = os.path.expandvars((valeur or "").strip().strip('"'))
    if not v or re.search(r"\$\{|%[A-Za-z_]\w*%", v):  # vide, ou variable restée non remplacée
        return None
    return os.path.abspath(os.path.expanduser(v))


def est_synchronise(dossier):
    """Vrai si le dossier est synchronisé vers le cloud (OneDrive) : les données comptables du client
    y quitteraient le poste, contrairement à ce que l'extension promet. Constaté le 17/10/2026."""
    d = os.path.normcase(os.path.abspath(dossier))
    for var in ("OneDrive", "OneDriveConsumer", "OneDriveCommercial"):
        v = os.environ.get(var)
        if v and d.startswith(os.path.normcase(os.path.abspath(v))):
            return True
    return "onedrive" in d


def dossier_par_defaut(documents_):
    r"""Documents\Facil-DEF, SAUF si Documents est synchronisé dans le cloud : alors %USERPROFILE%\Facil-DEF
    (local, non synchronisé). L'utilisateur reste libre de choisir un autre dossier dans le réglage."""
    if est_synchronise(documents_):
        return os.path.join(os.path.expanduser("~"), "Facil-DEF")
    return os.path.join(documents_, "Facil-DEF")


def racine():
    return racine_configuree(os.environ.get("FACIL_DEF_RACINE")) or dossier_par_defaut(documents())


def norme(p, cwd):
    p = os.path.expandvars(os.path.expanduser(str(p)))
    if not os.path.isabs(p):
        p = os.path.join(cwd or os.getcwd(), p)
    return os.path.normcase(os.path.realpath(os.path.normpath(p)))


def refuse(motif):
    sys.stderr.write(f"Accès refusé par le plugin Facil DEF : {motif} Le dossier Facil-DEF contient des données "
                     "comptables confidentielles ; passez par les outils facil-def (dossier_travail, generer_def, "
                     "questions_ouvertes, ouvrir_formulaire…), dont les sorties sont pseudonymisées.\n")
    sys.exit(2)


def main():
    try:
        appel = json.loads(sys.stdin.read())
        entree = appel.get("tool_input") or {}
    except (ValueError, AttributeError):
        refuse("appel illisible.")
    cwd = appel.get("cwd")
    R = norme(racine(), None)
    for k in CHAMPS_CHEMIN:
        v = entree.get(k)
        if isinstance(v, str) and v.strip():
            p = norme(v, cwd)
            if p == R or p.startswith(R + os.sep):
                refuse(f"{appel.get('tool_name', 'outil')} sur le dossier de travail.")
    texte = " ".join(str(entree.get(k) or "") for k in CHAMPS_TEXTE)
    if texte:
        t = os.path.normcase(os.path.expandvars(texte))
        if re.search(r"facil[-_ ]?def", t, re.I) or os.path.normcase(racine()) in t or R in t:
            refuse(f"{appel.get('tool_name', 'outil')} visant le dossier de travail.")
    sys.exit(0)


if __name__ == "__main__":
    main()
