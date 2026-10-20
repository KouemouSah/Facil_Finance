---
icon: lucide/list-checks
---

# Exigences produit (PRD)

<span class="statut statut--brouillon">brouillon</span> · Version 0.1 · 15/10/2026

!!! abstract "Règle de traçabilité"
    Chaque exigence porte un identifiant stable `EX-<domaine>-<n>`. Une spécification, un test ou un ticket la cite par cet identifiant. Une exigence retirée est **barrée**, jamais supprimée : son identifiant n'est jamais réattribué.

## 1. Vision

> Donner à chaque équipe comptable de l'espace OHADA une liasse **juste, prouvée et déposable**, produite à partir de ce qu'elle a déjà : sa balance, son grand livre, ses écritures. Aucune ressaisie, aucune migration, aucune donnée qui quitte ses murs sans son accord.

## 2. Personas

| Persona | Contexte | Ce qu'il attend | Ce qui le fait renoncer |
|---|---|---|---|
| **Aïcha, comptable unique d'une PME** (Douala) | Tient la comptabilité sur un logiciel local ; dépose la DSF chaque année dans l'urgence | Déposer sa balance et obtenir une liasse correcte, avec la liste de ce qui manque | Une ressaisie ; un écran en jargon informatique |
| **Martín, chef de mission en cabinet** (Malabo) | 40 dossiers par an, en FR et en ES | Traiter un dossier en heures et non en jours ; une piste de contrôle à montrer au client | Un chiffre qu'il ne peut pas justifier |
| **Directrice administrative et financière d'un groupe** (Abidjan) | Plusieurs sociétés, des auditeurs externes | Des états cohérents entre sociétés ; un reporting du dirigeant | Des données de groupe envoyées dans un cloud étranger |
| **Administrateur informatique** (Dakar) | Un serveur Linux, un accès par SSH | Installer et mettre à jour sans écran, avec un retour arrière possible | Docker imposé ; une dépendance système à gérer |
| **Expert-comptable valideur** (partenaire pays) | Signe les liasses | Voir chaque chiffre relié à ses comptes et au texte qui le fonde | Une boîte noire |

## 3. Exigences

Priorités : **D** = Doit · **De** = Devrait · **P** = Pourrait · **N** = N'aura pas dans cette version (MoSCoW).

### 3.1 Entrées (IMP)

| ID | Exigence | Priorité | Version | Critère d'acceptation |
|---|---|---|---|---|
| EX-IMP-1 | Importer une balance de 1 à 8 colonnes (xls, xlsx, csv), avec ou sans en-tête, reconnue par son contenu | D | 1.0 | 18 formats de référence reconnus ; toute ambiguïté est **signalée, jamais tranchée en silence** |
| EX-IMP-2 | Importer un grand livre seul et en **reconstituer la balance contrôlée** | D | 1.0 | Balance équilibrée ; à-nouveaux et comptes centralisés pris en compte |
| EX-IMP-3 | Importer balance **et** grand livre, et les rapprocher | D | 1.0 | Écart par compte, expliqué ou signalé |
| EX-IMP-4 | Importer les écritures (FEC ou équivalent) dans le grand livre de la base | De | 1.0 | Écritures immuables, horodatées, avec leur source |
| EX-IMP-5 | Reprendre la liasse de l'exercice précédent comme source N-1 | De | 1.0 | Colonnes N-1 renseignées et contrôlées |

### 3.2 Production (PROD)

| ID | Exigence | Priorité | Version | Critère d'acceptation |
|---|---|---|---|---|
| EX-PROD-1 | Produire les états du **système normal** sur le formulaire officiel du pays | D | 1.0 | Bilan équilibré ; résultat du compte de résultat = résultat du bilan ; chaque poste chiffré a sa ligne |
| EX-PROD-2 | Produire les états du **système minimal de trésorerie** | D | 1.0 | Formulaire SMT officiel du pays, contrôles du pack |
| EX-PROD-3 | **Adapter la liasse aux données** : notes sans montant ni information omises, et omission déclarée | D | 1.0 | Grille de couverture listant chaque note omise et son motif |
| EX-PROD-4 | Contrôle « note = poste » pour chaque note chiffrée | D | 1.0 | 0 écart non expliqué |
| EX-PROD-5 | Tableaux fiscaux du pays, chaque taux **cité avec son article** | D | 1.0 | Paramètres du pack, aucun taux dans le code |
| EX-PROD-6 | Sorties Excel (formules vivantes) et PDF, **sans Excel installé** | D | 1.0 | Valeurs identiques à Excel sur le jeu de référence |
| EX-PROD-7 | Versions PROJET (filigrane) et DÉFINITIVE (après validation explicite) ; une version n'est jamais écrasée | D | 1.0 | Historique des versions consultable |
| EX-PROD-8 | Liasse en FR, ES, PT (et EN au Cameroun) selon le pays | D | 1.0 | Libellés officiels tirés du pack, jamais d'une traduction automatique |

