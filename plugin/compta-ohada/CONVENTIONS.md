# Conventions du plugin « compta-ohada »

Chaque skill du plugin suit le **même pattern** (validé sur le pilote `immobilisations`).

## Anatomie obligatoire d'un SKILL.md
1. **Frontmatter** `name` + `description` (déclencheurs concrets, 3e personne).
2. **§0 Rôle & sécurité** — expertise OHADA/BTP, anonymisation, validation humaine, pas d'invention de taux/comptes.
3. **§1 Intake guidé** — les questions que Claude POSE avant de produire (jamais de CLI imposé à l'utilisateur).
4. **§2 Méthodologie** — étapes OHADA de la tâche.
5. **§3 Calcul** — Claude calcule ; moteur de référence déterministe optionnel si gouvernance.
6. **§4 Livrable Excel** — pré-remplir un template `.xlsx` (formules vivantes), remettre le fichier.
7. **§5 Citation & écriture** — plan de comptes (`../datas/`) et/ou loi citée par article.
8. **§6 Bornes** — quand renvoyer vers un autre skill.
9. **§7 Exemple travaillé** — un cas entrée → sortie.

## Templates Excel
- Onglet **Paramètres/Entrées** (saisie) → onglet **Résultat** (formules).
- Toujours une **cellule de contrôle** (`=OK/ÉCART`).
- Générés par `tools/build_templates.py` (openpyxl), pas à la main.

## Commandes
Une commande par cycle clé (`commands/<cycle>.md`) : `description`, `argument-hint`, corps qui impose l'intake guidé + le livrable Excel.

## Base documentaire
`../datas/` : loi de finances (citée par article) + plan de comptes SYSCOHADA (à remplacer par l'export Sage).

## Robustesse des entrées (scripts à données tabulaires)

### Balances : lecture par invariants comptables (`lib/detection_balance.py`)
Les moteurs qui lisent une **balance** (`agreger_balance_dsf.py`, `dossier_revision.py`, et `classer_documents.py`
pour la reconnaître) ne reconnaissent pas les colonnes par leur nom, mais par les **lois comptables** que leurs
montants respectent :
- équilibre des débits et des crédits ;
- une paire de soldes n'a jamais les deux côtés remplis ;
- ouverture + mouvements = solde ;
- classes 6-7 nulles à l'ouverture ;
- une ligne de cumul vaut la somme de ses sous-comptes.

Les en-têtes (FR/ES/EN) ne font que départager deux lectures.

**Formats couverts** :
- balances à 8, 6, 4, 2 ou 1 colonne, **avec ou sans en-tête** ;
- `.xls`, `.xlsx`, `.csv` ; toutes les feuilles d'un classeur sont essayées ;
- montants en nombre ou en texte (`1 234,56`, `1.234,56`, `(1 234)`) ;
- compte et libellé dans une même cellule ;
- lignes de cumul, y compris décalées : elles sont **prouvées** être des sommes, puis écartées.

**Non couverts** : le PDF (voir `documentation/analyse/decision-import-balances.md`, D3), et les balances N et N-1
dans deux fichiers séparés.

**Issues** :

| Statut | Signification | Comportement |
|---|---|---|
| `ok` | Une seule lecture possible | Le script continue |
| `a_confirmer` | Seules les colonnes secondaires sont incertaines (soldes N sûrs) | Le script continue et le signale |
| `ambigu` | Des soldes N différents selon la lecture (typiquement : soldes N-1 et N sans en-tête) | Le script **s'arrête (code 2)** |
| `illisible` | Aucune balance reconnue | Le script s'arrête (code 2) |

**Consigne au skill** : quand un script s'arrête sur une ambiguïté, **montrer à l'utilisateur les lectures
possibles** (listées sur stderr) et lui demander laquelle est la bonne. Relancer ensuite avec
`--gabarit "<nom>"`. **Ne jamais choisir à sa place.**

**Source unique** : `lib/detection_balance.py`. Les copies dans `skills/*/scripts/` sont produites par
`python tools/sync_lib.py`. `tools/package.py` refuse d'empaqueter si une copie diverge. **Ne jamais éditer une
copie.** Garde : `python tests/test_detection_balance.py` ; falsification :
`python tests/falsification_detection.py`.

### Autres fichiers tabulaires (parc d'immobilisations, données extra-comptables)
`registre_immobilisations.py` et `extraire_donnees.py` reconnaissent encore les colonnes **par leur nom**
(alias + normalisation, repérage de la ligne d'en-tête, override `--col-<champ> "<nom exact>"`). Ces fichiers
n'obéissent à aucun invariant comparable à ceux d'une balance.

**Consigne** : inspecter les en-têtes, faire confiance à l'auto-détection, et **si c'est ambigu, demander**.

## Zones de risque
🔴 fiscalité : jamais de taux « de mémoire », toujours citer la loi + validation. 🟡 calculs à revérifier. 🟢 Excel/structure.
