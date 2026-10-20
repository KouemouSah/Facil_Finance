# -*- coding: utf-8 -*-
"""Formulaire web LOCAL de la DEF : répondre aux questions, régénérer, valider — sans passer par Claude.

Sécurité (données fiscales) :
  - écoute sur 127.0.0.1 uniquement, port libre choisi par le système ;
  - jeton aléatoire exigé à CHAQUE requête (paramètre t, puis cookie HttpOnly SameSite=Strict) ;
  - en-tête Host contrôlé (127.0.0.1 / localhost seulement : parade au détournement DNS) ; Origin contrôlé sur POST ;
  - aucune ressource externe (styles, logo, script embarqués, script sous nonce CSP) ;
  - deux horloges tenues par le serveur : 15 min d'inactivité, 12 h au plus ; la page prévient une minute avant,
    un battement (une fois par minute au plus) porte l'activité du clavier au serveur, les onglets partagent le décompte.
    Ce qui ne se fait pas ici : aucune identité n'est gérée (poste individuel) — le jeton EST la crédence, et il meurt
    avec le serveur ; la reconnexion passe par Claude (outil ouvrir_formulaire), qui rend un nouveau lien.
Les réponses passent par espace_def.repondre (mêmes contrôles que depuis Claude) et sont réinjectées à la
régénération dans les classeurs ET les PDF.

Usage : python formulaire.py --entite "ALPHA SARL" --exercice 2025 [--racine DOSSIER] [--sans-navigateur]
        (depuis Claude : outil MCP ouvrir_formulaire)
"""
import argparse
import base64
import datetime
import html
import http.server
import json
import os
import secrets
import sys
import threading
import time
import urllib.parse
import webbrowser

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ICI), "skills", "dsf-syscohada", "scripts"))
import espace_def as ed  # noqa: E402

VERT, VERT_LOGO = "#3D7A22", "#488800"        # dérivé du logo Facil (#488800) pour un contraste AA de 5,2 sur blanc
INACTIVITE = 15 * 60                          # deux horloges (règle globale §3bis) : inactivité 15 min et durée absolue 12 h,
DUREE_MAX = 12 * 3600                         # tenues par le SERVEUR ; la page ne fait que prévenir, une minute avant
_SERVEURS = {}                                # dossier -> (serveur, url) : un formulaire par dossier de travail


def _logo():
    try:
        return base64.b64encode(open(os.path.join(ICI, "facil_logo.png"), "rb").read()).decode()
    except OSError:
        return ""


