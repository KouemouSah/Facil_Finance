---
icon: lucide/scale
---

# Décisions d'architecture (ADR)

Une fiche par décision structurante. Une décision **n'est jamais réécrite** : si elle change, une nouvelle fiche la **remplace** et l'ancienne passe au statut *remplacée par …*.

| N° | Décision | Statut | Date |
|---|---|---|---|
| [0001](0001-consigner-les-decisions.md) | Consigner les décisions sous forme d'ADR | acceptée | 15/10/2026 |
| [0002](0002-toujours-en-mode-serveur.md) | Toujours en mode serveur, même en monoposte | acceptée | 15/10/2026 |
| [0003](0003-distribution-autoportante.md) | Distribution autoportante, Windows et Linux toutes distributions, sans Docker | acceptée | 15/10/2026 |
| [0004](0004-erp-entree-par-la-production.md) | Architecture d'ERP, entrée sur le marché par la production | acceptée | 15/10/2026 |
| [0005](0005-reutiliser-le-moteur-def.md) | Réutiliser le moteur DEF existant comme bibliothèque | acceptée | 15/10/2026 |
| [0006](0006-packs-pays-declaratifs.md) | Packs pays déclaratifs, en couches, signés et datés | acceptée | 15/10/2026 |
| [0007](0007-kaem-ia-locale.md) | Kaem : IA locale sur processeur, Gemma 4 E4B téléchargé | acceptée sous réserve du banc | 15/10/2026 |
| [0008](0008-ia-ne-calcule-ni-ne-valide.md) | L'IA ne calcule ni ne valide | acceptée | 15/10/2026 |
| [0009](0009-pile-serveur.md) | Pile serveur : FastAPI, PostgreSQL, Valkey, Caddy | acceptée | 15/10/2026 |
| [0010](0010-identite-selon-edition.md) | Identité intégrée en édition installée, Keycloak en SaaS | acceptée | 15/10/2026 |
| [0011](0011-licence-proprietaire.md) | Licence propriétaire, entiercement pour les grands comptes | acceptée | 15/10/2026 |
| [0012](0012-documentation-as-code.md) | Documentation as code : Markdown, Mermaid, site hors ligne | acceptée | 15/10/2026 |
| [0013](0013-developpement-avec-claude-code.md) | Développement avec Claude Code, livraison en un mois | acceptée | 15/10/2026 |
| [0014](0014-documentation-par-le-plugin-doc-projet.md) | La documentation est produite et tenue par le plugin doc-projet | acceptée | 16/10/2026 |

## Gabarit d'une fiche

```markdown
# NNNN — Titre à l'infinitif ou au nominatif

Statut : proposée | acceptée | remplacée par NNNN · Date : JJ/MM/AAAA · Décideur : …

## Contexte        — le problème, les contraintes, ce qui force à décider maintenant
## Options         — au moins deux, avec ce qui les distingue
## Décision        — une phrase, puis les précisions
## Conséquences    — ce qui devient facile, ce qui devient difficile, ce qu'il faut surveiller
## Liens           — exigences (EX-…), risques (R…), autres ADR
```
