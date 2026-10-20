# -*- coding: utf-8 -*-
"""Garde du FORMULAIRE WEB LOCAL (serveur/formulaire.py) : accès, réponses, régénération, les deux horloges.

Vrai serveur HTTP sur 127.0.0.1, vrai dossier de travail (données de test_def_modele.py), génération sans PDF.
Lancer : python tests/test_formulaire.py     (code 0 = conforme)
FACIL_FORMULAIRE=<dossier> : éprouve une autre copie de formulaire.py (falsification).
"""
import csv
import datetime
import http.client
import json
import os
import re
import sys
import tempfile
import time
import urllib.parse

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "dsf-syscohada", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.environ.get("FACIL_FORMULAIRE") or os.path.join(ROOT, "serveur"))
import espace_def as ed  # noqa: E402
import formulaire as fo  # noqa: E402
import test_def_modele as tdm  # noqa: E402

ok = []


def check(nom, cond, detail=""):
    ok.append(bool(cond))
    print(f"  {'OK   ' if cond else 'ÉCHEC'} {nom}" + ("" if cond else f"  — {str(detail)[:300]}"))


def requete(url, methode="GET", chemin=None, corps=None, entetes=None):
    u = urllib.parse.urlparse(url)
    c = http.client.HTTPConnection(u.hostname, u.port, timeout=30)
    h = {"Host": f"127.0.0.1:{u.port}"}
    h.update(entetes or {})
    if corps is not None:
        corps = urllib.parse.urlencode(corps, doseq=True)
        h["Content-Type"] = "application/x-www-form-urlencoded"
    try:
        c.request(methode, chemin or (u.path + ("?" + u.query if u.query else "")), body=corps, headers=h)
        r = c.getresponse()
        return r.status, dict(r.getheaders()), r.read().decode("utf-8", "replace")
    except (ConnectionError, OSError) as e:
        return None, {}, repr(e)
    finally:
        c.close()


def preparer():
    d = ed.init(tempfile.mkdtemp(), "ENTITE TEST SA", 2025)
    src = os.path.join(d, "01_sources")
    with open(os.path.join(src, "balance.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Compte", "Intitulé", "Ouverture D", "Ouverture C", "Mvt D", "Mvt C", "Solde D", "Solde C"])
        for a, (o, md, mk) in tdm.B.items():
            s = o + md - mk
            w.writerow([a, tdm.LIB[a], max(o, 0), max(-o, 0), md, mk, max(s, 0), max(-s, 0)])
    tdm.modele(os.path.join(src, "reference.xlsx"))
    ed.generer(d, pdf=False)
    return d


def attendre(srv, limite=120):
    t0 = time.time()
    while srv.occupe() and time.time() - t0 < limite:
        time.sleep(0.2)


