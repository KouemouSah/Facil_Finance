# Plugin « compta-ohada »

Assistant comptable OHADA/SYSCOHADA révisé pour le BTP (Guinée Équatoriale), au format **plugin** (skills + commandes + templates Excel), inspiré du pattern Claude for Financial Services.

## Principe
Chaque skill : **guide l'utilisateur** (intake), applique la **méthodologie OHADA**, **calcule**, et produit un **livrable Excel auditable** (formules, pas des valeurs figées). Les textes officiels (loi de finances, plan de comptes) sont **cités**, jamais inventés.

## Structure
```
compta-ohada/
  .claude-plugin/plugin.json     manifeste
  commands/                      /amortissement (+ à venir : /cloture, /dsf, /rapprochement)
  skills/
    immobilisations-ohada/       skill pilote (Phase 1)
      SKILL.md
      templates/tableau-amortissement.xlsx
      scripts/amortissement.py   moteur de référence optionnel (gouvernance)
      references/plan-comptes-immo.md
```

## Surfaces de déploiement
- **Claude Desktop** : plugin complet (skills + commandes + MCP Sage à venir). Surface « puissance ».
- **claude.ai / Projects** : entrée simplifiée pour les néophytes (skills en Project knowledge).

## Base documentaire partagée
`../datas/` : `ley_tributaria_2024.md` (loi de finances, citée par article) et `plan-comptable-syscohada-standard.md` (à remplacer par l'export Sage réel).

## État
- ✅ Phase 0 — squelette & manifeste
- ✅ Phase 1 — skill pilote `immobilisations` (intake guidé + template Excel + commande + test)
- ✅ v0.2.0 (2026-09-28) — **lecture des balances par invariants comptables** (`lib/detection_balance.py`) :
  - xls, xlsx et csv ; de 8 à 1 colonne ; avec ou sans en-tête ; ambiguïtés signalées, jamais tranchées en silence ;
  - branchée sur `agreger_balance_dsf`, `dossier_revision` et `classer_documents` (qui reconnaît aussi le grand livre) ;
  - tests : `tests/`.
- ✅ v0.3.0 (2026-09-28) — **correspondance comptes → postes de la DEF reconstruite** (`mapping-comptes-dsf.json` v2) :
  - classe 1 SYSCOHADA ;
  - éclatement selon le sens du solde ;
  - colonnes brut / amortissements / net ;
  - compte 13 (résultat antérieur non affecté) ;
  - totaux et contrôles actif = passif, CJ = XI.

  Contrôle sur la DEF GE 2025 déposée du dossier pilote : **99/99 postes**, dont 77 identiques au franc près et 22 avec écart expliqué (`../documentation/analyse/reference/`). La doc lisible est générée depuis le JSON (`tools/gen_mapping_md.py`).
- ✅ v0.4.0 (2026-09-28) — **TF1 / TF2 de la DEF GE** (`lib/fiscal_ge.py` + `lib/parametres_fiscaux_ge.json`, chaque taux avec son article) :
  - résultat fiscal, IS, Cuota Mínima, déficits, acomptes, échéances ;
  - propositions de réintégration **confirmées par le libellé** du compte, jamais appliquées sans acceptation ;
  - classeur Excel en formules vivantes.

  Contrôle sur la DEF du dossier pilote : 33/33, dont Excel recalculé. Branché sur `calcul_is_ge.py` (skill fiscalité) et `monter_dsf.py`.
- ✅ v0.5.0 (2026-09-28) — **profil d'entreprise** (`--profil`, modèle `skills/dsf-syscohada/references/profil-entreprise.example.json`) :
  - loi / interprétations / faits ;
  - tout écart à la lecture stricte est appliqué mais **chiffré** ;
  - les faits inconnus deviennent des **questions d'entrée**, avec des indices tirés de la balance (non-résidents art. 76, marchés publics art. 80.3, société nouvelle).

  Avec le profil décrivant la DEF du dossier pilote : TF1/TF2 **identiques au franc près** (Excel recalculé inclus) et bilan à 81 postes exacts. Les seuls écarts restants sont des faits.
- ✅ v0.6.0 (2026-09-28) — **TF3 / TF4 / TF5 depuis le grand livre** :
  - `lib/grand_livre.py` : lecteur générique, par compte ou à plat, rapproché de la balance ;
  - `lib/tf345_ge.py` : IVA, salaires, paiements aux tiers, avec traçabilité ligne à ligne ;
  - commande `calcul_tf345_ge.py`, branchée aussi sur `monter_dsf.py`.

  Contrôle sur la DEF du dossier pilote : 34/34, classeur recalculé dans Excel ; les erreurs de la DEF sont corrigées et déclarées. Nouvelle **garde de reproductibilité** : résultats identiques sous plusieurs graines de hachage. `tools/sync_lib.py` refuse désormais d'écraser un fichier qui n'est pas une copie de `lib/`.
- ✅ v0.7.0 (2026-09-28) — **génération de la DEF complète** (`skills/dsf-syscohada/scripts/def_ge.py`, commande `/monter-dsf`) :
  - classeur présentable : couverture, identification, bilan, compte de résultat, TFT réconcilié, note 3, notes, TF1 à TF5 ;
  - **PDF automatique** ;
  - annexe interne de contrôles et de couverture ;
  - IS intégré par écriture simulée quand la balance ne le porte pas.

  Contrôle sur la DEF du dossier pilote : 139/139, totaux du TFT identiques.
- ✅ v0.8.0 (2026-09-28) — **DEF sur le modèle déposé, FR + ES** (`skills/dsf-syscohada/scripts/def_modele.py`) :
  - **même structure que la DEF de référence** : 51 feuilles, mêmes lignes et colonnes, même mise en forme ;
  - montants recalculés, jamais recopiés du modèle ; totaux, variations et échéances en formules vivantes ;
  - **FR = ES** hormis la langue (`references/i18n-def.json`, noms de feuilles compris) ;
  - identité **laissée vide**, saisie une fois en page de garde et reprise par formule dans tous les en-têtes ;
  - logo de l'entité en option (`--logo`) ;
  - TF5 hybride : tiers nommés et NIF repris du modèle, rapprochés du grand livre ;
  - **impression Excel = PDF** : zones d'impression et mise en page posées ;
  - **`--pro`** : modèle professionnel, mêmes cellules et formules, présentation normalisée, lignes nulles masquées ;
  - contrôles dans un classeur séparé.

  Contrôle sur la DEF du dossier pilote : **2 012 cellules identiques, 145 écarts tous expliqués, 0 inexpliqué**, FR = ES.
- ✅ v0.9.0 (2026-09-29) — **plugin autonome et installable** :
  - **dossier de travail** `Documents\Facil-DEF\<Entité>\<Exercice>` (01_sources, 02_xls, 03_pdf, 04_questions), sources reconnues par leur contenu, versions jamais écrasées, filigrane PROJET jusqu'à validation ;
  - **rendu sans Excel** : formules évaluées par le plugin (691/691 identiques à Excel), PDF natifs ;
  - **serveur MCP** `facil-def` (7 outils), environnement Python isolé, place de marché Claude Code, extension Claude Desktop `dist/facil-def.mcpb` ;
  - **formulaire web local** : 127.0.0.1, lien à jeton, fermeture après 15 min d'inactivité ou 12 h, logo Facil et pied de page « © Facil - AI Solutions Architect - Emac SAH <année> ».
- ✅ v0.10.0 (2026-10-01) — **production sans DEF déposée, toutes formes d'entrée** :
  - entrée : balance, grand livre, ou les deux ; avec le grand livre seul, la balance est reconstituée et contrôlée ;
  - **liasse au modèle SYSCOHADA système normal** (défaut), adaptée aux données : les notes sans montant ou sans information sont omises et signalées dans la grille ; tableaux fiscaux GE ajoutés ; format GE au choix ;
  - gabarit GE vierge embarqué ; contrôle « note = poste » ; formule du total général du formulaire officiel corrigée ;
  - formulaire local par étapes ; passerelle de confidentialité (pseudonymes, montants masqués, journal) ; Python embarqué.
- ✅ v0.10.1-0.10.3 (2026-10-16/17) — extension Claude Desktop : dossier par défaut robuste, formulaire sans page blanche (politique de référent `same-origin`, éprouvée dans Chromium).
- ✅ v0.11.0 (2026-10-17) — **reprise et validation** (même déroulé : dossier, dépôt dans 01_sources, puis génération) :
  - question « DEF précédente » à deux réponses (premier exercice / indisponible) ; DEF déposée après génération signalée, validation bloquée jusqu'à la régénération ; DEF d'un autre exercice ou en .xls écartée et dite ;
  - identité reprise d'une fiche entité, de la fiche posée à la validation précédente, ou de la page de garde de la DEF précédente — affichée avec son origine, corrigeable ;
  - mode « préparer et valider » : un seul lot de questions restantes, validation au nom donné après le clic de confirmation ; réponses appliquées (origine, date) et valideur au rapport de contrôle.
- ✅ v0.11.1 (2026-10-18) — DEF précédente en **PDF** reconnue (scannée ou texte) et dite, jamais ignorée en silence ; un guide ou une facture en PDF n'est pas pris pour une DEF. Lecture OCR des scans : lot à venir.
- ✅ v0.12.0 (2026-10-19) — **DEF précédente SCANNÉE lue sur le poste** (OCR local, rien ne sort) :
  - pages d'états trouvées seules, bilan tourné de 90° redressé, exercice lu ; colonnes par les traits du formulaire, codes de ligne recalés sur l'ordre officiel, décalage des montants mesuré, signe « - » cherché dans les pixels ;
  - chaque montant PROUVÉ par les formules SYSCOHADA ou marqué « à vérifier » ; jamais un chiffre calculé ; deux colonnes collées ou une formule 0 = 0 ne prouvent rien ;
  - lecture en arrière-plan (≈ 10-15 min par DEF), mise en cache ; compte de résultat N-1 repris (bilan N-1 toujours depuis les ouvertures, contrôle croisé) ; montants non prouvés confirmés dans le formulaire ;
  - mesuré sur deux DEF réelles numérisées : 48/48 et 49/50 formules justes ; runtime embarqué ≈ 440 Mo (moteur OCR) ;
  - rendu PDF sans Excel : traits verticaux des colonnes désormais tracés ; serveur MCP : bibliothèques natives préchargées (gel Windows corrigé).
- ✅ v0.13.0 (2026-10-19) — **rapport d'analyse financière pluriannuel** (interne, à chaque version) :
  - années N, N-1 et celles des DEF précédentes (Excel ou scannées) — 2022 à 2025 sur le dossier pilote ;
  - chiffres clés, bilan et compte de résultat comparés, soldes intermédiaires de gestion, 17 ratios (jamais calculés sur une base absente, nulle ou négative) ;
  - variations significatives (≥ 10 % et ≥ 1 % du total du bilan ou du CA) expliquées par les comptes qui portent l'écart, avec points à vérifier ; causes demandées en questions facultatives, jamais déduites ;
  - limite : sans les balances des années passées, l'écart par compte n'est expliqué que pour le bilan.
- ⚠️ Limites :
  - éclatement au niveau **compte** seulement (les avances fournisseurs tiers par tiers exigent la balance auxiliaire) ;
  - échéanciers des notes (< 1 an par défaut) à ventiler par l'entreprise ;
  - données extra-comptables à saisir : effectifs (27B), fiches R1-R3, notes 35-36, ratio de rentabilité économique ;
  - TF4 nominatif : fichier de paie requis.
- ⏳ Phases 2-5 — voir `.claude/plans/plugin-compta-ohada-plan.md`