CSS = f"""
:root {{ color-scheme:light; --vert:{VERT}; --vert-logo:{VERT_LOGO}; --bouton:{VERT}; --bouton-encre:#fff; --encre:#1a1a1a;
        --gris:#5a5a5a; --trait:#d9dde3; --champ:#8a939e; --fond:#f4f6f8; --surface:#fff; --ambre:#fff4d6; --ambre-encre:#6b4e00;
        --rouge:#a4262c; --rouge-fond:#fdf0f0; --ok:#e3f1dc; --ok-encre:#2d5a14; --imp:#e8eef8; --imp-encre:#1f3864;
        --ombre:0 1px 2px rgba(16,24,40,.06), 0 4px 14px rgba(16,24,40,.06); --rayon:12px; }}
@media (prefers-color-scheme: dark) {{
  :root {{ color-scheme:dark; --vert:#8fce6b; --encre:#e8eaed; --gris:#aab2bc; --trait:#3a4049; --champ:#6b7480; --fond:#121418;
          --surface:#1c1f24; --ambre:#4a3b0c; --ambre-encre:#ffe08a; --rouge:#ff8a8f; --rouge-fond:#3a1d1f; --ok:#1f3a14;
          --ok-encre:#b9e59c; --imp:#1f2c44; --imp-encre:#c6d6f5; --ombre:0 1px 2px rgba(0,0,0,.4); }}
  .entete img {{ background:#fff; border-radius:8px; padding:4px 8px; }}   /* logo noir : posé sur sa plaque claire */
}}
* {{ box-sizing:border-box; }}
[hidden] {{ display:none !important; }}          /* un élément masqué le reste, quel que soit son style d'affichage */
html {{ font-size: clamp(14px, 0.3vw + 12.8px, 16px); }}
body {{ margin:0; font-family:"Segoe UI", system-ui, -apple-system, Arial, sans-serif; color:var(--encre); background:var(--fond);
       line-height:1.45; display:flex; flex-direction:column; min-height:100vh; }}
svg.ic {{ width:18px; height:18px; flex:none; stroke:currentColor; fill:none; stroke-width:2; stroke-linecap:round; stroke-linejoin:round; }}
/* en-tête : logo centré, filet, entité et exercice */
.entete {{ background:var(--surface); padding:.55rem 1rem .6rem; display:flex; flex-direction:column; align-items:center; gap:.35rem;
          border-bottom:3px solid var(--vert-logo); }}
.entete img {{ height:40px; }}
.entete .filet {{ width:min(460px, 80%); border:0; border-top:1px solid var(--trait); margin:.1rem 0; }}
.entete .sous {{ color:var(--gris); font-size:.84rem; text-align:center; overflow-wrap:anywhere; }}
main {{ flex:1; width:100%; max-width:1180px; margin:0 auto; padding:.9rem 1.2rem 0; display:flex; flex-direction:column; }}
/* étapes */
.etapes ol {{ list-style:none; display:flex; gap:.35rem; margin:0 0 .8rem; padding:.2rem; overflow-x:auto; }}
.etapes li {{ flex:1 1 0; min-width:max-content; }}
.etapes a {{ display:flex; align-items:center; gap:.5rem; min-height:44px; padding:.3rem .7rem; border-radius:999px;
            text-decoration:none; color:var(--gris); border:1px solid transparent; font-size:.86rem; white-space:nowrap; }}
.etapes a:hover {{ background:var(--surface); border-color:var(--trait); }}
.etapes .num {{ width:26px; height:26px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center;
               border:2px solid var(--trait); font-weight:700; font-size:.8rem; background:var(--surface); }}
.etapes .fait .num {{ background:var(--ok); border-color:var(--ok-encre); color:var(--ok-encre); }}
.etapes a[aria-current="step"] {{ background:var(--surface); border-color:var(--vert); color:var(--encre); font-weight:600;
                                 box-shadow:var(--ombre); }}
.etapes a[aria-current="step"] .num {{ background:var(--bouton); border-color:var(--bouton); color:var(--bouton-encre); }}
/* cartes */
.carte {{ background:var(--surface); border:1px solid var(--trait); border-radius:var(--rayon); box-shadow:var(--ombre);
         padding:1rem 1.2rem; margin-bottom:.9rem; }}
.carte h2 {{ font-size:1.1rem; margin:0; display:flex; align-items:center; gap:.5rem; }}
.tete-etape {{ display:flex; justify-content:space-between; align-items:baseline; gap:1rem; flex-wrap:wrap; margin-bottom:.2rem; }}
.compteur {{ color:var(--gris); font-size:.84rem; }}
.aide {{ color:var(--gris); font-size:.86rem; margin:.1rem 0 .8rem; }}
.grille {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); gap:.75rem 1rem; }}
.req {{ color:var(--rouge); font-weight:700; margin-left:.15rem; }}
.lignes {{ display:flex; flex-direction:column; gap:.3rem; }}
.champ.ligne {{ display:grid; grid-template-columns:minmax(0, 1fr) minmax(180px, 230px); gap:.3rem 1rem; align-items:center;
               padding:.4rem .8rem; }}
.champ.ligne .ctx {{ margin:.1rem 0 0; }}
@media (max-width: 640px) {{ .champ.ligne {{ grid-template-columns:minmax(0, 1fr); }} }}
select {{ width:100%; min-height:44px; padding:.45rem .75rem; border:1px solid var(--champ); border-radius:8px;
         background:var(--surface); color:var(--encre); font:inherit; }}
select:focus {{ border-color:var(--vert); box-shadow:0 0 0 3px color-mix(in srgb, var(--vert) 22%, transparent); outline:none; }}
@media (max-width: 900px) {{ .grille {{ grid-template-columns:minmax(0, 1fr); }} }}
/* champs */
.champ {{ border:1px solid var(--trait); border-radius:10px; padding:.65rem .8rem; background:var(--surface); min-width:0; }}
.champ.ko {{ border-color:var(--rouge); background:var(--rouge-fond); }}
.champ.rep {{ border-color:color-mix(in srgb, var(--vert) 45%, var(--trait)); }}
.champ .lib {{ font-weight:600; font-size:.93rem; display:flex; gap:.4rem; align-items:flex-start; justify-content:space-between; }}
.champ .ctx {{ color:var(--gris); font-size:.8rem; margin:.1rem 0 .4rem; display:-webkit-box; -webkit-line-clamp:1;
              -webkit-box-orient:vertical; overflow:hidden; }}
.pastilles {{ display:flex; gap:.3rem; flex-wrap:wrap; flex:none; }}
.badge {{ font-size:.7rem; font-weight:700; padding:.1rem .45rem; border-radius:999px; white-space:nowrap; }}
.badge.obl {{ background:var(--ambre); color:var(--ambre-encre); }} .badge.imp {{ background:var(--imp); color:var(--imp-encre); }}
.badge.fait {{ background:var(--ok); color:var(--ok-encre); }}
input[type=text] {{ width:100%; min-height:44px; padding:.45rem .75rem; border:1px solid var(--champ); border-radius:8px;
                   background:var(--surface); color:var(--encre); font:inherit; }}
input[type=text]:focus {{ border-color:var(--vert); box-shadow:0 0 0 3px color-mix(in srgb, var(--vert) 22%, transparent); outline:none; }}
.segment {{ display:inline-flex; flex-wrap:wrap; gap:3px; padding:3px; border:1px solid var(--trait); border-radius:999px;
           background:var(--fond); }}
.segment label {{ position:relative; cursor:pointer; }}
.segment input {{ position:absolute; opacity:0; width:1px; height:1px; }}
.segment span {{ display:inline-flex; align-items:center; gap:.3rem; min-height:40px; padding:0 1rem; border-radius:999px;
                font-size:.9rem; }}
.segment input:checked + span {{ background:var(--bouton); color:var(--bouton-encre); font-weight:600; }}
.segment input:focus-visible + span {{ outline:3px solid #1f6feb; outline-offset:1px; }}
.erreur-champ {{ color:var(--rouge); font-size:.82rem; margin-top:.3rem; }}
/* boutons */
button, .bouton {{ display:inline-flex; align-items:center; justify-content:center; gap:.45rem; min-height:44px; padding:0 1.1rem;
                  border-radius:10px; border:1px solid var(--bouton); background:var(--bouton); color:var(--bouton-encre);
                  font:inherit; font-weight:600; cursor:pointer; text-decoration:none; }}
button.second, .bouton.second {{ background:var(--surface); color:var(--vert); border-color:var(--trait); }}
button:disabled {{ opacity:.5; cursor:not-allowed; }}
:focus-visible {{ outline:3px solid #1f6feb; outline-offset:2px; }}
.barre-actions {{ position:sticky; bottom:0; display:flex; gap:.6rem; align-items:center; justify-content:space-between;
                 flex-wrap:wrap; background:var(--fond); padding:.6rem 0 .7rem; border-top:1px solid var(--trait); margin-top:auto; }}
.barre-actions .droite {{ display:flex; gap:.6rem; flex-wrap:wrap; }}
.msg {{ padding:.55rem .9rem; border-radius:10px; margin-bottom:.8rem; display:flex; gap:.8rem; align-items:center; flex-wrap:wrap; }}
.msg.ok {{ background:var(--ok); color:var(--ok-encre); }} .msg.err {{ background:var(--rouge-fond); color:var(--rouge); }}
/* validation */
.deux {{ display:grid; grid-template-columns:minmax(0, 1.25fr) minmax(0, 1fr); gap:.9rem; align-items:start; }}
@media (max-width: 700px) {{ .deux {{ grid-template-columns:minmax(0, 1fr); }} }}   /* jamais plus large que l'écran */
@media (max-width: 900px) {{ .etapes .txt {{ display:none; }} .etapes a[aria-current="step"] .txt {{ display:inline; }}
  .etapes li {{ flex:0 0 auto; }} .etapes li:has(a[aria-current="step"]) {{ flex:1 1 auto; }} }}
.tuiles {{ display:grid; grid-template-columns:repeat(4, minmax(0, 1fr)); gap:.6rem; margin:.6rem 0; }}
@media (max-width: 640px) {{ .tuiles {{ grid-template-columns:repeat(2, minmax(0, 1fr)); }} }}
.tuiles div {{ background:var(--fond); border-radius:10px; padding:.5rem .7rem; font-size:.8rem; color:var(--gris);
              overflow-wrap:normal; hyphens:auto; }}   /* un libellé ne se coupe jamais au milieu d'un mot */
.tuiles b {{ display:block; font-size:1.25rem; color:var(--encre); }}
.carte.alerte {{ background:var(--ambre); color:var(--ambre-encre); margin-bottom:1rem; }}
.carte.alerte .aide, .carte.alerte h2 {{ color:var(--ambre-encre); }}
.reste {{ list-style:none; padding:0; margin:.2rem 0 .6rem; max-height:7.4rem; overflow:auto; }}
.reste li {{ display:flex; justify-content:space-between; gap:.6rem; padding:.28rem 0; border-bottom:1px solid var(--trait); font-size:.86rem; }}
.reste li span, .pile .dossier small {{ min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.reste a {{ color:var(--vert); font-weight:600; white-space:nowrap; }}
.pile {{ display:flex; flex-direction:column; gap:.55rem; margin-top:.7rem; }}
.pile button {{ justify-content:flex-start; width:100%; min-width:0; text-align:left; overflow:hidden; }}
.pile .dossier {{ display:flex; flex-direction:column; line-height:1.25; min-width:0; }}
.pile .dossier b {{ font-family:Consolas, "Cascadia Mono", monospace; }}
.pile .dossier small {{ font-weight:400; color:var(--gris); font-family:Consolas, "Cascadia Mono", monospace; font-size:.78rem; }}
.fichiers {{ list-style:none; padding:0; margin:.3rem 0 0; font-size:.8rem; color:var(--gris); max-height:7.2rem; overflow:auto;
            font-family:Consolas, "Cascadia Mono", monospace; }}
.valider {{ display:flex; gap:.6rem; flex-wrap:wrap; }}
.valider input {{ flex:1 1 220px; }}
footer {{ background:var(--surface); border-top:1px solid var(--trait); padding:.6rem 1.2rem; font-size:.8rem; color:var(--gris);
         display:flex; justify-content:space-between; flex-wrap:wrap; gap:.4rem; }}
main, .champ, .ctx {{ overflow-wrap:anywhere; }}
@media (max-width: 640px) {{ .entete img {{ height:38px; }} main {{ padding:.7rem .8rem 0; }} .carte {{ padding:.8rem; }}
  .barre-actions {{ flex-wrap:nowrap; }} .barre-actions .droite {{ flex-wrap:nowrap; }}
  .barre-actions .lbl {{ display:none; }} .barre-actions .court {{ display:inline; }}
  .barre-actions button.second {{ padding:0; width:44px; }} }}
.court {{ display:none; }}
.etapes ol {{ scrollbar-width:thin; }}
"""

