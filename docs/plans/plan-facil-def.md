---
icon: lucide/file-check
---

# Plan — plugin compta-ohada autonome et installable (lots L1 à L5)

*Ouvert le 29/09/2026. Décisions du porteur, prises le même jour :*
- *dossier de travail dans `Documents\Facil-DEF` ;*
- *serveur MCP, pour fonctionner à la fois dans Claude Desktop et dans Claude Code ;*
- *formulaire web en complément du chat.*

*Formulaire web :*
- *logo Facil comme concepteur ;*
- *pied de page « © Facil - AI Solutions Architect - Emac SAH <année calculée> ».*

*Confidentialité : la sortie des outils ne contient ni écritures ni soldes, seulement des statuts, des questions et des
chemins. Ce que Claude lit part chez Anthropic ; les calculs et les fichiers restent locaux.*

## Lots

| Lot | Contenu | État |
|---|---|---|
| **L1** | Dossier de travail (`espace_def.py`), reconnaissance des sources par leur contenu, versions horodatées, manifeste (empreintes), questions consolidées, réponses réinjectées dans les classeurs et les PDF, filigrane PROJET, validation tracée, commande `/monter-dsf` réécrite (point 3), saisies de l'entreprise prises en compte (point 5) | **fait** le 29/09 : test 18/18, falsification ; validé sur le dossier pilote réel |
| **L2** | Rendu sans Excel : évaluation des formules par le moteur, PDF par PyMuPDF, garde d'équivalence avec Excel (point 4) | **fait** le 29/09 :<br>• `formules_xl.py` (24/24) ;<br>• `lib/rendu_pdf.py` (13/13) ;<br>• équivalence : 691/691 formules identiques à Excel en FR et en ES ;<br>• chaîne complète sans Excel en 27 s ;<br>• 8 sabotages détectés.<br>Excel reste utilisé s'il est présent, par préférence d'aspect ; `FACIL_PDF=natif` force le rendu natif. |
| **L3** | Serveur MCP : outils `analyser_dossier`, `generer_def`, `questions_ouvertes`, `enregistrer_reponse`, `valider_version`, `ouvrir_formulaire`. Empaquetage Claude Code (`.mcp.json` du plugin) et Desktop (extension). Dépendances déclarées, test d'installation sur profil vierge, `INSTALL.md` réécrit (point 2) | **fait** le 29/09 :<br>• `serveur/mcp_def.py` (6 outils) et `serveur/lancer.py` (environnement isolé, créé depuis zéro en 83 s) ;<br>• validation officielle `claude plugin validate --strict` OK ;<br>• installation depuis un profil vierge OK, `claude mcp list` : Connected ;<br>• extension `dist/facil-def.mcpb` validée par `mcpb`, contenu rejoué 9/9.<br>**Non vérifié** : installation dans l'application Claude Desktop, signature. `ouvrir_formulaire` viendra avec L4. |
| **L4** | Formulaire web local : stdlib, 127.0.0.1, jeton, sans ressource externe, arrêt sur inactivité, port libre ; questions obligatoires puis facultatives, identité, NIF des tiers, effectifs (27B) ; bouton « Régénérer » ; logo Facil et pied de page ci-dessus | **fait** le 29/09 :<br>• `serveur/formulaire.py` et outil MCP `ouvrir_formulaire` (7ᵉ outil) ;<br>• deux horloges tenues par le serveur (15 min / 12 h, règle §3bis), préavis d'une minute, battement, onglets synchronisés ;<br>• CSP stricte sous nonce ;<br>• garde 35/35, falsification 14/14, MCP 10/10 ;<br>• vérifié à 375, 768 et 1366 px, dans les deux thèmes ; contraste minimal calculé 4,89 (clair) et 5,24 (sombre).<br>**Non fait** : effectifs 27B, faute de question produite par le moteur → L5.<br>**Limite déclarée** : une réponse texte ne s'efface pas depuis le formulaire (un champ vidé est ignoré) ; la corriger par une autre valeur. |
| **L5** | Banc de validation sur tout triplet (balance, GL, DEF déposée), puis 2 ou 3 dossiers réels du porteur (point 1) | banc : 2026-10-09 ; dossiers : à fournir |

*Demande du porteur du 29/09/2026 (soir) :*
- *utilisateurs sans Python ;*
- *confidentialité garantie par le serveur MCP (pseudonymisation) ;*
- *outils activés automatiquement ;*
- *plus de DEF déposée en production.*

