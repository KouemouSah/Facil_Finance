---
icon: lucide/file-check
---

# 0004 — Architecture d'ERP, entrée sur le marché par la production

Statut : acceptée · Date : 15/10/2026 · Décideur : architecte, sur délégation du porteur (décision D7)

## Contexte
`projet.md` décrivait un ERP comptable complet construit de zéro, soit 12 à 24 mois-homme avant le premier client. Or la valeur déjà prouvée, et la douleur du marché, est la **production** : liasse, contrôles, états. Le client a déjà un logiciel de saisie, et migrer coûte cher.

## Options
1. ERP complet dès la V1.
2. Outil de production seul, sans base comptable (un traitement de fichiers).
3. **Une base d'ERP (vrai grand livre) dès la V1, alimentée par import ; la saisie arrive ensuite.**

## Décision
Option 3. Le modèle de données porte dès la V1.0 des **écritures** : immuables, horodatées, avec leur source (`import`, puis `saisie`). La V1.0 les alimente par import ; la V1.2 ajoute la saisie, qui écrit dans les **mêmes tables**.

## Conséquences
- On vend dès la V1.0, aux cabinets, sans migrer leurs clients.
- La saisie complète ne demande aucune refonte : c'est un nouveau canal d'entrée.
- **Garde-fou contre la dispersion (R2)** : aucune fonction de saisie ou de lettrage n'entre en V1.0. Une demande en ce sens est notée pour la V1.2.

## Liens
EX-IMP-4 · R2 · [Feuille de route](../plans/feuille-de-route.md)
