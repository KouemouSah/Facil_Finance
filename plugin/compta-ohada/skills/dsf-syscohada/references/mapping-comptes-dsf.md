# Correspondance comptes SYSCOHADA → postes de la DEF/DSF

> **FICHIER GÉNÉRÉ** depuis `mapping-comptes-dsf.json` par `tools/gen_mapping_md.py` — ne pas éditer.
> Version 2.0 (2026-09-28). Codes REF, libellés et notes : ceux de la DEF GE 2025 déposée du dossier pilote (modèle de référence GE, faute de modèle officiel DGI). Structure des comptes : SYSCOHADA révisé (AUDCIF 2017).

## Conventions

- **actif** : brut = débit - crédit
- **amort** : amortissements / dépréciations = crédit - débit (colonne AMORT et PROV du bilan actif ; net = brut - amort)
- **passif** : crédit - débit (négatif si débiteur, ex. report à nouveau déficitaire, capital non appelé)
- **gestion** : crédit - débit : produits positifs, charges NÉGATIVES, comme dans la DEF
- **eclatement** : règle {debiteur, crediteur} : le signe du solde du COMPTE choisit le poste (actif D-C / passif C-D). Au niveau TIERS, seule une balance auxiliaire permet l'éclatement : sans elle, un compte collectif ne s'éclate qu'au niveau compte.
- **resultat** : CJ = somme des postes du compte de résultat. Le solde du 13 est un résultat ANTÉRIEUR non affecté tant que la balance n'est pas clôturée (classes 6-8 non soldées) : il est alors présenté en CH. Balance clôturée : 13 -> CJ.

## Bilan — actif

| REF | Poste | Note | Comptes (préfixes) |
|---|---|---|---|
| AD | **Immobilisations incorporelles** | 3 | = AE + AF + AG + AH |
| AE | Frais de développement et de prospection | 3 | 211, 2811 (amort./dépréc.), 2911 (amort./dépréc.) |
| AF | Brevets, licences, logiciels et droits similaires | 3 | 212, 213, 214, 2812 (amort./dépréc.), 2813 (amort./dépréc.), 2814 (amort./dépréc.), 2912 (amort./dépréc.), 2913 (amort./dépréc.), 2914 (amort./dépréc.) |
| AG | Fonds commercial et droit au bail | 3 | 215, 216, 2815 (amort./dépréc.), 2816 (amort./dépréc.), 2915 (amort./dépréc.), 2916 (amort./dépréc.) |
| AH | Autres immobilisations incorporelles | 3 | 217, 218, 219, 2817 (amort./dépréc.), 2818 (amort./dépréc.), 281 (amort./dépréc.), 291 (amort./dépréc.) |
| AI | **Immobilisations corporelles** | 3 | = AJ + AK + AL + AM + AN |
| AJ | Terrains | 3 | 22, 282 (amort./dépréc.), 292 (amort./dépréc.) |
| AK | Bâtiments | 3 | 231, 232, 233, 237, 239, 2831 (amort./dépréc.), 2832 (amort./dépréc.), 2833 (amort./dépréc.), 2837 (amort./dépréc.), 283 (amort./dépréc.), 293 (amort./dépréc.) |
| AL | Aménagements, agencements et installations | 3 | 234, 235, 238, 2834 (amort./dépréc.), 2835 (amort./dépréc.), 2838 (amort./dépréc.), 2934 (amort./dépréc.), 2935 (amort./dépréc.), 2938 (amort./dépréc.) |
| AM | Matériel, mobilier et actifs biologiques | 3 | 24, 284 (amort./dépréc.), 294 (amort./dépréc.) |
| AN | Matériel de transport | 3 | 245, 2845 (amort./dépréc.), 2945 (amort./dépréc.) |
| AP | Avances et acomptes versés sur immobilisations | 3 | 25, 295 (amort./dépréc.) |
| AQ | **Immobilisations financières** | 4 | = AR + AS |
| AR | Titres de participation | 4 | 26, 296 (amort./dépréc.) |
| AS | Autres immobilisations financières | 4 | 27, 297 (amort./dépréc.) |
| AZ | **TOTAL ACTIF IMMOBILISÉ** |  | = AD + AI + AP + AQ |
| BA | Actif circulant HAO | 5 | 48 si débiteur, 498 (amort./dépréc.) |
| BB | Stocks et encours | 6 | 3, 39 (amort./dépréc.) |
| BG | **Créances et emplois assimilés** |  | = BH + BI + BJ |
| BH | Fournisseurs avances versées | 17 | 40 si débiteur, 409 si débiteur, 490 (amort./dépréc.) |
| BI | Clients | 7 | 41 si débiteur, 491 (amort./dépréc.) |
| BJ | Autres créances | 8 | 42 si débiteur, 43 si débiteur, 44 si débiteur, 45 si débiteur, 46 si débiteur, 47 si débiteur, 492 (amort./dépréc.), 493 (amort./dépréc.), 494 (amort./dépréc.), 495 (amort./dépréc.), 496 (amort./dépréc.), 497 (amort./dépréc.) |
| BK | **TOTAL ACTIF CIRCULANT** |  | = BA + BB + BG |
| BQ | Titres de placement | 9 | 50, 590 (amort./dépréc.), 591 (amort./dépréc.) |
| BR | Valeurs à encaisser | 10 | 51 |
| BS | Banques, chèques postaux, caisse et assimilés | 11 | 52 si débiteur, 53 si débiteur, 54 si débiteur, 55 si débiteur, 57 si débiteur, 58 si débiteur, 56 si débiteur, 564 si débiteur, 565 si débiteur, 592 (amort./dépréc.), 593 (amort./dépréc.), 594 (amort./dépréc.) |
| BT | **TOTAL TRÉSORERIE-ACTIF** |  | = BQ + BR + BS |
| BU | Écart de conversion-Actif | 12 | 478 |
| BZ | **TOTAL GÉNÉRAL ACTIF** |  | = AZ + BK + BT + BU |

