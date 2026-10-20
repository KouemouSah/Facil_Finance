# -*- coding: utf-8 -*-
"""Serveur MCP « facil-def » : la DEF de Guinée équatoriale depuis un dossier de travail local.

Outils :
  dossier_travail      crée / retrouve Documents\\Facil-DEF\\<Entité>\\<Exercice> et dit quoi y déposer
  lister_dossiers      entités et exercices existants
  generer_def          génère automatiquement une version (PROJET), consolide les questions
  questions_ouvertes   questions à poser (obligatoires d'abord), avec impact et choix permis
  enregistrer_reponse  enregistre une réponse (contrôlée) ; régénérer ensuite
  valider_version      version définitive, seulement si aucune question obligatoire n'est ouverte
  ouvrir_formulaire    formulaire web local : répondre, régénérer, valider sans passer par la conversation
CONFIDENTIALITÉ : chaque sortie passe par la passerelle (confidentialite.py) — noms pseudonymisés, montants masqués,
chemins relatifs, contrôle final en échec fermé, journal local de tout ce qui est transmis ; chaque entrée est rendue
à ses valeurs réelles. Fonctionne dans Claude Code (plugin, .mcp.json) et Claude Desktop (extension).
"""
import contextlib
import functools
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ICI), "skills", "dsf-syscohada", "scripts"))
sys.path.insert(0, ICI)

from mcp.server.fastmcp import FastMCP  # noqa: E402

if os.environ.get("FACIL_DIAG_PILE"):       # diagnostic d'un blocage : pile de tous les fils écrite chaque minute
    import faulthandler
    faulthandler.dump_traceback_later(60, repeat=True, file=open(os.environ["FACIL_DIAG_PILE"], "w"))

import confidentialite as conf  # noqa: E402
import espace_def as ed  # noqa: E402

mcp = FastMCP("facil-def", instructions=(
    "Production de la DEF (Declaración Estadística y Fiscal, Guinée équatoriale) depuis un dossier de travail local. "
    "Pour TOUTE demande de DEF / DSF, utiliser ces outils, dans cet ordre : dossier_travail -> l'utilisateur dépose ses "
    "fichiers dans 01_sources -> generer_def (automatique, version PROJET) -> questions_ouvertes (poser les "
    "obligatoires, groupées, avec leur impact ; au-delà de quelques questions, proposer ouvrir_formulaire) -> "
    "enregistrer_reponse -> generer_def -> valider_version (sur demande explicite, avec le nom du valideur). "
    "Ne jamais inventer une réponse à une question obligatoire. "
    "MODE « PRÉPARER ET VALIDER » (« prépare et valide la DSF 2025 de X, validée par Y ») : le déroulé reste le même — "
    "dossier_travail, puis l'utilisateur dépose ses fichiers dans 01_sources ; rien ne se génère avant le dépôt. "
    "Ensuite generer_def : son résultat porte questions_a_poser et pret_a_valider. S'il reste des questions, les poser "
    "TOUTES dans UN SEUL message, enregistrer chaque réponse donnée, régénérer. Quand pret_a_valider est vrai, appeler "
    "valider_version avec le nom donné par l'utilisateur : la demande d'autorisation de l'outil est son clic de "
    "confirmation. Sans nom de valideur, le demander. "
    "DEF PRÉCÉDENTE SCANNÉE (PDF) : elle est lue SUR LE POSTE, en arrière-plan (environ 10 s par page) ; le résultat "
    "de generer_def porte lecture_scan (en cours, lue, échec). Pendant la lecture, dire à l'utilisateur d'attendre "
    "puis régénérer. Les montants lus que les formules n'ont pas prouvés (questions scan.*) se confirment dans le "
    "FORMULAIRE local (ouvrir_formulaire) : les montants étant masqués dans la conversation, ne jamais les "
    "demander ni les deviner ici. "
    "CONFIDENTIALITÉ : les sorties sont pseudonymisées sur le poste — ENTITE-A, TIERS-001, IDENT-002… désignent des "
    "noms réels que l'utilisateur connaît (et voit en clair dans le formulaire local) ; « [montant] » remplace un "
    "montant. Réutiliser ces pseudonymes tels quels dans les appels (entité, identifiants de question) : le serveur les "
    "rend à leur valeur réelle. Ne jamais chercher à lire les fichiers du dossier Facil-DEF ni à deviner un montant ; "
    "pour voir un montant, l'utilisateur ouvre le formulaire ou les classeurs sur son poste."))


