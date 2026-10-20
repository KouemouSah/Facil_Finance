---
name: presentation-decks
description: >-
  Système de design pour créer/modifier des présentations HTML « deck » (slides
  1920×1080, plein écran, navigables, imprimables PDF) au style riche validé.
  À UTILISER dès qu'il s'agit de créer, refondre ou éditer une présentation, des
  slides, un deck, un pitch/keynote, une « présentation HTML », un support de
  réunion, ou tout fichier `deck-*.html` / dossier `presentations/`. Fournit la
  coquille partagée (`assets/deck.css` + `deck.js`), un template paramétrable, le
  catalogue de composants et les règles de remplissage/qualité. Langue par défaut :
  français, mais le système est agnostique.
---

# Presentation decks — système de design

Tu crées des présentations en **HTML autonome** : chaque deck = un fichier de
`<section class="slide">` qui s'appuie sur la coquille partagée `assets/deck.css`
+ `assets/deck.js`. `deck.js` construit la navbar repliable, le plein écran, la
barre de progression, le deep-link `#n`, l'impression PDF et la mise à l'échelle
du canvas fixe **1920×1080**. Tu n'écris donc que des slides.

## Démarrage (à faire en premier)

1. **Copier les assets canoniques du skill** dans le projet cible s'ils n'y sont
   pas : `assets/deck.css` et `assets/deck.js` (ce dossier `skills/presentation-decks/assets/`
   est la **source de vérité** ; ne jamais repartir d'une autre version).
2. **Partir de `template.html`** (dans ce skill) — coquille vide avec couverture
   + 1 slide type. **Branding adaptatif à l'entreprise** (jamais codé en dur) :
   - **Placeholders flexibles** : `«CLIENT»`, `«TITRE»` (titre du deck/rapport — pas
     un « titre projet » figé), `«SECTION»`, `«SOUS-TITRE»`, `«AUTEUR-OU-DÉPARTEMENT»`
     (un **département**, ex. « Service Comptabilité », convient), `«CONTACT»` (e-mail
     **ou** département **ou** vide), `«MENTION-CONFIDENTIEL»`, `«ANNÉE»`, `«LOGO»`.
   - **Thème (couleurs/charte)** : le deck est 100 % piloté par les variables `:root`.
     Pour l'adapter à la marque, **surcharger ces variables dans le `<style>` de thème**
     du deck (déjà prévu après `deck.css`) — voir `assets/theme.example.css`. **Ne
     jamais modifier la palette de `deck.css`** (canonique, partagée).
   - **Dériver la palette** : si une **charte graphique** existe, utiliser ses couleurs ;
     sinon **analyser le LOGO** (Claude lit l'image → propose primaire + 1-2 accents) et
     **faire confirmer**. Vérifier le contraste/lisibilité après changement.
   - Réutiliser un **profil de marque** (`reporting-financier/references/profil-branding.example.json`)
     pour rester cohérent d'un deck/rapport à l'autre.
3. Lire `reference.md` (catalogue de composants + coordonnées + gotchas) **avant**
   de construire des infographies ou tableaux.

## Les 5 règles non négociables

1. **Remplissage ~80 % de contenu MATÉRIEL**, jamais 20–40 % avec du vide. Le
   « 80 % » = du contenu dense, **pas un conteneur étiré**.
2. **Anti-pattern n°1 interdit : `cards … fillrows grow`** qui étire les cartes en
   hauteur pendant que le texte reste en haut → grandes boîtes blanches (rejeté par
   le commanditaire). Parade : `cards … dense` + ancrer un pied (`.metarow`,
   `margin-top:auto`) **et/ou** remplir le reste avec un bandeau insight/KPI.
3. **Pas de petits textes/icônes.** Typo large, icônes vectorielles monochromes bien
   dimensionnées (jeu d'icônes dans `deck.js`).
4. **Choisir le composant selon la NATURE de la relation**, pas par défaut (voir
   « Choix du composant » ci-dessous).
5. **Modifications de `deck.css`/`deck.js` = ADDITIVES uniquement.** Ne jamais
   modifier/supprimer une classe ou icône existante (d'autres decks en dépendent).
   Nommer les nouveautés sans collision (grep préalable).

## Choix du composant (décisif)

| Nature de la relation | Composant | Jamais |
|---|---|---|
| Séquence d'étapes (process) | `.flow` (nœuds + flèches) ou `.timeline` (frise datée) | sur une relation non séquentielle |
| Plusieurs-vers-un / écosystème (hub + convergence) | `.eco` (infographie : nœuds px absolus + câbles SVG) | — |
| Stack / familles / regroupement | `.layers` (bandes pleine largeur + chips) | — |
| Correspondance ligne-à-ligne, données | `table.rich` (+ `.fill`) | `<table>` plat |
| Avant/Après | `.ba` (2 colonnes) | — |
| Comparaison de grandeurs | `.barchart` ; budgets/SLO | — |
| Un pourcentage clé | `.gauge` (donut SVG) | — |
| Diagramme UML de cas d'usage **petit** (≤5 acteurs, ≤8 UC) | `.ucd` | au-delà → **`.layers` groupé** (sinon plat de spaghettis) |
| **Finance** : Bilan/CR/SIG chiffrés, sous-totaux/totaux, variance N/N-1 | `table.fin` | `<table>` plat / `table.rich` (non numérique) |
| **Finance** : indicateurs clés avec évolution ▲/▼ | `.kpi-fin` | — |
| **Finance** : tendance temporelle (CA/EBE/trésorerie sur N mois) | `.linechart` | barres pour une série temporelle |
| **Finance** : cascade SIG / pont de variance (bridge) | `.waterfall` | — |
| **Finance** : structure de coûts / ventilation (100 % réparti) | `.stackbar` | — |

**Composants & icônes finance** : voir `reference.md § Finance` (recettes prêtes + icônes `i-trend-up/-down i-percent i-wallet i-bank i-receipt i-pie i-cash`). **Ne jamais inventer un chiffre** : valeurs issues des moteurs du plugin ou d'un Excel réel (`reporting-financier/scripts/xlsx_to_table.py`).

**Diapo de clôture obligatoire** : tout deck se termine par une slide de fin (`slide dark act0` : merci / contacts / prochaines étapes, bloc `.endgrid` optionnel). La couverture (`act0`) + la clôture encadrent le deck.

## Process

1. Lire les **docs sources** du dossier concerné (le contenu prime ; ne jamais
   inventer de chiffres — citer les sources réelles).
2. Choisir une **structure narrative** (couverture → contexte → cœur → preuve →
   synthèse). ~7–15 slides denses valent mieux que 12 plates.
3. Construire chaque slide : en-tête `.s-head` (kicker + titre + n° page + filet),
   corps `.s-body`, pied `.s-foot` (branding). Pagination `02…0N`.
4. Pour une infographie : **copier les patterns éprouvés** des decks existants
   (`reference.md` donne les recettes `.eco`/`.timeline`/`.ucd` avec coordonnées px).
5. **Vérifier le rendu / faire valider.** Ne jamais affirmer « terminé/vérifié »
   sans voir le rendu. Si le commanditaire valide lui-même (préférence courante),
   livrer en listant les **points de contrôle** : (a) aucune carte étirée ;
   (b) infographie alignée (aucun nœud retombé en haut-gauche) ; (c) tableaux/charts
   remplis ; (d) **rien ne passe sous `.s-foot`** ; (e) chrome cohérent ;
   (f) non-régression des autres decks (ajouts additifs).

## Palette & typo (déjà dans `deck.css`)

Fraunces (titres serif) + Inter (texte). Navy `#0F172A`, olive `#4A7C0C`/`#9DBE5C`,
rust `#C2410C`, teal `#0F766E`, crème `#FAF8F3`. Classes d'accent de slide :
`act1` (vert) `act2` (rust) `act3` (teal) `act0` (couverture).

## Maintenance

- Un composant ajouté à `deck.css` → **mettre à jour `reference.md`** ET reporter
  la copie dans **ce skill** (`assets/`) qui reste canonique.
- Voir `reference.md` pour le catalogue complet, les recettes d'infographie, les
  gotchas (débordement, positionnement absolu) et les leçons éprouvées.