## Bilan — passif

| REF | Poste | Note | Comptes (préfixes) |
|---|---|---|---|
| CA | Capital | 13 | 101, 102, 103, 104 |
| CB | Apporteurs capital non appelé (-) | 13 | 109 |
| CD | Primes liées au capital social | 14 | 105 |
| CE | Écarts de réévaluation | 3E | 106 |
| CF | Réserves indisponibles | 14 | 111, 112, 113 |
| CG | Réserves libres | 14 | 118 |
| CH | Report à nouveau (+ ou -) | 14 | 12 |
| CJ | Résultat net de l'exercice (bénéfice + ou perte -) |  | 13 |
| CL | Subventions d'investissement | 15 | 14 |
| CM | Provisions réglementées | 15 | 15 |
| CP | **TOTAL CAPITAUX PROPRES ET RESSOURCES ASSIMILÉES** |  | = CA + CB + CD + CE + CF + CG + CH + CJ + CL + CM |
| DA | Emprunts et dettes financières diverses | 16 | 16, 18 |
| DB | Dettes de location-acquisition | 16 | 17 |
| DC | Provisions pour risques et charges | 16 | 19 |
| DD | **TOTAL DETTES FINANCIÈRES ET RESSOURCES ASSIMILÉES** |  | = DA + DB + DC |
| DF | **TOTAL RESSOURCES STABLES** |  | = CP + DD |
| DH | Dettes circulantes HAO | 5 | 48 si créditeur |
| DI | Clients, avances reçues | 7 | 41 si créditeur |
| DJ | Fournisseurs d'exploitation | 17 | 40 si créditeur, 409 si créditeur |
| DK | Dettes fiscales et sociales | 18 | 42 si créditeur, 43 si créditeur, 44 si créditeur |
| DM | Autres dettes | 19 | 45 si créditeur, 46 si créditeur, 47 si créditeur |
| DN | Provisions pour risques à court terme | 19 | 499, 599 |
| DP | **TOTAL PASSIF CIRCULANT** |  | = DH + DI + DJ + DK + DM + DN |
| DQ | Banques, crédits d'escompte | 20 | 564 si créditeur, 565 si créditeur |
| DR | Banques, établissements financiers et crédits de trésorerie | 20 | 52 si créditeur, 53 si créditeur, 54 si créditeur, 55 si créditeur, 57 si créditeur, 58 si créditeur, 56 si créditeur |
| DT | **TOTAL TRÉSORERIE-PASSIF** |  | = DQ + DR |
| DV | Écart de conversion-Passif | 12 | 479 |
| DZ | **TOTAL GÉNÉRAL PASSIF** |  | = DF + DP + DT + DV |

