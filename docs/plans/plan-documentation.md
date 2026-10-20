---
icon: lucide/library
---

# Plan de documentation

<span class="statut statut--brouillon">brouillon</span> · Version 0.2 · 20/10/2026

Chaque document couvre **toutes les versions**, de V1.0 à V2.1. Il dit ce que chaque version ajoute ; il n'est pas écrit une fois par version. Un document qui n'existe pas encore **n'apparaît pas au menu** : il est listé ici, avec son échéance.

## 1. Inventaire

| Document | Emplacement | Versions couvertes | État | Échéance |
|---|---|---|---|---|
| Termes de référence | `tdr.md` | toutes | brouillon | **fait au cadrage** ({{cal:periode:s0}}) — à valider par le porteur |
| Exigences produit (PRD) | `prd.md` | toutes | brouillon | **fait au cadrage** — à valider |
| Glossaire | `glossaire.md` | toutes | brouillon | fait au cadrage, enrichi en continu |
| Registre des risques | `registre-risques.md` | toutes | brouillon | fait au cadrage, revu à chaque démonstration de sprint |
| Architecture (C4, déploiement, flux) | `architecture.md` | toutes | brouillon | fait au cadrage |
| ADR 0001 à 0013 | `adr/` | toutes | acceptées | fait au cadrage |
| Format du pack pays | `specs/pack-pays.md` | toutes | brouillon | fait au cadrage — **éprouvé par le pack Cameroun au sprint 1** ({{cal:fin:s1}}) |
| Roadmap | `plans/roadmap.md` | après la livraison | brouillon | fait au cadrage, revue chaque mois |
| Plan de versions, avec Gantt | `plans/feuille-de-route.md` | toutes | brouillon | fait au cadrage |
| Plan de sprints | `plans/sprints.md` | toutes | brouillon | fait au cadrage, mis à jour chaque vendredi |
| Couverture des pays | `plans/couverture-pays.md` | toutes | brouillon | fait au cadrage, mis à jour à chaque pack |
| Démarrer (poste, vérifications, Claude Code web) | `demarrer.md` | toutes | à jour | fait, constaté le 20/10 |
| Catalogue des modules | `catalogue-modules.md` | toutes | brouillon | constaté le 20/10, mis à jour à chaque module |
| Facil DEF, l'extension livrée | `facil-def.md` | Facil DEF 0.13 | livrée | fait, constaté le 20/10 |
| Plan de Facil DEF (lots, reprise) | `plans/plan-facil-def.md` | Facil DEF | en cours | réécrit à chaque version de l'extension |
| Chaîne d'intégration et de livraison | `chaine-livraison.md` | toutes | en place | fait, constaté le 20/10 |
| Stratégie de tests et de recette | `plans/strategie-tests.md` | toutes | à faire | {{cal:fin:s1}} (sprint 1) |
| Modèle de données cible | `modele-donnees.md` | V1.0 → V2.0 | **cible** | fait (constaté le 20/10) ; arrêté par la migration du premier jour du sprint 2 ({{cal:periode:s2}}) |
| **AppFlow** | `appflow.md` | V1.0 à V2.1 (Kaem compris) | à faire | {{cal:fin:s1}} — **avant** l'interface du sprint 2 |
| **UX/UI** (système de design, wireframes, écrans critiques, parcours vocal) | `ux-ui.md` | V1.0 à V2.1 | à faire | {{cal:fin:s1}} — **avant** l'interface du sprint 2 |
| **Schéma de la base (backend)** | `specs/schema-backend.md` | V1.0 → V2.0 (isolation par client) | à faire | {{cal:fin:s2}} — **régénéré depuis le code** à chaque fusion |
| Contrat d'API (OpenAPI) | `specs/api.md` | toutes | à faire | {{cal:fin:s2}} — généré depuis le code |
| Catalogue des commandes de Kaem | `specs/kaem-commandes.md` | V1.1 → V2.1 | à faire | {{cal:fin:s2}} — avant le sprint 3 |
| Banc d'évaluation de Kaem | `specs/kaem-banc.md` | V1.1, V2.1 | à faire | {{cal:fin:s2}} — avant le sprint 3 |
| Registre des licences (dépendances et modèles) | `specs/licences.md` | toutes | à faire | {{cal:fin:s2}}, puis à chaque nouvelle dépendance |
| Processus métier (BPMN) | `bpmn.md` | toutes | à faire | {{cal:fin:s3a}} |
| Cas d'utilisation | `cas-utilisation.md` | toutes | à faire | {{cal:fin:s3a}} |
| Analyse d'impact sur la protection des données | `specs/donnees-personnelles.md` | toutes, surtout V2.0 | à faire | {{cal:fin:s3}} — avant la fin du SaaS |
| **Vue couplée exigences ↔ processus** (choisir une exigence `EX-…` affiche le processus BPMN et l'écran AppFlow liés, et inversement) | page interactive du site | toutes | à faire, **après** le BPMN et l'AppFlow | {{cal:fin:s3}} |
| Sécurité et confidentialité | `securite-confidentialite.md` | toutes (dont l'isolation SaaS) | brouillon | première version (constaté le 20/10) ; complétée au durcissement ({{cal:fin:s5a}}) |
| Exploitation (installation, sauvegarde, mise à jour, incidents) | `plans/exploitation.md` | toutes, SaaS compris | à faire | {{cal:fin:s5a}} |
| Manuels de Facil DEF (FR, ES) | `manuels.md`, PDF publiés | Facil DEF 0.13 | **fait** | constaté le 20/10 |
| Manuels utilisateur de Facil Finance FR, ES, PT | `manuels.md` | toutes | à faire | {{cal:fin:recette}} (recette) |
| Contrats (licence, conditions générales, accord de traitement des données, engagement de service) | hors site, juriste | V1.0, V2.0 | à faire, **juriste** | {{cal:preuve:contrats_juriste}} — avant la première vente |

*Échéances alignées sur le [plan de sprints](sprints.md) : sprints {{cal:periode:s1}} à {{cal:periode:s4}}, recette {{cal:periode:recette}}, livraison le {{cal:jalon-long:livraison}}.*

## 2. Ce que j'ai ajouté à la demande initiale, et pourquoi

| Ajout | Pourquoi |
|---|---|
| Registre des risques | Le TDR en a besoin, et les jalons le revoient |
| Glossaire | Exigé par `projet.md` (§ 10.1) ; indispensable à un lecteur non comptable |
| Format du pack pays | C'est la pièce sur laquelle repose la couverture des 17 pays |
| Catalogue des commandes et banc de Kaem | Sans eux, l'[ADR 0008](../adr/0008-ia-ne-calcule-ni-ne-valide.md) n'est qu'une intention |
| Exploitation, licences, données personnelles | Ce sont les premières questions d'un client grand compte et d'un auditeur |
| Garde de confidentialité du site | Les analyses du projet touchent des dossiers réels : le site ne doit jamais publier un nom de client |

## 3. Comment ce site se construit

En local : `python docs/outils/construire_site.py` (ou double-clic sur `docs/Ouvrir la documentation.cmd` sous Windows). En ligne : le workflow `documentation.yml` le reconstruit à chaque poussée sur `develop` et le publie sur [GitHub Pages](https://kouemousah.github.io/Facil_Finance/documentation/). La construction est refusée si :
- un nom de client figure dans une page (liste locale, ou empreintes HMAC en CI) ;
- une page manque au menu, ou une entrée du menu n'a pas de page ;
- un lien est cassé, ou une page charge une ressource depuis Internet.

Voir l'[ADR 0012](../adr/0012-documentation-as-code.md) et la [chaîne de livraison](../chaine-livraison.md).
