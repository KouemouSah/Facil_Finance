---
icon: lucide/file-text
---

# Termes de référence (TDR)

<span class="statut statut--valide">validé</span> · Version 1.0 · 15/10/2026 · Validé par le porteur ; mis à jour au fil de l'avancement · Porteur : Facil - AI Solutions Architect - Emac SAH

!!! abstract "Objet"
    Ce document contractuel court s'adresse à un financeur, un partenaire, un sous-traitant ou un client grand compte. Il dit **ce qui sera livré, quand, comment on le reçoit et à quelles conditions**. Le détail des exigences est dans le [PRD](prd.md) ; les choix techniques sont dans les [ADR](adr/index.md).

## 1. Contexte

Dans les 17 États de l'OHADA, les entreprises produisent chaque année des états financiers selon le **SYSCOHADA révisé** (AUDCIF 2017). Elles déposent aussi une **liasse fiscale** (DSF, DEF en Guinée équatoriale), dont la forme varie selon le pays et l'administration. Cette production est aujourd'hui :

- **manuelle** : ressaisie de la balance dans des classeurs Excel non contrôlés ;
- **risquée** : erreurs de soldes, notes incohérentes avec les états, tableaux fiscaux recalculés à la main ;
- **mal outillée** : les logiciels du marché montent la liasse, mais ne **prouvent** pas qu'elle est juste. Ils ne couvrent souvent ni l'espagnol (Guinée équatoriale) ni le portugais (Guinée-Bissau).

Un premier moteur existe et a été validé sur un dossier réel de Guinée équatoriale. Il reproduit la liasse déposée, avec des écarts tous expliqués (voir [ADR 0005](adr/0005-reutiliser-le-moteur-def.md)).

## 2. Objectifs

| # | Objectif | Indicateur de réussite |
|---|---|---|
| O1 | Produire une liasse **juste et prouvée** à partir de la balance ou du grand livre | 30 liasses réelles reproduites par pays, au franc près ou avec des écarts expliqués |
| O2 | Couvrir progressivement **les 17 États**, en système normal et en système minimal | Packs pays validés par un expert local ([couverture](plans/couverture-pays.md)) |
| O3 | Installer **sans compétence technique** et **sans dépendance** | Installation sans assistance en moins de 30 minutes, sous Windows et sous Linux |
| O4 | Garantir la **confidentialité** des données financières | Aucune donnée ne quitte le poste ou le serveur sans décision explicite ; journal des sorties |
| O5 | Assister l'équipe comptable avec **Kaem**, sans lui confier ni calcul ni validation | Taux de réussite ≥ 90 % sur le banc d'évaluation métier |

## 3. Périmètre

Le périmètre couvre **les cinq versions** ; chacune est livrable et utile seule ([plan de versions](plans/feuille-de-route.md)). Les **packs pays** ne sont pas rattachés aux versions : chacun devient disponible quand il est validé, au trimestre indiqué par la [roadmap](plans/roadmap.md).

| Version | Dans le périmètre |
|---|---|
| **V1.0 — Socle** | Import de la balance, du grand livre et des écritures dans un grand livre immuable ; révision et contrôles ; états SN et SMT ; liasse fiscale (GE, Cameroun, Sénégal) ; versions PROJET et DÉFINITIVE ; sociétés, exercices, rôles et droits ; installation Windows et Linux, mode SSH ; sauvegardes ; licence hors ligne ; interface FR, ES, PT, EN |
| **V1.1 — Kaem (texte)** | Paquet IA local téléchargeable ; chat et palette de commandes ; explications d'écarts ; brouillons de notes et de remarques |
| **V1.2 — Production complète** | Saisie comptable, lettrage, clôtures mensuelles ; TVA périodique ; OCR des pièces avec validation humaine ; analyse des écritures (ISA 240) ; télédéclaration là où elle existe ; reporting du dirigeant |
| **V2.0 — SaaS** | Multi-clients isolés ; identité fédérée ; souscription et facturation ; hébergement régional ; engagement de service ; trajectoire ISO 27001 ; migration de l'édition installée vers le SaaS et retour |
| **V2.1 — Kaem (voix) et veille** | Écoute et voix féminine en FR, ES et PT ; alertes (échéances fiscales, anomalies) ; mot d'éveil en option sur une application de bureau |

