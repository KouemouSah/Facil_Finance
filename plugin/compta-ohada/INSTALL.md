# Installation — plugin « compta-ohada »

Deux voies de déploiement selon la surface. Le contenu livrable est dans `dist/` :
- `dist/compta-ohada.zip` — **plugin complet** (skills + commandes + templates + base documentaire).
- `dist/skills/<skill>.zip` — **skills individuels** (pour import dans Claude for Work / Team).

> ⚠️ Les mécanismes d'installation évoluent selon la version de Claude Desktop / Claude Code. Vérifier dans l'app la méthode en vigueur ; les étapes ci-dessous donnent la marche générale.

---

## Prérequis (les deux voies)
- **Rien à installer** sur un poste Windows : le plugin **embarque son propre Python** (`runtime/`, distribution officielle « embeddable » de python.org, 3.13.7) et toutes ses dépendances, déjà compilées.
  - Rien n'est écrit dans le registre ni dans un Python existant, et rien n'est téléchargé chez l'utilisateur.
  - Le serveur démarre en quelques secondes. Il n'y a plus d'installation au premier lancement, qui dépassait le délai de 60 s de Claude Code.
  - Coût : environ 140 Mo sur disque, dont 53 Mo pour le moteur PDF.
- **Excel n'est pas requis.** S'il est présent, il est utilisé pour l'aspect des PDF.
- **Windows seulement** pour le fonctionnement sans installation. Sur macOS ou Linux, la voie développeur reste possible, avec un Python ≥ 3.10 : `python serveur/lancer.py` crée un environnement isolé. Il faut alors adapter `.mcp.json`.

## Confidentialité (les deux voies)
- Calculs et fichiers restent sur le poste. Ce que Claude reçoit des outils est **pseudonymisé par le serveur**, qui applique trois règles :
  - noms de l'entité, des tiers et des personnes, identité et NIF → `ENTITE-A`, `TIERS-001`… ;
  - montants → `[montant]` ;
  - chemins → relatifs.
- Avant envoi, un contrôle final **bloque** toute sortie où subsisterait une valeur réelle.
- Tout ce qui est transmis est **journalisé** sur le poste : `Facil-DEF\journal_sorties.jsonl`. La table des pseudonymes (`Facil-DEF\.facil_coffre.json`) ne quitte jamais le poste.
- Dans Claude Code, un **hook** du plugin refuse toute lecture directe du dossier `Facil-DEF` par Claude.
- Réglage : dans l'extension Desktop, la case « nom de l'entité en clair » ; dans Claude Code, la variable `FACIL_CONFIDENTIALITE=standard`. Le défaut est « stricte ».
- **Limite** : ce que l'utilisateur écrit lui-même dans la conversation, ou un fichier qu'il y joint, part tel quel. Pour saisir sans rien envoyer, utiliser le formulaire local.

## Voie A — Claude Code (plugin complet : skills, commandes, serveur MCP)
1. Ajouter la place de marché Facil, puis installer le plugin :
   ```
   claude plugin marketplace add <dossier du plugin ou dépôt partagé>
   claude plugin install compta-ohada@facil
   ```
   Depuis une session, la commande `/plugin` offre les mêmes choix. **Contrôlé** : l'installation a été jouée depuis un profil Claude vierge.
2. Vérifier : `claude mcp list` doit afficher `plugin:compta-ohada:facil-def … ✓ Connected`.
3. Utiliser : `/monter-dsf <Entité> <Exercice>`, ou « prépare la DEF 2025 de <Entité> ».

## Voie A bis — Claude Desktop (extension)
1. Ouvrir `dist/facil-def.mcpb` (double-clic, ou Paramètres → Extensions → Installer une extension).
2. Choisir le **dossier de travail**, par défaut `Documents\Facil-DEF`.
3. Dans une conversation : « prépare la DEF 2025 de <Entité> ». Claude utilise les outils `dossier_travail`, `generer_def`, `questions_ouvertes`, `enregistrer_reponse`, `valider_version` et `ouvrir_formulaire`.

## Formulaire web local (les deux voies)
- « Ouvre le formulaire de la DEF » : Claude ouvre dans le navigateur une page servie **par le poste lui-même**. On y répond aux questions, on régénère la DEF et on valide la version.
- **Les réponses saisies là ne passent pas par la conversation.**
- Sécurité de la page :
  - écoute sur 127.0.0.1 uniquement ;
  - lien à jeton aléatoire, témoin `HttpOnly` et `SameSite=Strict` ;
  - contrôle de l'hôte et de l'origine ;
  - aucune ressource externe (politique CSP stricte).
