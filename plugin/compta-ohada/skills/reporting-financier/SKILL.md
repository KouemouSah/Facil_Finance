---
name: reporting-financier
description: >
  Génère des rapports financiers pour la direction d'une entreprise BTP en OHADA : reporting de gestion mensuel, rapport d'analyse financière, reporting chantiers, board deck, et rapport financier complet pour comité de direction aux standards cabinets/internationaux. Workflow MARKDOWN D'ABORD (rédiger et faire réviser en .md, puis convertir en PDF/DOCX/PPTX/XLSX). Les chiffres proviennent des moteurs déterministes (jamais inventés) ; Claude rédige le commentaire à partir de ces chiffres. À utiliser dès qu'on veut produire, structurer ou mettre en forme un rapport, un reporting ou une présentation financière.
---

# Reporting financier & rapports de direction — BTP / OHADA

Tu produis des rapports professionnels pour la direction. Contexte BTP, SYSCOHADA révisé, Guinée Équatoriale, devise XAF.

## 0. Règles (impératives)
- **Ancrage des chiffres** : tout nombre vient d'un **moteur déterministe** ou d'une donnée fournie — **jamais estimé par toi**. Tu rédiges le commentaire *à partir* de ces chiffres, tu ne les crées pas.
- **Narration & analyse obligatoires (pas de tableau nu)** : chaque section suit la trame **Faits → Causes/drivers → Implications (so what) → Action**. Un tableau est **toujours** accompagné d'une analyse en prose : que révèle le chiffre, *pourquoi* il varie (moteurs), quelle *conséquence*, quelle *décision*. Un rapport qui n'est qu'une suite de tableaux est **rejeté**.
- **Profondeur attendue** (pour une revue approfondie) : drivers de CA, structure de coûts, **cash‑flow** (du résultat à la trésorerie), **décomposition du BFR** (DSO/DPO), **comptes par chantier** (marge à terminaison), **scénarios/sensibilités**, **benchmarks** sectoriels (à valider), cartographie des risques, recommandations **chiffrées** (impact, responsable, échéance).
- **Visuels systématiques** : intégrer **graphiques, infographies et icônes vectorielles** adaptés au type de rapport (voir §6 Visuels).
- Données **anonymisées** hors identité nécessaire. **Validation** du chef comptable / de la direction avant diffusion.
- Distingue **faits** (chiffrés) et **hypothèses/recommandations**.

## 0bis. Deux familles de livrables — NE PAS CONFONDRE
| Famille | Container | Volume | Outil |
|---|---|---|---|
| **Rapport (document A4 portrait)** | Markdown → **DOCX/PDF** | **jusqu'à 40+ pages A4**, page de garde + sommaire + sections + annexes | compétences documentaires `docx`/`pdf` de Claude |
| **Deck (présentation 16:9)** | HTML `presentation-decks` | **5-15 slides**, **page de couverture + page de fin** obligatoires | skill `presentation-decks` (composants finance ajoutés) |

