---
icon: lucide/file-check
---

# 0001 — Consigner les décisions sous forme d'ADR

Statut : acceptée · Date : 15/10/2026 · Décideur : porteur et architecte

## Contexte
Les choix du projet étaient dispersés dans `projet.md`, dans plusieurs analyses et dans des conversations. Plusieurs se contredisaient : Docker ou paquet natif ; la V2 en SaaS ou en assistant vocal ; une licence LGPL ou propriétaire. Sans registre, quiconque reprend le projet ne sait plus ce qui a été tranché.

## Options
1. Continuer à amender `projet.md` en place.
2. **Une fiche par décision, numérotée et immuable**, avec un index.

## Décision
Option 2. `projet.md` reste le document d'entrée ; ses arbitrages (§ 0) renvoient vers les fiches.

## Conséquences
- Une décision se retrouve en une lecture, avec les options qu'elle a écartées.
- Coût : environ 30 minutes par décision. C'est le prix d'éviter de rouvrir un débat déjà tranché.

## Liens
[Plan de documentation](../plans/plan-documentation.md) · [ADR 0012](0012-documentation-as-code.md)
