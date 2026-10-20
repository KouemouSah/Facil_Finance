---
name: dsf-syscohada
description: >
  Monte une Déclaration Statistique et Fiscale (DSF / liasse SYSCOHADA révisé) de façon assistée à partir des enregistrements de clôture : balance APRÈS INVENTAIRE (N et N-1), sous-livres (registre d'immobilisations, grand livre auxiliaire tiers), données extra-comptables et retraitements de présentation. Agrège ces sources vers les postes DSF (mapping comptes → Notes/REF), peuple les Notes de la liasse, laisse cascader Bilan/CR/TFT, contrôle la cohérence. La balance en est le squelette, PAS la source unique. S'adapte aux documents habituels de l'utilisateur (mode adaptatif : classe et comprend ses fichiers) tout en gardant un référentiel OHADA prédéfini. À utiliser dès qu'on veut préparer, monter, remplir ou contrôler une DSF/liasse annuelle. Utilise EN PRIORITÉ le modèle de DSF de l'utilisateur ; le modèle bundlé n'est qu'un fallback.
allowed-tools: mcp__plugin_compta-ohada_facil-def__dossier_travail, mcp__plugin_compta-ohada_facil-def__lister_dossiers, mcp__plugin_compta-ohada_facil-def__generer_def, mcp__plugin_compta-ohada_facil-def__questions_ouvertes, mcp__plugin_compta-ohada_facil-def__enregistrer_reponse, mcp__plugin_compta-ohada_facil-def__ouvrir_formulaire
---

# Montage de la DSF (liasse SYSCOHADA révisé) — assemblage assisté

Tu montes une liasse DSF pour une entreprise BTP en OHADA. Devise XAF.

## 00. Guinée équatoriale : la DEF est AUTOMATIQUE (prioritaire sur tout ce qui suit)
- Pour une DEF / DSF de **Guinée équatoriale**, passe **par les outils MCP `facil-def`**, livrés et démarrés avec le plugin.
  - S'ils sont différés, charge-les **en une seule fois** :
    `ToolSearch` → `select:mcp__plugin_compta-ohada_facil-def__dossier_travail,…__generer_def,…__questions_ouvertes,…__enregistrer_reponse,…__valider_version,…__ouvrir_formulaire,…__lister_dossiers`.
  - Déroulé : commande `/monter-dsf`.
- **Ne demande pas le modèle d'abord.**
  - Balance, grand livre, ou les deux, déposés dans le dossier de travail → génération immédiate.
  - Grand livre seul : la balance en est reconstituée, puis contrôlée.
  - Sans DEF déposée, le **formulaire officiel GE embarqué** (gabarit, 51 feuilles) est employé.
  - Les questions viennent **après** le calcul, consolidées.
- **Confidentialité** :
  - Ne lis jamais les fichiers du dossier `Facil-DEF`. Le hook du plugin le refuse de toute façon.
  - Les sorties des outils sont pseudonymisées (ENTITE-A, TIERS-001…, « [montant] »). Réutilise ces pseudonymes tels quels.
  - Pour voir noms et montants en clair, l'utilisateur ouvre le formulaire local (`ouvrir_formulaire`).
- `valider_version` n'est **jamais** pré-autorisé : la validation définitive se demande explicitement, avec le nom du valideur.
  En mode « préparer et valider », il s'appelle quand `generer_def` rend `pret_a_valider` (questions restantes posées
  en un seul message d'abord) ; sa demande d'autorisation est le clic de confirmation.

## 0. RÈGLE DE MODÈLE (impérative)
- **Toujours utiliser EN PRIORITÉ le modèle de DSF fourni par l'utilisateur** (leur liasse, leurs fichiers de travail, leur façon de la monter). **Demande-le d'abord** et **adapte-toi à sa structure** (feuilles, cellules de saisie, notes, ordre) — ne présuppose pas la structure.
- Si l'utilisateur explique **comment il monte sa DSF**, suis sa méthode et mets à jour ton raisonnement en conséquence.
- **À défaut seulement**, utilise le modèle par défaut bundlé `../datas/DSF_Normal_MODELE-PAR-DEFAUT.xlsx` (+ `MODELE-TIERS_PAR-DEFAUT.xlsx`), en signalant que c'est un **modèle de secours** à confirmer.

## 0bis. Sécurité & conformité
- Données **anonymisées** hors identité déclarative nécessaire. Validation chef comptable obligatoire.
- ⚠️ **Format pays** : le modèle par défaut bundlé est **camerounais**. Le cœur SYSCOHADA (Bilan, CR, TFT, Notes 1-35) est uniforme OHADA, mais les **annexes fiscales (CF1/CF2), fiches R1-R3, notes statistiques** sont propres à l'administration. Pour une société de **Guinée Équatoriale**, la liasse officielle GE est **embarquée** (`templates/def_ge_gabarit.xlsx`, voir § 00) : ne pas la redemander.

## 1. Sources (la DSF n'est PAS montée depuis la seule balance)
La liasse s'assemble à partir de plusieurs sources — la balance en est le **squelette**, pas la totalité :
1. **Balance après inventaire** N et N-1 (clôture faite : amortissements, provisions, cut-off, régularisations déjà passés) → squelette Bilan/CR et montants des notes simples.
2. **Registre d'immobilisations** (mouvements : brut, acquisitions, cessions, dotations, amort. cumulés) → **Note 3** (note à mouvements, non dérivable de la balance). Skill `immobilisations-ohada`.
3. **Grand livre auxiliaire tiers** (ventilation par tiers, créances douteuses, **échéancier** < 1 an / 1-3 ans / > 3 ans) → **Notes 7/17** + échéances. `MODELE-TIERS`.
4. **Données extra-comptables** : identité (page de garde, R1-R3), effectifs et masse salariale, ventilations statistiques (notes sociales/commerciales), engagements hors bilan et sûretés (Note 1).
5. **Retraitements de présentation & fiscaux** : reclassements (part < 1 an / > 1 an d'un emprunt, part HAO), **passage résultat comptable → fiscal** (CF1/CF2). Ce sont des **jugements fournis**, non dérivables automatiquement.

### Intake guidé
Demander : le **modèle DSF de l'utilisateur** (sinon fallback) et sa méthode de montage ; la **balance N/N-1 après inventaire** ; le **registre d'immobilisations** ; le **détail tiers** ; les **données extra-comptables** ; les **retraitements**.

> **Nature des sources** (à ne pas confondre — voir `references/sources-dsf-ohada-vs-pratique.md`) : la balance, le grand livre et les états financiers sont **définis par OHADA** ; le registre d'immobilisations, l'auxiliaire tiers et les retraitements sont des **outils de pratique non normalisés** (propres à chaque entreprise) ; la liasse DSF, R1-R3, CF1/CF2 sont **définis par la DGI nationale**, pas par OHADA.

## 1bis. Deux modes (le prédéfini reste la référence, l'adaptatif l'enrichit)
- **Mode prédéfini (référence)** : le mapping comptes→postes et les sources ci-dessus, ancrés OHADA. Toujours disponible.
- **Mode adaptatif (documents de l'utilisateur)** — RECOMMANDÉ : l'utilisateur fournit **ses fichiers habituels et son modèle**. Procéder ainsi :
  1. **Classer** les documents fournis : `python scripts/classer_documents.py --fichiers <f1> <f2> ...` (ou `--dossier`). Il devine le rôle de chaque fichier (balance / registre / tiers / modèle DSF / inconnu) et la couverture des intrants.
  2. ⚠️ **Confirmer avec l'utilisateur** chaque rôle deviné et lui demander d'**expliquer sa méthode de montage** — la détection est une proposition, pas une vérité (ne jamais interpréter un fichier maison en silence).
  3. **Consigner** le tout dans un **profil utilisateur** réutilisable (`references/profil-utilisateur.example.json`) : documents→rôles confirmés, colonnes, méthode, cell-map.
  4. **Adapter** le montage à ce profil, en **complétant** le prédéfini (jamais en le supprimant) : ce qui manque dans les fichiers de l'utilisateur est comblé par le mode prédéfini + l'intake.

## 2. Méthodologie
1. **Vérifier la complétude des sources** (voir §3bis) et **lister ce qui manque**.
2. **Agréger la balance** (squelette) : `python scripts/agreger_balance_dsf.py --balance <balance>` — balance **.xls/.xlsx/.csv, 8 à 1 colonne(s), avec ou sans en-tête**, lue par **invariants comptables** (voir `CONVENTIONS.md`). Si le script s'arrête sur une **ambiguïté** (code 2, lectures possibles listées), **demander à l'utilisateur** laquelle est la bonne et relancer avec `--gabarit "<nom>"` ; ne jamais choisir à sa place. Le mapping v2 applique les conventions de la DEF (actif D−C, passif et résultat C−D, charges négatives), éclate les comptes **selon le signe du solde**, et produit brut / amortissements / net et les totaux. Deux contrôles l'accompagnent : **actif = passif** et **CJ = XI**. **Présenter à l'utilisateur les avertissements** du script : résultats antérieurs non affectés au 13, comptes non mappés, balance clôturée, et limite de l'éclatement au niveau du compte, qui demande la balance auxiliaire pour les avances fournisseurs. Traiter les **comptes non mappés** (ne jamais les ignorer). (Mapping : `references/mapping-comptes-dsf.json` ; humain : `mapping-comptes-dsf.md` ; squelette : `squelette-dsf.md`.)
3. **Alimenter les notes à mouvements** depuis les sous-livres : Note 3 via le **registre** (`immobilisations-ohada`), Notes 7/17 via le **détail tiers** et l'échéancier.
4. **Données extra-comptables — LIRE puis FORMALISER (pas de formulaire figé)** :
   - Cible = le **besoin normalisé** `references/besoin-extra-comptable.json` (ce que la DSF exige), PAS un gabarit à remplir à la main.
   - **Tabulaire / clé-valeur** (identité, effectifs, informations générales) → `python scripts/extraire_donnees.py --fichier <doc>` lit le document de l'utilisateur (libellés variés, valeur à droite ou dessous) et le mappe au besoin.
   - **Non structuré** (engagements hors bilan, sûretés, contrats) → **Claude lit le document et extrait** les champs du besoin, puis **fait confirmer** (pas de parseur figé ; ne jamais interpréter en silence).
   - **Jugement** (reclassements court/long, passage résultat fiscal) → **fourni par l'humain**, jamais deviné.
   - Signaler les besoins non couverts et demander.
5. **Peupler les Notes** de la liasse (points de saisie) ; le Bilan / CR / TFT **cascadent par formules**.
6. **Contrôler** (§4).

## 2bis. Générer la DEF complète (Guinée équatoriale) — classeur + PDF

**Porte d'entrée (v0.9) : le DOSSIER DE TRAVAIL** — `scripts/espace_def.py`, piloté par la commande `/monter-dsf`.
- **Emplacement** : `Documents\Facil-DEF\<Entité>\<Exercice>\` avec quatre sous-dossiers :
  - `01_sources` : l'utilisateur y dépose ses fichiers ;
  - `02_xls` et `03_pdf` : livrables versionnés ;
  - `04_questions` : questions et réponses.
- **Fonctionnement** :
  - reconnaissance des sources par leur **contenu**, logo par le nom ;
  - **génération automatique d'une version PROJET** (nom `_projet`, filigrane), puis toutes les questions en une fois ;
  - une balance illisible ou ambiguë est le seul arrêt avant calcul ;
  - les réponses (`04_questions\reponses.json`) sont réinjectées dans les classeurs ET les PDF : ne rien saisir dans les classeurs générés ;
  - la validation (`valider --par`) exige que toutes les questions obligatoires soient répondues, et produit la version définitive ;
  - `manifeste.json` trace les empreintes des sources, les réponses et les livrables de chaque version.
- **Sortie** : JSON sans donnée comptable (confidentialité).

**Moteur de la DEF sur le MODÈLE déposé** — `scripts/def_modele.py`, appelé par le dossier de travail via `produire()`.
`python scripts/def_modele.py --modele <DEF déposée .xlsx> --balance <B> --exercice <N> [--grand-livre GL] [--profil p.json] [--decisions d.json] --colonne-precedente N|N-1 [--logo logo.png] [--langues fr,es] --sortie <préfixe> [--pro] [--pdf]`

- **Même structure que la DEF de référence** : mêmes feuilles (51 pour le modèle GE), mêmes lignes, colonnes et mise en forme. La balance, annexe de l'art. 79.2, passe en fin de classeur.
- **FR et ES identiques** hormis la langue. Les libellés viennent de `references/i18n-def.json` (FR→ES pour les notes, ES→FR pour TF1-TF5), noms de feuilles compris. Aucun chiffre ne dépend de la langue : la garde de référence le vérifie cellule par cellule.
- **Montants du modèle JAMAIS recopiés** en colonne N ; chaque cellule chiffrée est :
  - soit recalculée :
    - postes : moteur `def_ge` ;
    - lignes « REF + comptes » : affectation compte → poste du moteur, sens compris ;
    - TF1-TF5 et note 34 ;
  - soit reprise du modèle pour N-1 et l'historique (`--colonne-precedente N` si le modèle est la DEF précédente) ;
  - soit posée en **formule vivante** : totaux, variations, échéances ;
  - soit **laissée vide sur fond ambre** : identité, effectifs, données extra-comptables.
- **Totaux** : la structure est celle que les **montants du modèle prouvent**, parmi quatre candidates : somme des lignes, somme des sous-totaux, net = total − dépréciations, produits − charges. À défaut de preuve, le choix se fait par le libellé, et c'est signalé.
- **Comptes hors nomenclature d'une note** : présentés à la ligne de même sous-classe, sinon à la ligne « autres » de la classe, et tracés dans les contrôles.
- **Identité** : saisie **une fois** en page de garde (D13 dénomination, D16 sigle, D17 adresse, D18 NIF) ; tous les en-têtes la reprennent par formule. L'identité du modèle n'est jamais recopiée.
- **TF5 hybride** : bénéficiaires, adresses, natures et NIF repris du TF5 du modèle, rapprochés d'un code tiers du grand livre par les libellés (confiance affichée) ; montant déclaré si le modèle est du même exercice, sinon celui du grand livre. Un NIF manquant est signalé (art. 27.2), non bloquant.
- **Deux sorties, deux rôles** :
  - le **classeur Excel** reprend la liasse officielle ; c'est le support de saisie et de dépôt. Zones d'impression et mise en page sont posées, donc l'impression Excel reproduit la liasse officielle. `--pdf-excel` en donne le PDF.
  - le **rapport PDF complet** (`--pdf`, `scripts/rapport_def.py`), un par langue :
    - le classeur est **recalculé par Excel**, relu en valeurs et remis en page (design `def_ge`) : les chiffres du rapport sont ceux du classeur ;
    - contenu : couverture, sommaire paginé, identification, états, **toutes les notes applicables** (lignes sans montant omises, plusieurs tableaux par note si le modèle en porte), tableau d'applicabilité des notes, TF1 à TF5 ;
    - sont écartés, et signalés : intercalaires, bilan paysage, table des codes (note 36), grille d'analyse ;
    - la balance fait l'objet d'un PDF à part, `_annexe-balance_<LANGUE>.pdf` (art. 79.2) ;
    - le **rapport de contrôle** l'accompagne (`scripts/controle_def.py`, `_controles.xlsx` et `.pdf`, interne, jamais déposé). C'est un rapport A4 **par sections et catégories**, conçu pour une lecture rapide :
      - couverture avec **verdict** et compteurs ;
      - 1. synthèse et points prioritaires avec leur impact ;
      - 2. cohérence comptable : contrôles **bloquants** (équilibre, articulation des états, IS, TFT, note 3), distingués des anomalies à voir ;
      - 3. fiscalité : chiffres clés, réintégrations acceptées et **proposées non intégrées avec leur impact sur l'IS**, interprétations de l'entreprise, questions d'entrée ;
      - 4. tiers (TF5) ;
      - 5. présentation : placements automatiques, cellules à saisir ;
      - 6. avertissements classés par catégorie ;
      - 7. **sources utilisées et méthode**, qui disent ce qui vient de la balance, du grand livre, du modèle, du profil et des décisions.
      - Chaque point porte un statut **écrit** (OK / À VOIR / ÉCART / INFO), jamais la couleur seule. Les montants sont au format français.
    - Sans Excel pour recalculer, le plugin produit à la place le rapport abrégé de `def_ge`, et le signale.
- **IS passé en charge** (y compris celui d'un exercice antérieur, art. 62.3.a) : le moteur fiscal le reconnaît **par la structure des pièces du grand livre**. Une pièce qui crédite le 441 sans débiter le 89 a des charges pour contrepartie. Principal = crédit 441 − majorations d'IS de la pièce. Il est **proposé** en réintégration (TF1 ligne 9), jamais appliqué sans acceptation.
- **Logo** (`--logo`, celui de l'entité) : **page de garde du classeur** et **couverture du rapport**, nulle part ailleurs.
- **CMF versée** : lue dans les fichiers, selon la règle du porteur : ce que la comptabilité enregistre comme versé est versé, et la quittance se joint au dépôt sans conditionner le calcul.
  - Un versement est un **débit du 441** sur l'exercice (grand livre, sinon mouvements de la balance).
  - Sont exclus : les rappels d'exercices antérieurs, et les versements de janvier N, qui soldent le 2e acompte de N-1 (art. 80.2).
  - Une saisie `cmf_versee` dans les décisions prime sur cette lecture.
- **`--pro`** : produit en plus le **modèle professionnel** :
  - **mêmes cellules et mêmes formules**, donc aucune divergence possible avec l'officiel ;
  - présentation normalisée : bandeaux d'en-tête, totaux sur fond clair, en-tête figé et répété à l'impression ;
  - lignes sans montant masquées (pas supprimées), avec la mention « Néant » si une note est entièrement vide.
- Contrôles et couverture : classeur **séparé** `<préfixe>_controles.xlsx`, jamais déposé.
- **Validé** contre la DEF GE 2025 du dossier pilote : 2 012 cellules identiques, 145 écarts tous expliqués (la garde de référence du dossier pilote (hors plugin)), FR = ES.

**Sans DEF déposée : le gabarit officiel embarqué** (`templates/def_ge_gabarit.xlsx` + `.json`) — c'est le cas NORMAL
d'un nouveau client, et le dossier de travail le choisit tout seul.
- **Même DEF de 51 feuilles**, colonne N identique à celle obtenue sur une DEF déposée. La preuve : 3 952 cellules
  identiques, 0 écart inexpliqué (la garde de référence du dossier pilote (hors plugin), hors plugin).
- Le gabarit est le formulaire purgé de toute donnée du dossier pilote. La structure des totaux, prouvée une fois sur
  des montants réels, est figée dans le `.json`.
- Sans DEF de l'exercice précédent :
  - bilan N-1 = soldes d'ouverture de la balance ;
  - N-1 des notes **vide** (jamais 0) ;
  - question obligatoire `sources.def_precedente` : la déposer (.xlsx, exercice N ou N-1), ou répondre « premier
    exercice » / « DEF précédente indisponible ». Une DEF déposée après la génération est signalée (formulaire :
    bandeau, validation bloquée) jusqu'à la régénération ; une DEF d'un autre exercice ou au format .xls est écartée et dite.
  - identité reprise des sources (fiche entité déposée, `fiche_entite.json` du dossier de l'entité posé à la
    validation, page de garde de la DEF précédente) : proposition affichée avec son origine, que la saisie remplace.
- **Modèle de la liasse** : choix `interp.modele_def`.
  - **SYSCOHADA système normal** (défaut) : `scripts/def_sn.py` sur le formulaire officiel OHADA (`templates/syscohada_sn_modele.xlsx`), avec les tableaux fiscaux GE. Même calcul que le format GE ; seule la présentation change, et les formules officielles sont gardées.
    - Notes remplies ligne par ligne par `references/correspondance-sn*.json` (la main prime).
    - Chaque note est contrôlée contre son poste ; les comptes hors nomenclature vont à la ligne « Autres… », tracés.
    - Formule du total général du formulaire corrigée (l'écart de conversion y est oublié).
    - Liasse adaptée : notes sans montant ou sans information omises ; notes extra-comptables gardées (à saisir) seulement si la balance montre qu'elles s'appliquent.
    - Gardes : `tests/test_sn.py`, `tests/falsification_sn.py` ; référence : la garde du dossier pilote (hors plugin).
  - **Format GE** (au choix) : classeurs FR / ES du format déposé.
  - Le français est au modèle SYSCOHADA ; l'espagnol reste au format GE en attendant la traduction.
- **Le classeur s'adapte aux données** :
  - une note sans aucun montant (N et N-1) est omise et signalée « néant » dans la grille d'analyse des notes ;
  - le rapport PDF applique la même règle (`rapport_def.utile`) ;
  - ne sont jamais omis : les états, les TF, les notes extra-comptables et les notes qui attendent une saisie ;
  - choix facultatif `interp.notes_neant = conserver` : les 51 feuilles.
- **Note applicable absente du formulaire** : un poste chiffré dont la note n'a pas de feuille (ex. subventions →
  note 15) est signalé au rapport de contrôle et dans `notes_applicables_absentes_du_formulaire`.
- Les montants que la DEF déposée portait sans qu'aucun calcul les produise sont « à saisir » (fond ambre) :
  actionnaires (note 13), montants en devises (note 12), note 28, historique de la note 31.
- Reconstruire le gabarit (mainteneur, fichiers du dossier pilote hors plugin) : `python tools/construire_gabarit.py`.
  Contrôle bloquant : aucun nom purgé ne subsiste. Gardes : `tests/test_gabarit.py`, `tests/falsification_gabarit.py`.

**Liasse abrégée** (ancienne voie, 14 feuilles, conservée pour la commande en ligne) : `scripts/def_ge.py` :
`python scripts/def_ge.py --balance <B> --exercice <N> --profil <p.json> [--decisions d.json] [--grand-livre GL] [--def-precedente DEF --colonne-precedente N|N-1] [--tiers t] --sortie DEF.xlsx --pdf`
(voir la commande `/monter-dsf`).

- **Contenu**, en présentation professionnelle bilingue d'en-têtes FR / ES :
  - couverture, sommaire, identification (fiche R1) ;
  - bilan actif et passif, compte de résultat, en N et N-1 ;
  - **TFT réconcilié** ;
  - note 3 (immobilisations, avec virements de poste à poste isolés et dotations calées sur 681/687) ;
  - notes de détail (composition des postes par compte) ;
  - TF1 à TF5.
- **Livrables** :
  - un **PDF de la DEF**, exporté par Excel, ou par LibreOffice à défaut ;
  - un **PDF de contrôle interne**, jamais joint au dépôt.
- **IS** : si la balance ne porte pas l'impôt, il est intégré par une **écriture simulée** (891 / 441) pour le montant dû selon TF2. Le dire à l'utilisateur : cette écriture **est à passer en comptabilité** avant la clôture.
- **Contrôles bloquant la remise** : **aucun** (règle du porteur). Mais **présenter les écarts** de l'annexe « Controles » avant toute remise.
- **N-1** :
  - lu dans une DEF précédente, **par ses en-têtes** (colonnes « NET » datées), et non par adresses de cellules ;
  - à défaut, pris dans les soldes d'ouverture de la balance, pour le bilan seulement.
- **Non produit, et déclaré** :
  - TF4 nominatif (fichier de paie) ;
  - identité des tiers du TF5 (fichier des tiers) ;
  - fiches R2 / R3 et notes 27B, 31, 34-36 (données extra-comptables) ;
  - libellés de postes en espagnol ;
  - échéanciers des notes.
- **Validé** contre la DEF GE 2025 déposée du dossier pilote : 139/139 comparaisons, **totaux du TFT identiques**, PDF de 20 pages.

## 3. Autonomie — ce qui est automatisable et ce qui ne l'est pas
- **Automatisable** (si les sources structurées sont fournies) : agrégation de la balance, alimentation des notes chiffrées et des notes à mouvements (depuis les sous-livres), peuplement des cellules via un **cell-map**, cascade des formules, contrôles.
- **NON automatisable** (jugement humain, à fournir) : reclassements de présentation, réintégrations/déductions fiscales, provisions et estimations, exactitude des données extra-comptables.
- ⚠️ La **balance seule** produit une DSF **incomplète et fausse** sur les notes → toujours combiner balance + sous-livres + intake + retraitements.
- Validation chef comptable **obligatoire** : l'automatisation **produit**, elle n'engage pas la responsabilité.

## 3bis. Mode automatique « one-click si complet »
Le montage peut être **entièrement automatisé** à la seule condition que TOUS les intrants requis soient présents et structurés. Procéder par une **porte de complétude** : si un élément manque, **s'arrêter et lister précisément ce qui manque** — ne JAMAIS produire une DSF partielle présentée comme complète.

Intrants requis (checklist) :
- [ ] Balance après inventaire N et N-1 (structurée)
- [ ] Registre d'immobilisations avec mouvements (→ Note 3)
- [ ] Détail tiers avec échéancier (→ Notes 7/17)
- [ ] Données extra-comptables (R1-R3, effectifs, statistiques, engagements)
- [ ] Retraitements de présentation + passage résultat fiscal (jugements fournis)
- [ ] Mapping comptes→postes validé **+ cell-map du modèle de l'utilisateur** (cellule de saisie de chaque valeur — voir `references/cell-map.example.json`)
- [ ] Modèle DSF (utilisateur, ou fallback confirmé pour le format GE)

Orchestrateur (chaîne unifiée « fichiers → DSF ») : `python scripts/monter_dsf.py --dossier <dossier> --exercice <N> [--cell-map <cm.json>] [--sortie <out.xlsx>]` (ou `--fichiers f1 f2 …`). Il enchaîne automatiquement :
1. **classe** les documents (`classer_documents`) → devine balance / registre / tiers / modèle DSF (**à confirmer**) ;
2. **lit** les données extra-comptables (`extraire_donnees`) → formalise vers le besoin ;
3. **agrège** la balance + **registre → Note 3C** ;
4. **porte de complétude** → liste ce qui manque ;
5. **peuple** une copie du modèle **si un cell-map est fourni**, sinon produit le pré-remplissage.
Overrides possibles : `--balance`, `--registre`, `--tiers`, `--modele`, `--intake` (prioritaires sur la détection).

> **Dépendance restante pour le 100 % automatique** : le **cell-map est propre à chaque modèle** (quelle cellule de quelle Note reçoit quelle valeur). Il se construit/valide une fois par modèle. Sans lui, l'assemblage produit les valeurs mais ne les écrit pas dans la liasse.

## 4. Contrôles de cohérence obligatoires
- Total actif = total passif ; résultat net CR = résultat au bilan.
- Somme des postes agrégés ≈ total balance (écart = comptes non mappés).
- Cohérence Notes ↔ états ; report à nouveau ; TVA.

## 5. Bornes
- Question fiscale ponctuelle / passage résultat fiscal → `fiscalite-guinee-equatoriale`.
- Amortissements détaillés (Note 3C) → `immobilisations-ohada` (registre).

## 6. Exemple travaillé (moteur testé)
Balance BTP → `agreger_balance_dsf.py` produit : TC Travaux **900 000 000** (Note 21), AN engins **600 000 000** (Note 3C), BI Clients **250 000 000** (Note 7), CA Capital **500 000 000** (Note 13), DA Emprunt **300 000 000** (Note 16)… + **compte non mappé signalé**. Ces cumuls alimentent les Notes ; la liasse recalcule le Bilan et le CR.