**Hors produit, dans toutes les versions** : paie, stocks, CRM, gestion commerciale. Facil Finance **importe** leurs résultats comptables ; elle ne les remplace pas.

## 4. Livrables

| Livrable | Forme | Critère de réception |
|---|---|---|
| Application Facil Finance | Installeurs Windows (MSI) et Linux (`.run`, `.deb`, `.rpm`), signés | Matrice d'installation verte ([ADR 0003](adr/0003-distribution-autoportante.md)) |
| Packs pays | Paquets de données signés | Validation par un expert local et reproduction de liasses réelles |
| Paquet IA Kaem | Téléchargement signé, ou clé USB | Banc d'évaluation passé sur le PC de référence le plus faible |
| Documentation | Ce site, plus les manuels FR/ES/PT | Revue et validation par le porteur |
| Code source | Dépôt, entiercement pour les grands comptes | Recette de construction reproductible |

## 5. Calendrier

**Implémentation en un mois, codée avec Claude Code ; livraison le {{cal:jalon-long:livraison}}** ([ADR 0013](adr/0013-developpement-avec-claude-code.md)).

| Étape | Dates |
|---|---|
| Cadrage (cette documentation) | {{cal:periode:s0}} |
| Sprint 1 — Fondations : format de pack, Cameroun, moteur extrait, GE convertie | {{cal:periode:s1}} |
| Sprint 2 — V1.0 Socle | {{cal:periode:s2}} |
| Sprint 3 — V1.1 et V1.2 | {{cal:periode:s3}} |
| Sprint 4 — V2.0 et V2.1 | {{cal:periode:s4}} |
| Durcissement | {{cal:periode:s5a}} |
| Recette métier | {{cal:periode:recette}} |
| **Livraison** | **{{cal:jalon-long:livraison}}** |

Le code des cinq versions est livré le {{cal:jalon-long:livraison}}. **La disponibilité commerciale de chaque version dépend de preuves externes**, que le codage ne raccourcit pas : packs validés par un expert local sur des liasses réelles, audit de sécurité pour le SaaS, contrats. Voir le [plan de versions](plans/feuille-de-route.md), le [plan de sprints](plans/sprints.md) et la [roadmap](plans/roadmap.md).

## 6. Organisation et gouvernance

| Rôle | Responsabilité | Qui |
|---|---|---|
| Porteur du produit | Arbitre le périmètre, valide les jalons | Facil — direction |
| Codage | Écrit le code, les tests et les gardes | **Claude Code** (Anthropic) |
| Développeur responsable | Relit, tranche, fusionne ; responsable de ce qui est livré | Équipe Facil *(à désigner, à plein temps pendant le mois)* |
| Expert-comptable valideur, par pays | Valide le pack pays et les liasses de référence | Partenaire local *(à désigner pour chaque pays)* |
| Juriste | Marque, contrats, données personnelles | *(à désigner)* |
| Clients pilotes | Fournissent des dossiers réels et reçoivent les versions de recette | *(à recruter : 2 ou 3 par pays)* |

Instances : un point de jalon à chaque fin de version ; un registre des décisions ([ADR](adr/index.md)) ; un [registre des risques](registre-risques.md) revu à chaque jalon.

## 7. Critères de réception d'une version

1. Toutes les exigences « Doit » du [PRD](prd.md) pour la version sont démontrées par un test **et** par une exécution réelle.
2. Les gardes de conformité comptable sont vertes. Chacune a été validée par une contre-épreuve : on y introduit volontairement une erreur, et elle doit la détecter.
3. La matrice d'installation est verte.
4. La documentation rendue fausse par la version est corrigée dans la même livraison.

## 8. Hypothèses et contraintes

- Le matériel cible est un PC **sans carte graphique, avec au moins 16 Go de RAM**, pour l'édition avec Kaem. Sans Kaem, 8 Go suffisent.
- Les modèles officiels de liasse sont publics, ou obtenus par l'expert local. **Côte d'Ivoire : aucun modèle officiel révisé n'a été trouvé à ce jour.**
- L'édition installée est **propriétaire** ([ADR 0011](adr/0011-licence-proprietaire.md)). La marque « Facil Finance » doit être déposée à l'OAPI, après une recherche d'antériorité.

## 9. Risques principaux

Voir le [registre des risques](registre-risques.md). Les trois premiers sont : la non-conformité d'une liasse nationale, la dispersion du périmètre et la lenteur de l'IA sur processeur seul.
