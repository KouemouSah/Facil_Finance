# -*- coding: utf-8 -*-
"""Garde de la PASSERELLE DE CONFIDENTIALITÉ (serveur/confidentialite.py) et du HOOK de lecture (serveur/garde_lecture.py).

Sorties réalistes d'outils (question de réintégration chiffrée, NIF de tiers, noms de fichiers, chemins) :
  - noms -> pseudonymes stables et réversibles ; montants -> masqués ; années et n° de compte des identifiants gardés ;
  - échec FERMÉ : une sortie où subsiste une valeur réelle est retenue, l'incident journalisé ;
  - journal local de ce qui est transmis ; mode « standard » : entité en clair, le reste protégé ;
  - hook : lecture du dossier Facil-DEF refusée (code 2), le reste autorisé.
Lancer : python tests/test_confidentialite.py     (code 0 = conforme)
FACIL_SERVEUR=<dossier> : éprouve une autre copie de serveur/ (falsification).
"""
import json
import os
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVEUR = os.environ.get("FACIL_SERVEUR") or os.path.join(ROOT, "serveur")
sys.path.insert(0, SERVEUR)
import confidentialite as conf  # noqa: E402

ok = []


def check(nom, cond, detail=""):
    ok.append(bool(cond))
    print(f"  {'OK   ' if cond else 'ÉCHEC'} {nom}" + ("" if cond else f"  — {str(detail)[:300]}"))


def dossier_exemple(racine):
    d = os.path.join(racine, "ALPHA_BTP_SARL", "2025")
    os.makedirs(os.path.join(d, "04_questions"))
    json.dump({"entite": "ALPHA BTP SARL", "exercice": 2025, "versions": []},
              open(os.path.join(d, "manifeste.json"), "w", encoding="utf-8"))
    json.dump([{"id": "tf5nif.HIDDEN CONSULTING SL", "question": "NIF du bénéficiaire « HIDDEN CONSULTING SL »"}],
              open(os.path.join(d, "04_questions", "questions.json"), "w", encoding="utf-8"))
    json.dump({"identite.raison_sociale": "ALPHA BTP SARL", "identite.nif": "04321XY-25/BN",
               "identite.dirigeant": "JEAN MARTIN", "identite.adresse": "Carretera del Aeropuerto, Malabo"},
              open(os.path.join(d, "04_questions", "reponses.json"), "w", encoding="utf-8"))
    return d


