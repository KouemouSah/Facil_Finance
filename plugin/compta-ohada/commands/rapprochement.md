---
description: État de rapprochement bancaire SYSCOHADA (livrable Excel avec contrôle)
argument-hint: [soldes et éléments en rapprochement]
---

Tu vas établir un **état de rapprochement bancaire** avec le skill `tresorerie-rapprochement-bancaire`.

Contexte (facultatif) : $ARGUMENTS

Déroulé :
1. **Intake guidé** : relevé bancaire et grand livre banque (anonymisés) ? solde comptable ? solde relevé ? éléments connus (chèques non débités, virements en cours, frais/agios) ?
2. **Méthode** : du solde relevé aux éléments en circulation → retrouver le solde comptable après régularisation.
3. **Livrable** : pré-remplis `skills/tresorerie-rapprochement-bancaire/templates/rapprochement-bancaire.xlsx` (contrôle `=OK/ÉCART`).
4. Comptabiliser les éléments manquants (631 frais bancaires) ; signaler les écarts anciens.
