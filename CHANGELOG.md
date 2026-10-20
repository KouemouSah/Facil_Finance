# Journal des modifications

Format : [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/). Versions de Facil Finance : `vX.Y.Z` sur `main`. L'extension Facil DEF (`plugin/compta-ohada`) garde sa propre numérotation, détaillée dans [docs/facil-def.md](docs/facil-def.md).

## [Non publié]

### Ajouté
- Dépôt public `KouemouSah/Facil_Finance` : moteur, packs pays, extension Facil DEF (`plugin/compta-ohada`), documentation (`docs/`), manuels (`manuel/`).
- CI/CD : `ci.yml` (confidentialité, lint, moteur sur Ubuntu et Windows, gardes du plugin sur Windows et Ubuntu), `documentation.yml` (site strict publié sur GitHub Pages avec portail et manuels), `securite.yml` (CodeQL), Dependabot.
- `outils/garde_confidentialite.py` : noms confidentiels contrôlés par empreintes HMAC (la liste et la clé restent hors dépôt), courriels, IBAN, téléphones ; contre-épreuves dans `tests/test_garde_confidentialite.py`.
- `outils/purger_classeur.py` : purge des liaisons externes, noms cachés et auteurs des classeurs ; `--verifier` en CI.
- `outils/construire_portail.py` (portail GitHub Pages), `outils/maj_readme.py` (feuille de route du README dérivée de `calendrier.yml`), `outils/installer_crochets.py`, `outils/preparer_environnement.sh` (sessions Claude Code web).
- `plugin/compta-ohada/tools/gardes_ci.py` : toutes les gardes du plugin avec le Python courant, chacune bornée par un délai.
- Documentation : Démarrer, Facil DEF, Manuels, Modèle de données cible, Catalogue des modules, Chaîne de livraison, Sécurité et confidentialité, Plan de Facil DEF ; sources du projet versionnées dans `docs/sources/`.
- Normalisation : LICENSE (propriétaire), CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, CODEOWNERS, formulaires de tickets, modèle de demande de fusion, `.editorconfig`, `.gitattributes`, `CLAUDE.md`.

### Corrigé
- **Gabarit GE** (`packs/GQ/2025.1/gabarits/def_ge.xlsx` et sa source dans le plugin) : 125 liaisons externes et 2 259 noms définis hérités d'autres classeurs, dont le cache contenait des noms de personnes et un numéro de compte bancaire, retirés avant publication ; auteurs des propriétés neutralisés dans tous les classeurs. Gardes du plugin et du moteur rejouées.
- Coordonnées de la SIC masquées dans `travaux/sic-releve.json`.

### Modifié
- Le plugin est cherché dans `plugin/compta-ohada` (et non plus à côté du dépôt) ; la parité noyau ↔ plugin n'est plus jamais sautée.

## [0.1.0] — Sprint 1 · Fondations

### Ajouté
- Format du pack pays : validation, signature Ed25519, résolution des couches OHADA ← zone ← pays, pack en vigueur à la date de clôture (`facil_moteur/packs`, `outils/facil_pack.py`).
- Packs `ohada/2017.1`, `cemac/2025.1`, `CM/2025.1` (préversion), `GQ/2025.1` (converti depuis le plugin).
- Noyau du moteur extrait en bibliothèque, source unique publiée vers le plugin avec garde de parité (ADR 0005).
- Démonstration : IS de la SIC 2025 (DSF publiée) reproduit au franc près.
- `outils/verifier_tout.py` en crochet pre-commit.