# icônes Lucide (vectorielles, monochromes), incluses : aucune ressource externe
_IC = {
    "gauche": '<path d="m15 18-6-6 6-6"/>', "droite": '<path d="m9 18 6-6-6-6"/>', "coche": '<path d="M20 6 9 17l-5-5"/>',
    "dossier": '<path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/>',
    "regenerer": '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>',
    "enregistrer": '<path d="M15.2 3a2 2 0 0 1 1.4.6l3.8 3.8a2 2 0 0 1 .6 1.4V19a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/><path d="M17 21v-7a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1v7"/><path d="M7 3v4a1 1 0 0 0 1 1h7"/>',
    "valider": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
}


def _ic(nom):
    return f'<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">{_IC[nom]}</svg>'


SCRIPT = """
(function(){
  var reste = __RESTE__, bord = document.getElementById('preavis'), txt = document.getElementById('preavis-txt');
  var canal = ('BroadcastChannel' in window) ? new BroadcastChannel('facil-def') : null, dernier = Date.now(), tic;
  function fermer(){
    clearInterval(tic); bord.hidden = false; bord.className = 'msg err';
    txt.textContent = 'Formulaire fermé (inactivité ou durée maximale atteinte). Vos réponses enregistrées sont conservées. '
      + 'Relancez-le depuis Claude : « ouvre le formulaire de la DEF ».';
    document.querySelectorAll('button, input').forEach(function(e){ e.disabled = true; });
  }
  function recu(j){ reste = j.reste; bord.hidden = true; }
  // porte l'activité de la page au serveur (une fois par minute au plus) ; un serveur arrêté ne se rouvre pas ainsi
  function battre(){
    dernier = Date.now();
    fetch('/battement', {method:'POST', credentials:'same-origin'})
      .then(function(r){ return r.ok ? r.json() : Promise.reject(); })
      .then(function(j){ recu(j); if (canal) canal.postMessage(j); }).catch(fermer);
  }
  ['keydown','pointerdown','scroll'].forEach(function(ev){
    addEventListener(ev, function(){ if (Date.now() - dernier > 60000) battre(); }, {passive:true}); });
  if (canal) canal.onmessage = function(e){ recu(e.data); };       // un seul décompte pour tous les onglets
  document.getElementById('prolonger').addEventListener('click', battre);
  var cur = document.querySelector('.etapes [aria-current="step"]');    // l'étape en cours reste visible (écran étroit)
  if (cur) cur.scrollIntoView({inline: 'center', block: 'nearest'});
  tic = setInterval(function(){
    reste -= 1;
    if (reste <= 0) { fermer(); return; }
    if (reste <= 60) { bord.hidden = false;
      txt.textContent = 'Sans activité, le formulaire se ferme dans ' + reste + ' s (motif : inactivité).'; }
  }, 1000);
})();
"""

TAILLE = 6                                   # questions par étape : deux colonnes de trois, sans défilement
SCAN = "DEF précédente scannée — montants à vérifier"
ORDRE = ["Sources", SCAN, "Identité de l'entité", "Faits sur l'entreprise", "Réintégrations fiscales (TF1)", "Tiers (TF5)"]
COURT = {"Sources": "Sources", "Identité de l'entité": "Identité", "Faits sur l'entreprise": "Faits",
         "Réintégrations fiscales (TF1)": "Réintégrations", "Tiers (TF5)": "Tiers TF5",
         "Choix d'interprétation (facultatif)": "Interprétations", SCAN: "DEF scannée",
         "Analyse financière (facultatif)": "Analyse"}
