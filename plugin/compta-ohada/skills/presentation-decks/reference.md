# Référence — composants, recettes & gotchas

Catalogue des classes de `assets/deck.css` et recettes d'usage. À lire avant de
construire infographies/tableaux. **Tout vit dans un canvas fixe 1920×1080** (mis à
l'échelle par `transform` dans `deck.js`) → le positionnement en **px absolus est
fiable au pixel**.

## Chrome d'une slide

```html
<section class="slide act1" data-title="Titre nav" data-icon="i-gear">
  <div class="s-head"><img class="hlogo" src="«LOGO»" alt=""/>
    <div class="htxt"><div class="k">KICKER</div><div class="t">Titre de slide</div></div>
    <div class="pg"><b>02</b></div></div>
  <div class="s-body"> … </div>
  <div class="s-foot"><div class="proj"><b>«SOUS-TITRE»</b></div>
    <div class="conf"><svg><use href="#i-lock"/></svg>«MENTION-CONFIDENTIEL»</div></div>
</section>
```
- Couverture : `<section class="slide dark act0">` avec `.hero` (`.eyebrow`, `h1 em`,
  `.sub`, `.metastrip`, `.bignum`) + `.cover-top` + `.s-foot`.
- `.s-head` accepte un bloc `.kpis` avant `.pg` (`.kpis+.pg{margin-left:32px}`).
- `data-title`/`data-icon` alimentent la navbar (`deck.js`). `data-icon` ∈ jeu d'icônes.

## Cartes — `.cards`

`.cards .g2/.g3/.g4` (colonnes) ; `.dense` (gap réduit). Carte `.card .c1/.c2/.c3`
(accent vert/rust/teal). Éléments : `.num` (grand numéral estompé), `.ic` (pastille
icône), `h3`, `ul.clean(.lg)`, `p`, `.chips`/`.pill`, `.tagrow`/`.tag(.mut)`.
**Ancrer le bas** : `.metarow` (`margin-top:auto`, libellé + valeur, `b.acc` serif),
`.cardfoot`, `.metric`. **Ne pas** utiliser `fillrows grow` (étirement = vide).

## Bandeaux & tableaux

- `.insight` (bandeau navy) : `.k` (kicker), `.row` avec `p`/`.big` + `.kpis`
  (`.v`, `.v.w`, `.v.r`, `.l`). Remplisseur de bas de slide par excellence.
- `table.rich` : en-tête navy, lignes alternées, `td b` navy, `.sub` (sous-libellé),
  badges `.bdg(.g/.r/.t/.n/.k)`. **`table.rich.fill`** = flex:1 (les lignes s'étirent
  pour remplir la hauteur). `vertical-align:middle` par défaut (demande commanditaire).
- `.ba` (avant/après) : 2 colonnes `.col.b` (rust) / `.col.a` (vert), `h4` + `ul.clean`.

## Schémas séquentiels

- `.flow` (`.flow.col` vertical) : `.node .c1/.c2/.c3/.ck` (`.k`, `.nt` icône+titre,
  `p`, `.mini` ancré bas) séparés par `.arrow` (`#i-chevR`). **≤ 7 nœuds** sinon trop
  serré.
- `.timeline` : frise horizontale, colonne vertébrale (`::before`) + jalons.
  `.tl-item.cX` › `.tl-date` (au-dessus), `.tl-dot` (sur la frise, icône optionnelle),
  `.tl-card` (`.tt` icône+titre, `p`, `.tf` ancré bas). Pour un **processus daté**.

## Schémas de regroupement

- `.layers` : bandes pleine largeur qui **remplissent la hauteur** (flex:1 chacune).
  `.layer.l1/.l2/.l3/.lk` › `.lhead` (250px : `.ic`, `.k`, `.t`) + `.lbody`
  (`.chip`/`.chip.solid` + `.ldesc`). **Le meilleur remplisseur** pour familles,
  stacks, « acteurs → éléments ». Préférer à un diagramme à lignes quand il y a
  beaucoup d'items.

## Charts

- `.budget` : barres SLO (`.row` = `.lab` + `.track`>`.fill(.t/.r)` + `.val`).
- `.barchart` : comparaison générique (`.bc-row` = `.bc-lab` + `.bc-track`>`.bc-bar(.r/.t/.n)`
  + `.bc-val`). Largeur de barre = `style="width:NN%"` proportionnelle à la grandeur.
- `.gauge` : donut SVG d'un pourcentage. `r=80` → circonférence ≈ 503 ;
  `stroke-dasharray="<pct·503> 503"` en inline. `.gctr .v/.l` au centre. `.gauge.c2/.c3`.
- `.legend` : `.lg-item.cX/.dash` (pastille + libellé) pour légender `.eco`/charts.

## Infographie écosystème — `.eco` (recette)

Pour relations **plusieurs-vers-un** (hub + convergence/rayonnement). Nœuds HTML en
**position absolue** + **une couche SVG inline** pour les câbles uniquement.

```html
<div class="eco" style="height:560px">
  <svg class="wires" viewBox="0 0 1792 560" preserveAspectRatio="none">
    <defs><marker id="p-t" markerWidth="9" markerHeight="9" refX="6" refY="3" orient="auto">
      <path d="M0,0 L6.5,3 L0,6" fill="none" stroke="#0F766E" stroke-width="1.8"/></marker></defs>
    <path d="M360,43 C580,60 600,296 730,300" fill="none" stroke="#0F766E" marker-end="url(#p-t)"/>
    <text class="wlab" x="392" y="282">Label majuscule</text>
  </svg>
  <div class="hub" style="left:736px;top:232px;width:320px;height:152px"><div class="hk">Kicker</div><div class="ht">Hub</div><div class="hs">desc</div><div class="seal"><svg><use href="#i-pen"/></svg>sceau</div></div>
  <div class="en c3" style="left:20px;top:6px;width:340px;height:74px"><div class="t"><span class="d"><svg><use href="#i-ship"/></svg></span>Nœud</div><div class="s">sous-titre</div></div>
</div>
```
- **Gotcha vérifié :** tout nœud custom (ex. `.hub`) **doit** déclarer `position:absolute`
  (les classes `.eco .hub`/`.en` le font déjà) sinon il retombe en haut-gauche.
- `.eco` largeur 1792 = largeur utile du `.s-body` (padding 64). `.wires` viewBox doit
  matcher la hauteur inline. SVG = **uniquement** les traits/flèches (`marker-end`).
- `.pin` = étiquette pastille (rust) ancrée dans l'`.eco`.

## Diagramme de cas d'usage — `.ucd`

Acteurs + ellipses UC + associations SVG (`.sys`/`.syslab`, `.uc.cX .id`,
`.actor.cX .av/.an/.ar`, `.uwires line`). **Leçon éprouvée :** au-delà de ~5 acteurs /
~8 UC, les associations deviennent illisibles → **préférer `.layers` groupé par
zone/acteur avec chips UC** (aucune ligne croisée, remplit la hauteur). Réserver
`.ucd` aux petits diagrammes.

## Gotchas de remplissage / débordement (éprouvés)

- **`fillrows grow` = vide blanc.** `flex:1`/`.grow` étire les cartes ; le texte reste
  en haut → grandes boîtes blanches. Densifier + ancrer (`.metarow margin-top:auto`)
  ou remplir le reste avec `.insight`.
- **Débordement sous `.s-foot`.** Un `table.rich` *sans* `.fill` à hauteur naturelle +
  cartes en-dessous **déborde** le canvas 1080 et rogne le bas (les `.metarow`
  disparaissent). Parade : tableau en **`rich fill`** (absorbe la hauteur), cartes
  **compactes sans `.metarow`** (ni `grow`). Toujours vérifier qu'aucun contenu ne
  passe sous le pied de page.
- **Trop de nœuds.** `.flow` > 7 ou `.ucd` chargé = serré/illisible → condenser ou
  passer à `.timeline`/`.layers`.
- **Slides denses** : viser le contenu matériel, mais garder la hiérarchie (un seul
  message fort par slide, le reste en appui).

## Icônes disponibles (`deck.js`, stroke `viewBox 0 0 24 24`)

`i-anchor i-ship i-map i-flow i-box i-pen i-warn i-users i-bolt i-check i-coins
i-shield i-q i-road i-lock i-target i-gear i-db i-layers i-server i-scale i-doc
i-mail i-calendar i-warehouse i-truck i-stamp i-sign i-chart` + UI (`i-chevL/R i-menu
i-expand i-print i-home`). En ajouter = paths **stroke** (fill="none") au même gabarit,
ajout **additif** dans l'objet `ICONS`.

## Composants : où regarder pour un exemple réel

Les decks de référence (s'ils existent dans le projet) montrent chaque pattern en
contexte : `.eco` (écosystème, modèle de données), `.timeline` (process daté),
`.flow` (pipeline/C4), `.layers` (stack, regroupement d'acteurs), `table.rich`
(ports/adapters, parcours), `.barchart`/`.gauge` (KPI/golden tests), `.ba`
(machine/humain). Copier les coordonnées et adapter.

## Finance — composants (compta / finance) & recettes

Icônes finance (ajoutées) : `i-trend-up i-trend-down i-percent i-wallet i-bank
i-receipt i-pie i-cash` (+ `i-coins i-scale i-chart` existantes).

**Choix du composant finance :**

| Besoin | Composant |
|---|---|
| Bilan / CR / SIG chiffrés, avec sous-totaux & totaux, variance N/N-1 | `table.fin` |
| Indicateurs clés avec évolution (▲/▼) | `.kpi-fin` |
| Tendance sur le temps (CA, EBE, trésorerie sur 12 mois) | `.linechart` |
| Cascade SIG / pont de résultat / variance (bridge) | `.waterfall` |
| Structure de coûts / ventilation (100 % réparti) | `.stackbar` |
| Un pourcentage clé (marge, taux) | `.gauge` (existant) |
| Comparaison de grandeurs (budget/réel) | `.barchart` (existant) |

### `table.fin` — tableau financier (nombres tabulaires, totaux, variance)
```html
<table class="fin">
  <thead><tr><th>Solde (SIG)</th><th class="num">N</th><th class="num">N-1</th><th class="num">% CA</th><th class="num">Var.</th></tr></thead>
  <tbody>
    <tr><td>Chiffre d'affaires</td><td class="num">2 400 000</td><td class="num">2 100 000</td><td class="num">100%</td><td class="num pos">+14,3%</td></tr>
    <tr class="subtot"><td>Valeur ajoutée</td><td class="num">700 000</td><td class="num">640 000</td><td class="num">29%</td><td class="num pos">+9,4%</td></tr>
    <tr><td>Charges de personnel<span class="sub">comptes 66</span></td><td class="num">400 000</td><td class="num">360 000</td><td class="num">17%</td><td class="num neg">+11,1%</td></tr>
    <tr class="totrow"><td>Résultat net</td><td class="num">150 000</td><td class="num">120 000</td><td class="num">6,3%</td><td class="num pos">+25%</td></tr>
  </tbody>
</table>
```
- `td.num` = aligné à droite, chiffres tabulaires. `td.pos` (vert) / `td.neg` (rust) pour la variance.
- `tr.subtot` (filet fin, gras) ; `tr.totrow` (double filet navy, serif) pour les totaux.
- Signe de la variance selon le sens : hausse d'un **produit** = `pos`, hausse d'une **charge** = `neg`.

### `.kpi-fin` — tuiles d'indicateurs avec delta
```html
<div class="kpi-fin">
  <div class="kf"><div class="kl">Chiffre d'affaires</div><div class="kv">2,40 Mds</div>
    <div class="kd up"><svg><use href="#i-trend-up"/></svg>+14,3% vs N-1</div><div class="ksub">XAF</div></div>
  <div class="kf c2"><div class="kl">Trésorerie nette</div><div class="kv">30 M</div>
    <div class="kd down"><svg><use href="#i-trend-down"/></svg>−45% vs N-1</div><div class="ksub">tension mars</div></div>
</div>
```

### `.linechart` — tendance (SVG inline). Canvas utile 1792 de large.
Points = `x` réparti, `y` = base − valeur·échelle. Aire optionnelle (`.lc-area`).
```html
<div class="linechart"><svg viewBox="0 0 1792 360" preserveAspectRatio="none">
  <line class="lc-axis" x1="0" y1="320" x2="1792" y2="320"/>
  <line class="lc-grid" x1="0" y1="160" x2="1792" y2="160"/>
  <path class="lc-area" d="M0,240 L360,180 L720,150 L1080,120 L1440,100 L1792,80 L1792,320 L0,320 Z"/>
  <path class="lc-line" d="M0,240 L360,180 L720,150 L1080,120 L1440,100 L1792,80"/>
  <circle class="lc-dot" cx="1080" cy="120" r="5"/>
  <text class="lc-lab" x="0" y="345">Jan</text><text class="lc-lab" x="1740" y="345">Déc</text>
</svg></div>
```
Deux séries : dupliquer `.lc-line.c2` (rust). Légender avec `.legend`.

### `.waterfall` — cascade SIG (colonnes de magnitude, ancrées au bas)
Chaque colonne : `.wf-bar` avec **hauteur inline en %** (∝ valeur / valeur max). Couleurs :
`total` (navy) pour les soldes, `neg` (rust) pour les déductions, `sub` (gris) pour un intermédiaire.
```html
<div class="waterfall">
  <div class="wf-col"><div class="wf-val">2 400</div><div class="wf-bar total" style="height:78%"></div><div class="wf-lab">Chiffre d'affaires</div></div>
  <div class="wf-col"><div class="wf-val">−1 700</div><div class="wf-bar neg" style="height:55%"></div><div class="wf-lab">Consommations</div></div>
  <div class="wf-col"><div class="wf-val">700</div><div class="wf-bar sub" style="height:23%"></div><div class="wf-lab">Valeur ajoutée</div></div>
  <div class="wf-col"><div class="wf-val">−400</div><div class="wf-bar neg" style="height:13%"></div><div class="wf-lab">Personnel</div></div>
  <div class="wf-col"><div class="wf-val">300</div><div class="wf-bar total" style="height:10%"></div><div class="wf-lab">EBE</div></div>
</div>
```
- `height` en **% de la hauteur du `.waterfall`** (parent à hauteur définie) → fiable. Éviter les marges en % (calculées sur la largeur, pas la hauteur).
- Pour un **vrai bridge flottant** (barres décalées), positionner les barres en `position:absolute` avec `bottom`/`height` en px calculés — plus délicat, à réserver si nécessaire.

### `.stackbar` — structure de coûts (100 % réparti)
```html
<div class="stackbar">
  <div class="sb-row"><div class="sb-lab">Coûts chantier A</div>
    <div class="sb-track"><span class="sb-seg s1" style="width:38%">MO 38%</span><span class="sb-seg s2" style="width:30%">Matériaux 30%</span><span class="sb-seg s3" style="width:20%">S-traitance</span><span class="sb-seg s4" style="width:12%">Autres</span></div></div>
</div>
```

### Diapo de clôture (obligatoire en fin de deck)
Réutiliser la couverture (`slide dark act0` + `.hero`) en version « merci / contacts / prochaines étapes ». Bloc optionnel `.endgrid` (2 colonnes `.ec` : `.k` + `.v`) pour contacts / annexes / prochaines étapes.

### Gotcha finance
- **Ne jamais inventer un chiffre.** Les nombres viennent des moteurs déterministes du plugin (`agreger_balance_dsf`, `ratios`, `avancement`, `registre`, `dossier_revision`) ou d'un Excel réel (`xlsx_to_table.py` du skill `reporting-financier`). Copier les valeurs exactes.
- Cohérence des signes (produit/charge) dans `table.fin` (pos/neg) et `waterfall` (neg).
