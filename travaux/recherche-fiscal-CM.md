# Paramètres fiscaux Cameroun — DSF exercice clos le 31/12/2025 (régime du réel)

Consulté le 2026-10-16. Sources officielles seulement (DGI impots.cm, Présidence prc.cm, MINFI/DGB).

## Méthode et limites (à lire avant le tableau)

- **Aucune édition « CGI 2025 » n'est encore téléchargeable sur impots.cm** : la page
  `https://www.impots.cm/fr/actualites/code-general-des-impots-2025` et le nœud
  `https://www.impots.cm/fr/node/e7bedcf3-f8a7-4c9d-954a-96d1a8368f8a` renvoient « Page non trouvée » (404).
  Les valeurs sont donc lues dans le **CGI édition 2026 (mis à jour au 1er janvier 2026)** et
  **recoupées avec le CGI édition 2024 (mis à jour au 1er janvier 2024)**. Une valeur identique dans
  les deux éditions est réputée en vigueur pendant tout 2025 (confiance « haute »).
- La **loi de finances 2025** (loi n° 2024/013 du 23/12/2024) et la **loi de finances 2026**
  (loi n° 2025/012 du 17/12/2025) publiées sont des **scans sans couche texte** : elles n'ont pas été
  lues intégralement. Le **projet de LF 2026** (DGB, texte) a servi à repérer les articles du CGI
  que la LF 2026 modifie.
- L'**arrêté n° 00000001/MINFI/DGI du 07/01/2025** (retenues à la source exercice 2025, pris en
  application de la LF 2025) a été lu en image : il confirme les taux TVA/AIR effectifs en 2025.

## Tableau