**Longueur selon le type (ne pas sur‑gonfler) :**
- **Reporting de gestion mensuel** → **concis, 8–15 pages**, orienté décision (un comité ne lit pas 40 pages/mois).
- **Revue financière approfondie / rapport annuel** → **20–40+ pages**, narration complète (voir Annexe E d'exemple).
- **Règle d'or** : la longueur suit la **profondeur d'analyse réelle**, jamais le remplissage. Verbeux‑mais‑creux est aussi grave que tableaux‑nus.

> ⚠️ **On ne monte PAS un rapport de 40 pages dans le système de deck** (slides 1920×1080 paysage) ni un deck dans un document A4. Chaque besoin son container. Le workflow Markdown-d'abord vaut pour les deux ; la mise en forme finale diffère.

## 1. Workflow — MARKDOWN D'ABORD (règle de l'utilisateur)
1. **Rédiger le rapport en Markdown** (`.md`) à partir d'un gabarit (`templates/`) — c'est la version révisable.
2. **Faire réviser** le contenu en Markdown (chiffres, commentaire, structure).
3. **UNE FOIS VALIDÉ**, mettre en forme selon la famille :
   - **Rapport A4** (jusqu'à 40+ pages) → skill `docx` ou `pdf` de Claude (portrait, paginé, sommaire).
   - **Deck** → skill **`presentation-decks`** (HTML riche, composants finance, couverture + clôture ; impression PDF intégrée). Un `.pptx` éditable n'est utile que si explicitement demandé (skill `pptx`).
   - **Classeur** → skill `xlsx`.
   - **Ne code aucun convertisseur** : la mise en forme est native.

## 2. Types de rapports (gabarits fournis)
| Rapport | Gabarit | Format cible habituel |
|---|---|---|
| Reporting de gestion mensuel | `templates/reporting-gestion-mensuel.md` | PDF / DOCX |
| Rapport d'analyse financière | `templates/rapport-analyse-financiere.md` | PDF / DOCX |
| Reporting chantiers BTP | `templates/reporting-chantiers-btp.md` | PDF / XLSX |
| Board deck direction | `templates/board-deck-direction.md` | PPTX |
| **Rapport financier complet — comité de direction** (standards cabinets/internationaux) | `templates/rapport-financier-comite-direction.md` | PDF / DOCX / PPTX |

## 3. Ancrage des chiffres — quel moteur alimente quoi
- **Bilan / Compte de résultat** : `dsf-syscohada/scripts/agreger_balance_dsf.py` (depuis la balance).
- **SIG (marge, VA, EBE, RAO, HAO, résultat net)** : template `etats-financiers-ohada` / calcul depuis le CR.
- **Ratios & BFR** : `analyse-financiere-btp/scripts/ratios.py`.
- **Variations & alertes N/N-1 par cycle** : `revision-comptes-ohada/scripts/dossier_revision.py`.
- **Chantiers (avancement, marge, perte à terminaison)** : `comptabilite-chantier-btp/scripts/avancement.py`.
- **Immobilisations** : `immobilisations-ohada/scripts/registre_immobilisations.py`.
- **Tableaux Excel réels** : `python scripts/xlsx_to_table.py --fichier <x.xlsx> --plage A3:E12 [--html]` → tableau **Markdown** (rapport) ou **`table.fin`** (deck), **valeurs exactes** (jamais re-saisies).
- **Graphiques** : décrire le graphe voulu (données + type) ; rendu à la mise en forme.

## 6. Visuels — quel visuel pour quoi
| Donnée à montrer | Deck (`presentation-decks`) | Rapport A4 (docx/pdf) |
|---|---|---|
| Bilan / CR / SIG chiffré, totaux, variance | `table.fin` | tableau Markdown (via xlsx_to_table) |
| Indicateurs clés + évolution ▲/▼ | `.kpi-fin` | encadré KPI |
| Tendance (CA/EBE/trésorerie sur N mois) | `.linechart` | graphe linéaire (à générer) |
| Cascade SIG / pont de variance | `.waterfall` | graphe cascade |
| Structure de coûts / ventilation | `.stackbar` / `.gauge` | graphe / camembert |
| Icônes (finance) | `i-trend-up/-down i-percent i-wallet i-bank i-receipt i-pie i-cash i-coins i-scale` | idem si support HTML |

Toujours **une interprétation sous chaque visuel**. Pour les decks : respecter la discipline `presentation-decks` (80 % de contenu matériel, pas de carte étirée, couverture + **page de fin**).

## 4. Adaptatif (modèle & marque de l'entreprise)
- **Structure** : si l'entreprise a un **gabarit de rapport** (plan-type), l'utiliser **en priorité** et adapter le Markdown à sa structure. À défaut, gabarits `templates/` comme baseline.
- **Marque (branding)** : adapter titres, auteur/**département**, contact, logo et **couleurs à la charte graphique** de l'entreprise — dériver la palette de la **charte** si elle existe, sinon **du logo** (analyser l'image, faire confirmer). Réutiliser `references/profil-branding.example.json` (logo, palette, `auteur_ou_departement`, `contact`, convention de titre). Pour un deck : reporter la palette dans le `<style>` de thème (`presentation-decks/assets/theme.example.css`).
- **Titre** : adapter au livrable (ex. « Reporting de gestion — Mars 2026 »), jamais un « titre projet » figé. **Contact** = e-mail **ou** département **ou** rien. Ne jamais imposer ; s'adapter.

## 5. Bornes
- Montage de la liasse DSF → `dsf-syscohada`. Ici : rapports de **pilotage/communication**, pas la liasse fiscale.
- Rédaction d'un courrier/mémo isolé → `redaction-comptable-pro`.

## 6. Discipline anti-hallucination (rappel)
Si un chiffre nécessaire n'est pas disponible via un moteur ou une donnée fournie : **laisser un placeholder `[à fournir]`** et le signaler — ne jamais combler par une estimation.
