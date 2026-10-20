---
description: Génère un rapport financier (Markdown d'abord, puis conversion PDF/DOCX/PPTX)
argument-hint: [type de rapport + période]
---

Tu vas produire un **rapport financier** avec le skill `reporting-financier`.

Contexte (facultatif) : $ARGUMENTS

Déroulé impératif :
1. **Choisir le rapport** et son gabarit (`skills/reporting-financier/templates/`) : reporting de gestion mensuel / analyse financière / chantiers / board deck / **rapport complet comité de direction**. Si l'utilisateur a un **modèle maison**, l'utiliser en priorité et s'y adapter.
2. **Réunir les chiffres via les moteurs déterministes** (agreger_balance_dsf, ratios, dossier_revision, avancement, registre) — **ne jamais inventer un chiffre** ; laisser `[à fournir]` si absent.
3. **Rédiger le rapport en Markdown** (version révisable) : chiffres ancrés + commentaire factuel (faits vs hypothèses).
4. **Faire réviser** le Markdown par l'utilisateur.
5. **Une fois validé, convertir** dans le format demandé avec les **compétences documentaires de Claude** : `pdf` / `docx` / `pptx` / `xlsx`. Ne code aucun convertisseur.
6. Rappeler la **validation** direction/chef comptable et que ce rapport ne remplace pas les états officiels/DSF.