def main():
    racine = tempfile.mkdtemp()
    d = dossier_exemple(racine)
    os.environ["FACIL_CONFIDENTIALITE"] = "stricte"
    P = conf.Passerelle(racine)
    P.apprendre_racine()
    sortie = {
        "dossier": d, "exercice": 2025, "version": 3,
        "sources": {"balance": "BALANCE ALPHA BTP SARL 2025.xls"},
        "livrables": [os.path.join("02_xls", "DEF_2025_v3_FR_projet.xlsx")],
        "questions": [
            {"id": "reint.64710000", "question": "Réintégrer 297 008 247 du compte 64710000 ?",
             "impact": "IS +74 252 062", "options": ["accepter", "refuser"], "contexte": "art. 62.3.a"},
            {"id": "tf5nif.HIDDEN CONSULTING SL", "question": "NIF du bénéficiaire « HIDDEN CONSULTING SL »",
             "contexte": "déclaré 1,272,700,235.69 ; dirigeant JEAN MARTIN ; siège Carretera del Aeropuerto, Malabo"}],
        "total": 1673778909.89,
    }
    print("== Filtrage (mode stricte)")
    f = P.sortie("generer_def", sortie)
    check("sortie filtrée TRANSMISE (le filtre suffit : le contrôle final n'a rien eu à retenir)", "erreur" not in f, f)
    f.setdefault("questions", [])
    s = json.dumps(f, ensure_ascii=False)
    for reel in ("ALPHA BTP", "ALPHA_BTP", "HIDDEN CONSULTING", "JEAN MARTIN", "04321XY", "Aeropuerto", racine):
        check(f"« {reel[:18]} » absent de la sortie", reel.lower() not in s.lower(), s[:200])
    for m in ("297 008 247", "74 252 062", "1,272,700,235", "1673778909"):
        check(f"montant « {m} » masqué", m not in s, s[:200])
    check("années et n° de compte des identifiants conservés (2025, reint.64710000)",
          '"exercice": 2025' in s and "reint.64710000" in s and "DEF_2025_v3" in s, s[:300])
    check("pseudonymes lisibles : ENTITE-A, TIERS-, PERS-, IDENT-", all(x in s for x in ("ENTITE-A", "TIERS-0", "PERS-0", "IDENT-0")), s)
    check("chemin relatif à la racine", "<Facil-DEF>" in s, s[:120])
    tid = next((q["id"] for q in f["questions"] if q["id"].startswith("tf5nif.")), "")
    check("entrée : pseudonyme rendu à sa valeur réelle (réponse à la bonne question)",
          P.entree(tid) == "tf5nif.HIDDEN CONSULTING SL" and P.entree("ENTITE-A") == "ALPHA BTP SARL", (tid, P.entree(tid)))
    P2 = conf.Passerelle(racine)
    P2.apprendre_racine()
    check("pseudonymes STABLES d'une session à l'autre (coffre local)",
          P2.sortie("x", {"q": "ALPHA BTP SARL"}).get("q") == "ENTITE-A")
    check("coffre local, jamais dans une sortie", os.path.exists(os.path.join(racine, ".facil_coffre.json"))
          and ".facil_coffre" not in s)

    print("== Échec fermé et journal")
    P.filtrer = lambda obj, cle=None: obj                    # panne simulée du filtre : rien n'est filtré
    b = P.sortie("generer_def", sortie)
    check("filtre en panne : la sortie est RETENUE, pas envoyée", "erreur" in b and "ALPHA" not in json.dumps(b), b)
    lignes = [json.loads(l) for l in open(os.path.join(racine, "journal_sorties.jsonl"), encoding="utf-8")]
    check("journal : sorties transmises horodatées et empreintes, incident tracé",
          len(lignes) >= 3 and all(len(x["empreinte"]) == 64 for x in lignes)
          and any(x["transmis"].get("BLOQUEE") for x in lignes if isinstance(x["transmis"], dict)), len(lignes))
    check("journal sans aucune valeur réelle", "ALPHA BTP" not in open(os.path.join(racine, "journal_sorties.jsonl"),
                                                                       encoding="utf-8").read())
    check("liste retenue : même forme (liste)", isinstance(P.sortie("questions_ouvertes", [{"q": "ALPHA BTP SARL"}]), list))

    print("== Mode standard : entité en clair, le reste protégé")
    r2 = tempfile.mkdtemp()
    dossier_exemple(r2)
    os.environ["FACIL_CONFIDENTIALITE"] = "standard"
    P3 = conf.Passerelle(r2)
    P3.apprendre_racine()
    s3 = json.dumps(P3.sortie("x", {"e": "ALPHA BTP SARL", "t": "HIDDEN CONSULTING SL 297 008 247"}), ensure_ascii=False)
    check("standard : l'entité reste lisible, tiers et montant protégés",
          "ALPHA BTP SARL" in s3 and "HIDDEN" not in s3 and "297" not in s3, s3)
    os.environ["FACIL_CONFIDENTIALITE"] = "stricte"

    print("== Hook : pas de lecture directe du dossier de travail")
    hook = os.path.join(SERVEUR, "garde_lecture.py")
    env = {**os.environ, "FACIL_DEF_RACINE": racine}

    def appel(outil, entree):
        p = subprocess.run([sys.executable, hook], input=json.dumps({"tool_name": outil, "tool_input": entree}),
                           capture_output=True, text=True, encoding="utf-8", env=env, timeout=30)
        return p.returncode, p.stderr
    c, err = appel("Read", {"file_path": os.path.join(d, "02_xls", "DEF.xlsx")})
    check("Read dans le dossier Facil-DEF : refusé (code 2), motif dit", c == 2 and "Facil-DEF" in err, (c, err))
    c, _ = appel("Read", {"file_path": os.path.join(d.upper(), "..", "2025", "manifeste.json")})
    check("chemin détourné (casse, ..) : refusé", c == 2, c)
    c, _ = appel("Grep", {"pattern": "x", "path": racine})
    check("Grep sur la racine : refusé", c == 2, c)
    c, _ = appel("Bash", {"command": f'cat "{os.path.join(d, "manifeste.json")}"'})
    check("Bash qui lit le dossier : refusé", c == 2, c)
    c, _ = appel("PowerShell", {"command": "Get-Content $env:USERPROFILE\\Documents\\Facil-DEF\\x\\2025\\manifeste.json"})
    check("PowerShell visant « Facil-DEF » : refusé", c == 2, c)
    c, _ = appel("Read", {"file_path": os.path.join(tempfile.gettempdir(), "autre.txt")})
    check("Read ailleurs : autorisé (code 0)", c == 0, c)
    c, _ = appel("Bash", {"command": "git status"})
    check("commande sans rapport : autorisée", c == 0, c)
    p = subprocess.run([sys.executable, hook], input="pas du json", capture_output=True, text=True, encoding="utf-8", env=env)
    check("entrée illisible : refus par prudence (échec fermé)", p.returncode == 2, p.returncode)
    print(f"\n{sum(ok)}/{len(ok)} contrôles conformes")
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
