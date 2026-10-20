---
description: Décompte d'une situation de travaux BTP (TVA, retenue de garantie, acompte) — livrable Excel
argument-hint: [montant HT, taux, acompte]
---

Tu vas établir le **décompte d'une situation de travaux** avec le skill `comptabilite-chantier-btp`.

Contexte (facultatif) : $ARGUMENTS

Déroulé :
1. **Intake guidé** : montant HT ? **taux de TVA** (à citer depuis la loi) ? taux de retenue de garantie (contrat) ? acompte à déduire ? révision de prix ?
2. **Calcul** : net à payer = HT révisé + TVA − retenue de garantie − acompte (contrôle possible via `scripts/situation_travaux.py`).
3. **Livrable** : pré-remplis `skills/comptabilite-chantier-btp/templates/situation-travaux.xlsx`.
4. Écriture (705, 443 TVA, RG en sous-compte de 411) ; TVA à valider.
