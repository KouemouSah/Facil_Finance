---
description: Génère la DEF (= DSF) de Guinée équatoriale depuis le dossier de travail — automatique d'abord, questions ensuite
argument-hint: [entité] [exercice]
allowed-tools: mcp__plugin_compta-ohada_facil-def__dossier_travail, mcp__plugin_compta-ohada_facil-def__lister_dossiers, mcp__plugin_compta-ohada_facil-def__generer_def, mcp__plugin_compta-ohada_facil-def__questions_ouvertes, mcp__plugin_compta-ohada_facil-def__enregistrer_reponse, mcp__plugin_compta-ohada_facil-def__ouvrir_formulaire
---

Tu vas **produire la DEF** (Declaración Estadística y Fiscal) avec le moteur du skill `dsf-syscohada`, depuis le
**dossier de travail** de l'entité. Contexte : $ARGUMENTS

**Voie préférée : les outils MCP du serveur `facil-def`**, livré avec le plugin :
- `dossier_travail` et `lister_dossiers` ;
- `generer_def` ;
- `questions_ouvertes` et `enregistrer_reponse` ;
- `valider_version` ;
- `ouvrir_formulaire`, qui ouvre le formulaire web local.

Les étapes ci-dessous leur correspondent une à une.
- Ils sont démarrés avec le plugin et pré-autorisés pour cette commande, sauf `valider_version`, qui reste soumis à accord.
- S'ils sont **différés**, charge-les tous en **un seul** appel : `ToolSearch` avec
  `select:mcp__plugin_compta-ohada_facil-def__dossier_travail,mcp__plugin_compta-ohada_facil-def__lister_dossiers,mcp__plugin_compta-ohada_facil-def__generer_def,mcp__plugin_compta-ohada_facil-def__questions_ouvertes,mcp__plugin_compta-ohada_facil-def__enregistrer_reponse,mcp__plugin_compta-ohada_facil-def__valider_version,mcp__plugin_compta-ohada_facil-def__ouvrir_formulaire`.

**Repli** si le serveur n'est pas disponible : le script `${CLAUDE_PLUGIN_ROOT}/skills/dsf-syscohada/scripts/espace_def.py`, avec les mêmes actions en ligne de commande. Sa sortie passe par la **même passerelle**. N'emploie jamais `--brut` : cette option est réservée à un humain dans son terminal.

**Confidentialité** :
- Les retours sont **pseudonymisés** sur le poste : `ENTITE-A`, `TIERS-001`, `IDENT-002`, et `[montant]` à la place des montants.
- Réutilise ces pseudonymes tels quels dans les appels : le serveur les rend à leur valeur réelle.
- Ne lis **jamais** les fichiers du dossier Facil-DEF (le hook du plugin le refuse) et ne devine aucun montant.
- Pour voir noms et montants en clair, l'utilisateur ouvre le formulaire local.
- Tout ce qui est transmis est journalisé sur le poste, dans `Facil-DEF\journal_sorties.jsonl`.