def main():
    reel = ed.generer
    ed.generer = lambda d, **k: reel(d, **{**k, "pdf": False})     # sans PDF : on garde la mécanique, pas le rendu
    d = preparer()
    url = fo.demarrer(d, navigateur=False)
    srv = fo._SERVEURS[d][0]
    port = srv.server_address[1]
    jeton = srv.jeton
    ck = {"Cookie": f"facil_t={jeton}"}

    print("== Écoute et accès")
    check("écoute sur 127.0.0.1 seulement, port libre", srv.server_address[0] == "127.0.0.1" and port > 0, srv.server_address)
    check("jeton aléatoire long (≥ 32 caractères)", len(jeton) >= 32, jeton)
    s, _, _ = requete(url.split("?")[0])
    check("sans jeton : 403", s == 403, s)
    s, _, _ = requete(url.split("?")[0] + "?t=" + "x" * len(jeton))
    check("jeton faux : 403", s == 403, s)
    s, _, _ = requete(url, entetes={"Host": f"attaquant.example:{port}"})
    check("Host étranger (détournement DNS) : 403", s == 403, s)
    avant = srv.derniere
    time.sleep(0.05)
    requete(url.split("?")[0])
    check("une requête refusée ne prolonge pas la session", srv.derniere == avant)

    print("== Page")
    s, h, page = requete(url)
    check("avec jeton : 200", s == 200, s)
    cookie = h.get("Set-Cookie", "")
    check("témoin HttpOnly + SameSite=Strict", "HttpOnly" in cookie and "SameSite=Strict" in cookie, cookie)
    csp = h.get("Content-Security-Policy", "")
    nonce = re.search(r"nonce-([\w-]+)", csp)
    check("CSP stricte : default-src 'none', script sous nonce de la page",
          "default-src 'none'" in csp and nonce and f'nonce="{nonce.group(1)}"' in page, csp)
    check("aucune ressource externe (src/href http)", not re.search(r'(src|href)="https?:', page))
    check("logo Facil embarqué", 'src="data:image/png;base64,' in page and 'alt="Facil"' in page)
    an = datetime.date.today().year
    check(f"pied de page « © Facil - AI Solutions Architect - Emac SAH {an} » (année calculée)",
          f"© Facil - AI Solutions Architect - Emac SAH {an}" in page)
    check("questions obligatoires affichées (identité)", "identite.raison_sociale" in page and "obligatoire" in page)
    print("== Parcours par étapes")
    check("en-tête sobre : logo centré, filet, entité et exercice — sans titre en carte",
          'class="entete"' in page and 'class="filet"' in page and "Déclaration fiscale et statistique" not in page
          and "exercice clos le 31/12/2025" in page)
    # 0.11.0 : le sigle ne se DEMANDE plus, mais s'affiche quand il est REPRIS de la DEF déposée (pour se relire)
    check("identité en UNE étape ; reprise de la DEF affichée, avec son origine, et corrigeable",
          page.count('class="champ') >= 6 and "identite.raison_sociale" in page and "identite.dirigeant" in page
          and 'value="ANCIENNE SA"' in page and "Repris : DEF précédente déposée (reference.xlsx)" in page
          and ("Sigle usuel" not in page or 'value="ANC"' in page))
    check("stepper : étapes numérotées, étape active annoncée (aria-current=\"step\"), dernière = Validation",
          'aria-label="Étapes"' in page and page.split('aria-label="Étapes"', 1)[-1].split("</nav>", 1)[0]
          .count('aria-current="step"') == 1 and ">Validation</span>" in page)
    tiers = [{"id": f"tf5nif.T{i}", "categorie": "Tiers (TF5)", "question": f"NIF du bénéficiaire T{i}", "options": [],
              "obligatoire": True, "contexte": "art. 27.2"} for i in range(14)]
    parts = [e for e in fo._etapes(tiers) if not e["validation"]]
    check("14 tiers au TF5 : découpés en étapes de 6 au plus (« Tiers TF5 1/3 »…)",
          len(parts) == 3 and all(len(e["questions"]) <= 6 for e in parts) and parts[0]["court"] == "Tiers TF5 1/3",
          [(e["court"], len(e["questions"])) for e in parts])
    s, _, p2 = requete(url, "GET", "/?e=1", entetes=ck)
    check("hors identité : au plus 6 questions par étape (pas de défilement pour remplir)",
          0 < p2.count('class="champ') <= 6, p2.count('class="champ'))
    s, h, _ = requete(url, "POST", "/repondre", {"t": jeton, "etape": "0", "aller": "suivant"}, ck)
    check("« Enregistrer et suivant » : enregistre puis passe à l'étape suivante", s == 303 and h.get("Location") == "/?e=1", h)
    s, h, _ = requete(url, "POST", "/repondre", {"t": jeton, "etape": "1", "aller": "precedent"}, ck)
    check("« Précédent » revient à l'étape d'avant", h.get("Location") == "/?e=0", h)
    s, _, pv = requete(url, "GET", "/?e=v", entetes=ck)
    check("étape Validation : récapitulatif, liste des obligatoires ouvertes avec lien « Répondre »",
          s == 200 and "Récapitulatif et validation" in pv and "Répondre</a>" in pv, s)
    import re as _re
    pile = _re.search(r'<form method="post" action="/ouvrir" class="pile">(.*?)</form>', pv, _re.S)
    regle = _re.search(r"\.pile \{([^}]*)\}", pv)
    texte_boutons = _re.sub(r"<[^>]+>", " ", pile.group(1)) if pile else ""
    check("livrables : deux boutons EMPILÉS (une colonne), intitulés seuls — ni chemin ni nom de dossier",
          pile and pile.group(1).count("<button") == 2 and "Ouvrir le dossier des PDF" in texte_boutons
          and "03_pdf" not in texte_boutons and "02_xls" not in texte_boutons and "\\" not in texte_boutons
          and regle and "flex-direction:column" in regle.group(1), (texte_boutons[:160], regle and regle.group(1)))
    check("préavis d'une minute et geste « Rester connecté » présents", "Rester connecté" in page and "reste <= 60" in page)
    check("cibles tactiles de 44 px", "min-height:44px" in page)

    print("== Réponses")
    s, _, _ = requete(url, "POST", "/repondre", {"t": jeton, "interp.base_cmf": "n'importe quoi"},
                      {"Origin": "http://evil.example"})
    check("POST d'une origine étrangère : 403", s == 403, s)
    s, _, page = requete(url, "POST", "/repondre", {"t": jeton, "interp.base_cmf": "n'importe quoi"})
    rep = ed.lire_json(os.path.join(d, "04_questions", "reponses.json"), {})
    check("réponse hors choix refusée et signalée, rien d'enregistré",
          s == 200 and "refusée" in page and "interp.base_cmf" not in rep, (s, rep.keys()))
    s, h, _ = requete(url, "POST", "/repondre", {"t": jeton, "identite.raison_sociale": "ENTITE TEST SA",
                                                 "identite.nif": "  ", "_x": "ignoré"}, ck)
    rep = ed.lire_json(os.path.join(d, "04_questions", "reponses.json"), {})
    check("réponse valide enregistrée par espace_def.repondre (journal)", s == 303
          and rep.get("identite.raison_sociale") == "ENTITE TEST SA" and rep.get("_journal"), rep)
    check("champ vide : pas de réponse écrite", "identite.nif" not in rep and "_x" not in rep, rep.keys())

    print("== Régénération en arrière-plan")
    n0 = len(ed.lire_json(os.path.join(d, "manifeste.json"), {}).get("versions", []))
    s, h, _ = requete(url, "POST", "/regenerer", {"t": jeton}, ck)
    check("régénérer : redirection immédiate (303) vers l'étape Validation", s == 303 and h.get("Location") == "/?e=v", (s, h))
    s, _, page = requete(url, entetes=ck)
    check("page d'attente pendant la génération", not srv.occupe() or "Génération en cours" in page)
    attendre(srv)
    man = ed.lire_json(os.path.join(d, "manifeste.json"), {})
    check("nouvelle version produite", len(man.get("versions", [])) == n0 + 1, len(man.get("versions", [])))
    check("réponse réinjectée dans la version", man["versions"][-1]["reponses_appliquees"].get("identite.raison_sociale")
          == "ENTITE TEST SA")
    s, _, page = requete(url, entetes=ck)
    check("message de fin de génération affiché", f"Version {n0 + 1} produite" in page, page[:200])
    requete(url, "POST", "/valider", {"t": jeton, "par": "Comptable"}, ck)
    attendre(srv)
    s, _, page = requete(url, entetes=ck)
    man = ed.lire_json(os.path.join(d, "manifeste.json"), {})
    check("validation refusée tant que des obligatoires sont ouvertes, et le motif se dit",
          "refusée" in page and man["versions"][-1]["statut"] == "projet", page[:200])
    s, _, corps = requete(url, "POST", "/battement", {}, ck)
    check("battement : 200 et temps restant ≤ 15 min", s == 200 and 0 < json.loads(corps)["reste"] <= 15 * 60, corps)

    print("== Deux horloges, éprouvées des deux côtés du seuil")
    t = srv.derniere
    check("inactivité : ouvert 1 ms avant la borne", srv.motif_fin(t + srv.inactivite - 0.001) is None)
    check("inactivité : fermé 1 ms après", srv.motif_fin(t + srv.inactivite + 0.001) == "inactivité")
    srv.derniere = srv.debut + srv.duree_max           # activité permanente : seule la durée absolue borne
    check("durée absolue : ouvert 1 ms avant", srv.motif_fin(srv.debut + srv.duree_max - 0.001) is None)
    check("durée absolue : fermé 1 ms après, même avec activité",
          srv.motif_fin(srv.debut + srv.duree_max + 0.001) == "durée maximale atteinte")
    srv.derniere = time.time()
    check("défauts : 15 min et 12 h", fo.INACTIVITE == 15 * 60 and fo.DUREE_MAX == 12 * 3600)

    print("== Fermeture réelle")
    srv.derniere = time.time() - srv.inactivite - 1     # inactivité simulée (la veille n'a pas encore tourné)
    s, _, corps = requete(url, "POST", "/battement", {}, ck)
    check("le serveur refuse passé le délai, motif dit (401 inactivité)", s == 401 and "inactivité" in corps, (s, corps[:120]))
    time.sleep(1)
    s, _, _ = requete(url, entetes=ck)
    check("un battement ne ressuscite pas : serveur arrêté", s is None, s)
    url2 = fo.demarrer(d, navigateur=False, inactivite=0.4, duree_max=100)
    check("relance : nouveau lien, nouveau jeton", url2 != url)
    time.sleep(1.2)
    s, _, _ = requete(url2)
    check("la veille ferme sans aucune requête (onglet abandonné)", s is None, s)

    print(f"\n{sum(ok)}/{len(ok)} contrôles conformes")
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