| Lot | Contenu | État |
|---|---|---|
| **L6** | **Gabarit vierge embarqué** : le formulaire officiel GE (51 feuilles), purgé de toute donnée du dossier pilote. Il comprend :<br>• identité remplacée par des repères ;<br>• montants mis à zéro, en gardant les cellules comme repères ;<br>• TF5, actionnaires, dirigeants et balance vidés ;<br>• structure des totaux PROUVÉE une fois, sur les montants du dossier pilote, puis figée dans un fichier annexe.<br>Sans DEF déposée : bilan N-1 tiré de l'ouverture de la balance, notes N-1 vides, et une question sur la DEF de l'exercice précédent.<br>Garde d'équivalence : même DEF qu'avec le modèle déposé sur la colonne N. | **fait** le 29/09 :<br>• `tools/construire_gabarit.py` : 68 noms purgés, contrôle de résidus bloquant ;<br>• équivalence : 3 952 cellules identiques, 0 écart inexpliqué ;<br>• `test_gabarit` 15/15 ; falsification 6/6 (plus 2 sur 3 pour la garde de référence) ;<br>• gardes voisines inchangées.<br>La garde du plugin a trouvé 3 défauts du constructeur (montants au-dessus de l'en-tête, réintégrations, balance), tous corrigés.<br>**Constat inscrit** (→ L5, 2026-10-09) : en mode modèle avec la DEF de l'exercice PRÉCÉDENT, les montants non calculés (notes 12, 28) sont recopiés de l'année d'avant. |
| **L7** | **Confidentialité**, mise en œuvre par une passerelle du serveur MCP :<br>• pseudonymes pour l'entité, les tiers, les NIF et les personnes (table locale, jamais transmise) ;<br>• montants masqués ;<br>• contrôle final bloquant, en échec fermé ;<br>• journal local de tout ce qui est transmis.<br>Côté Claude Code : un hook bloque la lecture directe du dossier de travail.<br>Plugin purgé des mentions du client pilote, avec une garde d'empaquetage (liste d'exclusion hors plugin). | **fait** le 29/09 :<br>• `serveur/confidentialite.py`, `serveur/garde_lecture.py`, `hooks/hooks.json` ;<br>• `test_confidentialite` 31/31, falsification 12/12 ; `test_garde_empaquetage` 5/5 ; MCP 14/14 ;<br>• hook prouvé en vraie session Claude Code (lecture refusée) ;<br>• 21 fichiers purgés, dont un vrai nom de tiers trouvé par la garde dans un test ;<br>• le jeton du formulaire n'est plus transmis ; la ligne de commande de repli passe elle aussi par la passerelle. |
| **L8** | **Activation automatique** : outils pré-autorisés dans la commande et le skill, instructions du serveur, chargement des outils différés (selon ce que Claude Code permet — vérifié dans sa documentation) | **fait** le 29/09 :<br>• `allowed-tools` dans `/monter-dsf` et le skill (6 outils ; `valider_version` exclu volontairement) ;<br>• consigne ToolSearch groupée ; instructions du serveur ;<br>• noms d'outils vérifiés dans une vraie session (7/7 identiques).<br>**Impossible** (documentation) : un plugin ne peut pas livrer une pré-autorisation globale, ni forcer le chargement non différé. |
| **L9** | **Sans Python** : ~~exécutable figé~~ → **Python officiel embarqué** (`runtime/`, 3.13.7 « embeddable », 140 Mo). Extension Desktop de type `binary`, `.mcp.json` et hook sur `runtime/python.exe` | **fait** le 29/09 :<br>• `tools/construire_runtime.py` ;<br>• les 14 gardes passent avec ce seul Python (`tools/gardes_sur_runtime.py`) ;<br>• serveur et hook prouvés en vraie session ;<br>• le gabarit est désormais inclus dans l'extension (il en manquait).<br>**Non vérifié** : installation dans l'application Desktop, signature.<br>**Limite** : Windows seulement sans installation. |


## Reprise

*Réécrite le 2026-10-19 (soir) ; complétée le 2026-10-20 (supports, clôture de session avant le sprint 2 de Facil Finance).*

- **Supports livrés le 20/10** (`C:\DSF\manuel`, sources dans `redaction/`, livrables dans `livrable/` et `livrable/es/`) :
  - manuel d'utilisation (20 p.), présentation commerciale (6 diapositives), flyer d'une page ;
  - français : « DSF » ; espagnol : « DEF ». La marque « Facil DEF », le dossier `Facil-DEF`, les fichiers `DEF_…` et les libellés de l'interface cités restent tels quels ;
  - reconstruire : `uv run "C:/Users/DELL/claude-plugins/plugins/documents-pro/scripts/generer.py" construire document.yaml -o ..\livrable` (idem `presentation.yaml`, et `document-es.yaml` / `presentation-es.yaml` vers `..\livrable\es`) ; flyer : `C:\DSF\compta-ohada\runtime\python.exe flyer\construire_flyer.py [es]` ;
  - captures masquées : `redaction/reperer_masques.py` → `captures.yaml` (nom du client, NIF, adresse, comptes, courriel, jeton).
- **Constaté par le porteur** : l'extension 0.13.0 est installée dans son Claude Desktop (captures du manuel) ; la lecture d'une DEF scannée y a pris moins de 3 minutes.
- **Décision attendue** : 0.13.1, interface en « DSF » en français (boutons et options qui disent « DEF »), puis nouvelles captures du manuel.

- **Version livrée** : 0.13.0, `dist/facil-def.mcpb` (190 Mo, runtime ≈ 440 Mo avec le moteur OCR) ; `test_mcp_def` 15/15 sur l'extension empaquetée.
- **Versions closes depuis le 16/10** :
  - 0.10.1 à 0.10.3 : dossier par défaut, page blanche du formulaire (Referrer-Policy).
  - 0.11.0 : DEF déposée après la génération signalée ; identité reprise des sources ; mode « préparer et valider ».
  - 0.11.1 : DEF en PDF reconnue.
  - 0.12.0 : DEF précédente SCANNÉE lue sur le poste (ocr_def.py) :
    - preuve par les formules SYSCOHADA ;
    - lecture en arrière-plan avec cache ;
    - compte de résultat N-1 repris ;
    - montants non prouvés confirmés dans le formulaire.
- **Preuves 0.12.0** :
  - `test_ocr_def` 23/23, dont « tout montant prouvé est juste » sur une DEF synthétique scannée (`tests/fabriquer_scan.py`).
  - DEF réelles numérisées (non versionnées) : 2024 → 48/48 formules, 212 montants prouvés sur 254 ; 2023 → 49/50.
  - Suite complète verte, y compris `test_mcp_def` 15/15 sur le contenu exact de l'extension.
- **Falsification OCR** : 4 mutations sur 5 détectées au premier passage. La 5ᵉ (« - » imprimé à part) n'était pas exercée par la DEF de test → test ciblé ajouté (section 0 bis) et rejoué seul (`FACIL_MUTATION="imprimé à part"`).
- **L13 FAIT (0.13.0)** : `analyse_financiere.py` — `test_analyse_financiere` 23/23, falsification 4/4 ; dossier pilote réel : 2022-2025, 16 variations expliquées. Limite : sans balances des années passées, l'écart par compte n'est expliqué que pour le bilan.
- **Prochain geste exact** : attendre le retour du porteur sur le rapport ; ensuite, exploiter les balances des années passées si elles sont fournies. (Ancien libellé de L13 : rapport d'analyse financière pluriannuel (N, N-1, N-2…). Il attend le feu vert du porteur.
  - Sources : la balance N, et les DEF ou balances des années passées (scannées ou Excel).
  - Contenu : variations, soldes intermédiaires de gestion, ratios.
  - Explications par compte quand la balance de l'année existe ; points à vérifier pour le personnel.
  - Causes métier : posées en questions facultatives, jamais inventées.
- **Tâches datées** :
  - 2026-10-20 : lire aussi la page de garde des DEF scannées (identité), avec l'OCR déjà en place.
  - 2026-10-20 : accélérer la lecture : environ 12 min par DEF de 44 pages seule, 40 min sur un poste chargé, sur le poste de développement ; moins de 3 min constatées chez le porteur. À mesurer avant d'optimiser.
  - 2026-10-21 : garde de délai dans `test_mcp_def`. Un gel du serveur fait aujourd'hui pendre le test au lieu de le faire échouer.
  - L10 (notes absentes du formulaire), L5 (banc sur dossiers réels), effectifs 27B : inchangés.
- **Limites déclarées** :
  - **Formulaire sans traits verticaux de colonnes** : ses montants sont déclarés illisibles (échec fermé), pas lus.
  - **Écart d'une unité** entre total actif et total passif (DEF 2023) : les montants concernés restent « à vérifier ».
- **Non vérifié** : l'installation de l'extension 0.12.0 dans Claude Desktop sur le poste du porteur (gel corrigé, voir la mémoire `mcp-dll-blocage-entree`). L'extension n'est pas signée.
- **Incidents à retenir** :
  - Une DLL chargée dans un outil MCP pendant la lecture de stdin fige le serveur → `mcp_def.precharger()`. Diagnostic : variable `FACIL_DIAG_PILE`.
  - Pip jamais dans le Python global ; le runtime s'installe par `--target`.
- **Non commité** : aucun, le dossier n'est pas un dépôt git.