def _silencieux(f, *a, **k):
    """Le canal MCP est la sortie standard : tout affichage d'un module de calcul part sur la sortie d'erreur."""
    with contextlib.redirect_stdout(sys.stderr):
        return f(*a, **k)


def _passerelle():
    p = conf.Passerelle(ed.racine_defaut())
    p.apprendre_racine()
    return p


def protege(f):
    """Entrées rendues à leurs valeurs réelles ; sortie filtrée, contrôlée (échec fermé) et journalisée."""
    @functools.wraps(f)
    def enveloppe(*a, **k):
        P = _passerelle()
        k = {n: (P.entree(v) if n in ("entite", "id") else v) for n, v in k.items()}
        res = f(*a, **k)
        P = _passerelle()                         # ce que l'outil vient d'écrire (réponse d'identité…) est appris
        return P.sortie(f.__name__, res)
    return enveloppe


def _dossier(entite, exercice):
    return _silencieux(ed.init, None, entite, int(exercice))


@mcp.tool()
@protege
def dossier_travail(entite: str, exercice: int) -> dict:
    """Crée (ou retrouve) le dossier de travail de l'entité pour l'exercice, et liste les fichiers déjà déposés
    avec le rôle reconnu (balance, grand livre, DEF de référence, logo)."""
    d = _dossier(entite, exercice)
    inv = _silencieux(ed.inventaire, d, entite)
    return {"dossier": d, "deposer_dans": os.path.join(d, "01_sources"),
            "attendus": "balance (obligatoire), grand livre, DEF de l'exercice précédent si elle existe (.xlsx : "
                        "comparatifs N-1 et identité de sa page de garde), fiche entité (facultative), logo de l'entité",
            "deposes": [{"fichier": x["fichier"], "role": x["role"]} for x in inv]}


@mcp.tool()
@protege
def lister_dossiers() -> list:
    """Entités et exercices présents dans le dossier Facil-DEF, avec la dernière version et son statut."""
    racine = ed.racine_defaut()
    out = []
    if os.path.isdir(racine):
        for e in sorted(os.listdir(racine)):
            for ex in sorted(os.listdir(os.path.join(racine, e))) if os.path.isdir(os.path.join(racine, e)) else []:
                m = ed.lire_json(os.path.join(racine, e, ex, "manifeste.json"), {})
                if not m:
                    continue
                v = (m.get("versions") or [{}])[-1]
                out.append({"entite": m.get("entite", e), "exercice": ex, "derniere_version": v.get("version"),
                            "statut": v.get("statut"), "questions_obligatoires_ouvertes": v.get("questions_obligatoires_ouvertes")})
    return out


@mcp.tool()
@protege
def generer_def(entite: str, exercice: int, pdf: bool = True) -> dict:
    """Génère automatiquement une nouvelle version PROJET de la DEF (classeurs FR/ES, rapports PDF, annexe balance,
    rapport de contrôle), réinjecte les réponses déjà données et consolide les questions. Peut prendre une minute."""
    d = _dossier(entite, exercice)
    res = _silencieux(ed.generer, d, pdf=pdf)
    if res.get("statut") == "projet":
        # mode « préparer et valider » : le LOT de questions restantes arrive avec la version, à poser en une fois
        res["questions_a_poser"] = _ouvertes(d, False)
        res["pret_a_valider"] = not res["questions_a_poser"]
    return res


