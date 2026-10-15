# Sources — couche OHADA 2017.1

| Donnée | Source | Nature | Consulté le |
|---|---|---|---|
| Plan de comptes, états financiers, notes annexes | Acte uniforme relatif au droit comptable et à l'information financière (AUDCIF), adopté le 26/01/2017, et SYSCOHADA révisé | officielle | 15/10/2026 |
| Codes de postes (REF) et règles « compte → poste » | Moteur Facil `mapping-comptes-dsf.json` v2, contrôlé sur une liasse déposée d'un dossier pilote (anonymisé) : 99/99 postes rapprochés | interne, éprouvée | 28/09/2026 |
| Formulaire du système normal (gabarit) | Formulaire DSF système normal de la DGI du Cameroun (version vierge) ; ses feuilles fiscales camerounaises sont propres au pack CM | officielle | 01/10/2026 |
| Correspondance « ligne du formulaire SN → postes » | Rapprochement de libellés (seuil 0,72), et correspondance écrite à la main qui prime | interne | 01/10/2026 |

**Lignes non écrites, volontairement** (compte incertain) : voir `non_ecrites` dans `correspondances/sn.json`. Le contrôle « note = poste » les signale si elles sont chiffrées.
