# Squelette de la liasse DSF (extrait du modèle officiel)

> Source : `DSF_Normal_VEROUILLE-09-03-2021.xlsx` — 74 feuilles. Extraction automatique (grounded), ne pas éditer à la main : régénérer via `tools/extract_dsf_skeleton.py`.

**Principe** : les Notes sont les points de saisie ; le Bilan et le Compte de résultat **agrègent les Notes par formules** (colonne « Formule »). Le mapping comptes→DSF (`mapping-comptes-dsf.md`) alimente les Notes.

## BILAN (feuille « BILAN PAYSAGE ») — 29 postes

| REF | Libellé | Note | Formule (source) |
|---|---|---|---|
| AD | IMMOBILISATIONS INCORPORELLES | =+SUM(D13:D16) | `=+SUM(E13:E16)` |
| AE | Frais de développement et de prospection |  | `=+'NOTE 3C'!C14` |
| AF | Brevet, licences, logiciels et droits similaires |  | `=+'NOTE 3C'!C15` |
| AG | Fond commercial et droit au bail |  | `=+'NOTE 3C'!C16` |
| AH | Autres immpobilisations incorporelles |  | `=+'NOTE 3C'!C17` |
| AI | IMMOBILISATIONS CORPORELLES | =+SUM(D18:D22) | `=+SUM(E18:E22)` |
| AJ | Terrains (1) (1) dont placement en net……………………./…............... |  | `` |
| AK | Bâtiments (1) dont placement net ………………../…...................... |  | `` |
| AL | Aménagements, agencements et installations |  | `` |
| AM | Matériel, mobilier et actifs biologiques |  | `` |
| AN | Matériel de transport |  | `` |
| AP | AVANCES ET ACOMPTES VERSES SUR IMMOBILISATION |  | `` |
| AQ | IMMOBILISATION FINANCIERES | =+SUM(D25:D26) | `=+SUM(E25:E26)` |
| AR | Titres de participation |  | `` |
| AS | Autres immobilisations financières |  | `` |
| AZ | TOTAL ACTIF IMMOBILISE | =+D24+D17+D12 | `=+E24+E17+E12` |
| BA | Actif circulant HAO | =+'NOTE 5 '!B12 | `=+'NOTE 5 '!B13` |
| BB | Stocks et encours | =+'NOTE 6 '!B19 | `=+'NOTE 6 '!B23` |
| BC | Créances et emplois assimilés |  | `` |
| BH | Fournisseurs avances versées | =+'NOTE 17 '!B20 | `` |
| BI | Clients | =+'NOTE 7 '!B22 | `=+'NOTE 7 '!B24` |
| BJ | Autres créances | =+'NOTE 8 '!B19 | `=+'NOTE 8 '!B21` |
| BK | TOTAL ACTIF CIRCULANT | =+SUM(D28:D33) | `=+SUM(E28:E33)` |
| BQ | Titres de placement | =+'NOTE 9 '!B16 | `=+'NOTE 9 '!B17` |
| BR | Valeurs à encaisser | =+'NOTE 10 '!B15 | `=+'NOTE 10 '!B16` |
| BS | Banques, chèques postaux, caisse et assimilés | =+'NOTE 11 '!B21 | `=+'NOTE 11 '!B22` |
| BT | TOTAL TRESORERIE - ACTIF | =+SUM(D35:D37) | `=+SUM(E35:E37)` |
| BU | Ecart de conversion - Actif |  | `` |
| BZ | TOTAL GENERAL | =+D39+D38+D34+D27 | `=+E39+E38+E34+E27` |

## COMPTE DE RÉSULTAT (feuille « COMPTE DE RESULTAT ») — 42 postes