1. **Entité et exercice** : repère-les dans les arguments. S'ils manquent, demande-les en **une seule** question.
2. **Dossier de travail** : `python <script> chemin --entite "<E>" --exercice <N>`.
   - Le dossier se crée par défaut dans `Documents\Facil-DEF\<Entité>\<Exercice>`.
   - Si `01_sources` est vide, dis à l'utilisateur d'y déposer **la balance, ou le grand livre, ou les deux** (les
     deux, c'est le mieux). Facultatif : la DEF de l'exercice précédent (au format .xlsx ; elle donne les
     comparatifs N-1 et l'identité de la page de garde), une fiche entité (raison sociale, NIF, adresse…, une fois
     pour toutes) et le logo. Donne-lui le chemin, puis attends qu'il confirme le dépôt.
   - Grand livre seul : la balance est reconstituée depuis ses écritures. Les à-nouveaux deviennent des ouvertures ;
     l'écriture de clôture est exclue ; les comptes centralisés sont repris. La balance obtenue est contrôlée
     (équilibre) ; déséquilibrée, elle suspend le calcul.
3. **Génération automatique** : `python <script> lancer --entite "<E>" --exercice <N>`.
   - `statut = bloque_avant_calcul` : pose la ou les questions renvoyées (balance absente ou ambiguë), puis
     `repondre` et relance.
   - `statut = projet` : annonce la version, les livrables (chemins) et le nombre de questions ouvertes par catégorie.
     La liasse française est au **modèle SYSCOHADA système normal**, adaptée aux données : les notes sans montant
     ni information sont omises et signalées dans la grille. L'espagnol est au format GE. Le choix « Modèle de la
     liasse » (facultatif) permet de repasser au format GE.
     Les PDF portent un filigrane PROJET.
4. **Questions** : `python <script> questions --entite "<E>" --exercice <N>`.
   - Présente d'abord les **obligatoires**, **groupées par catégorie**, avec leur **impact** : identité, faits,
     réintégrations (effet sur l'IS), NIF des tiers.
   - Mentionne les facultatives (choix d'interprétation) sans insister.
   - Dès qu'il y a plus de quelques questions (identité, NIF des tiers), propose le **formulaire local**
     (`ouvrir_formulaire`). Les réponses y restent sur le poste, sans passer par la conversation. On peut y
     régénérer la DEF et la valider. Il se ferme après 15 min d'inactivité ou 12 h ; rappeler l'outil rend un nouveau lien.
     Ne recopie jamais ce lien ailleurs : il contient le jeton d'accès.
   - Enregistre chaque réponse avec `repondre --id <id> --valeur <valeur>`. Une valeur hors des choix est refusée par
     le script : repose la question.
5. **Régénère** (`lancer`) après les réponses. Les réponses sont réinjectées dans les classeurs ET les PDF. Rappelle
   de ne rien saisir directement dans les classeurs générés.
6. **Validation** : seulement sur demande explicite de l'utilisateur, avec son nom :
   `python <script> valider --entite "<E>" --exercice <N> --par "<nom>"`.
   - Le script refuse tant qu'une question obligatoire est ouverte : liste-les.
   - Il refuse aussi si `01_sources` a changé depuis la dernière version (fichier déposé après la génération) :
     régénère, fais relire, puis valide.
   - Une fois validée, la version définitive (sans filigrane) est tracée dans `manifeste.json` et dans le rapport de
     contrôle : chaque réponse appliquée, son origine (formulaire, conversation, reprise d'une source), sa date, le
     valideur. L'identité retenue est posée dans `fiche_entite.json` du dossier de l'entité, pour l'exercice suivant.
   - **Mode « préparer et valider »** (« prépare et valide la DSF 2025 de X, validée par Y ») : le déroulé ne change
     pas — dossier, puis dépôt par l'utilisateur dans `01_sources`, rien avant. Ensuite : générer ; poser **en un seul
     message** toutes les questions obligatoires restantes (`questions_a_poser` du résultat de `generer_def`) ;
     enregistrer, régénérer ; quand `pret_a_valider` est vrai, `valider_version` avec le nom donné — la demande
     d'autorisation de l'outil est le clic de confirmation. Aucune réponse n'est inventée ; sans nom, le demander.
7. **Analyse financière pluriannuelle** (livrée à chaque version, `…_analyse-financiere…` dans 02_xls et 03_pdf,
   interne) :
   - années disponibles : N (balance), N-1, puis celles des DEF précédentes déposées (Excel ou scannées : une DEF
     scannée en donne deux) ;
   - contenu : chiffres clés, états comparés, soldes de gestion, ratios, variations significatives expliquées par
     compte, avec points à vérifier ;
   - les causes ne sont jamais déduites : questions facultatives « Analyse financière » (formulaire), reprises au
     rapport avec leur date. Les balances des années passées ne sont pas encore exploitées (explication par compte du
     compte de résultat limitée à l'exercice N).
8. **Rappelle** que la DEF se dépose après relecture et signature de la direction et de l'expert-comptable, et que le
   rapport de contrôle (`03_pdf\…_controle…pdf`) n'est jamais joint au dépôt.
