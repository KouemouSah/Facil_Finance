# -*- coding: utf-8 -*-
"""Garde du SERVEUR MCP (serveur/mcp_def.py), de bout en bout, par un vrai client MCP (stdio).
Le test tourne dans l'environnement ISOLÉ du plugin (serveur/lancer.py) : s'il est lancé avec un autre Python, il se
relance lui-même dans cet environnement, en le créant au besoin (première fois : 1 à 3 minutes).
Lancer : python tests/test_mcp_def.py     (code 0 = conforme)
"""
import asyncio
import csv
import json
import os
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "serveur"))

try:
    import mcp  # noqa: F401            (runtime embarqué ou environnement isolé : rien à faire)
except ImportError:
    import lancer                        # voie développeur seulement (le runtime embarqué n'a pas « venv »)
    if not lancer.pret() and not lancer.installer():
        print("ÉCHEC environnement isolé non installable")
        sys.exit(1)
    sys.exit(subprocess.call([lancer.python_env(), os.path.abspath(__file__)]))

from mcp import ClientSession, StdioServerParameters  # noqa: E402
from mcp.client.stdio import stdio_client  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "skills", "dsf-syscohada", "scripts"))
import test_def_modele as tdm  # noqa: E402

ok = []


def check(nom, cond, detail=""):
    ok.append(bool(cond))
    print(f"  {'OK   ' if cond else 'ÉCHEC'} {nom}" + ("" if cond else f"  — {detail}"))


def contenu(res, liste=False):
    """Résultat d'un outil. Une LISTE arrive en autant de blocs que d'éléments (un seul bloc si un seul élément) :
    le type attendu est donc dit par l'appelant, jamais deviné."""
    sc = getattr(res, "structuredContent", None)
    if sc:
        v = sc.get("result", sc) if isinstance(sc, dict) and set(sc) == {"result"} else sc
        return v if not liste or isinstance(v, list) else [v]
    morceaux = []
    for c in res.content or []:
        try:
            morceaux.append(json.loads(c.text))
        except ValueError:
            morceaux.append(c.text)
    if liste:
        return morceaux[0] if len(morceaux) == 1 and isinstance(morceaux[0], list) else morceaux
    return morceaux[0] if morceaux else None


