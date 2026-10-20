# -*- coding: utf-8 -*-
"""Garde du PARCOURS COMPLET du formulaire, comme un navigateur : chaque étape est remplie et envoyée
avec TOUS ses champs (listes présélectionnées comprises), par « Enregistrer et suivant ».

Incident du 17/10/2026 (utilisateur réel) : « Suivant » menait à une page blanche, l'étape suivante ne
s'ouvrait pas, et le récapitulatif de validation restait sur « Répondre » : l'utilisateur était bloqué.
Exigé ici, à chaque étape : 303 vers l'étape suivante, réponses enregistrées ; à la fin : plus aucune
question obligatoire ouverte, et le bouton de validation actif.

Lancer : python tests/test_formulaire_parcours.py      (code 0 = conforme)
"""
import html.parser
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import test_formulaire as tf  # noqa: E402  (même préparation : vrai dossier, vrai serveur)

ed, fo, requete = tf.ed, tf.fo, tf.requete
ok = []


def check(nom, cond, detail=""):
    ok.append(bool(cond))
    print(f"  {'OK   ' if cond else 'ÉCHEC'} {nom}" + ("" if cond else f"  — {str(detail)[:400]}"))


class Formulaire(html.parser.HTMLParser):
    """Champs envoyés par un navigateur pour le formulaire « /repondre » de la page."""

    def __init__(self):
        super().__init__()
        self.dans, self.champs, self.radios, self.select, self.options = False, [], {}, None, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "form":
            self.dans = a.get("action") == "/repondre"
        if not self.dans:
            return
        if tag == "input" and a.get("type") in ("hidden", "text", None):
            self.champs.append([a.get("name"), a.get("value", ""), a.get("type") or "text"])
        elif tag == "input" and a.get("type") == "radio":
            r = self.radios.setdefault(a["name"], {"options": [], "coche": None})
            r["options"].append(a.get("value"))
            if "checked" in a:
                r["coche"] = a.get("value")
        elif tag == "select":
            self.select, self.options = a.get("name"), []
        elif tag == "option" and self.select:
            self.options.append((a.get("value", ""), "selected" in a))

    def handle_endtag(self, tag):
        if tag == "select" and self.select:
            choisi = next((v for v, s in self.options if s), self.options[0][0] if self.options else "")
            self.champs.append([self.select, choisi, "select", [v for v, _ in self.options if v]])
            self.select = None
        if tag == "form":
            self.dans = False


VALEURS = {"identite.raison_sociale": "ENTITE TEST SA", "identite.nif": "TEST123456", "identite.adresse": "BP 1, Malabo",
           "identite.ville": "Malabo", "identite.telephone": "+240 000 000", "identite.dirigeant": "PERSONNE TEST",
           "identite.activite": "Bâtiment et travaux publics"}


def envoi_navigateur(page, k):
    """Remplit ce que l'utilisateur remplirait (champ vide → valeur plausible ; choix non fait → premier choix)."""
    f = Formulaire(); f.feed(page)
    corps = {}
    for c in f.champs:
        nom, val, typ = c[0], c[1], c[2]
        if not nom:
            continue
        if typ == "text" and not val:
            val = VALEURS.get(nom, "inconnu")
        if typ == "select" and not val and c[3]:
            val = c[3][0]
        corps[nom] = val
    for nom, r in f.radios.items():
        corps[nom] = r["coche"] or r["options"][0]
    corps["etape"] = str(k)
    corps["aller"] = "suivant"
    return corps


