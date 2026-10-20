# Sources de la DSF : ce qui est OHADA, ce qui est pratique, ce qui est DGI

Clarification importante (à ne pas confondre). Les documents servant à monter la DSF relèvent de **trois niveaux** de nature différente.

## 1. Défini par OHADA / SYSCOHADA (Acte uniforme AUDCIF)
- **Livres comptables obligatoires** : livre-journal, **grand livre**, **balance générale**, livre d'inventaire.
- **États financiers** : Bilan, Compte de résultat, **Tableau des flux de trésorerie**, **Notes annexes** (Notes 1 à 35+).
- **Plan de comptes** SYSCOHADA (classes et comptes), principes comptables.
> Ces éléments sont **normalisés et uniformes** dans les 17 pays OHADA.

## 2. Documents de travail — définis par la PRATIQUE (non normalisés)
- **Registre / fichier des immobilisations** (mouvements, dotations) — nécessaire pour justifier la Note 3, mais **sa forme n'est pas imposée par OHADA** : chaque logiciel/cabinet a la sienne.
- **Grand livre auxiliaire tiers**, balances âgées, échéanciers.
- **Tableaux de retraitement**, feuilles de reclassement, feuilles de saisie/liaison.
- « MODELE TIERS », cell-map, profils de montage.
> Ce sont des **outils**, propres à chaque entreprise → le plugin doit **s'adapter à ceux de l'utilisateur**, pas imposer un format.

## 3. Défini par l'ADMINISTRATION FISCALE nationale (DGI), pas OHADA
- Le **format de la liasse DSF** lui-même, la **page de garde**, les **fiches R1-R3**, les **tableaux fiscaux CF1/CF2**, les **notes statistiques** (sociales, commerciales).
> **Spécifique au pays.** Le modèle bundlé est camerounais ; pour la **Guinée Équatoriale**, exiger la liasse officielle de la DGI GE pour ces parties. Le cœur SYSCOHADA (niveau 1) reste, lui, uniforme.

## Conséquence pour le plugin
- Le **niveau 1 (OHADA)** = socle stable → le mapping comptes→postes et les états s'y ancrent (référence).
- Le **niveau 2 (pratique)** = **variable** → mode adaptatif : détecter/comprendre les documents de l'utilisateur, ne rien imposer.
- Le **niveau 3 (DGI)** = **national** → dépend du modèle fourni ; format GE à confirmer.
