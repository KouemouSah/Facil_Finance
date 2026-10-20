---
icon: lucide/file-check
---

# 0006 — Packs pays déclaratifs, en couches, signés et datés

Statut : acceptée · Date : 15/10/2026 · Décideur : architecte (arbitrage A5)

## Contexte
17 États, deux systèmes (SN, SMT), quatre langues de liasse, des lois de finances annuelles. Coder chaque pays reviendrait à maintenir 17 variantes du moteur. Le formulaire SN est pourtant **commun à l'OHADA** pour les états, et seules les annexes fiscales divergent.

## Options
1. Un module de code par pays.
2. **Des données déclaratives par couches** : OHADA commun ← zone (CEMAC, UEMOA) ← pays ← exercice.

## Décision
Option 2, selon le [format du pack pays](../specs/pack-pays.md). Un pack est :
- **daté** : il porte une période de validité, et le moteur choisit le pack en vigueur à la date de clôture ;
- **signé** : il est refusé si sa signature ne correspond pas ;
- **validé** : un expert local l'approuve, et il reproduit des liasses réelles.

## Conséquences
- Ajouter un pays, c'est écrire des données et des cas de test, sans toucher au moteur.
- **Une liasse ancienne reste reproductible** avec le pack de son exercice, même après la publication d'un pack plus récent.
- Il faut un **outil d'édition et de validation des packs** pour l'équipe interne. Il est prévu à la V1.0.

## Liens
EX-PROD-2, EX-PROD-5, EX-PROD-8 · R1, R8 · [Couverture des pays](../plans/couverture-pays.md)
