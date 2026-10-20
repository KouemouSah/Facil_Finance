---
icon: lucide/book-open
---

# Glossaire

<span class="statut statut--brouillon">brouillon</span> · Version 0.1 · 15/10/2026

## Référentiel comptable et fiscal

AUDCIF
:   Acte uniforme OHADA relatif au droit comptable et à l'information financière (adopté le 26/01/2017). Il fonde le SYSCOHADA révisé.

OHADA
:   Organisation pour l'harmonisation en Afrique du droit des affaires : 17 États membres.

SYSCOHADA révisé
:   Système comptable OHADA applicable depuis le 01/01/2018 (comptes personnels) et le 01/01/2019 (comptes consolidés).

SN — Système normal
:   Présentation complète : bilan, compte de résultat, tableau des flux de trésorerie (TFT) et notes annexes 1 à 35 et leurs subdivisions.

SMT — Système minimal de trésorerie
:   Présentation simplifiée, en recettes et dépenses, réservée aux très petites entités sous les seuils de chiffre d'affaires fixés par l'AUDCIF.

DSF
:   Déclaration statistique et fiscale : la liasse annuelle déposée auprès de l'administration fiscale. Elle réunit les états financiers et des tableaux fiscaux et statistiques.

DEF
:   *Declaración Estadística y Fiscal* : nom de la DSF en Guinée équatoriale.

Liasse
:   L'ensemble des feuilles d'une DSF ou d'une DEF.

Note annexe
:   Tableau explicatif d'un poste des états. Exemple : la note 3A, sur les immobilisations brutes.

Contrôle « note = poste »
:   Vérification que le total d'une note est égal au poste des états qu'elle détaille.

Balance (6 ou 8 colonnes)
:   Liste des comptes avec leurs soldes d'ouverture, leurs mouvements et leurs soldes de clôture, au débit et au crédit. La balance à 6 colonnes est la plus répandue dans les PME.

Grand livre
:   Détail des écritures, compte par compte.

À-nouveaux
:   Écritures d'ouverture reprenant les soldes de l'exercice précédent.

Réintégration
:   Charge comptable non déductible, ajoutée au résultat pour calculer l'impôt.

IS, minimum de perception
:   Impôt sur les sociétés, et impôt minimal dû même en cas de perte. Le minimum porte un nom différent selon le pays (*Cuota Mínima* en Guinée équatoriale).

## Zones et institutions

CEMAC
:   Communauté économique et monétaire de l'Afrique centrale. Monnaie : franc CFA BEAC (XAF).

UEMOA
:   Union économique et monétaire ouest-africaine. Monnaie : franc CFA BCEAO (XOF).

OAPI
:   Organisation africaine de la propriété intellectuelle (Accord de Bangui). Un seul dépôt de marque y couvre ses États membres.

DGI, DGID, OTR
:   Administrations fiscales : Direction générale des impôts (de nombreux pays), Direction générale des impôts et des domaines (Sénégal), Office togolais des recettes.

## Produit

Pack pays
:   Paquet de données versionné, signé et daté par exercice, qui décrit la liasse d'un pays ([spécification](specs/pack-pays.md)).

Moteur
:   La bibliothèque de calcul : lecture des balances, agrégation, états, contrôles et rendu. Elle ne contient **aucune règle propre à un pays** ; ces règles viennent des packs.

Passerelle de confidentialité
:   Composant par lequel passe toute donnée qui sort vers un service externe : pseudonymes, montants masqués, contrôle avant envoi (échec fermé), journal.

Kaem
:   L'assistante de Facil Finance (voix féminine). Elle explique, prépare et rédige. Elle ne calcule et ne valide jamais.

Version PROJET / DÉFINITIVE
:   Une liasse reste PROJET (avec filigrane) tant qu'une question obligatoire est ouverte. Elle devient DÉFINITIVE sur validation explicite d'un utilisateur habilité.

Garde ; contre-épreuve
:   Une garde est un test automatique qui bloque une livraison. Une contre-épreuve vérifie qu'une garde fonctionne : on y introduit volontairement une erreur, et la garde doit la détecter.

ADR
:   *Architecture Decision Record* : fiche qui consigne une décision structurante, avec son contexte, les options écartées et ses conséquences.
