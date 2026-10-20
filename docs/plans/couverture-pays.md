---
icon: lucide/globe
---

# Couverture des pays — les 17 États du SYSCOHADA

<span class="statut statut--brouillon">brouillon</span> · Version 0.1 · 15/10/2026 · Corpus : `datas/liasses-officielles/SOURCES.md`

## 1. État des modèles (constaté le 15/10/2026) et disponibilité prévue

| Rang | Pays | Zone | Monnaie | Langue de liasse | Modèle SN officiel | Modèle SMT officiel | Exemple réel | Pack | Disponibilité (roadmap) |
|---|---|---|---|---|---|---|---|---|---|
| 0 | Guinée équatoriale | CEMAC | XAF | ES (+ FR) | oui (dossier pilote) | à obtenir | oui (dossier pilote) | **converti au format pack** (sprint 1) : paramètres et calcul fiscal identiques au plugin | {{cal:pays:GQ}} |
| 1 | Cameroun | CEMAC | XAF | FR (+ EN) | **oui, Excel (DGI)** | PDF seulement | **oui (DSF 2025 publiée)** | **préversion** (sprint 1) : SN conforme au formulaire officiel, 23 paramètres sourcés, IS de la SIC reproduit au franc près ; SMT proposé | {{cal:pays:CM}} |
| 2 | Sénégal | UEMOA | XOF | FR | **oui, Excel (SEN ETAFI)** | oui, 2 variantes à départager | oui (2023) | à faire | {{cal:pays:SN}} |
| 3 | Togo | UEMOA | XOF | FR | oui, Excel (OTR, 2023) | oui, Excel (2019) | à chercher | à faire | {{cal:pays:TG}} |
| 4 | Gabon | CEMAC | XAF | FR | PDF (site privé) | à obtenir | à chercher | à faire | {{cal:pays:GA}} |
| 5 | Côte d'Ivoire | UEMOA | XOF | FR | **introuvable**, à demander à l'expert local ou à la DGI | ancien SYSCOA seulement | oui (SODECI 2019) | bloqué | {{cal:pays:CI}} |
| 6 | Congo | CEMAC | XAF | FR | site injoignable | — | — | bloqué | {{cal:pays:CG}} |
| 7 | Bénin | UEMOA | XOF | FR | sites injoignables (constaté le 15/10), à retenter | — | — | à faire | {{cal:pays:BJ}} |
| 8 | Burkina Faso | UEMOA | XOF | FR | bordereaux d'impôt seulement | — | — | à faire | {{cal:pays:BF}} |
| 9 | Mali | UEMOA | XOF | FR | manuel E-Liasse seulement | — | — | à faire | {{cal:pays:ML}} |
| 10 | Niger | UEMOA | XOF | FR | non trouvé | — | — | à faire | {{cal:pays:NE}} |
| 11 | Guinée-Bissau | UEMOA | XOF | **PT** | non cherché | — | — | à faire | {{cal:pays:GW}} |
| 12 | Tchad | CEMAC | XAF | FR | non trouvé | — | — | à faire | {{cal:pays:TD}} |
| 13 | Centrafrique | CEMAC | XAF | FR | non cherché | — | — | à faire | {{cal:pays:CF}} |
| 14 | Guinée | hors zone | GNF | FR | non trouvé | — | oui (ONG 2022) | à faire | {{cal:pays:GN}} |
| 15 | RD Congo | hors zone | CDF (et USD) | FR | non trouvé | — | — | à faire | {{cal:pays:CD}} |
| 16 | Comores | hors zone | KMF | FR | non cherché | — | — | à faire | {{cal:pays:KM}} |

La colonne *Disponibilité* est **générée** depuis `plans/calendrier.yml`, la même source que la [roadmap](roadmap.md) : les deux ne peuvent pas diverger.

**Règle d'ordre** : un pays avance quand son modèle officiel **et** son expert local sont disponibles, pas selon le rang prévu. La taille du marché ne départage que les pays prêts.

## 2. Ce qu'un pays doit fournir avant son pack

- [ ] le modèle officiel SN, et le SMT, de l'exercice en cours ;
- [ ] la notice de remplissage ;
- [ ] la loi de finances de l'exercice (taux, seuils, minimum de perception) ;
- [ ] au moins 10 liasses réelles déposées, avec leurs balances (anonymisées) ;
- [ ] un expert-comptable local qui signe la validation ;
- [ ] la plateforme de télédéclaration, si elle existe (pour la V1.2).

## 3. Prochaine action

**Pack Cameroun, suite** (voir les tâches reportées du [plan de sprints](sprints.md)) : gabarit Excel du SMT, cas où le minimum de perception l'emporte, puis **signature d'un expert-comptable inscrit à l'ONECCA** avant toute vente (R14). Pack Sénégal : sprint 2, fin {{cal:fin:s2}}.