### 3.3 Révision et contrôle (REV)

| ID | Exigence | Priorité | Version | Critère d'acceptation |
|---|---|---|---|---|
| EX-REV-1 | Les questions ouvertes sont consolidées, avec leur impact chiffré | D | 1.0 | Une seule liste, groupée et triée par impact |
| EX-REV-2 | Les réponses sont réinjectées partout où elles comptent | D | 1.0 | Régénération idempotente : même entrée, même sortie |
| EX-REV-3 | Remarques à l'attention de l'expert-comptable, exportables | De | 1.0 | Document généré avec la liasse |
| EX-REV-4 | Analyse des écritures (ISA 240 : écritures inhabituelles) | P | 1.2 | — |

### 3.4 Plateforme (PLAT)

| ID | Exigence | Priorité | Version | Critère d'acceptation |
|---|---|---|---|---|
| EX-PLAT-1 | **Toujours en mode serveur**, accès par navigateur, monoposte = serveur local | D | 1.0 | [ADR 0002](adr/0002-toujours-en-mode-serveur.md) |
| EX-PLAT-2 | Plusieurs sociétés et plusieurs exercices par installation | D | 1.0 | Cloisonnement prouvé par la base |
| EX-PLAT-3 | Rôles et droits par société, tenus **par la base** | D | 1.0 | Un accès refusé par l'écran l'est aussi par l'API |
| EX-PLAT-4 | Session à deux horloges : 15 min d'inactivité et 12 h au maximum, préavis d'une minute | D | 1.0 | Testé de part et d'autre de chaque seuil |
| EX-PLAT-5 | Installation sans assistance (`--unattended`) et mise à jour avec retour arrière | D | 1.0 | Matrice d'installation verte |
| EX-PLAT-6 | Sauvegarde chiffrée automatique ; restauration guidée et **testée** | D | 1.0 | Restauration exercée en CI |
| EX-PLAT-7 | Interface FR, ES, PT, EN | D | 1.0 | Aucun libellé en dur |
| EX-PLAT-8 | Licence hors ligne signée | D | 1.0 | Fonctionne sans Internet |

### 3.5 Confidentialité et IA (IA)

| ID | Exigence | Priorité | Version | Critère d'acceptation |
|---|---|---|---|---|
| EX-IA-1 | Kaem répond en texte sur un catalogue de commandes sûr | D | 1.1 | Banc métier ≥ 90 % |
| EX-IA-2 | Kaem **ne calcule ni ne valide** : il appelle le moteur et cite ses sources | D | 1.1 | [ADR 0008](adr/0008-ia-ne-calcule-ni-ne-valide.md) |
| EX-IA-3 | Modèle local, téléchargé et vérifié (empreinte, signature) ; l'application reste utilisable sans lui | D | 1.1 | [ADR 0007](adr/0007-kaem-ia-locale.md) |
| EX-IA-4 | Toute sortie vers un service externe passe par la passerelle de confidentialité et est journalisée | D | 1.0 | Contrôle avant envoi ; envoi bloqué en cas de doute |
| EX-IA-5 | Kaem parle (voix féminine) et écoute | De | 2.1 | Banc vocal FR/ES/PT |

### 3.6 Comptabilité et production complète (CPT) — V1.2

| ID | Exigence | Priorité | Version | Critère d'acceptation |
|---|---|---|---|---|
| EX-CPT-1 | Saisie d'écritures dans le **même grand livre** que les écritures importées ([ADR 0004](adr/0004-erp-entree-par-la-production.md)) | D | 1.2 | Écriture équilibrée, numérotée sans trou, immuable une fois validée ; correction par extourne |
| EX-CPT-2 | Lettrage des comptes de tiers | D | 1.2 | Lettrage et délettrage tracés |
| EX-CPT-3 | Clôture mensuelle et annuelle, périodes verrouillées | D | 1.2 | Aucune écriture possible dans une période close ; réouverture tracée et motivée |
| EX-CPT-4 | Déclarations de TVA périodiques, selon le pack | De | 1.2 | Rapprochement de la TVA avec le grand livre |
| EX-CPT-5 | OCR des pièces (factures, relevés) → **proposition** d'écriture | De | 1.2 | ≥ 90 % des champs justes sur le corpus de recette ; 0 écriture sans validation humaine |
| EX-CPT-6 | Télédéclaration vers la plateforme nationale, là où elle existe | P | 1.2 | Fichier accepté par la plateforme de test |
| EX-CPT-7 | Analyse des écritures inhabituelles (ISA 240) | De | 1.2 | Rapport par critère, avec le lien vers les écritures |

