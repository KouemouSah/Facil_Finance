---
description: Génère un plan d'amortissement SYSCOHADA (livrable Excel) via un intake guidé
argument-hint: [bien à amortir, ex. "engin 12M 5 ans"]
---

Tu vas produire un **plan d'amortissement SYSCOHADA révisé** et le **livrable Excel** correspondant, en appliquant le skill `immobilisations-ohada`.

Contexte utilisateur (facultatif) : $ARGUMENTS

Déroulé impératif :
1. **Intake guidé** — si une information manque, POSE les questions avant tout calcul : valeur d'origine, date de mise en service, durée d'utilité (politique de l'entreprise), méthode (linéaire/dégressif), coefficient si dégressif, valeur résiduelle éventuelle, prorata (jours base 360 / mois).
2. **Calcul** — établis le plan année par année (base, dotation, cumul, VNC) avec prorata la 1re année. Pour un contrôle déterministe, tu peux exécuter `skills/immobilisations-ohada/scripts/amortissement.py`.
3. **Livrable Excel** — pré-remplis le template `skills/immobilisations-ohada/templates/tableau-amortissement.xlsx` (paramètres + plan avec formules) et remets le fichier.
4. **Écriture & citation** — propose l'écriture (681 / 28x, n° à confirmer via `references/plan-comptes-immo.md`) et rappelle la validation humaine.

Ne devine aucune durée ni aucun taux : ils viennent de la politique de l'entreprise (ou, pour le fiscal, de la loi citée).
