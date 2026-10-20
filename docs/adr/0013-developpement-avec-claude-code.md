---
icon: lucide/file-check
---

# 0013 — Développement avec Claude Code, livraison en un mois

Statut : acceptée · Date : 15/10/2026 · Décideur : porteur (décision D8)

## Contexte
Le porteur fixe l'implémentation à **un mois**, livraison en **novembre 2026**, avec un codage réalisé par **Claude Code**. Le moteur existant (plugin `compta-ohada`) a déjà été construit ainsi, avec des gardes et des contre-épreuves. La méthode est donc éprouvée sur ce projet.

## Options
1. Une équipe classique de 3 développeurs, sur 18 à 20 mois.
2. **Claude Code écrit le code ; un développeur responsable relit, tranche et fusionne ; les gardes prouvent.**

## Décision
Option 2. Les règles suivantes ne sont pas négociables :
- **Rien n'est fusionné sans relecture humaine.** Le relecteur vérifie la sécurité, le SQL, la portée du changement et les licences des dépendances.
- **Toute garde a sa contre-épreuve** ; la « définition de terminé » du [plan de sprints](../plans/sprints.md) s'applique à chaque fusion.
- **Le dépôt porte ses règles** (`CLAUDE.md`, ADR) : Claude Code les lit à chaque session. Une décision prise une fois n'est pas reprise à chaque session.
- **Aucune donnée de client** dans les sessions de Claude Code : les cas de test sont anonymisés. Les originaux restent hors du dépôt, protégés par la passerelle de confidentialité et la garde de lecture.
- **La reprise est écrite** : chaque plan en cours a une section *Reprise*, mise à jour à chaque tâche close.

## Conséquences
- Le codage n'est plus le chemin critique. **La relecture, les validations d'experts, les audits et le juridique le deviennent** ([plan de versions](../plans/feuille-de-route.md)).
- Les estimations de `projet.md` (45 à 65 mois-homme) ne s'appliquent plus au codage. Elles restent pertinentes pour l'effort de validation des packs pays, qui ne se compresse pas.
- **Propriété du code produit** : à confirmer par le juriste au regard des conditions commerciales d'Anthropic en vigueur, avant l'entiercement et la première vente ([ADR 0011](0011-licence-proprietaire.md)).
- Risque de **volume** : plus de code que la relecture ne peut absorber (R12). On le surveille chaque jour ; le délai de relecture n'est jamais raccourci.

## Liens
[Plan de sprints](../plans/sprints.md) · [Roadmap](../plans/roadmap.md) · R12, R13
