---
icon: lucide/file-check
---

# 0014 — La documentation est produite et tenue par le plugin doc-projet

Statut : acceptée · Date : 16/10/2026 · Décideur : porteur et architecte

## Contexte
Le porteur veut automatiser, pour tout nouveau projet, la démarche suivie ici : brainstorm, recherche, analyse critique, décisions, puis documents et site, tenus à jour pendant l'implémentation, le tout lancé par une commande. Cette documentation-ci a été construite à la main, avant que l'outil existe.

## Options
1. Recopier `projet_doc` à la main pour chaque nouveau projet.
2. **Un plugin Claude Code (`doc-projet`)**, dont cette documentation devient la première instance.

## Décision
Option 2. Le plugin est dans `C:\DSF\plugins\doc-projet` (place de marché `facil-outils`). `projet_doc` a été migrée sur lui le 16/10/2026 :
- même squelette, gardes et charte ;
- paramètres dans `doc-projet.yml` ;
- phase 6, suivi.

Le site migré se construit à l'identique : 30 pages et 18 contre-épreuves vertes.

## Conséquences
- Une amélioration du design ou d'une garde se fait **dans le plugin**, puis se propage aux projets par `initialiser.py --forcer`. Elle ne se fait plus page par page.
- Les dates, indicateurs et blocs générés suivent leurs sources ; le contenu rédigé reste proposé au porteur, jamais réécrit en silence.
- Le hook du plugin note chaque fichier de code modifié pendant l'implémentation ; `/doc-projet-maj` le reflète dans ces documents.

## Liens
[ADR 0012](0012-documentation-as-code.md) · [ADR 0013](0013-developpement-avec-claude-code.md)