| REF | Libellé | Note | Formule (source) |
|---|---|---|---|
| TA | vente de marchandises (A) | 21 | `=+'NOTE 21'!E13` |
| RA | Achat de marchandises | 22 | `=+'NOTE 22'!E12` |
| RB | Variation de stock de marchandises | 6 | `=+'NOTE 6 '!B23-'NOTE 6 '!C23` |
| XA | MARGE COMMERCIALE (Somme TA à RB) |  | `=+E11-E12-E13` |
| TB | Vente de produits fabriqués B | 21 | `=+'NOTE 21'!E15` |
| TC | Travaux, services vendus C | 21 | `=+'NOTE 21'!E16` |
| TD | Produits accessoires D | 21 | `=+'NOTE 21'!E17` |
| XB | CHIFFRE D'AFFAIRES (A+B+C+D) |  | `=+E11+E15+E16+E17` |
| TE | Produits stockés (ou destokage) | 6 | `` |
| TF | Production immobilisée | 21 | `=+'NOTE 21'!E32` |
| TG | Subventions d'exploitation | 21 | `=+'NOTE 21'!E33` |
| TH | Autres produits | 21 | `=+'NOTE 21'!E34` |
| TI | Transfert de charges d'exploitation | 12 | `=+'NOTE 12 '!B26` |
| RC | Achats de matières premières et fournitures liées | 22 | `=+'NOTE 22'!E17` |
| RD | Variation de stocks de matières premières et fornitures liées | 6 | `=+'NOTE 6 '!C12-'NOTE 6 '!B12` |
| RE | Autres achats | 22 | `=+'NOTE 22'!E33` |
| RF | Variation de stock d'autres approvisionnement | 6 | `=+'NOTE 6 '!C13-'NOTE 6 '!B13` |
| RG | Transports | 23 | `=+'NOTE 23'!B15` |
| RH | Services extérieurs | 24 | `=+'NOTE 24'!B23` |
| RI | Impôts et taxes | 25 | `=+'NOTE 25'!B15` |
| RJ | Autres charges | 26 | `=+'NOTE 26'!B19` |
| XC | VALEUR AJOUTEE (XB + RA + RB) + (somme TE à RJ) |  | `` |
| RK | Charges de personnel | 27 | `=+'NOTE 27A'!B17` |
| XD | EXEDENT BRUT D'EXPLOITATION (XC+RK) | 28 | `=+E32+E33` |
| TJ | Reprises d'amortissements, provisions et dépréciations | 28 | `` |
| RL | Dotations aux amortissements, aux provisions et dépréciations | 3C&28 | `=+'NOTE 3C'!C28+'NOTE 28'!C31+'NOTE 28'!D31+'NOTE 28'!E31` |
| XE | RESULTAT D'EXPLOITATIIONS (XD + TJ + RL) |  | `=+E34+E35-E36` |
| TK | Revenus financiers et assimilés | 29 | `=+'NOTE 29'!B31` |
| TL | Reprises de provisions et dépréciations financières | 28 | `` |
| TM | Transfert de charges financières | 12 | `=+'NOTE 12 '!B29` |
| RM | Frais financiers et charges assimilées | 29 | `=+'NOTE 29'!B19` |
| RN | Dotations aux provisions et aux dépréciations financières | 3C&28 | `=+'NOTE 28'!D31` |
| XF | RESULTATS FINANCIERS (somme TK à RN) |  | `=+SUM(E38:E42)` |
| XG | RESULTAT DES ACTIVITES ORDINAIRES (XE+XF) |  | `` |
| TN | Produits et cessions d'immobilisations | 3D | `` |
| TO | Autres Produits HAO | 30 | `=+'NOTE 30'!B30` |
| RO | Valeurs comptables de cessiions d'immobilisations | 3D | `=+'NOTE 3D '!D27` |
| RP | Autres charges HAO | 30 | `=+'NOTE 30'!B28` |
| XH | RESULTATS HORS ACTIVITES ORDINAIRES (somme TN à RP) |  | `` |
| RQ | Participation des travailleurs | 30 | `=+'NOTE 30'!B16` |
| RS | Impôt sur le résultat |  | `` |
| XI | RESULTAT NET (XG+XH+RQ+RS) |  | `` |

## Index des feuilles / Notes