## Compte de résultat

| REF | Poste | Note | Comptes (préfixes) |
|---|---|---|---|
| TA | Ventes de marchandises | 21 | 701 |
| RA | Achats de marchandises | 22 | 601 |
| RB | Variation de stocks de marchandises | 6 | 6031 |
| XA | **MARGE COMMERCIALE** |  | = TA + RA + RB |
| TB | Ventes de produits fabriqués | 21 | 702, 703, 704 |
| TC | Travaux, services vendus | 21 | 705, 706 |
| TD | Produits accessoires | 21 | 707 |
| XB | **CHIFFRE D'AFFAIRES** |  | = TA + TB + TC + TD |
| TE | Production stockée (ou déstockage) | 6 | 73 |
| TF | Production immobilisée | 21 | 72 |
| TG | Subventions d'exploitation | 21 | 71 |
| TH | Autres produits | 21 | 75 |
| TI | Transferts de charges d'exploitation | 12 | 781 |
| RC | Achats de matières premières et fournitures liées | 22 | 602 |
| RD | Variation de stocks de matières premières | 6 | 6032 |
| RE | Autres achats | 22 | 604, 605, 608 |
| RF | Variation de stocks d'autres approvisionnements | 6 | 6033 |
| RG | Transports | 23 | 61 |
| RH | Services extérieurs | 24 | 62, 63 |
| RI | Impôts et taxes | 25 | 64 |
| RJ | Autres charges | 26 | 65 |
| XC | **VALEUR AJOUTÉE** |  | = XB + RA + RB + TE + TF + TG + TH + TI + RC + RD + RE + RF + RG + RH + RI + RJ |
| RK | Charges de personnel | 27 | 66 |
| XD | **EXCÉDENT BRUT D'EXPLOITATION** |  | = XC + RK |
| TJ | Reprises d'amortissements, provisions et dépréciations | 28 | 791, 798, 799 |
| RL | Dotations aux amortissements, provisions et dépréciations | 3C&28 | 681, 691 |
| XE | **RÉSULTAT D'EXPLOITATION** |  | = XD + TJ + RL |
| TK | Revenus financiers et assimilés | 29 | 77 |
| TL | Reprises de provisions et dépréciations financières | 28 | 797 |
| TM | Transferts de charges financières | 12 | 787 |
| RM | Frais financiers et charges assimilées | 29 | 67 |
| RN | Dotations aux provisions et dépréciations financières | 3C&28 | 687, 697 |
| XF | **RÉSULTAT FINANCIER** |  | = TK + TL + TM + RM + RN |
| XG | **RÉSULTAT DES ACTIVITÉS ORDINAIRES** |  | = XE + XF |
| TN | Produits des cessions d'immobilisations | 3D | 82 |
| TO | Autres produits HAO | 30 | 84, 86, 88 |
| RO | Valeurs comptables des cessions d'immobilisations | 3D | 81 |
| RP | Autres charges HAO | 30 | 83, 85 |
| XH | **RÉSULTAT HORS ACTIVITÉS ORDINAIRES** |  | = TN + TO + RO + RP |
| RQ | Participation des travailleurs | 30 | 87 |
| RS | Impôts sur le résultat |  | 89 |
| XI | **RÉSULTAT NET** |  | = XG + XH + RQ + RS |

## Hors des états

Classes/préfixes signalés sans être agrégés : 9.

## Limites connues

- L'éclatement par signe se fait au niveau du **compte**. Un tiers débiteur logé dans un compte collectif créditeur (ex. avances fournisseurs) n'est reclassé qu'avec une **balance auxiliaire**.
- Le N-1 d'une DEF vient de la DEF précédente déposée, pas de la balance N (sauf balance comparative).
- Validé au franc près contre la DEF GE 2025 déposée du dossier pilote, écarts expliqués : la garde de référence du dossier pilote (hors plugin).
