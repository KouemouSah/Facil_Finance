# -*- coding: utf-8 -*-
"""Flyer commercial Facil DEF : création libre (HTML/CSS, A4 pleine page), imprimée en PDF par Edge sans en-tête.
Charte Facil (couleurs et polices du thème), logo Facil, icônes Lucide (vectorielles, monochromes)."""
import base64
import glob
import os
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
THEME = r"C:\Users\DELL\claude-plugins\plugins\documents-pro\themes\facil"
ICONES = os.path.join(os.environ["LOCALAPPDATA"], "documents-pro", "icones")
POLICES = os.path.join(os.environ["LOCALAPPDATA"], "Microsoft", "Windows", "Fonts")
SORTIE = os.path.abspath(os.path.join(ICI, "..", "..", "livrable", "Flyer-Facil-DEF.pdf"))
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def ico(nom, taille=24, couleur="currentColor", trait=2):
    svg = open(os.path.join(ICONES, f"{nom}.svg"), encoding="utf-8").read()
    svg = svg[svg.index("<svg"):]
    svg = svg.replace('width="24"', f'width="{taille}"').replace('height="24"', f'height="{taille}"')
    return svg.replace('stroke="currentColor"', f'stroke="{couleur}"').replace('stroke-width="2"', f'stroke-width="{trait}"')


def b64(p):
    return base64.b64encode(open(p, "rb").read()).decode()


def police(motif):
    p = next(iter(sorted(glob.glob(os.path.join(POLICES, motif)))), None)
    return "file:///" + p.replace("\\", "/") if p else None


FONTS = {"Poppins": [("PoppinsBold*", 700), ("PoppinsSemiBold*", 600), ("PoppinsMedium*", 500)],
         "Inter": [("Inter-Regular*", 400), ("Inter_*Regular*", 400), ("InterSemiBold*", 600), ("Inter-SemiBold*", 600),
                   ("InterBold*", 700), ("Inter-Bold*", 700)]}
faces = []
for fam, lst in FONTS.items():
    for motif, poids in lst:
        u = police(motif)
        if u:
            faces.append(f"@font-face{{font-family:'{fam}F';src:url('{u}');font-weight:{poids};}}")

VERT, VERT_T, NUIT, CLAIR, FOND, ENCRE, TEXTE, GRIS = "#468C00", "#326E00", "#1B4A1F", "#9CCB5E", "#EEF5E4", "#141414", "#33372F", "#5E645A"

html = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>
{''.join(faces)}
@page {{ size: A4; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: 210mm; height: 297mm; }}
body {{ font-family: 'InterF', 'Inter', sans-serif; color: {TEXTE}; font-size: 10pt; line-height: 1.45;
       -webkit-print-color-adjust: exact; print-color-adjust: exact; overflow: hidden; position: relative; }}
.titre {{ font-family: 'PoppinsF', 'Poppins', sans-serif; }}

