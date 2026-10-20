<!--
GABARIT — Rapport financier complet pour comité de direction (standards cabinets / internationaux).
Workflow : rédiger/compléter ce .md → faire réviser → convertir (PDF/DOCX/PPTX) via les compétences documentaires de Claude.
Règle : «placeholders» = chiffres à FOURNIR par un moteur déterministe ou une donnée réelle. Ne jamais inventer.
Les notes _(source: ...)_ indiquent quel moteur alimente la section.
-->

# Rapport financier — «Raison sociale»
### Comité de direction — Exercice/Période «période» · Devise : XAF

**Établi le** «date» · **Référentiel** : SYSCOHADA révisé (OHADA) · **Secteur** : BTP · **Statut** : projet à valider

---

## 1. Résumé exécutif
_(3-5 messages clés, factuels, chacun adossé à un chiffre)_
- «Message 1 — ex. Chiffre d'affaires «CA» XAF, «±x %» vs N-1»
- «Message 2 — rentabilité : EBE «EBE» XAF, marge «x %» du CA»
- «Message 3 — trésorerie / BFR»
- «Message 4 — chantiers»
- **Appréciation d'ensemble** : «synthèse en 2 lignes»

## 2. Faits marquants de la période
- «Événements significatifs, variations notables (>seuil), décisions»
_(source: dossier_revision.py pour les variations N/N-1 > seuil)_

## 3. Performance — Compte de résultat & Soldes Intermédiaires de Gestion
| Solde (SIG SYSCOHADA) | «N» | «N-1» | % CA | Var. |
|---|---|---|---|---|
| Chiffre d'affaires | «...» | «...» | 100% | «...» |
| Marge commerciale | «...» | «...» | «...» | «...» |
| Valeur ajoutée | «...» | «...» | «...» | «...» |
| Excédent brut d'exploitation (EBE) | «...» | «...» | «...» | «...» |
| Résultat d'exploitation | «...» | «...» | «...» | «...» |
| Résultat des activités ordinaires (RAO) | «...» | «...» | «...» | «...» |
| Résultat HAO | «...» | «...» | «...» | «...» |
| **Résultat net** | «...» | «...» | «...» | «...» |

_(source: agreger_balance_dsf.py → CR ; SIG calculés)_
**Analyse** : «commentaire des écarts significatifs, moteurs de la performance»

## 4. Structure financière — Bilan
| Grandes masses | «N» | «N-1» |
|---|---|---|
| Actif immobilisé net | «...» | «...» |
| Actif circulant | «...» | «...» |
| Trésorerie-actif | «...» | «...» |
| **Total actif** | «...» | «...» |
| Capitaux propres | «...» | «...» |
| Dettes financières | «...» | «...» |
| Passif circulant | «...» | «...» |

**Analyse** : «solidité des capitaux propres, endettement, équilibre financier (FR/BFR/TN)»
_(source: agreger_balance_dsf.py → Bilan)_

## 5. Trésorerie & Besoin en Fonds de Roulement
- **Fonds de roulement** : «FR» · **BFR** : «BFR» · **Trésorerie nette** : «TN»
- **BFR en jours de CA** : «x j» · leviers BTP : retenues de garantie, décomptes, acomptes.
- Position et tension éventuelle : «commentaire»
_(source: ratios.py — BFR, délais clients/fournisseurs)_

## 6. Indicateurs clés (KPI / ratios)
| Ratio | «N» | «N-1» | Lecture |
|---|---|---|---|
| Liquidité générale | «...» | «...» | «...» |
| Autonomie financière | «...» | «...» | «...» |
| Endettement | «...» | «...» | «...» |
| Rentabilité financière | «...» | «...» | «...» |
| Délai clients (j) | «...» | «...» | «...» |
| Délai fournisseurs (j) | «...» | «...» | «...» |
_(source: ratios.py — repères sectoriels BTP à valider)_
**Graphique suggéré** : évolution EBE et marge sur 12 mois _(à générer à la conversion)_.

## 7. Activité BTP — chantiers
| Chantier | Avancement | CA reconnu | Marge à date | Dérive | Alerte |
|---|---|---|---|---|---|
| «codé» | «x %» | «...» | «...» | «...» | «...» |
| **Total / top risques** | | | | | |
_(source: avancement.py par chantier ; reporting chantier)_

## 8. Risques & points d'attention
- «Risques financiers, chantiers déficitaires (perte à terminaison), concentration clients, trésorerie»
_(source: avancement.py — provisions perte à terminaison ; dossier_revision — anomalies)_

## 9. Perspectives
- «Carnet de commandes, tendances, hypothèses — présentées comme telles»

## 10. Recommandations
1. «Action — responsable — échéance»
2. «...»

---
### Annexes
- A1. Compte de résultat détaillé · A2. Bilan détaillé · A3. Tableau des ratios · A4. Détail chantiers
_(tableaux issus des moteurs / templates Excel)_

> Rapport établi à des fins de pilotage interne. Chiffres à valider ; ne se substitue pas aux états financiers officiels ni à la DSF.