| clé | valeur | unité | article | texte et année | URL | consulté le | confiance |
| --- | --- | --- | --- | --- | --- | --- | --- |
| is.taux_normal | 30 | % du bénéfice imposable | CGI art. 17 (1) | CGI éd. 2026 ; identique CGI éd. 2024 | [CGI 2026] ; [CGI 2024] | 2026-10-16 | haute |
| is.taux_reduit | 25 | % | CGI art. 17 bis (1)-(2) | idem ; applicable depuis l'exercice clos le 31/12/2022 | [CGI 2026] ; [CGI 2024] | 2026-10-16 | haute |
| is.taux_reduit.seuil_ca | CA ≤ 3 000 000 000 | FCFA | CGI art. 17 bis (1) (« égal ou inférieur à trois (3) milliards ») | idem | [CGI 2026] ; [CGI 2024] | 2026-10-16 | haute |
| cac.taux (IS, IRPP, TVA) | 10 | % du principal | Code fiscalité locale art. C 83 (1) (CGI 2026) ; art. C 54 (CGI 2024) | loi n° 2024/020 du 23/12/2024 (fiscalité locale) intégrée CGI 2026 ; CGI 2024 | [CGI 2026] ; [CGI 2024] | 2026-10-16 | haute |
| is.taux_effectif_normal | 33 (= 30 × 1,10) | % | calcul art. 17 + C 83 | dérivé | — | 2026-10-16 | haute (calcul) |
| is.taux_effectif_reduit | 27,5 (= 25 × 1,10) | % | calcul art. 17 bis + C 83 | dérivé | — | 2026-10-16 | haute (calcul) |
| is.acompte_mensuel.reel | 2 (+10 % CAC = 2,2) | % du CA HT du mois, payé le 15 du mois suivant | CGI art. 21 (1) a | CGI 2026 ; taux 2,2 % AIR « régime du réel » confirmé pour 2025 par l'arrêté du 07/01/2025 art. 2 | [CGI 2026] ; [Arrêté 2025] | 2026-10-16 | haute |
| is.acompte.marge_administree | 14 % de la marge brute (+10 % CAC) ; option droit commun 2,2 % du CA | — | CGI art. 21 (1) b-c | CGI 2026 | [CGI 2026] | 2026-10-16 | haute |
| is.minimum_perception.taux | 2 % (ou 14 % de la marge brute, secteurs à marge administrée) + 10 % CAC = 2,2 % | % de la base de référence | CGI art. 22 (2) | CGI 2026 ; identique CGI 2024 | [CGI 2026] ; [CGI 2024] | 2026-10-16 | haute |
| is.minimum_perception.base | CA global brut HT de l'« exercice précédent », arrondi au millier inférieur (marge brute pour activités à marge administrée) | FCFA | CGI art. 23 | CGI 2026 | [CGI 2026] | 2026-10-16 | haute (texte cité à la lettre) |
| is.minimum_perception.nature | Plancher : « l'impôt dû ne peut être inférieur à… » ; les trop-perçus d'acomptes s'imputent sur les acomptes futurs, remboursés en cas de cessation | — | CGI art. 22 (2), art. 21 (4) | CGI 2026 | [CGI 2026] | 2026-10-16 | moyenne (voir non confirmé) |
| is.minimum_perception.regime_simplifie | 5 % | % | CGI art. 22 (2) dernier al. | CGI 2026 et 2024 ; **supprimé dans le projet LF 2026** (contradiction, voir plus bas) | [CGI 2026] ; [Projet LF 2026] | 2026-10-16 | sans objet au réel |
| deficit.report | 4 exercices suivant l'exercice déficitaire (6 ans : établissements de crédit, entreprises du portefeuille de l'État en restructuration) | exercices | CGI art. 12 (1)-(2) | CGI 2026 ; identique CGI 2024 | [CGI 2026] ; [CGI 2024] | 2026-10-16 | haute |
| tva.taux_general | 17,5 | % | CGI art. 142 (1) a | CGI 2026 ; identique CGI 2024 | [CGI 2026] ; [CGI 2024] | 2026-10-16 | haute |
| tva.taux_effectif | 19,25 (= 17,5 × 1,10) | % | art. 142 (2) (CAC « inclus au taux général ») + C 83 ; 19,25 % écrit dans l'arrêté du 07/01/2025 art. 2 | Arrêté MINFI 2025 | [Arrêté 2025] ; [CGI 2026] | 2026-10-16 | haute |
| tva.taux_zero | 0 | % | CGI art. 142 (1) a, (3) | CGI 2026 et 2024 | [CGI 2026] | 2026-10-16 | haute (liste des opérations non relue) |
| tva.taux_reduit | 10 % — **instauré par la LF 2026, non applicable en 2025** (absent du CGI 2024) | % | CGI art. 142 (1), (4) | LF 2026 ; CGI 2026 | [CGI 2026] ; [MINFI LF 2026] | 2026-10-16 | haute |
| reint.frais_siege_assistance | 2,5 % du bénéfice imposable avant déduction des frais en cause ; en déficit : dernier exercice bénéficiaire non prescrit ; déficit continu / entreprise nouvelle : 1 % du CA (à défaut de CA : total des charges) ; BTP : 1 % du CA ; bureaux d'études agréés : 5 % du CA ; services comptables et fiscaux payés hors CEMAC non déductibles | — | CGI art. 7-A-1-d | CGI 2026 ; 2,5 % et 1 % aussi dans CGI 2024 | [CGI 2026] ; [CGI 2024] | 2026-10-16 | haute |
| reint.redevances_brevets_marques | 2,5 % du bénéfice imposable avant déduction (sociétés liées) ; hors CEMAC + liées : distribution | — | CGI art. 7-A-1-d | CGI 2026 | [CGI 2026] | 2026-10-16 | haute |
| reint.commissions_achats | 1 % du montant des achats | — | CGI art. 7-A-1-d | CGI 2026 | [CGI 2026] | 2026-10-16 | haute |
| reint.locations_associe_25pc | 2,5 % du bénéfice fiscal avant déduction (locations autres qu'immeubles, associé ≥ 25 %) | — | CGI art. 7-A-2 | CGI 2026 ; reconduit par projet LF 2026 | [CGI 2026] | 2026-10-16 | haute |
| reint.dons_liberalites | non déductibles sauf organismes d'intérêt général / R&D situés au Cameroun : 0,5 % du CA de l'exercice ; clubs d'élite / organismes sportifs agréés : 5 % du CA ; déduction totale : ARV VIH/SIDA à l'État ou CTD, R&D agréée agriculture-santé-élevage | % du CA | CGI art. 7-A-5 | CGI 2026 ; 0,5 % aussi CGI 2024 | [CGI 2026] ; [CGI 2024] | 2026-10-16 | haute |
| reint.interets_cca | taux des avances de la Banque Centrale + 2 points ; convention écrite enregistrée ; capital entièrement libéré ; associés ≥ 25 % : avances ≤ 1,5 × capitaux propres et intérêts ≤ 25 % du résultat avant IS, avant ces intérêts et avant amortissements | — | CGI art. 7-B | CGI 2026 ; même rédaction CGI 2024 | [CGI 2026] ; [CGI 2024] | 2026-10-16 | haute (la valeur chiffrée du taux BEAC n'est pas dans le CGI) |
| reint.provisions | déductibles si pertes/charges nettement précisées, rendues probables, constatées en comptabilité ; conditions propres aux créances douteuses ; non déductibles : provisions pour pertes de change, charges prises en compte l'année de leur ordonnancement, provisions pour congés/voyages des associés ; règles d'étalement banques (50 %/an ; 25-50-25 % sur 3 ans si garanties réelles) | — | CGI art. 7-E, 7-F, 7-A-1 | CGI 2026 | [CGI 2026] | 2026-10-16 | haute |
| reint.charges_especes | charges ≥ 100 000 FCFA par opération payées en espèces non déductibles (+ factures sans mentions, hors système de facturation électronique, fournisseurs hors fichier actif) | FCFA | CGI art. 8 bis | CGI 2026 | [CGI 2026] | 2026-10-16 | haute |
| amort.materiel_automobile | léger en ville 25 % ; location/auto-école 33,33 % ; lourd/brousse 33,33 % ; tracteurs 20 % (taux maxima) ; seuil petit matériel 500 000 FCFA | %/an | CGI art. 7-D | CGI 2026 | [CGI 2026] | 2026-10-16 | haute |
| dsf.date_limite | 15 mars (structure grandes entreprises) ; 15 avril (CIME et centres spécialisés) ; 15 mai (centres de fiscalité locale et particuliers) | date (2026 pour l'exercice 2025) | CGI art. 18 (1) | CGI 2026 ; identique CGI 2024 ; reconduit par projet LF 2026 | [CGI 2026] ; [CGI 2024] ; [Projet LF 2026] | 2026-10-16 | haute |
| dsf.pieces_jointes | états financiers SYSCOHADA (CIMA/COBAC selon secteur) + DIPE obligatoire | — | CGI art. 18 (1)-(3) | CGI 2026 | [CGI 2026] | 2026-10-16 | haute |
| regime.reel.seuil | CA annuel HT ≥ 50 000 000 FCFA (entreprises individuelles et personnes morales) ; + d'office : pétrole, mines, gaz, crédit, microfinance, assurance, téléphonie mobile, agréés, etc. | FCFA | CGI art. 93 quater | CGI 2024 (al. 3) et CGI 2026 (al. 2) | [CGI 2026] ; [CGI 2024] | 2026-10-16 | haute |
| regime.maintien | 2 ans dans le régime initial si le CA passe sous le seuil | ans | CGI art. 93 quinquies | CGI 2026 | [CGI 2026] | 2026-10-16 | haute |

### URL ouvertes

- [CGI 2026] https://www.impots.cm/sites/default/files/documents/CODE%20GENERAL%20DES%20IMPOTS%202026%20SITE%20DGI%20VERSION%20FRANCAISE.pdf (« Mis à jour au 1er janvier 2026 », édition officielle DGI)
- [CGI 2024] https://www.impots.cm/sites/default/files/documents/CGI%202024%20version%20francaise.pdf (« Mis à jour au 1er janvier 2024 »)
- [Arrêté 2025] https://www.impots.cm/sites/default/files/documents/ARRETE%20N%C2%B0001%20DU%2007%20JANV%202025%20VF-compress%C3%A9.pdf (arrêté n° 00000001/MINFI/DGI du 07/01/2025, exercice 2025)
- [LF 2025] https://www.impots.cm/sites/default/files/documents/loi_n_2024_013_du_23_12_2024-web.pdf (loi n° 2024/013 du 23/12/2024 — scan, non exploité)
- [LF 2026] https://www.prc.cm/files/c0/a1/8a/f2384c46567a032046599c65f95c5aa6.pdf (loi n° 2025/012 du 17/12/2025 — scan, non exploité)
- [Projet LF 2026] https://www.dgb.cm/wp-content/uploads/2025/11/PROJET-DE-LOI-FINANCES-2026_FR_26112025.pdf (projet, DGB/MINFI)
- [MINFI LF 2026] https://minfi.gov.cm/loi-de-finances-2026-comprendre-les-nouvelles-mesures/
- Liste des documents DGI : https://www.impots.cm/fr/documents/39

## Contradictions et évolutions repérées

1. **Régimes sous le réel en 2025.** Le CGI 2024 prévoit impôt libératoire (< 10 M) / simplifié
   (10–50 M) / réel (≥ 50 M) ; le CGI 2026 prévoit IGS (< 50 M ; < 30 M professions libérales) /
   réel. L'arrêté du 07/01/2025 cite encore un taux AIR de 5,5 % pour le « régime simplifié » en
   2025. Le **seuil du réel (≥ 50 M FCFA) est le même dans les deux éditions** ; la date exacte de
   la bascule vers l'IGS (LF 2025 ou LF 2026) n'est pas confirmée (textes de loi scannés).
2. **Minimum de perception 5 % du régime simplifié** : marqué « (Supprimé) » dans le projet LF 2026,
   mais toujours présent dans le CGI éd. 2026. Sans effet pour une entreprise au réel.
3. **TVA à taux réduit de 10 %** : créée par la LF 2026 → **ne vaut pas pour 2025**.
4. Le projet LF 2026 modifie les art. 7, 18, 21, 22, 93 quater, 142 du CGI. Pour les paramètres
   du tableau, les nouvelles rédactions reprennent les valeurs antérieures (art. 7-A-2, 18, 22 al. 2,
   93 quater al. 2). Aucune disposition transitoire visant l'IS des résultats 2025 n'a été vue dans
   le projet ; la loi promulguée n'a pas pu être lue en texte.

## Non confirmé

- **Plafond de base amortissable des véhicules de tourisme** : **aucun plafond trouvé** dans le CGI
  (art. 7-D ne donne que des taux maximaux) ; seules exclusions : dépenses liées aux bateaux de
  plaisance, avions de tourisme, résidences d'agrément, chasse, pêche sportive (art. 7-A-1-c).
  À traiter comme « pas de plafond légal », sous réserve d'une doctrine non consultée.
- **Valeur chiffrée du « taux des avances de la Banque Centrale »** pour 2025 (BEAC) : non
  recherchée sur une source BEAC ; le CGI ne fixe que « + 2 points ».
- **Caractère libératoire ou non du minimum de perception** et règle d'imputation des acomptes sur
  l'IS final : l'art. 22 (2) en fait un plancher ; la règle « impôt annuel diminué des acomptes, solde
  au 15 mars » n'a été trouvée explicitement que pour l'IRPP-BIC (section des modalités de perception),
  pas dans la section IS. La date limite de paiement du solde d'IS n'est pas confirmée.
- **Base du minimum de perception** : l'art. 23 dit « chiffre d'affaires global réalisé au cours de
  l'exercice précédent » ; cité à la lettre, sans circulaire qui l'éclaire.
- **Contenu de la LF 2025 et de la LF 2026 promulguées** et des **circulaires d'application LF 2025**
  (`CIRCULAIRE LF2025..pdf`) et **LF 2026** : documents scannés ou non trouvés sur impots.cm.
- **Seuils du système minimal de trésorerie (AUDCIF)** : non recherchés dans l'Acte uniforme ; le
  CGI ne les fixe pas.
- **Liste exhaustive des opérations au taux zéro de TVA / exonérations** : non relue.