AIDE = {"Sources": "Ce qu'il manque pour calculer ou compléter la DEF.",
        "Analyse financière (facultatif)": "Variations significatives entre les deux derniers exercices. Les faits "
                                           "chiffrés et les points à vérifier sont donnés ; la CAUSE, seule l'entreprise "
                                           "la connaît : elle figurera au rapport d'analyse.",
        SCAN: "Montants lus sur la DEF scannée que les formules SYSCOHADA n'ont pas pu prouver. Comparez chacun au "
              "document papier, corrigez si besoin, puis enregistrez : seuls les montants confirmés sont utilisés.",
        "Identité de l'entité": "Saisie une seule fois : reprise sur la page de garde, dans tous les en-têtes et sur la couverture du rapport.",
        "Faits sur l'entreprise": "Des faits que les fichiers ne disent pas ; ils changent le calcul de l'impôt.",
        "Réintégrations fiscales (TF1)": "Propositions du moteur fiscal : chaque décision change l'IS dû.",
        "Tiers (TF5)": "NIF des bénéficiaires déclarés (art. 27.2). Répondez « inconnu » si l'entreprise ne le détient pas.",
        "Choix d'interprétation (facultatif)": "Sans réponse : lecture stricte de la loi. Un autre choix est appliqué, et son écart chiffré au rapport."}


