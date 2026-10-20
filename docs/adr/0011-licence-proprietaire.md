---
icon: lucide/file-check
---

# 0011 — Licence propriétaire, entiercement pour les grands comptes

Statut : acceptée · Date : 15/10/2026 · Décideur : architecte, sur délégation du porteur (arbitrage A8)

## Contexte
`projet.md` (§ 11.5) envisageait une licence LGPL, comme Odoo. La valeur du produit tient dans les **packs pays** (gabarits, correspondances, paramètres fiscaux validés), qui sont des données. Sous licence libre, ils seraient copiables.

## Décision
- Licence **propriétaire** pour l'application et les packs.
- Licence signée, vérifiable **hors ligne**.
- **Entiercement du code** pour les grands comptes, qui garantit la continuité si l'éditeur disparaît.
- Les modules partenaires sont encadrés par contrat.

## Conséquences
- Il faut un contrat de licence, des conditions générales, un accord de traitement des données et une clause de responsabilité, rédigés par un juriste avant la première vente.
- Les dépendances doivent rester compatibles avec une distribution fermée : pas d'AGPL, de SSPL ni de RSAL (R7).

## Liens
[projet.md § 18](../sources/projet.md) · R5, R7
