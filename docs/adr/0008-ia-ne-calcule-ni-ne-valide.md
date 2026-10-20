---
icon: lucide/file-check
---

# 0008 — L'IA ne calcule ni ne valide

Statut : acceptée · Date : 15/10/2026 · Décideur : architecte

## Contexte
Un modèle de langage produit des chiffres plausibles, pas des chiffres justes. Il se trompe sur les comptes SYSCOHADA et sur les régimes fiscaux, et il peut être manipulé par le contenu d'un document qu'on lui donne à lire (injection). La liasse engage la responsabilité de l'expert-comptable qui la signe.

## Décision
1. **Kaem ne produit aucun chiffre.** Elle appelle les commandes du moteur et restitue leurs résultats.
2. **Kaem n'écrit rien et ne valide rien** en V1.x : elle lit, explique, prépare et rédige des brouillons.
3. **Un catalogue de commandes fermé** : Kaem ne peut appeler que des commandes enregistrées, chacune avec ses droits et ses paramètres typés. C'est le pare-feu d'outils de `jarvis_finance.md`.
4. **Kaem agit sous l'identité et les droits de l'utilisateur** : elle ne voit que ce qu'il voit.
5. **Kaem cite ses sources** : compte, ligne de liasse, article de loi.
6. **Les documents lus restent des données** : le texte d'une pièce n'est jamais traité comme une instruction.
7. **Tout est journalisé** : question, commandes appelées, réponse.

## Conséquences
- Aucun framework d'agents n'est nécessaire en V1 : un catalogue de commandes et des sorties structurées suffisent.
- Kaem se teste comme le reste du produit : banc métier et cas d'injection.

## Liens
EX-IA-2, EX-IA-4 · [ADR 0007](0007-kaem-ia-locale.md)