- Fermeture : le serveur ferme après **15 min d'inactivité** ou **12 h** au plus. La page prévient une minute avant et propose « Rester connecté ». Pour rouvrir, redemander le formulaire à Claude : il rend un nouveau lien.
- Hors de Claude : `python serveur/formulaire.py --entite "<Entité>" --exercice <N>`, avec le Python de l'environnement isolé.

L'extension est validée et empaquetée par l'outil officiel `mcpb`, et son contenu a été rejoué hors de Claude : 9/9. **Non vérifié à ce jour** :
- l'installation dans l'application Claude Desktop elle-même ;
- la signature de l'extension, qui exige un certificat de l'éditeur (`npx @anthropic-ai/mcpb sign`).

---

## Voie B — Claude for Work / Team (surface « néophyte »)

Les 5 comptables travaillent surtout dans le chat web où les commandes ne sont pas garanties. On importe les **skills individuels** et on crée des **Projects miroirs**.

1. **Importer les skills** : Paramètres → Capabilities/Skills → importer chaque `dist/skills/<skill>.zip` (ou côté admin pour toute l'équipe). Vérifier au préalable que la fonctionnalité Skills est activée sur l'espace Team.
2. **Créer les Projects miroirs** (voir `../04-skills-agents-metiers.md`) : un Project par domaine, avec dans les instructions le corps du `SKILL.md` correspondant (l'intake guidé fonctionne tel quel).
3. **Base documentaire** : téléverser dans la connaissance du Project les fichiers de `datas/` (`ley_tributaria_2024.md`, `plan-comptable-syscohada-standard.md`, et le futur export Sage).
4. **Templates Excel** : mettre les `.xlsx` des dossiers `skills/*/templates/` à disposition des utilisateurs (dossier partagé ou joints au Project), pour que Claude les pré-remplisse.

---

## Câblage de la base documentaire (obligatoire pour le skill fiscal)
- Le plugin embarque une **copie** de la base dans `compta-ohada/datas/` (loi de finances + plan de comptes).
- **Source de vérité = `claude-compta/datas/`** (central). À chaque mise à jour (décret, note DGI, **export Sage réel**), mettre à jour le central puis re-synchroniser la copie du plugin et re-packager.

## Vérification (recette rapide)
- `/amortissement` → l'assistant pose l'intake, calcule, et pré-remplit `tableau-amortissement.xlsx` (contrôle « OK », VNC finale 0).
- `/dsf` avec un cas → réponse **citant un article** de la loi (ex. art. 52), jamais un taux « de mémoire ».
- Ouvrir 2-3 templates dans Excel → les cellules de contrôle affichent « OK ».

## Maintenance
- **Runtime embarqué** : `python tools/construire_runtime.py`. Il est idempotent et reconstruit le runtime si `serveur/requirements.txt` change ; `package.py` l'appelle. Preuve : `python tools/gardes_sur_runtime.py` rejoue toutes les gardes avec ce seul Python.
- **Gabarit officiel** : `python tools/construire_gabarit.py` (fichiers du dossier pilote, hors plugin).
- **Garde d'empaquetage** : `package.py` refuse d'empaqueter si une valeur de `documentation/analyse/reference/noms_confidentiels.txt` (liste tenue HORS plugin) figure dans un fichier ou un classeur du plugin.
- Dépendances : `serveur/requirements.txt`. Elles sont installées dans le runtime embarqué ; le lanceur `serveur/lancer.py` sert à la voie développeur.
  - `xlrd` : lecture des balances `.xls` ;
  - `pillow` : logos ;
  - `pymupdf` : PDF natifs, filigrane PROJET, pagination ;
  - `mcp` : serveur ; la version 1.x est volontaire, la 2.x ayant renommé son API.
- Serveur MCP : `serveur/mcp_def.py`, déclaré pour Claude Code dans `.mcp.json` et pour Claude Desktop dans `extension/manifest.json`. Garde : `python tests/test_mcp_def.py` (vrai client MCP, 10 contrôles, dont l'ouverture du formulaire).
- Extension Desktop : `python tools/construire_extension.py` (également appelé par `package.py`).
- **Rapports PDF : Excel n'est plus requis.**
  - Les formules sont évaluées par le plugin (`formules_xl.py`, prouvé identique à Excel sur la DEF du dossier pilote).
  - Les PDF sont rendus par PyMuPDF (`rendu_pdf.py`).
  - Si Excel est présent, il reste utilisé pour l'export, par préférence d'aspect. `FACIL_PDF=natif` force le rendu natif.
- **Dossier de travail** : `Documents\Facil-DEF\<Entité>\<Exercice>\` (01_sources, 02_xls, 03_pdf, 04_questions, manifeste.json). Il est créé au premier lancement de `/monter-dsf`. Pour le placer ailleurs, définir la variable `FACIL_DEF_RACINE`.
- Régénérer les templates : `python tools/build_templates.py`.
- **Moteur de lecture des balances** : il se modifie **uniquement** dans `lib/detection_balance.py`, puis
  `python tools/sync_lib.py` le recopie dans les skills qui l'embarquent.
- Tests : `python tests/test_detection_balance.py` (balance synthétique ; la balance réelle se passe par
  `DSF_BALANCE_REELLE=<chemin>` et `DSF_RESULTAT_REEL=<résultat>`). Falsification :
  `python tests/falsification_detection.py`.
- **Correspondance comptes → postes DEF** :
  - elle ne se modifie que dans `skills/dsf-syscohada/references/mapping-comptes-dsf.json` ;
  - `python tools/gen_mapping_md.py` régénère ensuite la doc lisible ;
  - garde : `python tests/test_mapping_dsf.py` ; falsification : `python tests/falsification_mapping.py` ;
  - validation sur un cas réel : la garde de référence du dossier pilote (hors plugin), hors plugin puisqu'il utilise les données du client.
- **Moteur fiscal GE (TF1/TF2)** :
  - il se modifie dans `lib/fiscal_ge.py`, et ses taux dans `lib/parametres_fiscaux_ge.json`, où chaque valeur cite son article ; puis `python tools/sync_lib.py` ;
  - garde : `python tests/test_fiscal_ge.py` ; falsification : `python tests/falsification_fiscal.py` ;
  - validation réelle : la garde de référence du dossier pilote (hors plugin), qui recalcule le classeur dans Excel.
- **TF3/TF4/TF5 et lecture du grand livre** :
  - ils se modifient dans `lib/grand_livre.py` et `lib/tf345_ge.py`, puis `python tools/sync_lib.py` ;
  - garde : `python tests/test_tf345_ge.py` (reproductibilité incluse) ; falsification : `python tests/falsification_tf345.py` ;
  - validation réelle : la garde de référence du dossier pilote (hors plugin).
- **DEF complète et PDF** (`skills/dsf-syscohada/scripts/def_ge.py`) :
  - le PDF passe par Excel s'il est présent, sinon par le rendu natif (PyMuPDF), sinon par LibreOffice ;
  - garde : `python tests/test_def_ge.py` ; falsification : `python tests/falsification_def.py` ;
  - validation réelle : la garde de référence du dossier pilote (hors plugin).
- **DEF sur le modèle déposé** (`skills/dsf-syscohada/scripts/def_modele.py`) :
  - mêmes prérequis PDF que ci-dessus ; logo : Pillow (`pip install pillow`), qu'openpyxl exige pour insérer une image ;
  - garde : `python tests/test_def_modele.py` ; falsification : `python tests/falsification_def_modele.py` ;
  - validation réelle : la garde de référence du dossier pilote (hors plugin), et équivalence évaluateur / Excel : la garde de référence du dossier pilote (hors plugin). Excel sert de référence dans ces deux gardes.
- **Rendu sans Excel** :
  - `formules_xl.py` : garde `tests/test_formules_xl.py` ;
  - `lib/rendu_pdf.py` : garde `tests/test_rendu_pdf.py` ;
  - falsification des deux : `tests/falsification_rendu.py`.
- **Dossier de travail** (`espace_def.py`) : garde `tests/test_espace_def.py`, falsification `tests/falsification_espace_def.py`.
- **Formulaire web** (`serveur/formulaire.py`) : garde `tests/test_formulaire.py` (vrai serveur, 35 contrôles, horloges éprouvées des deux côtés du seuil) ; falsification `tests/falsification_formulaire.py` (14 sabotages, ≈ 10 min).
- ⚠️ `tools/sync_lib.py` **refuse d'écraser** un fichier de skill qui n'est pas une copie de `lib/`. Un homonyme se renomme : c'est ainsi que la commande est devenue `calcul_tf345_ge.py`.
- Re-valider + re-packager : `python tools/package.py` → vérifie les copies du moteur, **lance les tests**,
  régénère `dist/`. Refuse d'empaqueter si une copie diverge ou si un test échoue.
- Ajouter un cycle : créer `skills/<cycle>/SKILL.md` (suivre `CONVENTIONS.md`), une commande, un template dans `build_templates.py`.
