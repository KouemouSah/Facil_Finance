---
icon: lucide/file-check
---

# 0005 — Réutiliser le moteur DEF existant comme bibliothèque

Statut : acceptée · Date : 15/10/2026 · Décideur : architecte (arbitrage A3)

## Contexte
Le plugin `compta-ohada` (v0.10.0) produit déjà la liasse SYSCOHADA (système normal) et la liasse de Guinée équatoriale à partir d'une balance ou d'un grand livre. Il est validé par des tests de référence sur un dossier réel :
- liasse GE : 3 952 cellules identiques à la liasse déposée, 0 écart inexpliqué ;
- liasse SN : 61 contrôles, 0 écart ;
- rendu sans Excel : 691 formules sur 691 identiques à Excel.

## Options
1. Réécrire le moteur dans la nouvelle application.
2. **Extraire le moteur en bibliothèque Python** (`facil_moteur`), utilisée à la fois par le plugin et par l'application.

## Décision
Option 2. Ce qui dépend d'un pays sort du code et part dans le pack ([ADR 0006](0006-packs-pays-declaratifs.md)). Le moteur garde la lecture des balances, l'agrégation, le rendu et l'exécution des contrôles.

## Conséquences
- Un seul moteur à prouver. Les tests et contre-épreuves existants le suivent.
- **Le travail d'extraction est réel** : les règles de la Guinée équatoriale, aujourd'hui dans le code (`fiscal_ge.py`, `tf345_ge.py`, le gabarit), doivent devenir un pack. Le pack Cameroun sert de **premier client du format** ; la Guinée équatoriale est convertie ensuite. Test de réussite : la liasse GE reste identique au franc près.

## Liens
EX-PROD-1 à EX-PROD-6 · R10 · [Format du pack pays](../specs/pack-pays.md)