/* ---------- ouverture */
.hero {{ position: relative; height: 96mm; padding: 10mm 16mm 0 16mm; color: #fff; overflow: hidden;
        background: radial-gradient(120% 140% at 85% 10%, #1d6b31 0%, #105C2C 38%, #0E3416 100%); }}
.hero .filigrane {{ position: absolute; right: -22mm; top: -6mm; width: 112mm; opacity: .10; }}
.hero .logo {{ height: 11mm; }}
.tag {{ display: inline-block; margin-top: 7mm; font-weight: 600; font-size: 7.6pt; letter-spacing: .22em;
        text-transform: uppercase; color: {CLAIR}; border: 1px solid rgba(156,203,94,.55); border-radius: 20mm;
        padding: 1.4mm 3.6mm; }}
.h1 {{ margin-top: 4mm; font-size: 30pt; line-height: 1.04; font-weight: 700; letter-spacing: -.01em; }}
.h1 em {{ font-style: normal; color: {CLAIR}; }}
.chapo {{ margin-top: 3.5mm; width: 150mm; font-size: 10.5pt; line-height: 1.5; color: #DCE8D2; }}
.chapo b {{ color: #fff; font-weight: 600; }}

/* ---------- douleurs */
.douleurs {{ margin: -5mm 16mm 0 16mm; position: relative; background: #fff; border-radius: 4mm;
            box-shadow: 0 3mm 9mm rgba(14,52,22,.18); padding: 4.5mm 6mm 4.5mm 6mm; }}
.douleurs h2 {{ font-size: 13pt; color: {ENCRE}; font-weight: 700; margin-bottom: 3.5mm; }}
.douleurs .grille {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 5mm; }}
.douleur {{ display: flex; gap: 3mm; align-items: flex-start; }}
.douleur .pastille {{ flex: none; width: 10mm; height: 10mm; border-radius: 50%; background: #FBEDEA;
                     display: flex; align-items: center; justify-content: center; }}
.douleur b {{ display: block; font-family: 'PoppinsF', sans-serif; font-weight: 600; color: {ENCRE}; font-size: 9.6pt;
             line-height: 1.25; margin-bottom: 1mm; }}
.douleur span {{ font-size: 8.6pt; color: {GRIS}; line-height: 1.4; }}

/* ---------- promesse en 3 étapes */
.section {{ padding: 0 16mm; }}
.surtitre {{ margin-top: 4.5mm; font-weight: 600; font-size: 7.6pt; letter-spacing: .22em; text-transform: uppercase;
            color: {VERT_T}; }}
.h2 {{ font-size: 16pt; font-weight: 700; color: {ENCRE}; line-height: 1.15; margin-top: 1.5mm; }}
.h2 em {{ font-style: normal; color: {VERT}; }}
.etapes {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 0; margin-top: 3.5mm; position: relative; }}
.etape {{ padding: 0 4mm 0 0; position: relative; }}
.etape .num {{ font-family: 'PoppinsF', sans-serif; font-weight: 700; font-size: 24pt; line-height: 1; color: {FOND};
              -webkit-text-stroke: 1.2px {VERT}; }}
.etape .ic {{ position: absolute; top: 0.5mm; left: 15mm; width: 9mm; height: 9mm; border-radius: 3mm;
             background: {VERT}; display: flex; align-items: center; justify-content: center; }}
.etape b {{ display: block; margin-top: 1.5mm; font-family: 'PoppinsF', sans-serif; font-weight: 700; font-size: 11.5pt;
           color: {ENCRE}; }}
.etape span {{ font-size: 8.8pt; color: {TEXTE}; }}
.fleche {{ position: absolute; top: 4mm; right: 3mm; }}

/* ---------- bénéfices + bonus */
.duo {{ display: grid; grid-template-columns: 1.32fr 1fr; gap: 5mm; margin-top: 4mm; }}
.benef {{ display: grid; grid-template-columns: 1fr 1fr; gap: 3.2mm; }}
.carte {{ background: {FOND}; border-radius: 3mm; padding: 3mm 3.4mm; }}
.carte .t {{ display: flex; gap: 2mm; align-items: center; font-family: 'PoppinsF', sans-serif; font-weight: 600;
            font-size: 9.6pt; color: {ENCRE}; margin-bottom: 1.2mm; }}
.carte span {{ font-size: 8.3pt; color: {TEXTE}; line-height: 1.38; display: block; }}
.bonus {{ position: relative; border-radius: 4mm; padding: 4.5mm 5mm 4mm 5mm; color: #fff; overflow: hidden;
         background: linear-gradient(150deg, {VERT} 0%, {VERT_T} 100%); }}
.bonus .ruban {{ position: absolute; top: 4.2mm; right: -9mm; transform: rotate(35deg); background: #fff; color: {VERT_T};
                font-weight: 700; font-size: 7pt; letter-spacing: .2em; padding: 1mm 11mm; }}
.bonus .gros {{ font-family: 'PoppinsF', sans-serif; font-weight: 700; font-size: 28pt; line-height: 1; margin-top: 1.5mm; }}
.bonus .gros small {{ font-size: 12pt; font-weight: 600; }}
.bonus b {{ display: block; font-family: 'PoppinsF', sans-serif; font-weight: 700; font-size: 12pt; line-height: 1.2;
           margin-top: 1.5mm; }}
.bonus span {{ display: block; font-size: 8.6pt; color: #EAF3DC; margin-top: 2mm; line-height: 1.42; }}

/* ---------- appel à l'action */
.cta {{ position: absolute; left: 0; right: 0; bottom: 0; height: 63mm; padding: 6mm 16mm 0 16mm; color: #fff;
       background: radial-gradient(130% 160% at 10% 100%, #105C2C 0%, #0E3416 60%, #0b2a12 100%); }}
.cta .grille {{ display: grid; grid-template-columns: 42mm 1fr; gap: 8mm; align-items: center; }}
.chrono {{ width: 40mm; height: 40mm; border-radius: 50%; border: 2mm solid {CLAIR}; display: flex;
          flex-direction: column; align-items: center; justify-content: center; text-align: center; }}
.chrono .n {{ font-family: 'PoppinsF', sans-serif; font-weight: 700; font-size: 34pt; line-height: .95; }}
.chrono .u {{ font-size: 8pt; letter-spacing: .18em; text-transform: uppercase; color: {CLAIR}; font-weight: 600; }}
.cta .k {{ font-weight: 600; font-size: 7.6pt; letter-spacing: .22em; text-transform: uppercase; color: {CLAIR}; }}
.cta .h {{ font-family: 'PoppinsF', sans-serif; font-weight: 700; font-size: 19pt; line-height: 1.12; margin-top: 2mm; }}
.cta .s {{ font-size: 9.6pt; color: #DCE8D2; margin-top: 2.5mm; line-height: 1.45; }}
.bouton {{ display: inline-flex; gap: 2.5mm; align-items: center; margin-top: 3mm; background: {CLAIR}; color: #0E3416;
          font-family: 'PoppinsF', sans-serif; font-weight: 700; font-size: 10.5pt; padding: 2.6mm 5.5mm; border-radius: 20mm; }}
.contacts {{ position: absolute; left: 16mm; right: 16mm; bottom: 5mm; display: flex; justify-content: space-between;
            border-top: 1px solid rgba(156,203,94,.35); padding-top: 3mm; font-size: 8.4pt; color: #DCE8D2; }}
.contacts div {{ display: flex; align-items: center; gap: 1.8mm; }}
</style></head><body>

<div class="hero">
  <img class="filigrane" src="data:image/png;base64,{b64(os.path.join(THEME, 'icone.png'))}">
  <img class="logo" src="data:image/png;base64,{b64(os.path.join(THEME, 'logo-blanc.png'))}">
  <div><span class="tag">Facil DEF  ·  Guinée équatoriale  ·  SYSCOHADA révisé</span></div>
  <div class="h1 titre">Arrêtez de ressaisir<br>votre DSF.<br><em>Déposez la balance.</em></div>
  <div class="chapo">Facil DEF calcule votre <b>Déclaration statistique et fiscale (DSF) complète</b>, sur votre poste :
  liasse, notes et tableaux fiscaux, prêts à relire et à <b>valider à votre nom</b>.</div>
</div>

<div class="douleurs">
  <h2 class="titre">Chaque année, la même course contre la montre ?</h2>
  <div class="grille">
    <div class="douleur"><div class="pastille">{ico('clock', 20, '#B5452F')}</div>
      <div><b>Des jours de ressaisie</b><span>La balance recopiée à la main, feuille après feuille.</span></div></div>
    <div class="douleur"><div class="pastille">{ico('scroll-text', 20, '#B5452F')}</div>
      <div><b>La DSF N-1 sur papier</b><span>Les comparatifs repris d'un document scanné.</span></div></div>
    <div class="douleur"><div class="pastille">{ico('alert-triangle', 20, '#B5452F')}</div>
      <div><b>Les écarts au dépôt</b><span>Découverts trop tard, sans trace des choix fiscaux.</span></div></div>
  </div>
</div>

<div class="section">
  <div class="surtitre">La méthode Facil DEF</div>
  <div class="h2 titre">Trois gestes, <em>et votre DSF est prête.</em></div>
  <div class="etapes">
    <div class="etape"><div class="num">01</div><div class="ic">{ico('file-input', 20, '#fff')}</div>
      <b>Déposez</b><span>Balance et grand livre, tels qu'ils sortent de votre logiciel.</span>
      <div class="fleche">{ico('arrow-right', 18, VERT)}</div></div>
    <div class="etape"><div class="num">02</div><div class="ic">{ico('list-checks', 20, '#fff')}</div>
      <b>Décidez</b><span>Seules les questions que vos fichiers ne tranchent pas, une seule fois.</span>
      <div class="fleche">{ico('arrow-right', 18, VERT)}</div></div>
    <div class="etape"><div class="num">03</div><div class="ic">{ico('badge-check', 20, '#fff')}</div>
      <b>Validez</b><span>La version définitive, sans filigrane, à votre nom.</span></div>
  </div>

  <div class="duo">
    <div class="benef">
      <div class="carte"><div class="t">{ico('files', 16, VERT_T)}Une DSF complète</div>
        <span>Liasse SYSCOHADA, TF1 à TF5, version espagnole, rapports PDF.</span></div>
      <div class="carte"><div class="t">{ico('shield-check', 16, VERT_T)}Données chez vous</div>
        <span>Calculs sur votre poste ; noms et montants jamais exposés.</span></div>
      <div class="carte"><div class="t">{ico('scan-line', 16, VERT_T)}Scans lus, prouvés</div>
        <span>Votre DSF N-1, même scannée, vérifiée par les formules.</span></div>
      <div class="carte"><div class="t">{ico('file-search', 16, VERT_T)}Tout est tracé</div>
        <span>Contrôles, effet sur l'IS, date et valideur.</span></div>
    </div>
    <div class="bonus">
      <div class="ruban">BONUS</div>
      {ico('gift', 26, '#fff')}
      <div class="gros titre">3 <small>exercices</small></div>
      <b>Analyse financière offerte, sur vos 3 derniers exercices</b>
      <span>17 ratios, soldes de gestion et variations expliquées compte par compte, avec les points à vérifier avant le dépôt.</span>
    </div>
  </div>
</div>

<div class="cta">
  <div class="grille">
    <div class="chrono"><div class="n">15</div><div class="u">minutes<br>maximum</div></div>
    <div>
      <div class="k">Démonstration sur vos propres fichiers</div>
      <div class="h">Apportez votre balance.<br>Voyez votre DSF se construire.</div>
      <div class="s">Sur vos propres données, avec l'analyse de vos 3 derniers exercices en bonus.</div>
      <div class="bouton">{ico('calendar-check', 18, '#0E3416', 2.4)} Réservez votre démonstration</div>
    </div>
  </div>
  <div class="contacts">
    <div>{ico('mail', 14, CLAIR)} sah@emacsah.com</div>
    <div>{ico('phone', 14, CLAIR)} +33 6 99 33 12 30</div>
    <div>{ico('globe', 14, CLAIR)} emacsah.com</div>
    <div style="color:#9FB59A">Emac SAH  ·  SIRET 108 750 407 00018  ·  Paris, France</div>
  </div>
</div>
</body></html>"""

suffixe = ""
if "es" in sys.argv[1:]:          # version espagnole : python construire_flyer.py es
    sys.path.insert(0, ICI)       # le Python embarqué n'ajoute pas le dossier du script au chemin
    from textes_es import TRADUCTIONS
    absents = [fr for fr, _ in TRADUCTIONS if fr not in html]
    if absents:
        sys.exit("Textes français introuvables, traduction à mettre à jour : " + " | ".join(absents))
    for fr, es in TRADUCTIONS:
        html = html.replace(fr, es)
    SORTIE = os.path.abspath(os.path.join(ICI, "..", "..", "livrable", "es", "Folleto-Facil-DEF.pdf"))
    suffixe = "-es"

page = os.path.join(ICI, f"flyer{suffixe}.html")
open(page, "w", encoding="utf-8").write(html)
os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
r = subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf-no-header",
                    f"--print-to-pdf={SORTIE}", "file:///" + page.replace("\\", "/")], capture_output=True, text=True,
                   timeout=120)
import pymupdf  # noqa: E402
d = pymupdf.open(SORTIE)
print("pages :", d.page_count, "|", SORTIE)
d[0].get_pixmap(dpi=110).save(os.path.join(ICI, f"apercu{suffixe}.png"))
print("polices incorporées :", sorted({f[3] for f in d[0].get_fonts()}))