| # | Feuille | Titre (le cas échéant) |
|---|---|---|
| 1 | ENTETE |  |
| 2 | SOMMAIRE |  |
| 3 | PAGE DE GARDE | PAGE DE GARDE |
| 4 | INFORMATIONS GENERALES |  |
| 5 | Fiche R1 |  |
| 6 | Fiche R2 |  |
| 7 | Fiche R3 |  |
| 8 | STATISTIQUES ET SYNTHESES | II. NOTES STATISTIQUES ET DE SYNTHESES |
| 9 | GRILLE D'ANALYSE DES NOTES | GRILLE D'ANALYSE DES NOTES |
| 10 | BILAN PAYSAGE | BILAN PAYSAGE |
| 11 | COMPTE DE RESULTAT | COMPTE DE RESULTAT |
| 12 | TABLEAU DES FLUX DE TRESORERIE | TABLEAU DES FLUX DE TRESORERIE |
| 13 | Note 1 | NOTE 1 |
| 14 | NOTE 2 | NOTE 2 |
| 15 | NOTE 3A | NOTE 3A IMMOBILISATIONS BRUTES |
| 16 | NOTE 3B | NOTE 3B BIENS PRIS EN LOCATION ACQUISITION |
| 17 | NOTE  3C | NOTE 3C |
| 18 | CO1-NOTE 3C | C01/NOTE 3C |
| 19 | NOTE 3D |  |
| 20 | NOTE 3E | NOTE 3E |
| 21 | NOTE 3F | NOTE 3F TABLEAU D'ETALEMENT DES CHARGES IMMOBILISEES |
| 22 | NOTE 4 | NOTE 4 IMMOBILISATIONS FINANCIERES |
| 23 | NOTE 5 | NOTE 5 ACTIF CIRCULANT HAO |
| 24 | NOTE 6 | NOTE 6 STOCKS ET EN COURS (¹) |
| 25 | NOTE 7 | NOTE 7 CLIENTS |
| 26 | NOTE 8 | NOTE 8 AUTRES CREANCES |
| 27 | NOTE 9 | NOTE 9 |
| 28 | NOTE 10 | NOTE 10 |
| 29 | NOTE 11 | NOTE 11 |
| 30 | NOTE 12 | NOTE 12 |
| 31 | NOTE 13 | NOTE 13 CAPITAL : VALEUR NOMINALE DES ACTIONS OU PARTS |
| 32 | NOTE 14 | NOTE 14 |
| 33 | NOTE 15A | NOTE 15 A |
| 34 | NOTE 15B | NOTE 15B |
| 35 | NOTE 16A | NOTE 16A |
| 36 | NOTE 17 | NOTE 17 |
| 37 | C1-NOTE 17 | C1/NOTE 17 |
| 38 | NOTE 19 | NOTE 19 |
| 39 | NOTE 20 | NOTE 20 |
| 40 | NOTE 23 | NOTE 23 TRANSPORTS |
| 41 | NOTE 24 | NOTE 24 SERVICES EXTERIEURS |
| 42 | NOTE 25 | NOTE 25 |
| 43 | C1-NOTE 25 | C1/Note 25 |
| 44 | C2-NOTE 25 | C2/NOTE 25 |
| 45 | NOTE 26 | NOTE 26 |
| 46 | NOTE 28 | NOTE 28 |
| 47 | C1-NOTE 28 | C1/NOTE 28 |
| 48 | C2-NOTE 28 | C2/NOTE 28 |
| 49 | NOTE 29 | NOTE 29 CHARGES ET REVENUS FINANCIERS |
| 50 | NOTE 30 | NOTE 30 AUTRES CHARGES ET PRODUITS HAO |
| 51 | NOTE 31 | NOTE 31 REPARTITION DU RESULTAT ET AUTRES ELEMENTS CARACTERISTIQUES DES CINQ DERNIERS EXERCICES |
| 52 | NOTE 32 | NOTE 32 PRODUCTION DE L'EXERCICE |
| 53 | NOTE 33 | NOTE 33 ACHATS DESTINES A LA PRODUCTION |
| 54 | NOTE 34 | NOTE 34: |
| 55 | NOTES STAT SOCIALE ET ENVI |  |
| 56 | NOTE 16B | NOTE 16B |
| 57 | NOTE 16B BIS | NOTE 16B bis ENGAGEMENTS DE RETRAITE ET AVANTAGES ASSIMILES |
| 58 | NOTE 16C | NOTE 16C ACTIFS ET PASSIFS EVENTUELS |
| 59 | NOTE 18 | NOTE 18 DETTES FISCALES ET SOCIALES |
| 60 | NOTE 27A | NOTE 27A CHARGES DE PERSONNEL |
| 61 | C1-NOTE 27A | C1/NOTE 27A |
| 62 | NOTE 27B | NOTE 27B |
| 63 | NOTE 35 | NOTE 35 : |
| 64 | NOTES STAT A CARACTERE COMMERCI |  |
| 65 | NOTE 21 | NOTE 21 |
| 66 | NOTE 22 | NOTE 22 |
| 67 | AUTRES ANNEXES FISCA |  |
| 68 | CF1 | TABLEAU DE PASSAGE DU RESULTAT COMPTABLE AVANT IMPOT AU RESULAT FISCAL |
| 69 | CF1 BIS | TABLEAU DE DETERMINATION DE L’IMPOT SUR LE RESULTAT : IMPOT SUR LE BENEFICE FISCAL |
| 70 | CF1 TER | TABLEAU DE DETERMINATION DE L'IMPOT SUR LE RESULTAT: MINIMUM DE PERCEPTION |
| 71 | CF1 QUATER | TABLEAU DE DETERMINATION DE L’IMPOT SUR LE RESULTAT : RECAPITULATIF DES VERSEMENTS D’ACOMPTES ET DE RETENUES SUBIES D’IMPOT SUR LES SOCIETES DE L’EXERCICE |
| 72 | CF2 |  |
| 73 | CF2 BIS |  |
| 74 | CF2  TER |  |