def main():
    reel = ed.generer
    ed.generer = lambda d, **k: reel(d, **{**k, "pdf": False})
    d = tf.preparer()
    url = fo.demarrer(d, navigateur=False)
    srv = fo._SERVEURS[d][0]
    ck = {"Cookie": f"facil_t={srv.jeton}"}
    n_etapes = len(fo._etapes(fo._questions(d)))
    print(f"== Parcours complet : {n_etapes} étapes (la dernière est la validation)")

    for k in range(n_etapes - 1):
        s, _, page = requete(url.split("?")[0] + f"?e={k}", entetes=ck)
        titre = re.search(r'<h2 id="titre-etape">(.*?)</h2>', page)
        titre = titre.group(1) if titre else "?"
        corps = envoi_navigateur(page, k)
        s, h, retour = requete(url, "POST", "/repondre", corps, ck)
        check(f"étape {k + 1} « {titre} » : « Suivant » redirige vers l'étape {k + 2}",
              s == 303 and h.get("Location") == f"/?e={k + 1}", (s, h.get("Location"), retour[-300:]))
        attendu = {n: v for n, v in corps.items() if n not in ("t", "etape", "aller") and v}
        enregistrees = ed.lire_json(os.path.join(d, "04_questions", "reponses.json"), {})
        manquantes = [n for n in attendu if n in [q["id"] for q in fo._questions(d)] and n not in enregistrees
                      and not attendu[n] == "defaut"]
        check(f"étape {k + 1} : réponses enregistrées", not manquantes, manquantes)

    s, _, page = requete(url.split("?")[0] + "?e=v", entetes=ck)
    ouvertes = [q["id"] for q in fo._questions(d) if q["obligatoire"] and not q.get("reponse")]
    check("validation : plus aucune question obligatoire ouverte", not ouvertes, ouvertes)
    check("validation : le récapitulatif ne propose plus « Répondre »", "Répondre" not in page, re.findall(r".{60}Répondre.{20}", page)[:2])
    bouton = re.search(r'<form method="post" action="/valider">.*?</form>', page, re.S)
    check("validation : le bouton de validation est actif", bouton and "disabled" not in bouton.group(0),
          bouton.group(0)[:300] if bouton else "formulaire de validation absent")
    print("== Origine et référent, comme un VRAI navigateur — cause prouvée de l'incident du 16-17/10/2026")
    port = srv.server_address[1]
    s, h, _ = requete(url, entetes=ck)
    politique = h.get("Referrer-Policy")
    check("politique de référent « same-origin » (avec « no-referrer », Chrome et Edge envoient « Origin: null » "
          "sur chaque POST, et le formulaire se refusait lui-même)", politique == "same-origin", politique)
    s, h, _ = requete(url, "POST", "/repondre", {"t": srv.jeton, "etape": "0", "aller": "suivant"},
                      {**ck, "Origin": f"http://127.0.0.1:{port}"})
    check("POST avec l'origine que le navigateur envoie désormais : accepté, « Suivant » avance",
          s == 303 and h.get("Location") == "/?e=1", (s, h.get("Location")))
    s, _, page = requete(url, "POST", "/repondre", {"t": srv.jeton, "etape": "0", "aller": "suivant"},
                         {**ck, "Origin": "https://site-etranger.example"})
    check("POST d'une origine étrangère : refusé, avec une page qui l'explique (protection intacte)",
          s == 403 and "Requête refusée" in page, (s, page[:200]))
    s, _, _ = requete(url, "POST", "/repondre", {"t": srv.jeton, "etape": "0", "aller": "suivant"},
                      {**ck, "Origin": "null"})
    check("POST « Origin: null » : toujours refusé (c'est pourquoi la politique de référent ne doit pas le provoquer)",
          s == 403, s)

    print("== Fichier tenu par un autre programme (OneDrive, antivirus) — incident du 17/10/2026")
    p_rep = os.path.join(d, "04_questions", "reponses.json")
    avant = ed.lire_json(p_rep, {})
    vrai_replace, compte = os.replace, {"n": 0}

    def replace_tenu_brievement(a, b):                  # refusé 3 fois, puis accepté
        compte["n"] += 1
        if compte["n"] <= 3:
            raise PermissionError(5, "Accès refusé", b)
        return vrai_replace(a, b)
    os.replace = replace_tenu_brievement
    try:
        s, h, _ = requete(url, "POST", "/repondre", {"t": srv.jeton, "etape": "0", "aller": "suivant",
                                                     "identite.ville": "Bata"}, ck)
    finally:
        os.replace = vrai_replace
    check("verrou bref : l'enregistrement aboutit quand même, et « Suivant » avance", s == 303 and h.get("Location") == "/?e=1",
          (s, h.get("Location")))
    apres = ed.lire_json(p_rep, {})
    check("verrou bref : la nouvelle réponse est enregistrée, les anciennes conservées",
          apres.get("identite.ville") == "Bata" and all(apres.get(k) == v for k, v in avant.items()
                                                         if not k.startswith("_") and k != "identite.ville"))

    def replace_tenu_toujours(a, b):
        raise PermissionError(5, "Accès refusé", b)
    os.replace = replace_tenu_toujours
    ed_pause = ed.PAUSE
    ed.PAUSE = 0.001                                     # test rapide
    try:
        s, _, page = requete(url, "POST", "/repondre", {"t": srv.jeton, "etape": "0", "aller": "suivant",
                                                        "identite.ville": "Ebebiyin"}, ck)
    finally:
        os.replace = vrai_replace
        ed.PAUSE = ed_pause
    check("verrou durable : une PAGE d'explication (503), jamais une page blanche", s == 503 and "pas abouti" in page
          and "Réessayer" in page, (s, page[:200]))
    check("verrou durable : aucune réponse perdue", ed.lire_json(p_rep, {}).get("identite.ville") == "Bata")

    import builtins
    vrai_open, essais = builtins.open, {"n": 0}

    def open_tenu(f, *a, **k):
        if str(f) == p_rep and (not a or "r" in a[0]) and "w" not in (a[0] if a else ""):
            essais["n"] += 1
            if essais["n"] <= 2:
                raise PermissionError(32, "Le fichier est utilisé par un autre processus", f)
        return vrai_open(f, *a, **k)
    builtins.open = open_tenu
    try:
        lu = ed.lire_json(p_rep, {})
    finally:
        builtins.open = vrai_open
    check("lecture d'un fichier tenu un instant : relu, JAMAIS pris pour vide", lu.get("identite.ville") == "Bata", lu.keys())
    builtins.open = lambda f, *a, **k: (_ for _ in ()).throw(PermissionError(32, "tenu", f)) if str(f) == p_rep else vrai_open(f, *a, **k)
    ed.PAUSE = 0.001
    try:
        try:
            ed.lire_json(p_rep, {}); leve = False
        except ed.FichierIndisponible:
            leve = True
    finally:
        builtins.open = vrai_open
        ed.PAUSE = ed_pause
    check("lecture d'un fichier tenu durablement : erreur explicite, pas un « vide » qui écraserait tout", leve)

    print("== Erreur imprévue : cause affichée et tracée localement")
    journal = os.path.join(d, "04_questions", "erreurs_formulaire.log")
    check("le verrou durable ci-dessus est tracé dans 04_questions/erreurs_formulaire.log",
          os.path.exists(journal) and "FichierIndisponible" in open(journal, encoding="utf-8").read())
    vrai_repondre = ed.repondre

    def repondre_en_panne(*a, **k):
        raise ValueError("panne simulée pour le test")
    ed.repondre = repondre_en_panne
    try:
        s, _, page = requete(url, "POST", "/repondre", {"t": srv.jeton, "etape": "1", "aller": "suivant",
                                                        "identite.ville": "Mongomo"}, ck)
    finally:
        ed.repondre = vrai_repondre
    check("erreur imprévue : page lisible (500) qui NOMME la cause, jamais une page blanche",
          s == 500 and "ValueError" in page and "panne simulée" in page and "Réessayer" in page, (s, page[:200]))
    check("erreur imprévue : tracée dans le journal local", "panne simulée" in open(journal, encoding="utf-8").read())

    print("== Dossier par défaut hors du cloud")
    vrai_docs = ed.documents
    ed.documents = lambda: os.path.join(os.path.expanduser("~"), "OneDrive", "Documents")
    os.environ.pop("FACIL_DEF_RACINE", None)
    try:
        r = ed.racine_defaut()
    finally:
        ed.documents = vrai_docs
    check("Documents synchronisé par OneDrive → dossier de travail LOCAL (%USERPROFILE%\\Facil-DEF)",
          os.path.normcase(r) == os.path.normcase(os.path.join(os.path.expanduser("~"), "Facil-DEF")), r)
    ed.documents = lambda: os.path.join(os.path.expanduser("~"), "Documents")
    try:
        r = ed.racine_defaut()
    finally:
        ed.documents = vrai_docs
    check("Documents local → Documents\\Facil-DEF (inchangé)", r.endswith(os.path.join("Documents", "Facil-DEF")), r)

    fo.arreter(d) if hasattr(fo, "arreter") else None
    print(f"{sum(ok)}/{len(ok)} contrôles conformes")
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