async def parcours(racine):
    env = {**os.environ, "FACIL_DEF_RACINE": racine, "FACIL_PDF": "natif"}
    # FACIL_MCP_SERVEUR : jouer le même parcours sur une autre copie du serveur (ex. l'extension .mcpb dépaquetée)
    serveur = os.environ.get("FACIL_MCP_SERVEUR") or os.path.join(ROOT, "serveur", "mcp_def.py")
    print(f"  serveur testé : {serveur}")
    p = StdioServerParameters(command=sys.executable, args=[serveur], env=env)
    async with stdio_client(p) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            outils = {t.name for t in (await s.list_tools()).tools}
            check("7 outils exposés", outils >= {"dossier_travail", "lister_dossiers", "generer_def", "questions_ouvertes",
                                                 "enregistrer_reponse", "valider_version", "ouvrir_formulaire"}, outils)
            args = {"entite": "ENTITE MCP SA", "exercice": 2025}
            d = contenu(await s.call_tool("dossier_travail", args))
            sys.path.insert(0, os.path.join(ROOT, "serveur"))
            import confidentialite                                     # le test, lui, est SUR le poste : il a le coffre
            reel = lambda p: (confidentialite.Coffre(racine).reel(p).replace("<Facil-DEF>", racine)   # noqa: E731
                              .replace("ENTITE MCP SA", "ENTITE_MCP_SA"))          # nom affiché -> nom de dossier
            check("dossier créé sous la racine configurée, chemin transmis RELATIF", d["dossier"].startswith("<Facil-DEF>")
                  and os.path.isdir(reel(d["dossier"])) and d["deposes"] == [], d)
            check("entité PSEUDONYMISÉE dans la sortie (mode stricte)", "ENTITE MCP" not in json.dumps(d)
                  and "ENTITE-A" in json.dumps(d), d)
            src = reel(d["deposer_dans"])
            with open(os.path.join(src, "balance.csv"), "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f, delimiter=";")
                w.writerow(["Compte", "Intitulé", "Ouverture D", "Ouverture C", "Mvt D", "Mvt C", "Solde D", "Solde C"])
                for a, (o, md, mk) in tdm.B.items():
                    sd = o + md - mk
                    w.writerow([a, tdm.LIB[a], max(o, 0), max(-o, 0), md, mk, max(sd, 0), max(-sd, 0)])
            tdm.modele(os.path.join(src, "reference.xlsx"))
            g = contenu(await s.call_tool("generer_def", {**args, "pdf": True}))
            check("génération automatique : v1 PROJET, PDF produits sans Excel", g.get("statut") == "projet" and g.get("version") == 1
                  and any(x.endswith(".pdf") for x in g.get("livrables", [])), g)
            qs = contenu(await s.call_tool("questions_ouvertes", args), liste=True)
            # 0.11.0 : la raison sociale est REPRISE de la page de garde de la DEF déposée (proposition affichée au
            # formulaire, donc répondue) ; l'adresse, absente de cette page de garde, reste demandée
            check("questions obligatoires renvoyées : l'identité absente des sources (adresse), pas celle reprise",
                  any(q["id"] == "identite.adresse" for q in qs) and not any(q["id"] == "identite.raison_sociale" for q in qs),
                  [q["id"] for q in qs][:6])
            check("lot de questions et « prêt à valider » rendus avec la version (mode préparer et valider)",
                  isinstance(g.get("questions_a_poser"), list) and g.get("pret_a_valider") is False
                  and {q["id"] for q in g["questions_a_poser"]} == {q["id"] for q in qs}, g.get("pret_a_valider"))
            check("aucune donnée comptable dans les réponses de l'outil", "150000" not in json.dumps(g) + json.dumps(qs))
            g2 = contenu(await s.call_tool("generer_def", {"entite": "ENTITE-A", "exercice": 2025, "pdf": False}))
            check("le pseudonyme est accepté en ENTRÉE (même dossier, version 2)", g2.get("version") == 2, g2)
            journal = os.path.join(racine, "journal_sorties.jsonl")
            lignes = open(journal, encoding="utf-8").read().splitlines() if os.path.exists(journal) else []
            check("journal local : chaque sortie transmise y figure, sans le nom réel",
                  len(lignes) >= 4 and "ENTITE MCP" not in "".join(lignes), len(lignes))
            ref = contenu(await s.call_tool("enregistrer_reponse", {**args, "id": "interp.base_cmf", "valeur": "absurde"}))
            check("réponse hors choix refusée", "refuse" in ref, ref)
            v = contenu(await s.call_tool("valider_version", {**args, "par": "Testeur"}))
            check("validation refusée tant que des obligatoires sont ouvertes", v.get("statut") == "refuse", v)
            for q in qs:
                await s.call_tool("enregistrer_reponse", {**args, "id": q["id"], "valeur": (q["options"] or ["ENTITE MCP SA"])[0]})
            v = contenu(await s.call_tool("valider_version", {**args, "par": "Testeur"}))
            check("validation acceptée : version définitive", v.get("statut") == "definitive", v)
            f = contenu(await s.call_tool("ouvrir_formulaire", {**args, "navigateur": False}))
            check("ouvrir_formulaire : le jeton d'accès n'est PAS transmis", "?t=" not in json.dumps(f), f)
            adresse, code = "", None
            try:
                adresse = next(l[4:].strip() for l in open(reel(f["raccourci_local"]), encoding="utf-8") if l.startswith("URL="))
                import urllib.request
                code = urllib.request.urlopen(adresse, timeout=10).status
            except Exception as e:
                code = repr(e)
            check("raccourci local : lien 127.0.0.1 à jeton, page servie", adresse.startswith("http://127.0.0.1:")
                  and "?t=" in adresse and code == 200, (adresse[:40], code))
            l = contenu(await s.call_tool("lister_dossiers", {}), liste=True)
            check("lister_dossiers : entité, exercice, statut définitif", any(x["statut"] == "definitive" for x in l), l)


def main():
    racine = tempfile.mkdtemp()
    asyncio.run(parcours(racine))
    print(f"\n{sum(ok)}/{len(ok)} contrôles conformes")
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
