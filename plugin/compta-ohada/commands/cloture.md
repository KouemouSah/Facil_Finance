---
description: Écritures de régularisation de clôture SYSCOHADA (livrable Excel équilibré)
argument-hint: [opération à régulariser]
---

Tu vas produire une (ou des) **écriture(s) de régularisation de clôture** avec le skill `cloture-comptable-ohada`.

Contexte (facultatif) : $ARGUMENTS

Déroulé :
1. **Intake guidé** : type d'opération (charge à payer / produit à recevoir / CCA-PCA / abonnement / provision) ? montant HT/TVA, période, pièce ? règle si provision ?
2. **Écriture** : rattachement à l'exercice + contrepassation à l'ouverture si besoin ; comptes via `../datas/plan-comptable-syscohada-standard.md`.
3. **Livrable** : pré-remplis `skills/cloture-comptable-ohada/templates/ecritures-regularisation.xlsx` (journal équilibré, contrôle `=OK/ÉCART`).
4. Section « Points à valider par le chef comptable ».