def _ouvertes(d, facultatives):
    qs = ed.lire_json(os.path.join(d, "04_questions", "questions.json"), [])
    rep = ed.lire_json(os.path.join(d, "04_questions", "reponses.json"), {})
    out = []
    for q in qs:
        r = rep.get(q["id"], q.get("reponse"))
        if r in (None, "") and (q["obligatoire"] or facultatives):
            out.append({k: q.get(k) for k in ("id", "categorie", "question", "type", "options", "obligatoire", "impact", "contexte", "defaut")})
    return out


@mcp.tool()
@protege
def questions_ouvertes(entite: str, exercice: int, facultatives: bool = False) -> list:
    """Questions à poser à l'utilisateur : obligatoires sans réponse (et facultatives si demandé), avec catégorie,
    type, choix permis et impact. À poser groupées par catégorie."""
    return _ouvertes(_dossier(entite, exercice), facultatives)


@mcp.tool()
@protege
def enregistrer_reponse(entite: str, exercice: int, id: str, valeur: str) -> dict:
    """Enregistre la réponse de l'utilisateur à une question (valeur contrôlée : hors des choix permis, refus).
    L'identifiant peut contenir un pseudonyme (ex. tf5nif.TIERS-003) : il est rendu à sa valeur réelle.
    Appeler ensuite generer_def pour la réinjecter dans les classeurs et les PDF."""
    d = _dossier(entite, exercice)
    try:
        return _silencieux(ed.repondre, d, id, valeur, canal="conversation")
    except SystemExit as e:
        return {"refuse": str(e)}


@mcp.tool()
@protege
def valider_version(entite: str, exercice: int, par: str) -> dict:
    """Produit la version DÉFINITIVE (sans filigrane), seulement si aucune question obligatoire n'est ouverte et si
    01_sources n'a pas changé depuis la dernière version (sinon : refus motivé, régénérer d'abord). Le rapport de
    contrôle liste chaque réponse appliquée, son origine, sa date, et qui a validé. À n'appeler que sur demande
    explicite de l'utilisateur, avec le nom de la personne qui valide — jamais un nom deviné."""
    d = _dossier(entite, exercice)
    return _silencieux(ed.valider, d, par)


@mcp.tool()
@protege
def ouvrir_formulaire(entite: str, exercice: int, navigateur: bool = True) -> dict:
    """Ouvre le formulaire web LOCAL (127.0.0.1) où l'utilisateur voit les noms et montants en clair, répond aux
    questions, régénère et valide — sans que rien passe par la conversation. Le lien d'accès (jeton) n'est PAS
    transmis : le navigateur s'ouvre directement, et un raccourci « formulaire.url » est posé dans 04_questions.
    Fermeture après 15 min d'inactivité ou 12 h ; rappeler cet outil rend un nouveau lien."""
    import formulaire
    d = _dossier(entite, exercice)
    url = _silencieux(formulaire.demarrer, d, navigateur)
    raccourci = os.path.join(d, "04_questions", "formulaire.url")
    with open(raccourci, "w", encoding="utf-8") as f:           # raccourci Internet Windows : double-clic = ouverture
        f.write(f"[InternetShortcut]\nURL={url}\n")
    return {"ouvert_dans_le_navigateur": bool(navigateur), "raccourci_local": raccourci,
            "fermeture": "15 min d'inactivité ou 12 h au plus"}


def precharger():
    """Bibliothèques NATIVES chargées AVANT que le serveur ne lise son entrée. Sous Windows, une DLL chargée pendant
    qu'un autre fil attend sur le tube d'entrée peut se figer à son initialisation (constaté le 19/10/2026 : numpy,
    importé par openpyxl, bloquait generer_def indéfiniment — 0 % de CPU — depuis son ajout au runtime pour l'OCR)."""
    for nom in ("numpy", "openpyxl", "pymupdf"):
        try:
            __import__(nom)
        except ImportError:
            pass


if __name__ == "__main__":
    precharger()
    mcp.run()
