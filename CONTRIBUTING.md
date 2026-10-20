# Contribuer à Facil Finance

## Branches

| Branche | Rôle | Qui y écrit |
|---|---|---|
| `develop` | Intégration, **branche par défaut** ; le site de documentation est publié depuis elle | demandes de fusion relues |
| `main` | Versions livrées, étiquetées `vX.Y.Z` | fusion de `develop` à chaque version |
| `feat/…`, `fix/…`, `docs/…`, `ci/…`, `refactor/…`, `test/…` | Travail en cours, partent de `develop` | l'auteur |
| `claude/…` | Branches ouvertes par Claude Code (poste ou web) | Claude Code, relues avant fusion |

Les deux branches longues sont protégées : fusion par demande seulement, vérifications vertes exigées.

## Messages de commit

Format [Conventional Commits](https://www.conventionalcommits.org/fr/), en français :

```
<type>(<portée>): <résumé à l'infinitif, sans point final>

Pourquoi ce changement ; ce qui a été prouvé, et comment.
```

Types : `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `ci`, `build`, `chore`. Portées : `moteur`, `packs`, `pack-<PAYS>`, `plugin`, `ocr`, `analyse`, `docs`, `ci`, `api`, `base`, `interface`, `installeurs`, `kaem`.

Exemple : `fix(pack-GQ): purger les liaisons externes du gabarit DEF`.

## Avant d'ouvrir une demande de fusion

```bash
python outils/verifier_tout.py                      # packs + tests + parité noyau ↔ plugin
python outils/garde_confidentialite.py              # aucune donnée de client
python outils/purger_classeur.py --verifier $(git ls-files '*.xlsx')
python plugin/compta-ohada/tools/gardes_ci.py       # gardes du plugin
python docs/outils/construire_site.py               # documentation (si elle change)
```

Le crochet local `pre-commit` (installé par `python outils/installer_crochets.py`) rejoue `verifier_tout.py` et la garde de confidentialité : un commit rouge est refusé.

## Définition de « fait »

Une tâche n'est pas faite quand le code marche. Elle est faite quand :

1. **la preuve est en exécution** : sortie réelle de commande dans la demande de fusion, pas « ça devrait marcher » ;
2. **toute garde ajoutée a été falsifiée** : une mutation la fait rougir (voir `tests/falsifi*`) ;
3. **la portée est mesurée** : qui d'autre lit cette table, appelle cette route, dépend de ce nom ;
4. **le SQL est relu** : filtre indexé, pas de N+1, lecture bornée, verrou pris où il faut ;
5. **la documentation que le changement rend fausse est corrigée** dans la même demande ;
6. **le cycle de vie est complet** : créer, corriger, suspendre, reprendre, tracer, purger, droits.

## Règles qui ne se négocient pas

- **Aucune donnée de client dans le dépôt**, ni dans un ticket : balances, liasses, noms, identifiants fiscaux, coordonnées, captures non masquées. Un exemple se fabrique (`plugin/compta-ohada/tests/fabriquer_scan.py`).
- **Aucune règle de pays dans le moteur** : tout vient d'un pack.
- **Aucun taux sans article** : un paramètre fiscal cite sa source.
- **Le noyau se corrige dans `facil_moteur/noyau/`**, jamais dans sa copie du plugin.
- **Une valeur connue d'avance se choisit dans une liste**, elle ne se saisit pas.
- **Aucune dépendance sous AGPL, SSPL ou RSAL** (licence propriétaire, ADR 0011).
- **Jamais de `pip install` dans le Python du système** : environnement virtuel, ou `--target` pour le runtime embarqué.

## Tickets

Utilisez les formulaires (anomalie, fonctionnalité, tâche). Une tâche porte : son sprint (jalon), son exigence (`EX-…`), sa zone, sa taille, et sa définition de « fait ».
