# CLAUDE.md — Facil_Finance

Consignes pour Claude Code (poste ou **web**). Elles priment sur les habitudes par défaut. Langue de travail : **français** (code, commentaires, commits, documentation) ; l'interface du produit est traduite en espagnol et en portugais.

## 1. Ce qu'on construit

**Facil Finance** : plateforme de production financière **SYSCOHADA révisé** pour les 17 États de l'OHADA. Elle part de la balance et du grand livre, produit la liasse fiscale (états, notes, tableaux fiscaux), la fait valider par une personne nommée, et garde la trace de tout. Livraison V1 le **30/11/2026**.

**Facil DEF** (`plugin/compta-ohada`) est le produit déjà livré (extension Claude Desktop, v0.13.0) pour la Guinée équatoriale. Son moteur est la **référence métier** : Facil Finance le réutilise (ADR 0005), il ne le réécrit pas.

Vocabulaire : en français on écrit **DSF** (Déclaration statistique et fiscale) ; **DEF** est le terme espagnol. La marque « Facil DEF », le dossier `Facil-DEF` et les fichiers `DEF_…` ne changent pas.

## 2. Carte du dépôt

| Chemin | Contenu |
|---|---|
| `facil_moteur/noyau/` | Lecture balances et grands livres, formules Excel, rendu PDF. **Source unique**, publiée vers le plugin (`outils/publier_vers_plugin.py`, garde de parité) |
| `facil_moteur/packs/` | Format des packs pays : validation, signature Ed25519, couches OHADA ← zone ← pays, pack en vigueur à la date de clôture |
| `packs/` | `ohada/2017.1`, `cemac/2025.1`, `CM/2025.1` (préversion), `GQ/2025.1` |
| `plugin/compta-ohada/` | Facil DEF : skills, serveur MCP (`serveur/mcp_def.py`), formulaire local, OCR des DSF scannées, analyse financière, tests |
| `outils/` | Recettes : `verifier_tout.py`, `facil_pack.py`, `garde_confidentialite.py`, `purger_classeur.py`, conversions |
| `tests/` | Tests du moteur et des packs, une contre-épreuve par garde |
| `docs/` | Documentation projet (MkDocs) : cadrage, PRD, architecture, ADR, specs, plans, sprints. Publiée sur GitHub Pages |
| `manuel/` | Manuel d'utilisation, présentation, flyer de Facil DEF (FR « DSF », ES « DEF ») : sources et PDF |

## 3. Commandes

```bash
# environnement (jamais dans le Python du système)
python -m venv .venv && . .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements-dev.txt
pip install -r plugin/compta-ohada/serveur/requirements.txt          # gardes du plugin
pip install --no-deps rapidocr_onnxruntime==1.4.4                    # OCR (version figée)
pip install -r docs/requirements.txt                                  # documentation

python outils/verifier_tout.py                     # packs + tests + parité noyau ↔ plugin
python outils/garde_confidentialite.py             # données de clients (clé : FACIL_CLE_CONFIDENTIALITE)
python outils/purger_classeur.py --verifier $(git ls-files '*.xlsx')
python plugin/compta-ohada/tools/gardes_ci.py      # toutes les gardes du plugin
python docs/outils/construire_site.py              # site de documentation (strict)
```

En session web, `.claude/settings.json` lance `outils/preparer_environnement.sh` au démarrage.

## 4. Où reprendre

- **Plan de sprints et reprise** : `docs/plans/sprints.md`, sections 2 à 4. Tâches : tickets GitHub, un jalon par sprint.
- **Plan de Facil DEF** : `docs/plans/plan-facil-def.md`, section Reprise.
- **Décisions** : `docs/adr/` — ne pas rouvrir une décision acceptée sans ADR qui la remplace.
- **Exigences** : `docs/prd.md` (identifiants `EX-…`), risques : `docs/registre-risques.md`.

## 5. Règles du produit (non négociables)

1. **Aucune règle de pays dans le moteur** : taux, libellés, lignes, contrôles viennent d'un pack.
2. **Aucun taux sans article** : un paramètre fiscal cite sa source et sa date.
3. **Une liasse se prouve** : chaque poste relié à ses comptes, chaque contrôle consigné, chaque écart expliqué. « Calculé » ≠ « déclaré » ≠ « prouvé ».
4. **Rien n'est écrasé** : écritures, versions de liasse et réponses sont horodatées et conservées.
5. **Les droits sont tenus par la base**, pas seulement par l'écran.
6. **L'IA (Kaem) ne calcule ni ne valide** (ADR 0008) ; elle explique et prépare.
7. **Aucune sortie sans passerelle** : ce qui quitte le poste est pseudonymisé, montants masqués, journalisé.
8. **Le noyau se corrige dans `facil_moteur/noyau/`**, jamais dans sa copie du plugin.

## 6. Confidentialité — le dépôt est PUBLIC

- **Jamais de données de client** : balances, liasses, DSF réelles, noms, NIF, adresses, comptes bancaires, captures non masquées. Ni dans le code, ni dans les tests, ni dans un ticket, ni dans un message de commit.
- Les exemples se **fabriquent** (`plugin/compta-ohada/tests/fabriquer_scan.py`, balances synthétiques).
- Tout classeur ajouté passe par `outils/purger_classeur.py` (liaisons externes, noms cachés, auteurs).
- La liste des noms confidentiels n'est **pas** dans le dépôt ; seules ses empreintes HMAC le sont. Sans clé, la garde le dit ; en CI elle est exigée.

## 7. Méthode de travail

- **Une tâche se termine par une clôture** : preuve en exécution (sortie réelle), SQL relu (index, N+1, `LIMIT`, verrou), geste manuel répété → recette, portée mesurée, **gardes falsifiées** (une mutation par garde), documentation rendue fausse corrigée.
- **Cycle de vie complet** d'une fonctionnalité : qui la crée, la corrige, la suspend, la reprend ; où lire son état et son historique ; qui est prévenu ; rejeu et échec à mi-chemin ; donnée à l'état final ; droits.
- **Une valeur connue d'avance se choisit dans une liste** dérivée de sa source (garde de parité), jamais ressaisie.
- **Sessions** : deux horloges (inactivité 15 min, durée absolue 12 h), tenues par le serveur ; la page prévient une minute avant.
- **Interface** : en-tête de page portant ses commandes, tableaux paginés (20/40/50, choix retenu), filtres en tête de colonne, icônes Lucide seulement, contraste AA calculé, année du pied de page calculée.
- **Ce qui n'est pas fait** devient un ticket daté, jamais un commentaire `TODO`.
- **Ce qu'on n'a pas prouvé se dit** dans la demande de fusion.
- **Dépendances** : aucune sous AGPL, SSPL ou RSAL.

## 8. Git

- Branche par défaut `develop` ; `main` = versions. Travail sur `feat/…`, `fix/…`, `docs/…` ; Claude Code web ouvre `claude/…`.
- Commits [Conventional Commits](https://www.conventionalcommits.org/fr/) en français : `fix(pack-GQ): purger les liaisons externes`.
- Demande de fusion vers `develop`, CI verte exigée. Jamais de `--no-verify`, jamais de poussée forcée sur `develop` ou `main`.