def _page(d, contenu, message="", erreur=False, rafraichir=None, nonce="", reste=INACTIVITE, etapes=""):
    man = ed.lire_json(os.path.join(d, "manifeste.json"), {})
    v = (man.get("versions") or [{}])[-1]
    annee = datetime.date.today().year                  # année CALCULÉE, jamais écrite
    logo = _logo()
    meta = f'<meta http-equiv="refresh" content="{rafraichir}">' if rafraichir else ""
    msg = f'<div class="msg {"err" if erreur else "ok"}" role="status">{message}</div>' if message else ""
    sous = " · ".join(x for x in (html.escape(man.get("entite", "")),
                                  f"exercice clos le 31/12/{html.escape(str(man.get('exercice', '')))}",
                                  f"version {v['version']} — {html.escape(str(v.get('statut', '')))}" if v.get("version") else "") if x)
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
{meta}<title>DEF {html.escape(str(man.get('exercice', '')))} — {html.escape(man.get('entite', ''))}</title><style>{CSS}</style></head>
<body><header class="entete">{f'<img src="data:image/png;base64,{logo}" alt="Facil">' if logo else ''}<hr class="filet">
<div class="sous">{sous}</div></header>
<main><div id="preavis" class="msg" role="alert" hidden><span id="preavis-txt"></span>
<button type="button" id="prolonger" class="second">Rester connecté</button></div>{etapes}
{msg}{contenu}</main>
<footer><span>© Facil - AI Solutions Architect - Emac SAH {annee}</span>
<span>Données traitées exclusivement sur ce poste · formulaire local</span></footer>
{f'<script nonce="{nonce}">{SCRIPT.replace("__RESTE__", str(int(reste)))}</script>' if nonce else ''}</body></html>"""


def _etat(d):
    man = ed.lire_json(os.path.join(d, "manifeste.json"), {})
    v = (man.get("versions") or [{}])[-1]
    return v, man


def _questions(d):
    qs = ed.lire_json(os.path.join(d, "04_questions", "questions.json"), [])
    rep = ed.lire_json(os.path.join(d, "04_questions", "reponses.json"), {})
    for q in qs:
        q["reponse"] = rep.get(q["id"], q.get("reponse"))
    return qs


# codes internes -> mots de l'utilisateur (jamais « True », « ca » ou « ligne_distincte » à l'écran)
CLAIR = {True: "oui", False: "non", "True": "oui", "False": "non", "ca": "chiffre d'affaires", "produits": "tous les produits",
         "ligne_distincte": "ligne distincte", "dans_paiements": "dans les « pagos »",
         "syscohada": "SYSCOHADA système normal", "ge": "format GE (DEF déposée)"}
UNE_ETAPE = ("Identité de l'entité", "Choix d'interprétation (facultatif)")
EN_LIGNES = ("Choix d'interprétation (facultatif)",)       # choix d'expert : une ligne compacte chacun


def _poids(q):
    """Place qu'une question prend à l'écran (1 = libellé court + un champ) : libellé long, choix nombreux -> plus."""
    w = 1.0
    if len(q.get("question") or "") > 95:
        w += 0.5
    if sum(len(str(o)) for o in q.get("options") or []) > 34:
        w += 0.5
    return w


def _etapes(qs):
    """Une étape par catégorie (obligatoires d'abord, dans l'ordre métier), découpée en parties de TAILLE questions ;
    la dernière étape est la validation. [{titre, court, partie, n, questions, validation}]"""
    cats = {}
    for q in qs:
        cats.setdefault(q["categorie"], []).append(q)
    ordre = sorted(cats, key=lambda c: (not any(q["obligatoire"] for q in cats[c]), ORDRE.index(c) if c in ORDRE else 99))
    out = []
    for c in ordre:
        parts, cur, charge = [], [], 0.0
        for q in cats[c]:                                # découpe au POIDS : une question longue compte davantage
            w = _poids(q)
            # l'identité tient TOUJOURS en une étape (un seul formulaire) ; les autres catégories se découpent
            if cur and c not in UNE_ETAPE and (charge + w > TAILLE or len(cur) >= TAILLE):
                parts.append(cur)
                cur, charge = [], 0.0
            cur.append(q)
            charge += w
        if cur:
            parts.append(cur)
        n = len(parts)
        for i, qs_ in enumerate(parts):
            out.append({"titre": c, "court": COURT.get(c, c) + (f" {i + 1}/{n}" if n > 1 else ""), "partie": i + 1, "n": n,
                        "questions": qs_, "validation": False})
    out.append({"titre": "Validation", "court": "Validation", "questions": [], "validation": True})
    return out


def _complete(e):
    return bool(e["questions"]) and all(q.get("reponse") for q in e["questions"] if q["obligatoire"]) and \
        (any(q["obligatoire"] for q in e["questions"]) or all(q.get("reponse") for q in e["questions"]))


def _barre_etapes(etapes, k):
    lis = []
    for i, e in enumerate(etapes):
        cur = ' aria-current="step"' if i == k else ""
        fait = _complete(e)
        num = _ic("coche") if fait and i != k else str(i + 1)
        lis.append(f'<li class="{"fait" if fait else ""}"><a href="/?e={i}"{cur}><span class="num">{num}</span>'
                   f'<span class="txt">{html.escape(e["court"])}</span></a></li>')
    return f'<nav class="etapes" aria-label="Étapes"><ol>{"".join(lis)}</ol></nav>'


def _champ(q, erreurs, commun=None, ligne=False):
    nom = html.escape(q["id"])
    val = q.get("reponse") or ""
    fid = "q_" + "".join(ch if ch.isalnum() else "_" for ch in q["id"])
    # sobre : l'obligatoire est un astérisque ; seul l'impact (effet chiffré) garde une pastille
    req = '<span class="req" aria-label="obligatoire">*</span>' if q["obligatoire"] else ""
    badges = f'<span class="badge imp">{html.escape(q["impact"])}</span>' if q.get("impact") else ""
    if q.get("options"):
        options = list(q["options"])
        if val and val not in options:                   # valeur enregistrée hors liste : reste lisible (et cochée)
            options.append(val)
        clair = lambda x: CLAIR.get(x, str(x).replace("_", " "))                                                  # noqa: E731
        lib = lambda o: f"par défaut ({clair(q.get('defaut'))})" if o == "defaut" else clair(o)                    # noqa: E731
        if len(options) > 4 or ligne:                    # liste longue, ou présentation en lignes : liste déroulante
            # un choix facultatif part présélectionné sur son défaut : rien à faire si l'on ne veut pas s'en écarter
            choisi = val or ("defaut" if "defaut" in options else "")
            opts = "".join(f'<option value="{html.escape(o)}"{" selected" if o == choisi else ""}>{html.escape(lib(o))}</option>'
                           for o in options)
            vide = "" if choisi else '<option value="" selected>— choisir —</option>'
            entree = f'<select name="{nom}" aria-labelledby="{fid}">{vide}{opts}</select>'
        else:
            opts = "".join(f'<label><input type="radio" name="{nom}" value="{html.escape(o)}"{" checked" if o == val else ""}>'
                           f'<span>{html.escape(lib(o))}</span></label>' for o in options)
            entree = f'<div class="segment" role="radiogroup" aria-labelledby="{fid}">{opts}</div>'
    else:
        # montant lu sur un scan : PROPOSÉ dans le champ, enregistré seulement quand l'utilisateur valide l'étape
        propose = val or q.get("proposition") or ""
        entree = (f'<input type="text" id="{fid}_in" name="{nom}" value="{html.escape(str(propose))}" aria-labelledby="{fid}" '
                  f'autocomplete="off"{" inputmode=numeric" if q.get("proposition") else ""}>')
    err = erreurs.get(q["id"])
    ctx = html.escape(q.get("contexte") or "") if q.get("contexte") != commun else ""   # contexte commun : dit une fois
    ctx_html = f'<div class="ctx" title="{ctx}">{ctx}</div>' if ctx else ""
    if ligne:                                            # question (et contexte) à gauche, choix à droite
        return (f'<div class="champ ligne{" ko" if err else ""}{" rep" if val else ""}"><div><div class="lib">'
                f'<span id="{fid}">{html.escape(q["question"])}{req}</span></div>{ctx_html}</div>{entree}'
                f'{f"<div class=erreur-champ role=alert>{html.escape(err)}</div>" if err else ""}</div>')
    return (f'<div class="champ{" ko" if err else ""}{" rep" if val else ""}">'
            f'<div class="lib"><span id="{fid}">{html.escape(q["question"])}{req}</span><span class="pastilles">{badges}</span></div>'
            f'{ctx_html}{entree}'
            f'{f"<div class=erreur-champ role=alert>{html.escape(err)}</div>" if err else ""}</div>')


def _etape_questions(etapes, k, jeton, erreurs):
    e = etapes[k]
    suivant = etapes[k + 1]["court"] if k + 1 < len(etapes) else ""
    compteur = f"Étape {k + 1} sur {len(etapes)}" + (f" · partie {e['partie']} sur {e['n']}" if e["n"] > 1 else "")
    prec = (f'<button type="submit" name="aller" value="precedent" class="second" aria-label="Précédent">{_ic("gauche")}'
            f'<span class="lbl">Précédent</span></button>' if k > 0 else "<span></span>")
    ctxs = {q.get("contexte") for q in e["questions"]}
    commun = ctxs.pop() if len(ctxs) == 1 and len(e["questions"]) > 1 else None   # même contexte partout : une seule fois
    aide = commun or AIDE.get(e["titre"], "")
    return (f'<form method="post" action="/repondre" class="etape-form"><input type="hidden" name="t" value="{jeton}">'
            f'<input type="hidden" name="etape" value="{k}"><section class="carte" aria-labelledby="titre-etape">'
            f'<div class="tete-etape"><h2 id="titre-etape">{html.escape(e["titre"])}</h2><span class="compteur">{compteur}</span></div>'
            f'<p class="aide">{html.escape(aide)}'
            f'{" <span class=req>*</span> obligatoire" if any(q["obligatoire"] for q in e["questions"]) else ""}</p>'
            + (f'<div class="lignes">{"".join(_champ(q, erreurs, commun, ligne=True) for q in e["questions"])}</div></section>'
               if e["titre"] in EN_LIGNES else
               f'<div class="grille">{"".join(_champ(q, erreurs, commun) for q in e["questions"])}</div></section>') +
            f'<div class="barre-actions">{prec}<div class="droite">'
            f'<button type="submit" name="aller" value="rester" class="second" aria-label="Enregistrer">{_ic("enregistrer")}'
            f'<span class="lbl">Enregistrer</span></button>'
            f'<button type="submit" name="aller" value="suivant"><span class="lbl">Enregistrer et suivant : {html.escape(suivant)}</span>'
            f'<span class="court">Suivant</span>{_ic("droite")}</button>'
            f'</div></div></form>')


def _etape_validation(d, etapes, k, jeton, sources_changees=False):
    v, man = _etat(d)
    qs = [q for e in etapes for q in e["questions"]]
    obl = [q for q in qs if q["obligatoire"]]
    ouvertes = [(i, q) for i, e in enumerate(etapes) for q in e["questions"] if q["obligatoire"] and not q.get("reponse")]
    tuiles = (f'<div class="tuiles"><div>Version<b>{v.get("version", "—")}</b></div>'
              f'<div>Statut<b>{html.escape(str(v.get("statut", "aucune")))}</b></div>'
              f'<div>Obligatoires ouvertes<b>{len(ouvertes)} / {len(obl)}</b></div>'
              f'<div>Facultatives<b>{sum(1 for q in qs if not q["obligatoire"])}</b></div></div>')
    reste = "".join(f'<li><span title="{html.escape(q["question"])}">{html.escape(q["question"])}</span>'
                    f'<a href="/?e={i}">Répondre</a></li>' for i, q in ouvertes)
    recap = (f'<section class="carte"><h2>{_ic("valider")}Récapitulatif et validation</h2>{tuiles}'
             + (f'<p class="aide">Questions obligatoires encore ouvertes :</p><ul class="reste">{reste}</ul>' if ouvertes else
                '<p class="aide">Toutes les questions obligatoires ont une réponse.</p>')
             + f'<form method="post" action="/valider"><input type="hidden" name="t" value="{jeton}">'
               f'<label class="lib" for="par">Valider la version définitive — nom de la personne qui valide</label>'
               f'<div class="valider"><input type="text" id="par" name="par" required autocomplete="name">'
               f'<button type="submit"{" disabled" if ouvertes or sources_changees else ""}>{_ic("valider")}Valider</button></div>'
               f'<p class="aide">{"Régénérez d’abord : 01_sources a changé depuis cette version (voir le bandeau)." if sources_changees else "Possible quand toutes les questions obligatoires ont une réponse." if ouvertes else "Produit la version définitive, sans filigrane, tracée dans le manifeste et le rapport de contrôle."}</p></form></section>')
    livr = v.get("livrables", [])
    dossiers = [("03_pdf", "Ouvrir le dossier des PDF"), ("02_xls", "Ouvrir le dossier des classeurs")]
    # nom du dossier en évidence ; chemin complet sur une ligne (entier au survol)
    # sobre : l'intitulé seul (ni chemin ni nom de dossier) ; le bouton ouvre le dossier sur le poste
    boutons = "".join(f'<button class="second" name="quoi" value="{q}">{_ic("dossier")}{lab}</button>' for q, lab in dossiers)
    n_xls = sum(1 for x in livr if x.lower().endswith(".xlsx"))
    de_version = f" de la version {v['version']}" if v.get("version") else ""
    livrables = (f'<section class="carte"><h2>{_ic("dossier")}Livrables{de_version}</h2>'
                 f'<p class="aide">{n_xls} classeur(s) · {len(livr) - n_xls} PDF</p>'
                 f'<form method="post" action="/ouvrir" class="pile"><input type="hidden" name="t" value="{jeton}">{boutons}</form>'
                 f'<form method="post" action="/regenerer" class="pile"><input type="hidden" name="t" value="{jeton}">'
                 f'<button type="submit">{_ic("regenerer")}Régénérer la DEF avec les réponses</button></form></section>')
    retour = (f'<div class="barre-actions"><a class="bouton second" href="/?e={max(k - 1, 0)}">{_ic("gauche")}Précédent</a>'
              f'<span></span></div>')
    return f'<div class="deux">{recap}{livrables}</div>{retour}'


def _modif_sources(d):
    """Fichiers ajoutés, remplacés ou retirés dans 01_sources depuis la dernière version ({} si rien)."""
    try:
        return ed.sources_modifiees(d) or {}
    except Exception:                                    # noqa: BLE001 — une sonde ne casse pas la page
        return {}


ROLES_CLAIRS = {"balance": "balance", "grand_livre": "grand livre", "modele_dsf": "DEF précédente", "logo": "logo",
                "fiche_entite": "fiche entité", "pdf_scanne": "PDF scanné (non lu sans OCR)", "def_pdf": "DEF en PDF"}


def _bandeau_sources(modif, jeton):
    """Incident du 16/10/2026 : une DEF déposée APRÈS la génération restait invisible, et la question « DEF
    précédente » bloquait la validation. Le formulaire le DIT, et offre le seul bon geste : régénérer."""
    if not modif:
        return ""
    verbes = {"ajoutes": "nouveau fichier", "remplaces": "fichier remplacé", "retires": "fichier retiré"}   # accord neutre
    items = "".join(f"<li>{html.escape(x['fichier'])} — {ROLES_CLAIRS.get(x['role'], x['role'])} : {verbes[k]}</li>"
                    for k in verbes for x in modif.get(k, []))
    return (f'<section class="carte alerte" role="status" aria-labelledby="titre-sources"><h2 id="titre-sources">'
            f'{_ic("regenerer")}Nouveaux fichiers dans 01_sources</h2>'
            f'<p class="aide">Depuis la version {html.escape(str(modif.get("depuis_version")))}, 01_sources a changé. '
            f'Régénérez pour les prendre en compte : les questions se mettent à jour (par exemple, celle de la DEF '
            f'précédente disparaît quand elle est reconnue).</p><ul class="reste">{items}</ul>'
            f'<form method="post" action="/regenerer" class="pile"><input type="hidden" name="t" value="{jeton}">'
            f'<button type="submit">{_ic("regenerer")}Régénérer maintenant</button></form></section>')


def _accueil(d, jeton, erreurs=None, message="", erreur=False, nonce="", reste=INACTIVITE, etape=None):
    erreurs = erreurs or {}
    etapes = _etapes(_questions(d))
    modif = _modif_sources(d)
    if etape is None or not (0 <= etape < len(etapes)):
        # par défaut : la première étape qui a encore une question obligatoire ouverte, sinon la validation
        etape = next((i for i, e in enumerate(etapes) if any(q["obligatoire"] and not q.get("reponse") for q in e["questions"])),
                     len(etapes) - 1)
    if erreurs:                                          # erreurs : l'étape qui porte la première question refusée
        etape = next((i for i, e in enumerate(etapes) if any(q["id"] in erreurs for q in e["questions"])), etape)
    e = etapes[etape]
    contenu = _bandeau_sources(modif, jeton) + (_etape_validation(d, etapes, etape, jeton, bool(modif)) if e["validation"]
                                                 else _etape_questions(etapes, etape, jeton, erreurs))
    return _page(d, contenu, message, erreur, nonce=nonce, reste=reste, etapes=_barre_etapes(etapes, etape))


class Gestionnaire(http.server.BaseHTTPRequestHandler):
    server_version = "FacilDEF"

    def log_message(self, *a):                          # aucun journal d'accès sur la sortie standard
        pass

    def _autorise(self, params):
        hote = (self.headers.get("Host") or "").split(":")[0]
        if hote not in ("127.0.0.1", "localhost"):
            return False
        cookie = dict(x.strip().split("=", 1) for x in (self.headers.get("Cookie") or "").split(";") if "=" in x)
        jeton = params.get("t", [None])[0] or cookie.get("facil_t")
        return secrets.compare_digest(str(jeton or ""), self.server.jeton)

    def _envoyer(self, code, corps, type_="text/html; charset=utf-8", nonce=""):
        b = corps.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", type_)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Frame-Options", "DENY")
        # « same-origin » et NON « no-referrer » : avec no-referrer, Chrome et Edge envoient « Origin: null » sur
        # chaque POST, et la garde d'origine refusait le formulaire lui-même (incident du 16-17/10/2026 :
        # « Suivant » → page « Origine refusée », réponses non enregistrées). Le référent ne quitte toujours pas le poste.
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; img-src data:; "
                         "connect-src 'self'; form-action 'self'; frame-ancestors 'none'"
                         + (f"; script-src 'nonce-{nonce}'" if nonce else ""))
        if code < 400:
            self.send_header("Set-Cookie", f"facil_t={self.server.jeton}; HttpOnly; SameSite=Strict; Path=/")
        self.end_headers()
        self.wfile.write(b)

    def _entree(self, params):
        """Contrôle commun : jeton, puis les deux horloges. Le SERVEUR décide ; une requête refusée ne prolonge rien."""
        if not self._autorise(params):
            self._envoyer(403, "<h1>Accès refusé</h1><p>Ouvrez le formulaire depuis le lien fourni par Claude.</p>")
            return False
        motif = self.server.motif_fin()
        if motif:
            self._envoyer(401, f"<h1>Formulaire fermé</h1><p>Motif : {motif}. Vos réponses enregistrées sont conservées. "
                               "Relancez-le depuis Claude : « ouvre le formulaire de la DEF ».</p>")
            self.server.fermer(motif)
            return False
        self.server.derniere = time.time()
        return True

    # Aucune erreur ne doit produire une page BLANCHE (incident du 17/10/2026 : l'utilisateur restait bloqué
    # sans savoir quoi faire). Toute erreur imprévue rend une page qui dit ce qui s'est passé et quoi faire.
    def do_GET(self):
        self._sans_page_blanche(self._get)

    def do_POST(self):
        self._sans_page_blanche(self._post)

    def _sans_page_blanche(self, traiter):
        try:
            traiter()
        except Exception as e:                                       # noqa: BLE001 — filet de dernier recours
            import traceback
            traceback.print_exc(file=sys.stderr)                     # trace pour le journal, jamais pour la page
            indisponible = isinstance(e, getattr(ed, "FichierIndisponible", ()))
            cause = str(e) if indisponible else f"erreur inattendue du formulaire ({type(e).__name__} : {e})"
            conseil = ("Un autre programme tenait un fichier du dossier de travail (antivirus, indexation Windows, "
                       "synchronisation). Attendez quelques secondes, puis cliquez sur « Réessayer »."
                       if indisponible else "Cliquez sur « Réessayer ». Si l'erreur revient, demandez à Claude "
                       "de relancer le formulaire de la DEF, et transmettez le fichier 04_questions\\erreurs_formulaire.log.")
            self._journaliser_erreur(e)
            corps = (f'<section class="carte" role="alert"><h2>L\u2019enregistrement n\u2019a pas abouti</h2>'
                     f'<p>{html.escape(cause)}</p><p>{html.escape(conseil)}</p>'
                     f'<p>Les réponses déjà enregistrées sont conservées.</p>'
                     f'<p><a class="bouton" href="/?e={html.escape(self._etape_demandee())}">Réessayer</a></p></section>')
            try:
                self._envoyer(503 if indisponible else 500, _page(self.server.dossier, corps, erreur=True))
            except Exception:                                       # noqa: BLE001 — la page d'erreur elle-même a échoué
                self._envoyer(500, "<h1>L'enregistrement n'a pas abouti</h1><p>Réessayez, ou relancez le formulaire depuis Claude.</p>")

    def _journaliser_erreur(self, e):
        """Trace LOCALE de l'erreur, dans le dossier de l'exercice : sans elle, une panne chez l'utilisateur ne se
        diagnostique pas (constaté le 17/10/2026). Elle ne quitte jamais le poste."""
        try:
            import traceback
            p = os.path.join(self.server.dossier, "04_questions", "erreurs_formulaire.log")
            with open(p, "a", encoding="utf-8") as f:
                f.write(f"--- {time.strftime('%Y-%m-%d %H:%M:%S')} {self.command} {urllib.parse.urlparse(self.path).path}\n")
                f.write("".join(traceback.format_exception(type(e), e, e.__traceback__)))
        except Exception:                                           # noqa: BLE001 — le journal ne doit rien casser
            pass

    def _etape_demandee(self):
        try:
            return str(int(urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("e", ["0"])[0]))
        except ValueError:
            return "0"

    def _get(self):
        u = urllib.parse.urlparse(self.path)
        if not self._entree(urllib.parse.parse_qs(u.query)):
            return
        if u.path == "/etat":
            return self._envoyer(200, json.dumps({"en_cours": self.server.occupe(), "reste": self.server.reste()}),
                                 "application/json")
        if self.server.occupe():
            return self._envoyer(200, _page(self.server.dossier, '<p class="carte" role="status">Génération en cours… '
                                            'cette page se met à jour toute seule.</p>', rafraichir=3))
        msg, err = self.server.dernier_message
        self.server.dernier_message = ("", False)
        nonce = secrets.token_urlsafe(12)
        e = (urllib.parse.parse_qs(u.query).get("e") or [""])[0]
        etape = int(e) if e.isdigit() else (10_000 if e == "v" else None)       # « v » : l'étape de validation
        if etape == 10_000:
            etape = len(_etapes(_questions(self.server.dossier))) - 1
        return self._envoyer(200, _accueil(self.server.dossier, self.server.jeton, message=msg, erreur=err, nonce=nonce,
                                           reste=self.server.reste(), etape=etape), nonce=nonce)

    def _en_fond(self, fonction, libelle):
        def travail():
            try:
                r = fonction()
                if r.get("statut") == "refuse":
                    self.server.dernier_message = (f"{libelle} refusée : {r.get('raison', '')}", True)
                else:
                    self.server.dernier_message = (
                        f"Version {r.get('version')} produite ({r.get('statut')}) — "
                        f"{r.get('questions_obligatoires_ouvertes', 0)} question(s) obligatoire(s) ouverte(s).", False)
            except (Exception, SystemExit) as e:             # l'échec se dit, il ne se tait pas
                self.server.dernier_message = (f"Échec — {libelle} : {e}", True)
        self.server.tache = threading.Thread(target=travail, daemon=True)
        self.server.tache.start()

    def _post(self):
        n = min(int(self.headers.get("Content-Length") or 0), 1_000_000)    # lecture bornée
        donnees = urllib.parse.parse_qs(self.rfile.read(n).decode("utf-8", "replace"), keep_blank_values=True)
        origine = self.headers.get("Origin")
        if origine and urllib.parse.urlparse(origine).hostname not in ("127.0.0.1", "localhost"):
            return self._envoyer(403, _page(self.server.dossier, '<section class="carte" role="alert"><h2>Requête refusée</h2>'
                                  "<p>Cette demande ne vient pas du formulaire ouvert sur ce poste (origine étrangère). "
                                  "Rien n'a été enregistré.</p><p><a class=\"bouton\" href=\"/\">Revenir au formulaire</a></p></section>",
                                  erreur=True))
        if not self._entree(donnees):
            return
        d = self.server.dossier
        chemin = urllib.parse.urlparse(self.path).path
        vers = "/?e=v"                                   # après une action de l'étape de validation : on y revient
        if chemin == "/battement":
            return self._envoyer(200, json.dumps({"reste": self.server.reste()}), "application/json")
        if self.server.occupe() and chemin in ("/repondre", "/regenerer", "/valider"):
            self.server.dernier_message = ("Une génération est déjà en cours : patientez.", True)
        elif chemin in ("/repondre", "/regenerer"):
            actuelles = ed.lire_json(os.path.join(d, "04_questions", "reponses.json"), {})
            erreurs, n_ok = {}, 0
            for k, v in donnees.items():
                if k in ("t", "etape", "aller") or k.startswith("_"):
                    continue
                val = v[0].strip()
                if not val or actuelles.get(k) == val:
                    continue
                try:
                    ed.repondre(d, k, val, canal="formulaire")
                    n_ok += 1
                except SystemExit as e:
                    erreurs[k] = str(e)
            if erreurs:                                  # on reste sur l'étape, champs refusés signalés
                nonce = secrets.token_urlsafe(12)
                return self._envoyer(200, _accueil(d, self.server.jeton, erreurs, f"{len(erreurs)} réponse(s) refusée(s) — "
                                                   "corrigez les champs signalés.", True, nonce, self.server.reste()), nonce=nonce)
            if chemin == "/regenerer":
                self._en_fond(lambda: ed.generer(d), "génération")
            else:
                # chaque « Suivant » ENREGISTRE : une fermeture du formulaire ne perd rien
                k = int((donnees.get("etape") or ["0"])[0] or 0)
                aller = (donnees.get("aller") or ["rester"])[0]
                vers = f"/?e={max(k + (1 if aller == 'suivant' else -1 if aller == 'precedent' else 0), 0)}"
                if n_ok:
                    self.server.dernier_message = (f"{n_ok} réponse(s) enregistrée(s). Régénérez la DEF à l'étape "
                                                   "Validation pour les y voir.", False)
        elif chemin == "/valider":
            par = (donnees.get("par") or [""])[0].strip()
            self._en_fond(lambda: ed.valider(d, par), "validation")
        elif chemin == "/ouvrir":
            quoi = (donnees.get("quoi") or [""])[0]
            if quoi in ("02_xls", "03_pdf") and hasattr(os, "startfile"):    # liste fermée : jamais un chemin du navigateur
                os.startfile(os.path.join(d, quoi))                           # noqa: S606
        self.send_response(303)
        self.send_header("Location", vers)
        self.end_headers()


class Serveur(http.server.ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, dossier, inactivite, duree_max):
        super().__init__(("127.0.0.1", 0), Gestionnaire)
        self.dossier, self.inactivite, self.duree_max = dossier, inactivite, duree_max
        self.jeton, self.debut = secrets.token_urlsafe(24), time.time()
        self.derniere, self.tache, self.actif, self.motif = self.debut, None, True, None
        self.dernier_message = ("", False)

    def occupe(self):
        return bool(self.tache and self.tache.is_alive())

    def motif_fin(self, maintenant=None):
        t = time.time() if maintenant is None else maintenant
        if not self.actif:
            return self.motif or "arrêté"
        if t - self.debut > self.duree_max:              # la durée absolue borne même une session active
            return "durée maximale atteinte"
        if t - self.derniere > self.inactivite and not self.occupe():
            return "inactivité"
        return None

    def reste(self):
        t = time.time()
        return max(0, int(min(self.inactivite - (t - self.derniere), self.duree_max - (t - self.debut))))

    def fermer(self, motif):
        if self.actif:
            self.actif, self.motif = False, motif
            threading.Thread(target=self.shutdown, daemon=True).start()


def demarrer(dossier, navigateur=True, inactivite=INACTIVITE, duree_max=DUREE_MAX):
    """Démarre (ou retrouve) le formulaire d'un dossier de travail ; retourne son adresse (jeton compris)."""
    if dossier in _SERVEURS and not _SERVEURS[dossier][0].motif_fin():
        url = _SERVEURS[dossier][1]
    else:
        srv = Serveur(dossier, inactivite, duree_max)
        url = f"http://127.0.0.1:{srv.server_address[1]}/?t={srv.jeton}"

        def veille():                                    # ferme aussi sans requête : un onglet abandonné ne garde rien ouvert
            while srv.actif:
                time.sleep(min(30, max(min(inactivite, duree_max) / 4, 0.05)))
                motif = srv.motif_fin()
                if motif:
                    srv.fermer(motif)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        threading.Thread(target=veille, daemon=True).start()
        _SERVEURS[dossier] = (srv, url)
    if navigateur:
        webbrowser.open(url)
    return url


def main():
    p = argparse.ArgumentParser(description="Formulaire local de la DEF.")
    p.add_argument("--entite", required=True)
    p.add_argument("--exercice", type=int, required=True)
    p.add_argument("--racine")
    p.add_argument("--sans-navigateur", action="store_true")
    a = p.parse_args()
    d = ed.init(a.racine, a.entite, a.exercice)
    url = demarrer(d, navigateur=not a.sans_navigateur)
    print(f"Formulaire : {url}  (arrêt après {INACTIVITE // 60} min d'inactivité ou {DUREE_MAX // 3600} h ; Ctrl+C pour arrêter)")
    try:
        while _SERVEURS[d][0].actif:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
