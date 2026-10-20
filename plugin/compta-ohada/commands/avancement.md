---
description: Avancement d'un chantier BTP (CA à reconnaître, marge, perte à terminaison) — livrable Excel
argument-hint: [coûts engagés, coût total, marché]
---

Tu vas calculer l'**avancement d'un chantier** (méthode à l'avancement) avec le skill `comptabilite-chantier-btp`.

Contexte (facultatif) : $ARGUMENTS

Déroulé :
1. **Intake guidé** : coûts engagés à date ? coût total estimé ? prix du marché ? (ou % d'avancement physique) ? méthode retenue par l'entreprise ?
2. **Calcul** : avancement = coûts engagés / coût total ; CA reconnu = prix × avancement ; provision perte à terminaison si déficitaire (contrôle via `scripts/avancement.py`).
3. **Livrable** : pré-remplis `skills/comptabilite-chantier-btp/templates/avancement-chantier.xlsx`.
4. Signale le risque de double comptage (CA à l'avancement vs en-cours).