### 3.7 Reporting (REP) — V1.0 à V1.2

| ID | Exigence | Priorité | Version | Critère d'acceptation |
|---|---|---|---|---|
| EX-REP-1 | Cartes de synthèse par société : résultat, trésorerie, capitaux propres, BFR | D | 1.0 | Chiffres identiques aux états produits |
| EX-REP-2 | Comparaison N / N-1, avec des ratios SYSCOHADA | D | 1.0 | Formule de chaque ratio documentée |
| EX-REP-3 | Tableau de bord du dirigeant (mensuel) | De | 1.2 | Mis à jour à chaque clôture mensuelle |
| EX-REP-4 | Export et impression de tout tableau | D | 1.0 | Excel, PDF, impression A4 et A3 |

### 3.8 SaaS (SAAS) — V2.0

| ID | Exigence | Priorité | Version | Critère d'acceptation |
|---|---|---|---|---|
| EX-SAAS-1 | Isolation des clients **par la base** (sécurité au niveau des lignes) et une clé de chiffrement par client | D | 2.0 | Banc d'isolation : 0 donnée lue d'un autre client, testé aussi en contre-épreuve |
| EX-SAAS-2 | Identité fédérée (OIDC, Keycloak), double authentification | D | 2.0 | [ADR 0010](adr/0010-identite-selon-edition.md) |
| EX-SAAS-3 | Souscription, essai, facturation et résiliation, **avec restitution des données** | D | 2.0 | Export complet, dans un format ouvert, en moins de 24 h |
| EX-SAAS-4 | Hébergement régional ; données localisées selon le pays quand la loi l'exige | D | 2.0 | Région de stockage choisie à la souscription ; affichée dans la console |
| EX-SAAS-5 | Migration de l'édition installée vers le SaaS, **et retour** | D | 2.0 | Migration aller-retour sans perte sur le jeu de référence |
| EX-SAAS-6 | Engagement de service : disponibilité, sauvegardes, restauration | D | 2.0 | Restauration exercée chaque mois |
| EX-SAAS-7 | Console d'exploitation, et supervision par client | D | 2.0 | Alerte avant saturation |

### 3.9 Kaem voix et veille (VOX) — V2.1

| ID | Exigence | Priorité | Version | Critère d'acceptation |
|---|---|---|---|---|
| EX-VOX-1 | Kaem écoute et répond à voix féminine en FR, ES et PT | D | 2.1 | Banc vocal : 100 phrases comptables par langue |
| EX-VOX-2 | Le micro est activé par un geste explicite ; un témoin d'écoute est visible ; le micro peut être coupé | D | 2.1 | Aucun son enregistré hors d'une écoute signalée |
| EX-VOX-3 | Veille : échéances fiscales du pack et anomalies détectées, notifiées | De | 2.1 | Une alerte cite sa règle et son échéance |
| EX-VOX-4 | Mot d'éveil local sur une application de bureau, en option, avec consentement tracé | P | 2.1 | Désactivé par défaut |

## 4. Mesures de succès

| Mesure | Cible | Comment on la mesure |
|---|---|---|
| Liasses reproduites par pays validé | ≥ 30, écarts tous expliqués | Banc de reproduction |
| Durée d'un dossier type, de l'import à la liasse PROJET | < 1 h (contre plusieurs jours aujourd'hui, *hypothèse à mesurer chez les pilotes*) | Horodatage des étapes |
| Installation sans assistance | < 30 min | Matrice d'installation |
| Écarts non expliqués dans une liasse livrée | 0 | Grille de contrôle |
| Réussite de Kaem sur le banc métier (V1.1) | ≥ 90 % | Banc d'évaluation |
| Clients SaaS migrés sans perte (V2.0) | 100 % | Comparaison avant et après sur le jeu de référence |
| Disponibilité du SaaS (V2.0) | engagement à fixer avec le juriste | Supervision |

## 5. Ce qui n'est pas encore décidé

- **Le prix des éditions** : il sera proposé après la mesure de l'effort réel sur le premier pack pays.
- **La plateforme de télédéclaration** : elle existe dans certains pays (SEN ETAFI au Sénégal, E-Liasse au Mali). Le raccordement se fera pays par pays, en V1.2.
