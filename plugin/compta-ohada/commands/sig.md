---
description: Soldes Intermédiaires de Gestion SYSCOHADA + commentaire (livrable Excel)
argument-hint: [période / agrégats]
---

Tu vas produire les **Soldes Intermédiaires de Gestion (SYSCOHADA révisé)** et, si demandé, le commentaire de gestion, avec le skill `etats-financiers-ohada`.

Contexte (facultatif) : $ARGUMENTS

Déroulé :
1. **Intake guidé** : quel livrable (SIG / commentaire / TFT / cohérence) ? période et comparatif ? compte de résultat par nature (anonymisé) ? seuil de significativité ?
2. **Calcul** : cascade marge → valeur ajoutée → EBE → résultat d'exploitation → RAO → HAO → résultat net (valeur + % du CA).
3. **Livrable** : pré-remplis `skills/etats-financiers-ohada/templates/sig-syscohada.xlsx` (entrées → cascade par formules + contrôle) et remets le fichier.
4. Sépare faits et hypothèses ; signale les postes manquants.
