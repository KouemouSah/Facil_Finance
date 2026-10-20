---
icon: lucide/file-text
---

# Document Projet — « Facil Finance » (anciennement « Facil Gestion », renommé le 15/10/2026 — D2)

> **Document d'entrée** pour la génération du dossier de documentation projet complet (PRD, spécifications techniques, BPMN, cas d'utilisation, ADR, documents Product/Domain/Architecture, plans d'implémentation). Voir §10 pour la directive détaillée.

---

## 0. Arbitrages du 15/10/2026 — ils priment sur le reste du document

*Source : l'analyse critique croisée de ce document, de `jarvis_finance.md` et du plugin existant (`documentation/analyse/analyse-critique-projet-jarvis.md`). Les passages corrigés en place portent la mention ⟲ 15/10.*

| # | Arbitrage | Remplace |
|---|---|---|
| A1 | **V1 = autonome (Windows, Linux toutes distributions, mode SSH) ; V2 = SaaS multi-clients.** L'assistant IA suit une piste continue : texte en V1.1, voix et proactivité en V2.1 | « V2 = assistant vocal » (§ 1.3, § 3.2, § 8) |
| A2 | **Point d'entrée = couche de production et de contrôle** au-dessus des logiciels existants : import de la balance, du grand livre et des écritures, puis révision, états, liasse, contrôles et reporting. La saisie complète (§ 3.1) devient un module ultérieur | ERP complet dès la V1.0 (§ 8) |
| A3 | **Le moteur DEF existant** (`compta-ohada/`) est le cœur de calcul : liasse SN et GE, contrôles, lecture des balances et des grands livres, passerelle de confidentialité. Il est extrait en bibliothèque, pas réécrit (§ 14) | construction de zéro |
| A4 | **Linux : paquet autoportant multi-distributions** (glibc ≥ 2.28, x86_64 et aarch64), toute la pile embarquée. Docker n'est **pas** un prérequis (§ 15) | Docker Compose (§ 4, § 6.2, § 6.4) |
| A5 | **Les 17 États du SYSCOHADA**, en packs pays signés et versionnés ; 5 monnaies (XAF, XOF, GNF, KMF, CDF) ; liasses en FR, ES, PT et EN ; **SN et SMT** dans chaque pack (§ 16) | « GE + un pays de référence » |
| A6 | **Modèle d'IA local dans un paquet séparé et optionnel**, avec détection du matériel et 3 niveaux. Moteur llama.cpp en autonome, vLLM en serveur. Registre des licences de modèles (§ 17) | IA dans l'installeur de base |
| A7 | **« Jarvis » reste un nom de code interne.** Marque déposée à l'OAPI (plus un dépôt national en RDC) ; contrats et licences prêts avant la première vente (§ 18) | absent |
| A8 | **Licence du produit propriétaire**, avec entiercement du code pour les grands comptes | LGPL « à décider » (§ 11.5) |
| A9 | **La gouvernance de l'IA de `jarvis_finance.md` est reprise** : pare-feu d'outils, passerelle, approbation humaine, preuves, audit chaîné. **Ses choix de pile ne le sont pas tels quels** (§ 19) | — |

### 0.1 Décisions du porteur du 15/10/2026 (second tour)

| # | Décision | Conséquence |
|---|---|---|
| D1 | **Toujours en mode serveur**, même en monoposte, comme Odoo | Un seul mode d'exécution : un service (systemd ou service Windows), accès par navigateur, `127.0.0.1` en monoposte et réseau local sur option. Le multi-utilisateurs est natif, sans réinstallation. **Supprime l'édition « monoposte » distincte** prévue au § 6.3 |
| D2 | **Nom commercial : « Facil Finance »**, signé du logo Facil existant | Recherche d'antériorité à l'OAPI avant le dépôt. « Facil » est peu distinctif : déposer la marque **semi-figurative** (nom + logo) |
| D3 | **Moteur vocal : « Kaem »**, voix féminine | ⚠ Vérification du 15/10 : **KAEM Technologies (Inde) commercialise des logiciels sous ce nom, dont « KAEM Accounts », un logiciel de comptabilité**. Même domaine, donc risque de confusion. Kaem reste le **nom de l'assistant dans le produit** ; on ne le dépose pas seul avant une recherche à l'OAPI et un avis de juriste. Variante plus sûre : « Kaem by Facil » |
| D4 | **IA locale téléchargée à l'installation** ; modèle proposé : Gemma 4 E4B | Retenu, sous réserve du banc d'évaluation (§ 17.1) |
| D5 | **Matériel cible : sans GPU, 16 Go de RAM minimum** | Le niveau « IA complète avec GPU » devient une option. Tout se dimensionne sur le processeur (§ 17.1) |
| D6 | **Pays** : ordre du § 16 validé. **SN + SMT par pays** | Collecte des liasses officielles en cours (`datas/liasses-officielles/SOURCES.md`) |
| D7 | Positionnement : **l'architecture d'un ERP, l'entrée par la production** (décision d'expert, A2 précisé) | La base de données porte dès la V1.0 un vrai grand livre (écritures importées, horodatées, immuables). La saisie, qui arrive en V1.2, écrit dans les **mêmes tables**. Rien n'est à refaire le jour où le produit devient un ERP complet |
| D9 | **Pas d'expert-comptable camerounais à ce stade** : Claude travaille en expert, à partir des documents collectés (`datas/liasses-officielles/`) et de la loi de finances du Cameroun (décision du porteur du 15/10/2026) | Le pack Cameroun est produit et reproduit sur les liasses publiées, mais il reste en **préversion** jusqu'à la signature d'un expert-comptable inscrit à l'ordre (risque R14 de `projet_doc`) |
| D8 | **Implémentation en un mois, codée avec Claude Code ; livraison le 30/11/2026** (décision du porteur du 15/10/2026) | Le code des cinq versions est livré le 30/11. La disponibilité de chaque version reste conditionnée à ses preuves externes : experts locaux, liasses réelles, audit de sécurité, juriste. Voir `projet_doc/plans/feuille-de-route.md` et l'ADR 0013. Les estimations en mois-homme du § 8 ne valent plus pour le codage |

La documentation projet détaillée vit dans `projet_doc/` ; pour la consulter, lancer `projet_doc/Ouvrir la documentation.cmd`.

**Reste ouvert** : le prix des éditions. Je proposerai une grille quand le banc de validation des liasses aura chiffré l'effort par pays.

---

## 1. Reformulation de la problématique (langage métier)

### 1.1 Contexte réglementaire et métier

Dans l'espace OHADA (17 États membres, dont la **Guinée équatoriale**), la tenue de la comptabilité et la production des états financiers sont régies par l'**AUDCIF** (Acte Uniforme relatif au Droit Comptable et à l'Information Financière, adopté le 26 janvier 2017) et par le **SYSCOHADA révisé**, applicable depuis le 1er janvier 2018 pour les comptes personnels et le 1er janvier 2019 pour les comptes consolidés. Le SYSCOHADA révisé a supprimé le système allégé et maintient le **système minimal de trésorerie (SMT)** et le **système normal**, selon la taille de l'entité.

En Guinée équatoriale, cette exigence comptable se double d'une réalité singulière : pays hispanophone membre de la **CEMAC** et de l'OHADA, il a adopté le **19 novembre 2024 un nouveau Code Général des Impôts (Ley n°1/2024)**, aligné sur les directives CEMAC, les Actes uniformes OHADA et les recommandations du FMI. Les entités y sont donc soumises à une **double contrainte de conformité** : un référentiel comptable francophone harmonisé (SYSCOHADA) et une fiscalité nationale en pleine refonte, avec des obligations déclaratives (liasses fiscales, états financiers annuels, DSF ou équivalent local) dont les formats varient par pays et par administration.

### 1.2 Problématique (reformulée)

Les PME, cabinets comptables et directions financières opérant en zone OHADA — et particulièrement en Guinée équatoriale — peinent à produire, dans les délais et avec une fiabilité suffisante, les **états financiers annuels (bilan, compte de résultat, tableau des flux de trésorerie, notes annexes)**, la **liasse fiscale / DSF**, les **balances et grands livres**, ainsi que des **reportings analytiques de gestion**, parce que :

1. les données comptables sont dispersées (Excel, papier, logiciels hétérogènes, saisies multiples) ;
2. la production de la liasse est un travail manuel, répétitif et fortement exposé au risque d'erreur (soldes, rapprochements, retraitements fiscaux) ;
3. les outils existants (liasses Excel automatisées, logiciels type Thalia XCOA, LIASSE RÉVISÉE, etc.) traitent le **montage final** de la liasse mais pas la chaîne complète : ingestion → tenue de comptabilité → clôture → génération → reporting décisionnel ;
4. les ERP généralistes occidentaux (SAP, Sage, Odoo standard) ne couvrent pas nativement le SYSCOHADA (plan comptable, états financiers, tableaux fiscaux) et sont coûteux à adapter ;
5. la dimension multilingue (espagnol/français en Guinée équatoriale) et la faible connectivité réseau de certaines zones imposent une solution **installable localement, autonome, et hors-cloud optionnelle**.

### 1.3 Vision produit

Concevoir, développer et déployer **Facil Gestion** : une plateforme web de comptabilité et de gestion financière conforme SYSCOHADA révisé, à **architecture modulaire de type ERP open-source** (inspirée d'Odoo), distribuable en mode **all-in-one installable** (Windows / Linux) embarquant ses propres composants, capable de :

- **ingérer** les données comptables (saisie manuelle, import CSV/Excel, connecteurs bancaires) ;
- **calculer et générer automatiquement** : balances (générale et auxiliaire), grands livres, journaux, états financiers annuels selon le système applicable (normal / SMT), liasse fiscale et DSF paramétrable par pays (format Guinée équatoriale, Cameroun, Côte d'Ivoire, etc.), rapports financiers et tableaux de bord analytiques ;
- **gérer les utilisateurs et les droits** (RBAC multi-sociétés, multi-exercices) ;
- **installer/activer/désactiver des modules à chaud** et se **mettre à jour sans réinstallation ni interruption de service** (migrations de schéma de base de données et déploiements en continu via pipelines).

⟲ 15/10 : **la version 2 est le SaaS multi-clients** (A1). L'assistant décrit ci-dessous suit sa propre piste : **texte en V1.1, voix en V2.1**. « Jarvis » n'en est que le nom de code (A7). Description d'origine :
la plateforme embarquera un **assistant conversationnel IA local (type "Jarvis")** : dialogue vocal bidirectionnel (STT → LLM local → TTS) capable de comprendre les demandes métier, d'exécuter des workflows (ex. « Génère la balance du mois de juin », « Montre-moi le chiffre d'affaires par client », « Lance la clôture mensuelle ») et de restituer les résultats vocalement et à l'écran, **entièrement en local** pour la confidentialité des données financières.

---

## 2. Objectifs métiers (critiques, hiérarchisés)

| # | Objectif | Indicateur de succès (KPI) | Priorité |
|---|----------|---------------------------|----------|
| OB1 | Fiabiliser la production des états financiers conformes AUDCIF/SYSCOHADA révisé | 0 recalcul manuel des agrégats ; cohérence bilan/Résultat vérifiée automatiquement ; conformité au plan comptable OHADA (classes 1–9) | Must |
| OB2 | Réduire le temps de montage de la liasse fiscale / DSF | Passer de plusieurs jours à < 1 journée pour une PME ; génération en < 60 s une fois les écritures validées | Must |
| OB3 | Paramétrabilité multi-pays de la liasse | Formats par pays éditables via fichiers de configuration (pas de code) ; ≥ 2 formats livrés à la V1 (Guinée équatoriale + 1 pays de référence) | Must |
| OB4 | Centraliser et fiabiliser l'ingestion des données | Import CSV/Excel avec validation, rapprochement et piste d'audit ; 0 saisie double | Must |
| OB5 | Donner au dirigeant/comptable une vision temps réel | Dashboards : trésorerie, créances/dettes (balances âgées), résultat, ratios ; actualisation à chaque validation d'écriture | Must |
| OB6 | Déploiement simple et autonome | Installateur all-in-one (Windows/Linux) ; installation < 30 min sans expertise DevOps | Must |
| OB7 | Exploitation continue | Mise à jour applicative, des modules et du schéma BD sans interruption ni réinstallation | Must |
| OB8 | Sécurité et conformité | RBAC granulaire, chiffrement, pistes d'audit ; conformité loi n°1/2024 (Guinée équatoriale) et bonnes pratiques RGPD-like | Must |
| OB9 | Multilinguisme métier | Interface FR + ES minimum ; rapports FR ou ES selon la législation locale | Should |
| OB10 | Assistant IA vocal local (V2) | Exécution vocale des tâches métier courantes ; latence de bout en bouche < 5 s sur matériel cible ; 100 % on-premise | V2 |

**Points critiques assumés :**
- La **conformité SYSCOHADA n'est pas une fonctionnalité, c'est un invariant** : chaque écriture, chaque compte, chaque état doit être conforme dès la conception du modèle de données. Un moteur comptable « à peu près » est un produit mort.
- Le **paramétrage des liasses par pays** est le principal risque fonctionnel : les formats et tableaux fiscaux évoluent avec chaque législation (ex. refonte fiscale guinéen-équatorienne de 2024). Ils doivent donc être pilotés par **données (JSON/YAML/Excel templates)** et non codés en dur.
- La promesse « mise à jour à chaud sans interruption » impose une discipline d'architecture dès la V1 (migrations versionnées, compatibilité ascendante N/N-1, feature flags) — impossible à greffer après coup.

---

## 3. Périmètre (scope)

### 3.1 V1 — Plateforme comptable et reporting

**Inclus :**
- Module **Sociétés & Exercices** : multi-sociétés, multi-exercices, clôture/réouverture, périodes.
- Module **Plan Comptable OHADA** : plan SYSCOHADA révisé pré-chargé (classes 1–9), extensible par société, avec contrôle de cohérence (comptes réservés, mapping comptes locaux).
- Module **Saisie & Journaux** : journaux (achats, ventes, banque, caisse, OD), saisie des écritures, pièces jointes, lettrage, validation workflow (brouillon → validé → verrouillé).
- Module **Ingestion de données** : stratégie en deux paliers (voir §6.6) :
  - **Palier 1 (V1, obligatoire)** : import CSV/Excel (écritures, balances, plans de comptes, tiers) avec mapping assisté, contrôles de validation, rapports d'anomalies ; saisie manuelle avec formulaires intelligents ; API REST d'ingestion.
  - **Palier 2 (V1.5, assistance LLM/OCR locale)** : extraction automatique de documents (PDF factures/relevés, photos/numérisations) via OCR local + LLM local, **toujours avec validation humaine avant écriture**.
- Module **Clôture** : clôture mensuelle et annuelle, écritures d'inventaire, régularisations, calcul du résultat, report à nouveau.
- Module **États Financiers SYSCOHADA** : Bilan, Compte de Résultat (par nature et par fonction), Tableau des Flux de Trésorerie (TFF), Notes Annexes ; selon système normal et SMT.
- Module **Liasse fiscale / DSF** : moteur de génération piloté par templates par pays ; export Excel (formats officiels automatisés) et PDF.
- Module **Balances & Grands Livres** : balance générale, balance auxiliaire par tiers, grand livre général et auxiliaire, journaux, exports.
- Module **Reporting & Dashboards** : tableaux de bord temps réel (trésorerie, balance âgée clients/fournisseurs, chiffre d'affaires, marges, ratios), rapport financier périodique, exports PDF/Excel.
- Module **Administration & RBAC** : utilisateurs, rôles (admin, comptable, valideur, lecteur), permissions par module et par société, multi-boutique/multi-entité.
- **Mode réseau multi-utilisateurs** : l'application est nativement client-serveur — le serveur (app + PostgreSQL) s'installe sur un poste serveur (ou un PC dédié du réseau local), les autres utilisateurs s'y connectent depuis leur navigateur ; gestion de la concurrence d'accès (verrouillage optimiste des écritures en cours de saisie, verrouillage des périodes clôturées), notifications temps réel (WebSockets) pour les validations et tâches de fond.
- Module **Mises à jour** : gestionnaire de modules (installer/activer/désactiver), migrations de BD versionnées, mises à jour à chaud via pipeline.
- Module **Audit & Traçabilité** : journal d'audit inaltérable des opérations sensibles, historique des écritures, pièces justificatives.

**Exclus V1 :** paie, immobilisations avancées (AMT approfondie en V1.1 possible), facturation électronique, e-commerce, comptabilité consolidée, modules métiers non financiers.

### 3.2 Assistant IA « Kaem » (voix féminine ; ex-nom de code « Jarvis ») — texte en V1.1, voix en V2.1 ⟲ 15/10

> ⟲ 15/10 : la gouvernance, le niveau de matériel et les licences de modèles sont précisés aux §§ 17 et 19. En V1.x, l'assistant **lit, explique et prépare** ; il ne valide aucune écriture. Les **langues** sont FR, ES, PT et EN (et non FR/ES seulement).

- **STT local** (type Whisper / faster-whisper) : transcription FR/ES.
- **LLM local** (type Ollama + Llama 3.x / Qwen / Gemma) avec **RAG sur les données comptables de la société** et **function calling mappé sur l'API métier** : l'assistant appelle les workflows existants (générer balance, interroger dashboards, créer une écriture dictée avec confirmation, lancer la clôture, expliquer un solde).
- **TTS local** (type Piper) : restitution vocale FR/ES.
- Mode conversationnel vocal et textuel ; exécution des actions avec confirmation explicite pour les écritures.
- Gouvernement de l'IA : chaque action exécutée par l'assistant est journalisée dans la piste d'audit ; l'assistant n'a que les droits RBAC de l'utilisateur qui parle.

---

## 4. Analyse des contraintes

| Contrainte | Analyse critique |
|---|---|
| **Conformité réglementaire** | AUDCIF/SYSCOHADA révisé (états financiers, SMT/normal, plan comptable) + fiscalité locale (Guinée équatoriale : Ley n°1/2024, formats déclaratifs locaux à confirmer auprès de la DGI locale). ⚠️ **Risque majeur** : les formats officiels exacts de la liasse guinéen-équatorienne doivent être obtenus et maintenus par un expert-comptable validé ; prévoir un référentiel de formats versionné par pays et par exercice. |
| **Budget / délais** | Hypothèse de contrainte forte (PME/cabinet). Implications : stack open-source uniquement (PostgreSQL, backend et frontend open-source, pas de licence), architecture modulaire mais **livraison par incréments** (V1.0 cœur comptable + balance/grand livre, V1.1 liasse + dashboards, V1.2 ingestion avancée), pas de sur-ingénierie initiale. |
| **Sécurité / confidentialité** | Données financières sensibles, marché à faible confiance cloud. Implications : chiffrement au repos et en transit, RBAC, audit logs, exécution 100 % on-premise possible, 2FA, sauvegardes chiffrées automatisées. |
| **Déploiement autonome** | Mode all-in-one à la Odoo : un installateur embarquant le serveur applicatif, la BD (PostgreSQL embarqué ou Docker), le frontend et les modules. ~~Implications : conteneurisation (Docker/Podman + docker-compose) pour Linux~~. ⟲ 15/10 : **paquet autoportant** pour toutes les distributions Linux et pour Windows, pile embarquée, sans Docker requis ; l'image conteneur reste une option (§ 15). |
| **Mise à jour à chaud** | Contradiction partielle avec « installable sur PC » : sans orchestrateur, la mise à jour à chaud est limitée. Solution réaliste : mode monoposte → mise à jour « au redémarrage rapide » avec migrations transactionnelles et temps d'indisponibilité < 1 min ; mode serveur → pipeline CI/CD (blue/green ou rolling) avec **zéro interruption**. Il faut assumer cette dualité et ne pas promettre « à chaud » au sens strict en monoposte. |
| **Contexte Guinée équatoriale** | Hispanophone : i18n obligatoire dès la V1 (FR/ES), rapports dans la langue de l'administration locale ; faible bande passante : frontend léger, pas de dépendance CDN à l'exécution, mode dégradé ; matériel modeste : performance cible sur machine 8 Go RAM / CPU 4 cœurs. |
| **V2 IA locale** | Un LLM vocal local (STT+LLM+TTS) exige 8–16 Go RAM dédiés, un GPU/CPU puissant et une stack d'inférence — **incompatible avec le matériel minimal cible de la V1**. Décision d'architecture : service IA optionnel, installable uniquement sur machines capables, avec détection de capacité et dégradation en assistant textuel. |

---

## 5. Analyse de faisabilité

| Domaine | Faisabilité | Points de vigilance |
|---|---|---|
| Moteur comptable SYSCOHADA | ✅ Élevée | Le SYSCOHADA révisé est un référentiel documenté et stable depuis 2018 ; le plan comptable et les états financiers sont normés (AUDCIF, PCGO). La difficulté est la rigueur du modèle (parties doubles, lettrage, clôture, système SMT vs normal), pas la technologie. |
| Génération liasse / DSF | ✅ Élevée, avec condition | Preuve de marché : liasses Excel automatisées et logiciels dédiés existent (ex. Thalia XCOA 5, LIASSE RÉVISÉE). La génération technique (moteur de templates Excel/PDF) est maîtrisée. **Condition** : se procurer les formats officiels de chaque pays visé ; vérification par expert-comptable. |
| Architecture modulaire type Odoo | ✅ Élevée | Modèle éprouvé : noyau + modules déclaratifs (manifeste, hooks d'installation, migrations versionnées), registre de modules, RBAC. Faisable avec une stack web moderne ; attention à ne pas réimplémenter Odoo (expliquer en revue si réutiliser Odoo serait plus rentable : licence LGPL, mais couverture SYSCOHADA à développer de toute façon — le build from scratch est défendable pour un périmètre focalisé comptabilité/finance). |
| All-in-one installable | ✅ Élevée | Docker Compose / installateur desktop ; patterns éprouvés (Odoo, Firefly, etc.). |
| Mises à jour sans réinstallation | ✅ Moyenne-élevée | Faisable via migrations versionnées (type Alembic/Flyway), gestion de versions de modules, feature flags, pipeline CI/CD. En monoposte, accepter un micro-redémarrage ; en serveur, zéro-downtime atteignable. |
| Ingestion de données | ✅ Élevée | Import CSV/Excel avec mapping assisté = technique éprouvée ; la valeur est dans la **qualité des contrôles** (détecte doublons, déséquilibre, comptes inconnus, exercice erroné). |
| Dashboards & rapports | ✅ Élevée | Rien de bloquant techniquement ; attention à la fraîcheur des données (agrégats matérialisés ou requêtes temps réel — arbitrager selon la volumétrie). |
| Assistant vocal IA local (V2) | ⚠️ Moyenne | La stack existe et est éprouvée (Whisper/faster-whisper STT, Ollama + Llama 3.x/Qwen, Piper TTS, function calling). **Mais** : latence acceptable < 5 s nécessite du matériel correct (≥ 16 Go RAM, idéalement GPU) ; les modèles doivent gérer FR et ES (espagnol guinéen-équatorien) ; la fiabilité du STT sur vocabulaire comptable exige du post-traitement ; la sécurité exige un garde-fou strict (confirmation des écritures, permissions de l'utilisateur). Traitable en V2 avec un périmètre de workflows initialement restreint (consultation + génération de rapports, puis actions en écriture). |
| Conformité fiscale locale Guinée équatoriale | ⚠️ Moyenne | La loi 1/2024 est récente ; les formats déclaratifs doivent être collectés et suivis. Mitigation : référentiel de formats piloté par données + partenaire expert-comptable local. |
| Coût total | ⚠️ Point d'attention critique | Le périmètre décrit (ERP modulaire + moteur SYSCOHADA + liasses multi-pays + ingestion + dashboards + V2 IA) est un projet de 12–24 mois-homme minimum en approche classique. **Recommandation ferme : livrer par tranches V1.0 → V1.2 → V2, chaque tranche déployable et utile seule.** |

---

## 6. Architecture cible (indicative — à affiner et documenter en vues C4/ADR)

### 6.1 Vue d'ensemble

```
[ Navigateur / PWA ]
        │ HTTPS
[ Reverse Proxy (Nginx/Caddy, embarqué) ]
        │
[ Noyau applicatif (Backend monolithe modulaire) ]
   ├─ Module Core (RBAC, sociétés, i18n, audit)
   ├─ Module Comptabilité (plan OHADA, journaux, écritures, lettrage)
   ├─ Module Clôture & ÉF (balances, GL, états financiers, TFF, notes)
   ├─ Module Liasse/DSF (moteur de templates par pays)
   ├─ Module Ingestion (imports, mapping, contrôles, API)
   ├─ Module Reporting (dashboards, rapports, exports)
   ├─ Module Module Manager (installer/activer modules, migrations)
   └─ (V2) Module Assistant IA (STT / LLM local / TTS / function calling)
        │
[ PostgreSQL (embarqué dans l'installateur) ]
[ Object storage local (pièces jointes, exports) ]
```

### 6.2 Choix techniques (décision actée — à formaliser dans un ADR)

- **Stack : Python, build from scratch, framework FastAPI** (décision actée — à documenter dans un ADR avec alternatives et conséquences). Architecture explicitement structurée : **FastAPI + SQLAlchemy 2.x + Alembic** (migrations versionnées) + **Pydantic v2** (contrats de validation) + worker asynchrone (ex. ARQ/RQ sur Redis ou worker interne) pour les jobs de fond. Le noyau doit embarquer son propre **système de modules applicatifs** (registre, manifestes, hooks d'installation/mise à jour, migrations par module) — FastAPI apporte le framework web, pas cette couche. Convention de projet imposée : structure modulaire (`core/`, `modules/<module>/` avec `manifest.yaml`, `routes.py`, `models.py`, `services.py`, `migrations/`), dependency injection des services, OpenAPI généré = contrat d'API de référence.
- **BD : PostgreSQL** (transactionnel, JSONB pour templates de liasse, robuste, embarquable, MVCC adaptée au multi-utilisateurs concurrent).
- **Frontend : SPA/PWA légère** (React ou Vue + design system open-source), i18n FR/ES, aucun CDN à l'exécution, exports PDF côté serveur.
- **Génération documents : moteur de templates** (Excel via openpyxl, PDF via WeasyPrint) avec formats de liasse stockés en **données de configuration versionnées par pays**.
- ~~**Packaging : Docker Compose (Linux) + installateur Windows InnoSetup**~~ ⟲ 15/10 : **paquet autoportant** (Python relocalisable, PostgreSQL, Valkey, Caddy, interface statique) → `.run` multi-distributions + `.deb`/`.rpm` minces + image OCI optionnelle ; Windows : MSI/InnoSetup avec le même contenu (§ 15).
- ⟲ 15/10 : **Redis → Valkey** (BSD) : depuis la version 7.4, Redis est sous licences RSAL/SSPL, à éviter dans un produit fermé distribué. **Frontend** : export statique, sans Node.js à l'exécution.
- **Mises à jour : pipeline CI/CD** (build → tests → image/artefact signé → migration BD transactionnelle → déploiement rolling/blue-green). Chaque module porte son n° de version et ses migrations ; le Module Manager applique les migrations au démarrage de l'app (monoposte) ou via pipeline (serveur).
- **V2 IA :** faster-whisper (STT) + Ollama avec modèle FR/ES (ex. Llama 3.x / Qwen 2.5) + Piper (TTS) ; RAG sur les écritures/agrégats via l'API interne ; function calling strict sur catalogue de workflows ; exécution sous l'identité RBAC de l'utilisateur.

### 6.3 Architecture réseau multi-utilisateurs

Deux topologies de déploiement, mêmes binaires :

1. **Monoposte** : tout sur une machine (app + PostgreSQL embarqué + navigateur local).
2. **Serveur réseau (cas nominal)** : le serveur applicatif + PostgreSQL sont installés sur un poste dédié du réseau local (LAN). Les utilisateurs accèdent via navigateur sur `https://<serveur>:<port>` ; l'installateur configure automatiquement le pare-feu et le certificat TLS local (autorité locale générée à l'installation). Prérequis réseau documentés ; support d'un accès distant via VPN ou reverse proxy exposé (option sécurisée).

Exigences spécifiques au multi-utilisateurs :
- Concurrence : verrouillage optimiste sur les écritures en saisie (résolution propre du « déjà validé par un autre »), blocage des exercices/périodes clôturées, un seul utilisateur peut lancer une clôture à la fois (verrou applicatif + verrou BD).
- Temps réel : WebSockets/SSE pour notifications (validations, clôtures, fin de génération de liasse).
- Sauvegarde centralisée sur le serveur ; le monoposte sauvegarde localement.
- Scalabilité cible : 5–30 utilisateurs simultanés par instance (PME/cabinet), volumétrie 100 000–500 000 écritures/an — dimensionnement à valider par des tests de charge.

### 6.4 Chaîne de build et génération des installateurs (assistée par LLM)

Le développement s'appuie sur un **LLM dans la chaîne de production**, qui doit générer et maintenir **automatiquement, selon les normes professionnelles du métier**, l'outillage de livraison :

- **Chaîne de build et génération des installateurs (assistée par LLM)** : le développement s'appuie sur un LLM dans la chaîne de production, qui génère et maintient automatiquement, selon les normes professionnelles du métier, l'outillage de livraison : (installation dans Program Files, données dans ProgramData, icônes bureau + menu Démarrer, association de fichiers éventuelle, désinstallation propre, écrivain de version), configuration des icônes (`.ico` générées aux bonnes dimensions), signature optionnelle du binaire.
- **Installateur Linux** ⟲ 15/10 : **un seul contenu autoportant** compilé sur glibc 2.28, pour x86_64 et aarch64. Il est livré :
  - en script `.run` (interactif ou `--unattended` pour le SSH), qui crée les services systemd ou, à défaut, un superviseur intégré, et gère SELinux, AppArmor et le pare-feu ;
  - en enveloppes `.deb` / `.rpm` minces (dépôt signé) ;
  - en image OCI (Alpine et Kubernetes).

  ~~AppImage~~ est inadapté à un service serveur multi-utilisateurs (§ 15).
- **Vérification des prérequis avant installation** (obligatoire) : l'installateur détecte et vérifie — OS et version supportés (Windows 10/11, distributions Linux majeures), RAM minimale (8 Go serveur), espace disque, présence/absence de PostgreSQL (embarqué si absent, réutilisation avec mise en garde si présent), ports disponibles, droits administrateur ; il bloque proprement avec un message explicite ou propose une remédiation si un prérequis manque.
- Ces artefacts de build (scripts d'installateur, configs d'icônes, contrôles de prérequis) sont **versionnés, testés en CI** (installation/désinstallation automatique sur VM Windows/Linux de test) et régénérés par le LLM à chaque évolution — jamais édités à la main.

### 6.6 Stratégie d'ingestion assistée par LLM/OCR (décision d'expert, argumentée)

**Question posée : intégrer dès la V1 le LLM local pour l'ingestion OCR des données, ou se limiter à l'import Excel et à la saisie manuelle ?**

**Avis d'expert : les deux, mais séquencés — l'ingestion OCR/LLM doit être un module V1.5, pas une dépendance de la V1.**

Arguments :
1. **La V1 doit tenir sa promesse métier seule** : fiabilité comptable + liasse + dashboards. Y accoler l'OCR en bloc critique ferait dépendre la conformité fiscale (invariant du produit) d'un composant probabiliste (taux d'extraction OCR variable selon la qualité des scans, photos de téléphone, mise en page locales). Une écriture mal extraite qui passe en comptabilité = risque réglementaire direct.
2. **Le matériel cible de la V1 (8 Go RAM) ne peut pas héberger confortablement STT/OCR/LLM en production** ; l'imposer ferait exploser le prérequis système et la promesse « installable partout ».
3. **Mais techniquement, c'est faisable et c'est un différenciateur majeur** — la stack existe : OCR local (Tesseract ou PaddleOCR, ce dernier plus robuste sur factures), extraction structurée par LLM local (Ollama + modèle FR/ES avec JSON Schema strict sur les champs : date, tiers, montant HT/TVA/TT, devise, références), rattachement au plan comptable OHADA assisté. C'est le même service LLM que la V2 : **construire en V1 l'infrastructure du service LLM (module optionnel, détection de capacité, file de jobs) prépare la V2 à coût marginal.**
4. **Les documents réels fournis par le porteur du projet (jeux d'exemples de factures/relevés locaux)** seront constitués en **corpus de test d'extraction** dès la V1 : chaque format de document est annoté (valeurs attendues) et devient un test automatisé de non-régression du pipeline OCR→LLM→écriture proposée. C'est la méthode professionnelle pour fiabiliser un composant probabiliste.
5. **Règle d'or absolue : l'IA propose, l'humain dispose.** Toute écriture issue de l'ingestion assistée naît en **brouillon pré-rempli**, avec score de confiance par champ, surlignage de la zone source sur le document, et validation explicite. Jamais d'écriture automatique sans validation humaine en V1.x.

**Conséquence sur le plan** : le module « Ingestion assistée OCR/LLM » est spécifié dès la V1 (modèle de données, contrats d'API, pipeline), livré en palier V1.5 sur les formats documentaires du corpus (factures fournisseurs, relevés bancaires), puis étendu en V2 au dialogue vocal. Les documents du porteur servent de base de recette dès la spécification.

### 6.7 Principes d'architecture non négociables

1. **Immutabilité comptable** : une écriture validée n'est jamais modifiée, seulement extournée ; verrouillage d'exercice.
2. **Piste d'audit complète** : qui/quoi/quand sur chaque opération sensible (validation, clôture, export, modification de configuration fiscale).
3. **Modules activables à chaud** : activation/désactivation sans réinstallation ; les données du module désactivé sont conservées.
4. **Compatibilité ascendante N/N-1** pour chaque migration BD et chaque mise à jour de module.
5. **Zéro connaissance métier codée en dur dans les templates de pays** : tout dans des fichiers de configuration versionnés (tests de non-régression par pays).
6. **i18n dès le premier jour** : interface et documents métier FR/ES.

---

## 7. Exigences de sécurité

- Authentification : sessions signées + JWT court, 2FA (TOTP), politique de mots de passe.
- Autorisation : RBAC granulaire (rôle × module × action × société) ; principe du moindre privilège ; vérification côté serveur systématique.
- Chiffrement : TLS 1.3 en transit, chiffrement au repos (BD et pièces jointes), secrets dans un coffre local (ex. age/enclosure chiffrée).
- Sauvegardes : automatiques, chiffrées, testées (restauration vérifiée dans le pipeline).
- Cloisonnement IA (V2) : le LLM n'accède qu'aux scopes autorisés par le RBAC ; aucune écriture comptable sans confirmation utilisateur explicite ; prompts et réponses journalisées.
- Journal d'audit append-only (haché).
- Conformité : AUDCIF (conservation des pièces comptables 10 ans), loi fiscale guinéen-équatorienne n°1/2024, pratiques RGPD-like pour les données personnelles des utilisateurs.

---

## 8. Jalons recommandés

| Jalon | Contenu | Critère de sortie |
|---|---|---|
| **V1.0** | Noyau + RBAC + plan OHADA + journaux/saisie + balances + grand livre + clôture mensuelle + installateur all-in-one (Windows/Linux, vérification des prérequis) + **mode réseau multi-utilisateurs** | Saisie d'un mois réel, balance et GL corrects certifiés par un comptable ; installation < 30 min ; 5 utilisateurs concurrents sans erreur |
| **V1.1** | États financiers (normal + SMT) + liasse fiscale pays 1 (Guinée équatoriale) + pays 2 (référence) + exports Excel/PDF | Liasse validée par expert-comptable sur un cas réel |
| **V1.2** | Ingestion CSV/Excel assistée + dashboards temps réel + rapports périodiques + mises à jour à chaud (pipeline + migrations) | Import d'une balance d'ouverture complète ; mise à jour de module sans réinstallation démontrée |
| **V1.5** | **Module d'ingestion assistée OCR + LLM local** (factures fournisseurs, relevés bancaires) avec validation humaine obligatoire, entraîné sur le corpus de documents réels fournis ; infrastructure du service LLM (capacité détectée, file de jobs) posée pour la V2 | ≥ 90 % des champs clés extraits correctement sur le corpus de recette ; 0 écriture sans validation humaine |
| ~~**V2.0**~~ | ~~Assistant IA vocal local~~ — ⟲ 15/10 : remplacé par la feuille de route unifiée ci-dessous | — |

**⟲ 15/10 — Feuille de route unifiée** (elle prime sur le tableau ci-dessus) :

| Version | Contenu | Critère de sortie |
|---|---|---|
| **V1.0 Socle** | Moteur DEF extrait (§ 14) ; application web + ligne de commande ; PostgreSQL ; comptes, rôles, droits ; import balance / grand livre / écritures ; révision et contrôles ; états SN et SMT ; liasse GE + 3 pays ; paquets Windows et Linux autoportants ; licence hors ligne | 30 liasses réelles par pays au franc près ; installation sans assistance < 30 min |
| **V1.1 Assistant texte** | Palette de commandes, chat sur le catalogue de commandes, explications d'écarts, rédaction de notes ; paquet IA optionnel | Jeu d'évaluation métier ≥ 90 % ; aucune écriture par l'IA |
| **V1.2 Production** | OCR (§ 6.6), révision avancée, analyse des écritures, TVA, télédéclaration ; saisie comptable complète si le marché la demande | Corpus documentaire ≥ 90 % |
| **V2.0 SaaS** | Multi-clients (isolation au niveau des lignes, clé par client), Keycloak, facturation, hébergement régional, trajectoire ISO 27001 | Audit de sécurité externe |
| **V2.1 Voix** | STT / TTS sur le serveur, veille et alertes, application de bureau avec mot d'éveil en option | 10 parcours vocaux < 5 s |

Effort revu (hypothèse) : V1.0 à V1.2 ≈ 25 à 35 mois-homme ; V2.x ≈ 20 à 30 ; packs pays ≈ 1 à 2 mois-homme chacun, plus un expert local.

---

## 9. Risques majeurs et mitigations

| Risque | Gravité | Mitigation |
|---|---|---|
| Non-conformité des liasses aux formats officiels d'un pays | 🔴 | Référentiel de formats versionné piloté par données + validation expert-comptable par pays + tests de non-régression |
| Sous-estimation du moteur comptable (clôtures, lettrage, SMT) | 🔴 | V1.0 dédiée au cœur comptable uniquement ; recette avec un cabinet partenaire |
| Matériel insuffisant pour l'IA locale V2 et l'OCR V1.5 | 🟠 | Service IA optionnel avec détection de capacité ; dégradation en ingestion Excel/saisie manuelle (le produit reste pleinement fonctionnel sans IA) |
| Extraction OCR/LLM erronée aboutissant à une écriture fausse | 🔴 (V1.5) | Validation humaine obligatoire de toute écriture issue de l'IA ; score de confiance par champ ; surlignage source ; corpus de tests annotés sur documents réels ; jamais d'écriture automatique non validée |
| Dérive du périmètre (« refaire Odoo ») | 🟠 | Charte de périmètre stricte ; tout module non financier refusé en V1 |
| Mise à jour à chaud impossible en monoposte | 🟠 | Communication claire : micro-redémarrage en monoposte, zéro-downtime en serveur |
| Formats fiscaux changeants (loi 1/2024 récente) | 🟠 | Veille réglementaire + templates éditables sans redéploiement |
| Sécurité d'une app installée chez des PME (updates non appliqués) | 🟠 | Vérification de version au démarrage + auto-mise à jour optionnelle signée |

---

## 10. Directive — production du dossier de documentation projet

### 10.1 Démarche exigée

1. **Analyse critique** du présent document : identifier zones d'ombre, contradictions, hypothèses implicites et risques non traités ; challenger tout choix non justifié.
2. **Interrogation proactive** : poser toute question nécessaire pour mieux cerner le sujet (formats officiels de liasse, taux de TVA/retenues locaux, volumétries, matériel cible, priorités de modules…) — ne jamais combler un silence par une supposition présentée comme une exigence.
3. **Reformulation** : reformuler les points ambigus, mal ordonnés ou incomplets, en signalant explicitement chaque reformulation.
4. **Vocabulaire** : tout terme métier du référentiel OHADA (AUDCIF, SMT, TFF, lettrage, DSF, PCGO…) doit figurer dans un **glossaire** intégré à la documentation.

### 10.2 Livrables attendus — la documentation projet complète

Chaque document doit être maintenu dans le dépôt (versionné avec le code) et **traçable** (matrice PRD → spécifications → tests) :

| Livrable | Contenu attendu |
|---|---|
| **PRD** (Product Requirements Document) | Vision, personas, user stories par module avec critères d'acceptation, KPI, priorisation MoSCoW |
| **Spécifications fonctionnelles** | Description détaillée du comportement attendu de chaque module fonctionnel (saisie, clôture, liasse, ingestion, dashboards, RBAC…) : règles de gestion numérotées, cas nominaux et cas d'erreur, maquettes d'écrans (wireframes), contraintes métier SYSCOHADA appliquées à chaque écran/processus |
| **Spécifications techniques** | Modèle de données SQL complet, contrats d'API OpenAPI, spécifications de sécurité, formats de configuration (liasses, taxes), système de modules et migrations |
| **Manuels utilisateur** | Guides FR/ES par profil (comptable, valideur, dirigeant, administrateur) : installation, première prise en main, saisie, clôture, génération de liasse, lecture des dashboards, dépannage — accessibles depuis le site web de documentation |
| **BPMN** | Processus métier modélisés : ingestion (Excel/CSV puis OCR assisté), saisie → validation → clôture, génération de liasse/DSF, mise à jour applicative, installation et vérification des prérequis |
| **Cas d'utilisation** | Use cases textuels structurés + diagrammes, par acteur (admin, comptable, valideur, lecteur, assistant IA en V2) |
| **ADR** (Architecture Decision Records) | Une fiche par décision structurante avec contexte, alternatives, décision, conséquences : FastAPI, PostgreSQL, build from scratch vs Odoo, système de modules, IA locale on-premise, validation humaine obligatoire des écritures IA, packaging InnoSetup, etc. |
| **Documents Product / Domain / Architecture** | Vision produit et roadmap ; modèle de domaine (DDD, bornes contextes : comptabilité, ingestion, reporting, administration) ; vues C4 (contexte, conteneurs, composants, code) |
| **Plans d'implémentation** | Découpage en sprints aligné sur V1.0 → V2.0, stratégie de tests (dont tests de conformité comptable), plan de déploiement (installateurs, CI/CD), backlog priorisé |
| **TDR** (termes de référence) ⟲ 15/10 | **Nouveau.** Le document contractuel court (≤ 10 pages) qu'on remet à un financeur, un partenaire, un sous-traitant ou un client grand compte : contexte, objectifs, périmètre et hors périmètre, livrables, calendrier, organisation et gouvernance, critères de réception, hypothèses et risques. Il est **dérivé** de ce document (§§ 0 à 2, 8 et 9) et du PRD, et reste aligné sur eux par renvoi, jamais par recopie |
| **AppFlow** (parcours dans l'application) ⟲ 15/10 | **Nouveau.** Les enchaînements d'écrans par profil : de la connexion à la liasse validée, avec les embranchements (erreur d'import, question bloquante, session expirée, rôle insuffisant) et le retour à la page et à la ligne d'origine. Diagrammes Mermaid. **À distinguer** des BPMN, qui décrivent le processus métier, et des cas d'utilisation, qui décrivent le but d'un acteur : l'AppFlow décrit **l'écran suivant** |
| **UX/UI** ⟲ 15/10 | **Existait en partie** (règles du § 12, livrables du § 12.8), mais sans dossier ni document propre. Il devient un livrable à part entière : système de design (tokens, composants, états), wireframes, maquettes des 6 à 8 écrans critiques, règles d'accessibilité **mesurées** et parcours vocal de Kaem (états : écoute, réflexion, réponse, coupure du micro) |
| **Backend schema** ⟲ 15/10 | **Existait sous un autre nom** (« modèle de données SQL complet » des spécifications techniques). Il en sort comme document autonome et **régénéré depuis le code** : diagramme entité-relation, tables, contraintes, index, politiques de sécurité au niveau des lignes (SaaS), schéma des packs pays, migrations. Il n'est jamais rédigé à la main en parallèle du code |

### 10.3 Organisation du dossier projet et de la documentation

Toute la documentation vit dans un dossier **`documentation/`** à la racine du dépôt, créé et organisé par le générateur en sous-dossiers cohérents. Structure cible (à ajuster si nécessaire, mais le site web doit toujours regrouper l'intégralité) :

```
documentation/
├─ tdr/                     # Termes de référence (⟲ 15/10)
├─ prd/                     # PRD, vision produit, personas
├─ appflow/                 # Parcours écran par écran, par profil (⟲ 15/10)
├─ ux-ui/                   # Système de design, wireframes, maquettes (⟲ 15/10)
├─ specs-fonctionnelles/     # Specs fonctionnelles par module + wireframes
├─ specs-techniques/        # Specs techniques, OpenAPI, sécurité, format des packs pays
│   └─ schema-backend/      # Schéma de la base, régénéré depuis le code (⟲ 15/10)
├─ adr/                     # Architecture Decision Records (numérotés)
├─ bpmn/                    # Diagrammes BPMN (sources as-code)
├─ use-cases/               # Cas d'utilisation et diagrammes
├─ architecture/            # Vues C4, modèle de domaine (DDD)
├─ plans-implementation/    # Roadmap, sprints, stratégie de tests, déploiement
├─ manuels-utilisateur/     # Manuels FR/ES par profil
├─ template/                # Modèles et fichiers d'exemple à analyser
│   └─ corpus-ingestion/    # Documents réels fournis (factures, relevés,
│                           # fichiers Excel/CSV) + annotations attendues
└─ site/                    # Configuration du site web (MkDocs/Docusaurus)
```

- Le dossier **`template/`** contient les **modèles de fichiers et documents d'exemple** fournis par le porteur du projet : le générateur doit les **analyser** (types de documents, structures de fichiers Excel/CSV, formats de factures et relevés) et s'en servir comme base de conception des formats d'import, du mapping et du corpus de recette de l'ingestion OCR (§6.6). Chaque modèle analysé fait l'objet d'une fiche descriptive dans la documentation.
- Le dossier **`site/`** porte la configuration du **site web statique qui agrège toute la documentation** — toutes les sections ci-dessus, manuels utilisateur compris — avec navigation par section, recherche plein texte et versionning visibles. Le site est généré depuis les sources Markdown et déployable en local ou en ligne.
- Les manuels utilisateur suivent la même chaîne : sources Markdown dans `manuels-utilisateur/`, rendus dans le même site web, avec captures d'écran stockées en assets vectoriels ou PNG optimisés.

### 10.4 Formats de sortie

- Chaque document produit en **Markdown versionné dans le dépôt** (la documentation vit avec le code, sinon elle meurt à la première itération).
- Rendu **web navigable** sous forme de site statique (ex. MkDocs Material ou Docusaurus) généré depuis ces sources.
- **Schémas as-code vectoriels et régénérables** : diagrammes (C4, ER/BDD, BPMN, séquences, états) en Mermaid ou PlantUML — jamais d'images bitmap figées.
- **Iconographie vectorielle monographique cohérente** : un seul style graphique (une seule bibliothèque d'icônes vectorielles, ex. Lucide/Tabler, une seule palette) pour toute la documentation et l'interface du produit.
- Navigation, recherche plein texte et versionning visibles sur le site web généré.

### 10.5 Questions bloquantes à poser avant d'inventer

Notamment : les formats officiels de liasse à cibler (Guinée équatoriale en priorité), les taux de TVA/retentes locaux applicables, le matériel cible de la V2, les volumétries réelles attendues, et le détail du corpus de documents réels fournis par le porteur (factures, relevés) pour la recette de l'ingestion OCR.

Intégrer tous les points de la section 11 (monnaie XAF, migration de données, jobs de fond, tests de conformité comptable, canal de mise à jour, etc.) aux spécifications et au plan d'implémentation.

---

## 11. Points complémentaires identifiés par l'expert (non cités initialement — à traiter)

Ces dimensions, absentes de l'énoncé initial, sont pourtant indispensables à la viabilité du produit. Elles doivent être intégrées aux spécifications et plans d'implémentation.

### 11.1 Monnaie, localisation et fiscalité appliquée
- **Monnaie** : la Guinée équatoriale est membre de la CEMAC → monnaie **franc CFA (XAF)**. Le moteur doit gérer : devise unique par société (V1), multi-devises avec écarts de conversion (V1.2+) car AUDCIF l'exige dès lors qu'il y a des opérations en devises ; symboles, séparateurs décimaux et formats de date localisés (FR/ES).
- **Taxes** : TVA CEMAC (taux et mécanismes locaux à confirmer : loi 1/2024), retenues à la source, retenues sur salaires si paie ultérieure — paramétrage par pays, tables de taux versionnées par période (un taux de TVA change : la table historisée garantit la cohérence des écritures passées).
- **Exercice comptable** : année civile obligatoire (AUDCIF), avec périodes mensuelles verrouillables.

### 11.2 Migration des données existantes (critical pour l'adoption)
Les clients existants ont déjà une comptabilité (Excel, Sage, logiciels locaux). Prévoir un **module de migration** : import de balance d'ouverture, import des écritures de l'exercice en cours, mapping depuis les plans de comptes les plus courants de la zone. Sans cela, le coût de bascule tue l'adoption.

### 11.3 Gestion documentaire et pièces justificatives
- Pièces jointes aux écritures (PDF/photos), quotas de stockage, recherche.
- **Ingestion assistée OCR + LLM local** : traitée en §6.6 — spécifiée en V1, livrée en V1.5 sur corpus de documents réels fournis par le porteur (factures, relevés), avec validation humaine systématique ; socle technique du dialogue vocal de la V2.

### 11.4 Observabilité et exploitation
- Logs applicatifs structurés (niveaux, rotation), supervision de l'état du serveur (mémoire, BD, jobs de génération), métriques d'usage local (opt-in uniquement, respect de la confidentialité).
- **Jobs de fond** : génération de liasses et d'exports lourds en tâches asynchrones (file de jobs, ex. Celery/RQ ou worker interne) avec suivi de progression dans l'UI — indispensable en multi-utilisateurs.

### 11.5 Qualité et processus de développement (avec LLM dans la boucle)
- **Tests** : pyramid stricte — unitaires (moteur comptable : parties doubles, lettrage, clôture), intégration (API, migrations), **tests de conformité comptable** sur jeux d'écritures de référence dont les soldes attendus sont validés par un expert-comptable (c'est le garde-fou absolu du produit), tests end-to-end de l'installateur sur VM Windows/Linux.
- **Revue du code généré par LLM** : tout code généré passe la CI (lint, tests, revue humaine) ; le LLM est un accélérateur, pas un oracle — responsabilité et validation humaines explicites.
- **Documentation** : doc développeur (architecture, ajout d'un module, ajout d'un format de liasse), doc utilisateur FR/ES, doc d'installation/de mise à jour.
- ~~**Licence open-source du produit** : à décider (ex. LGPL)~~ ⟲ 15/10 : **licence propriétaire** (A8). Les packs pays sont la valeur du produit ; sous LGPL, ils seraient copiables. Modules partenaires sous contrat, entiercement du code pour les grands comptes (§ 18).

### 11.6 Cycle de vie produit et support
- **Canal de mise à jour** : serveur de versions (RSS/HTTP + signature des paquets), notification in-app, application automatique optionnelle ; gestion des cas « plusieurs versions de retard » (migrations cumulables).
- **Support et entraide** : guide de diagnostic embarqué (export de logs anonymisé), procédure de restauration testée.
- **Formation / onboarding** : données de démonstration intégrées (société fictive avec un exercice complet), parcours guidé de première saisie — le public cible (PME peu outillées) en a besoin.
- **Modèle économique** : produit + services (paramétrage des liasses, migration de données, formation), éventuellement marketplace de modules. À arbitrer car cela influence la licence et l'architecture des modules.

### 11.7 Continuité et reprise d'activité
- Sauvegardes automatiques chiffrées (rétention paramétrable, 10 ans de conservation des pièces comptables selon AUDCIF), restauration guidée, procédure documentée de migration serveur → nouveau matériel.
- Résilience locale : coupures électriques fréquentes en zone cible → PostgreSQL configuré pour reprise sur crash, avertissement sur l'utilisation onduleur, état « écritures en cours » non perdu (sauvegarde automatique des brouillons).

### 11.8 Accessibilité et UX
- UI simple pour profils non comptables (dirigeants) ; accessibilité de base (contrastes, navigation clavier) ; fonctionnement sur connexions lentes (pas de bundle JS démesuré, assets locaux).
- **Impression** : les états (balances, GL, liasse) doivent être imprimables proprement (formats A4/A3, en-têtes, pagination) — besoin réel majeur des cabinets.

## 12. Règles de design (design system « Facil Gestion »)

Le design n'est pas une couche cosmétique : pour un outil comptable utilisé quotidiennement par des profils variés (comptable expert, dirigeant non financier, administrateur) dans un contexte de connexions lentes et de matériel modeste, il est un facteur d'adoption direct. Un **design system** formalisé est un livrable à part entière, versionné dans `documentation/` et consommé par le frontend (tokens de design + composants).

### 12.1 Principes directeurs

1. **Densité maîtrisée** : la comptabilité est un métier de données (grilles, balances, listes d'écritures). L'UI doit afficher beaucoup d'information sans étouffer — tableaux denses mais respirants, alignements rigoureux des chiffres (tabulaires, justification à droite des montants, séparateurs de milliers, devise visible), hiérarchie typographique stricte. Interdiction des grandes cartes décoratives au détriment de la densité utile.
2. **Confiance et sobriété** : palette sobre et professionnelle (1 couleur primaire, neutres chauds, sémantique dédiée : vert = validé/crédit, rouge = alerte/débit ou erreur, ambre = brouillon/en attente — la sémantique comptable prime sur l'esthétique). Pas d'animations gratuites, pas d'illustrations superflues. Chaque élément visuel doit justifier sa présence.
3. **Le statut est toujours visible** : chaque objet (écriture, pièce, période, exercise, liasse) porte un statut explicite (brouillon / validé / verrouillé / en anomalie) rendu visuellement — badge de statut systématique, jamais seulement par position ni par menu. L'immutabilité comptable (§6.7) doit se *voir*.
4. **L'IA propose, l'interface montre la preuve** : pour l'ingestion OCR/LLM, l'écran de validation affiche côte à côte le document source (zone extraite surlignée) et les champs pré-remplis, avec score de confiance par champ — le design rend l'IA auditable, pas magique.
5. **Progressivité des profils** : une même donnée, plusieurs lectures — vue « comptable » (dense, technique) et vue « dirigeant » (dashboards, synthèse) ; pas de sur-simplification qui masque la rigueur, pas de technicité imposée au non-comptable.
6. **Accessibilité et contexte local** : contrastes AA minimum (WCAG 2.1), navigation clavier complète, tailles de police ≥ 14 px, aucune couleur porteuse d'information seule ; lisible sur écrans modestes (1366×768) et en plein soleil (matériels d'entrée de gamme).

### 12.2 Design tokens (règles de base à affiner en atelier)

- **Couleurs** : la couleur primaire du produit **dérive du logo de l'application** (fourni par le porteur) — la charte graphique entière (primaire, déclinaisons de teintes, accents) est **déduite automatiquement du logo** et non choisie arbitrairement ; le logo et l'icône fournis sont la source de vérité de l'identité visuelle. Neutres en échelle documentée (50→900), 3 sémantiques (succès/alerte/erreur) + états comptables (brouillon/validé/verrouillé) ; dark mode non prioritaire en V1 (contexte bureautique) mais tokens conçus pour le permettre plus tard.
- **Typographie** : une seule famille sans-serif open-source pour l'UI (ex. Inter) ; **police tabulaire (chiffres à chasse fixe) obligatoire pour tous les montants et colonnes numériques** — règle non négociable en comptabilité ; hiérarchie limitée à 4 niveaux.
- **Espacement et grille** : échelle d'espacement unique (base 4 ou 8 px), grilles de tableaux à colonnes fixes réglables par l'utilisateur (largeurs mémorisées).
- **Iconographie** : vectorielle monographique, une seule bibliothèque (ex. Lucide), une seule épaisseur de trait, jamais de mélange de styles — cohérence avec la documentation (§10.4).
- **Composants** : design system basé sur une bibliothèque open-source accessible (ex. shadcn/ui, Radix) personnalisée par tokens, jamais de composants fait main quand un composant accessible existe ; chaque composant documenté (usage, états, limites) dans le site de documentation.
- **Mouvement** : transitions seulement pour informer (apparition de résultats, changement de statut), 150–250 ms maximum ; jamais de mouvement décoratif.

### 12.3 Patterns d'interaction imposés

- **Tableaux = composant central** : tri multi-colonnes, filtres combinables, recherche globale, export contextuel (Excel/PDF) toujours accessible, totalisation visible (pied de tableau), pagination ou défilement virtuel selon volumétrie.
- **Saisie comptable clavier-first** : les comptables saisissent vite au clavier — navigation inter-champs fluide (Tab/Shift+Tab), recherche de compte par frappe directe (préfixe + libellé), raccourcis documentés (Ctrl+S valider, Ctrl+N nouvelle écriture), aucun clic obligatoire pour un flux de saisie courant.
- **Validation en deux temps partout** : brouillon → validation explicite (jamais d'enregistrement implicite d'une écriture) ; actions irréversibles (clôture, verrouillage) derrière une confirmation claire récapitulant les conséquences ; extourne documentée comme action de premier ordre, pas un contournement.
- **Messages d'anomalie pédagogiques** : une erreur comptable (écriture déséquilibrée, compte inconnu, période verrouillée) doit expliquer *pourquoi* et proposer la correction, jamais un code technique brut.
- **Tâches longues visibles** : génération de liasse, imports, OCR → barre de progression + notification de fin (WebSockets, §6.4), l'utilisateur n'attend jamais devant un écran figé sans information.
- **Vide et premiers pas** : chaque écran vide propose l'action suivante (« Importez votre balance d'ouverture », « Créez votre première société ») ; parcours guidé et société de démonstration intégrés (§11.6).
- **Imprimé pensé dès le design** : les états (balance, GL, liasse) sont conçus pour l'écran ET l'impression A4 (en-têtes, pagination, totaux reportés) — besoin critique des cabinets.

### 12.4 Comportements de layout et de navigation (règles détaillées)

- **Sidebar repliable avec réajustement fluide** : la sidebar principale se replie/déplie ; **lorsqu'elle se rabaisse, le contenu principal se réajuste automatiquement pour occuper l'espace libéré, et lorsqu'elle se rouvre, il se réajuste à nouveau sur l'espace restant** — transition douce, sans saut visuel ni rechargement, les tableaux et graphiques se redimensionnant en conséquence (le redimensionnement des tableaux préserve les largeurs de colonnes définies par l'utilisateur là où c'est possible).
- **Logo vs icône** : **l'icône de l'application s'affiche lorsque la sidebar est repliée, le logo complet (horizontal) lorsqu'elle est dépliée** ; les deux assets sont fournis par le porteur et versionnés dans le design system.
- **Préférence mémorisée** : l'état replié/déplié est persisté par utilisateur ; sur petits écrans (< 1024 px), la sidebar devient un panneau overlay (ouvre/se ferme par bouton et par touche Échap) et ne réduit jamais l'espace de travail.
- **Menus organisés en groupes repliables** : les menus sont regroupés par domaine fonctionnel (Saisie, Clôture, États financiers, Liasse, Reporting, Administration…) ; **chaque groupe est repliable et ses sous-menus ne s'affichent que lorsque le groupe est ouvert** (accordéon, un groupe recommandé ouvert à la fois pour éviter le scroll infini) ; en sidebar repliée, seuls les groupes (icônes) sont visibles et le survol/clic ouvre un flyout listant les sous-menus.
- **Indicateurs d'état dans la navigation** : badge de compteur sur les menus concernés (ex. nombre d'écritures en brouillon, anomalies d'import, jobs en cours) ; le groupe actif et l'élément actif sont visuellement identifiables en permanence.
- **Fil d'Ariane et contexte multi-sociétés** : sélecteur de société et d'exercice toujours visible (barre supérieure), verrouillage de période signalé globalement (bandeau discret quand la période consultée est clôturée).
- **Responsive** : le layout cible d'abord le desktop (poste de travail) ; en dessous de 1024 px, bascule en layout tablette (sidebar overlay) ; usage mobile limité en V1 à la consultation (dashboards, soldes) — la saisie comptable dense reste desktop.
- **Largeur de page** : le contenu principal a une largeur maximale lisible pour les formulaires (colonne centrée) mais les tableaux et dashboards occupent toute la largeur disponible.

### 12.5 Règles de composants (formes, états, comportements)

- **Formes** : un seul rayon d'angle pour toute l'application (tokens, ex. 8 px pour conteneurs, 6 px pour boutons/inputs — valeurs finales déduites de la charte) ; boutons à une seule hauteur standard (+ variante compacte pour les barres d'outils de tableaux) ; densité de formulaire réglable (standard / compact pour les utilisateurs avancés).
- **Tableaux — pagination** : pagination explicite par défaut (choix de taille de page : 25/50/100, mémorisée par utilisateur et par écran) avec décompte total ; **défilement virtuel** (sans pagination) pour les très grands volumes (grand livre complet) ; l'en-tête de tableau reste figé (sticky) au défilement ; les totaux sont rapportés en pied de tableau et **restent visibles au défilement** (pied sticky) ; colonnes : réordonnancement, masquage, largeurs mémorisées ; sélection multiple avec barre d'actions contextuelles (valider, extourner, exporter) ; export de la sélection ou du filtre courant, jamais seulement de la page visible sauf mention explicite.
- **Tableaux — états** : skeleton de chargement (pas de spinner plein écran), état vide guidant, message d'erreur dans la grille (pas de toast seul), tri et filtres signalés visuellement (indicateurs + bouton « réinitialiser les filtres »).
- **Formulaires** : validation en ligne au champ (au blur) résumée en haut du formulaire à la soumission ; jamais de perte de saisie (brouillons auto-sauvegardés, §11.7) ; champs montants avec formatage à la saisie (espaces de milliers, devise alignée) et refus silencieux des caractères invalides ; date-picker FR/ES selon la locale.
- **Modales vs pages** : une modale uniquement pour les actions courtes et contextuelles (confirmation, sélection d'un tiers) ; tout le reste (édition d'écriture, paramétrage) ouvre une page/onglet dédié — pas de formulaires complexes en modale.
- **Notifications/toasts** : dur, discret, actionnable quand c'est pertinent (« Voir le résultat » après génération d'une liasse) ; jamais utilisé pour les erreurs bloquantes qui exigent une décision.
- **États de composants systématiques** : chaque composant documenté avec ses 5 états (défaut, survol, focus, actif/désactivé, erreur) — règle de complétude du design system.
- **Barre de commandes des écrans clés** : actions primaires à droite (Valider), actions destructrices séparées et jamais adjacentes à l'action primaire (Extourner/Supprimer) ; raccourcis clavier affichés en info-bulles.

### 12.6 Composants métier spécifiques (le cœur de la valeur produit)

Ce sont les composants qui n'existent dans aucune bibliothèque générique et doivent être **conçus sur mesure** — ils concentrent l'effort de design :

- **Arbre du plan comptable OHADA** : vue hiérarchique repliable par classe → compte → sous-compte (mêmes règles d'accordéon que la sidebar) ; recherche instantanée qui **ouvre automatiquement les branches** contenant un résultat et surligne les correspondances (préfixe + libellé) ; badges de type (compte de bilan/résultat, mouvements, lettrable) ; glisser-déposer interdit (l'arbre est normé) ; colonnes soldes débiteur/crédit alignées en tabulaire ; action « voir les écritures de ce compte » en un clic depuis n'importe quel nœud.
- **Grille de saisie d'écriture par lots** : saisie de type tableur (lignes débit/crédit, ajout de ligne au clavier par Entrée, suppression par raccourci), **solde de la pièce affiché en temps réel** (badge débiteur/crédit équilibré → vert), autocomplétion compte + tiers, contrepartie suggérée selon le journal, pièce déséquilibrée **ne peut pas être validée** (bouton désactivé + message explicite) ; brouillons auto-sauvegardés ligne à ligne (résistance aux coupures, §11.7).
- **Écran de validation OCR/LLM (V1.5)** : disposition tri-partite — document source (zone extraite surlignée, zoomable), formulaire pré-rempli, liste des champs par score de confiance ; chaque champ cliquable **surligne sa zone source** et réciproquement ; champs à faible confiance visuellement signalés et regroupés en tête ; compte OHADA proposé par l'IA mais modifiable, la modification est apprise (retour d'expérience utilisateur conservé) ; barre latérale de file « 12 pièces à traiter » avec navigation clavier (pièce suivante/précédente).
- **Sélecteur de période/exercice** : composant récurrent partout (balances, GL, dashboards) — un seul et même composant, avec presets (mois courant, trimestre, exercice), indication claire des **périodes verrouillées** (grisées, non sélectionnables), et rappel permanent de l'exercice actif ; les rapports affichent toujours en en-tête la période exacte et la société concernées.
- **Génération de liasse — écran de pilotage** : checklist visuelle des étapes (contrôles préalables → cohérence bilan/résultat → génération → export), chaque contrôle affiché avec son statut et sa capacité à être **exploré** (ex. « 3 écritures non lettrées — voir »), jamais un message global bloquant sans détail ; export Excel et PDF avec aperçu avant téléchargement ; verrouillage de la liasse documenté dans la piste d'audit.
- **Journal d'audit (UI)** : consultation filtrable par utilisateur/action/objet/date, différences avant/après lisibles (pas de JSON brut pour les non-techniciens), export pour l'expert-comptable ; entrée d'audit **non modifiable ni supprimable** depuis l'UI — c'est visible et assumé.
- **Assistant d'import (wizard)** : progression en étapes (déposer le fichier → mapper les colonnes → prévisualisation des N premières lignes avec détection d'anomalies colorées → importer) ; chaque étape sauvegardable ; **rapport d'anomalies téléchargeable** avec numéros de lignes et motifs ; les mappings de colonnes mémorisés par source de fichier pour ne refaire le mapping qu'une fois.
- **Dashboard dirigeant** : cartes KPI (solde trésorerie, créances/dettes, résultat) avec **sparkline et évolution vs période précédente** ; hiérarchie de lecture gauche→droite (liquide → activity → performance) ; chaque chiffre cliquable → détail jusqu'à la ligne d'écriture (drill-down intégral, promesse clé) ; les graphiques n'affichent **jamais de 3D, jamais de double axe, jamais de camembert au-delà de 5 segments** — règles de data-visualisation strictes (barres pour comparaisons, lignes pour séries temporelles, tooltip précis avec valeurs exactes).
- **Commande globale (Ctrl+K)** : palette de commandes permettant d'atteindre n'importe quel écran, société, compte ou action (« générer balance mars ») — accélérateur décisif pour les utilisateurs intensifs et **point d'ancrage du dialogue vocal V2** (les intents vocaux s'appuient sur le même catalogue de commandes).
- **Assistant vocal (V2) — design spécifique** : indicateur d'état discret et omniprésent (écoutant / traite / parle), transcription affichée en direct, toute action proposée par l'IA **présentée à l'écran pour confirmation** (jamais d'exécution d'écriture en aveugle), voix et language FR/ES suivant la locale ; en cas de doute l'assistant répond à l'écran et vocalement avec le détail.

### 12.7 États globaux et parcours transverses

- **Onboarding guidé** : première connexion → checklist de démarrage (créer/importer une société, importer la balance d'ouverture, saisir une première écriture, générer une balance) ; la société de démonstration (§11.6) est accessible en un clic depuis cette checklist ; la checklist disparaît une fois terminée, revivable depuis l'aide.
- **Aide contextuelle** : icône d'aide par écran ouvrant la section correspondante du **manuel utilisateur** (le site web de documentation, §10.3) — un seul endroit de vérité pour l'aide ; raccourci clavier `?` ouvrant la liste des raccourcis.
- **États d'application** : page d'erreur avec action de reprise (pas d'erreur technique brute), page de maintenance lors des mises à jour serveur, bandeau discret de perte de connexion réseau (reconnexion automatique, saisies locales préservées).
- **Sélecteur de société multi-onglets** : l'utilisateur peut garder ouverts plusieurs contextes (société A / société B) en onglets dans l'application, chaque onglet conservant son contexte de période — cas d'usage réel des cabinets multi-clients.
- **i18n visuel** : tous les libellés conçus pour FR et ES (pas de libellés français surdimensionnés), formats de nombre/date pilotés par la locale, montants toujours accompagnés du code devise dans les exports (XAF).


### 12.8 Livrables de design attendus

- **Charte graphique déclinée depuis le logo** : le générateur doit extraire/déduire du logo fourni (couleurs dominantes, teintes, éventuellement la forme pour le rayon d'angle et le style graphique) la charte complète — tokens primaires, déclinaisons, accents — et la documenter ; le logo (sidebar dépliée) et l'icône (sidebar repliée, favicon, installateur, icônes bureau) sont fournis par le porteur et intégrés au design system.
- Fichier de tokens de design (JSON/CSS variables) versionné au dépôt ;
- Bibliothèque de composants documentée (Storybook ou équivalent, rendu dans le site web de documentation) ;
- Wireframes des écrans clés (saisie d'écriture, validation OCR, balance, dashboard dirigeant, génération de liasse, installateur) produits avec les spécifications fonctionnelles ;
- Maquettes haute fidélité limitées aux 6–8 écrans critiques ; le reste dérive des composants du design system — pas de maquette pixel par pixel de chaque écran (coût inutile).
- Prototype interactif du seul comportement de navigation (sidebar repliable + groupes de menus) pour validation ergonomique avant le développement du shell applicatif.

## 13. Références (sources consultées)

- OHADA — AUDCIF / SYSCOHADA révisé (adoption 26/01/2017 ; application 01/01/2018 comptes personnels, 01/01/2019 consolidés) ; les 17 États membres incluent la Guinée équatoriale.
- Direction Générale des Impôts (Cameroun) — Déclarations Statistiques et Fiscales (DSF) selon le SYSCOHADA révisé ; suppression du système allégé, maintien du système normal et du SMT.
- Ley n°1/2024 du 19/11/2024 — nouveau Code Général des Impôts de la République de Guinée équatoriale (aligné CEMAC/OHADA/FMI).
- Produits de référence du marché (liasses Excel automatisées OHADA, Thalia XCOA, LIASSE RÉVISÉE) — preuve de faisabilité du montage de liasse automatisé.
- Stack IA locale éprouvée pour la V2 : Whisper/faster-whisper (STT), Ollama + Llama 3.x/Qwen/Gemma (LLM local), Piper (TTS) — assistants vocaux 100 % offline documentés.
- ⟲ 15/10 : `documentation/analyse/analyse-critique-projet-jarvis.md` (analyse croisée) et `documentation/analyse/strategie-produit-v1-v2.md` (note stratégique).

---

## 14. Actif existant à réutiliser ⟲ 15/10

Le plugin `compta-ohada/` (v0.10.0) est un **actif prouvé**. Il est extrait en bibliothèque Python : on ne le réécrit pas.

| Brique | Fichier(s) | Ce qu'elle apporte | Preuve |
|---|---|---|---|
| Lecture des balances | `lib/detection_balance.py` | Balances de 1 à 8 colonnes, avec ou sans en-tête ; ambiguïtés signalées | 18 tests |
| Grand livre et balance reconstituée | `lib/grand_livre.py` | Grand livre seul → balance contrôlée ; à-nouveaux et comptes centralisés | Dossier pilote : 349 comptes équilibrés |
| Liasse SN | `def_sn.py`, `templates/syscohada_sn_modele.xlsx` | Formulaire officiel, élagage adaptatif, contrôle « note = poste » | Référence conforme, 61 contrôles, 0 écart |
| Liasse GE | `def_modele.py`, `def_ge.py`, gabarit vierge | Format GE, FR = ES | 3 952 cellules identiques |
| Fiscalité GE | `lib/fiscal_ge.py`, `lib/tf345_ge.py`, `parametres_fiscaux_ge.json` | IS, minimum, TVA, salaires, tiers ; chaque taux cité avec son article | 48 et 39 tests |
| Rendu sans Excel | évaluateur de formules, PDF natifs | Production sur serveur sans Office | 691/691 identiques à Excel |
| Confidentialité | `serveur/confidentialite.py` | Pseudonymes, montants masqués, contrôle avant envoi, journal | 31 tests et 12 contre-épreuves |
| Formulaire local | `serveur/formulaire.py` | Jeton, CSP, deux horloges de session | 44 tests |
| Runtime embarqué | `tools/construire_runtime.py` | Python autonome sous Windows : le **modèle du paquet Linux** | Extension rejouée 14/14 |

**Méthode à reprendre telle quelle** :
- chaque garde est validée par une **contre-épreuve** (une mutation, la garde doit rougir) ;
- les tests de référence sur données réelles restent **hors du produit** ;
- aucun nom de client dans le produit (garde d'empaquetage).

## 15. Distribution : Windows, Linux toutes distributions, SSH ⟲ 15/10

**Exigence** : chaque version embarque sa pile et ses outils, et **aucune dépendance n'est demandée au système** au-delà du noyau, de la glibc et, en option, du pilote GPU.

| Élément | Choix | Raison |
|---|---|---|
| Base de compatibilité | glibc 2.28 (norme `manylinux_2_28`) | Debian 10+, Ubuntu 20.04+, RHEL / Alma / Rocky 8+, SUSE 15+, Fedora |
| Architectures | x86_64, aarch64 | Serveurs ARM, petits serveurs de cabinet |
| Python | Python autonome relocalisable (python-build-standalone) | Même principe que le runtime Windows actuel |
| Base de données | Binaires PostgreSQL relocalisables, `initdb` à l'installation | Pas de paquet système, pas de conflit avec un PostgreSQL existant |
| File d'attente et cache | Valkey (BSD), ou worker interne en édition Standard | Licence ; légèreté |
| Serveur web | Caddy (binaire unique, TLS automatique ou autorité locale) | Une seule pièce, sans configuration manuelle |
| Interface | Fichiers statiques précompilés | Pas de Node.js à l'exécution |
| Services | Unités systemd ; superviseur intégré quand systemd est absent | Conteneurs, WSL, distributions minimales |
| Installeur | `.run` autoextractible et signé : interactif ou `--unattended --config fichier` ; mise à jour avec retour arrière | Mode SSH sans écran |
| Enveloppes | `.deb` / `.rpm` minces (dépôt signé), image OCI, MSI / InnoSetup sous Windows | **Un contenu, plusieurs enveloppes** |
| Mode SSH | Ligne de commande complète, interface texte, tunnel `ssh -L` pour l'interface web | Administration sans port public |
| Contrôles d'installation | Version de glibc, architecture, RAM, disque, ports, SELinux / AppArmor, pare-feu, pilote GPU (si paquet IA) | Bloquer proprement plutôt qu'échouer en silence |

**Ce qui ne s'embarque pas, et pourquoi** : les pilotes GPU (ils font partie du système) et le noyau. Docker Desktop est payant pour les entreprises au-delà de certains seuils : il n'est jamais imposé.

**Matrice de recette** : installation, mise à jour et désinstallation automatisées en CI sur Debian 12, Ubuntu 22.04 et 24.04, Rocky 9, openSUSE 15, Fedora, Windows 10 et 11, en x86_64 et aarch64.

## 16. Couverture : les 17 États du SYSCOHADA ⟲ 15/10

| Zone | États | Monnaie | Langue de la liasse |
|---|---|---|---|
| UEMOA | Bénin, Burkina Faso, Côte d'Ivoire, Guinée-Bissau, Mali, Niger, Sénégal, Togo | XOF | FR ; PT (Guinée-Bissau) |
| CEMAC | Cameroun, Centrafrique, Congo, Gabon, Guinée équatoriale, Tchad | XAF | FR ; ES (GE) ; EN (Cameroun, en option) |
| Hors zones | Comores, Guinée, RD Congo | KMF, GNF, CDF | FR |

- **Pack pays** = jeu de données **versionné, signé et daté par exercice**. Il contient :
  - le gabarit de liasse et les correspondances lignes → comptes ;
  - les paramètres fiscaux, **chaque taux avec son article** ;
  - les libellés officiels ;
  - les contrôles propres au pays ;
  - le **système normal et le SMT**.
- **Validation d'un pack** : un expert-comptable local et au moins 10 liasses réelles déposées, reproduites avec des écarts tous expliqués (la méthode du dossier pilote GE).
- **Ordre proposé** (décision ouverte) :
  1. GE (fait) ;
  2. Cameroun, Côte d'Ivoire, Sénégal ;
  3. Gabon, Congo ;
  4. le reste de l'UEMOA ;
  5. RDC, Guinée, Comores.
- **État du corpus au 15/10/2026** (`datas/liasses-officielles/SOURCES.md`, 33 fichiers publics) :
  - **Cameroun** : SN officiel en Excel, annexes SN et SMT en PDF, 4 guides et une DSF réelle (SIC). Il manque le SMT en Excel.
  - **Sénégal** : SN et SMT officiels en Excel (plateforme SEN ETAFI), avec un exemple réel. Il reste à savoir laquelle des deux variantes SMT est en vigueur.
  - **Togo** : SN 2023 et SMT 2019 officiels en Excel.
  - **Côte d'Ivoire** : exemples seulement (liasse SODECI 2019 complète) ; **aucun modèle officiel révisé trouvé**.
  - **Gabon** : DSF en PDF seulement.
  - **Congo, Bénin, Mali** : sites injoignables, à retenter.
  - **Niger, Tchad, RDC** : rien trouvé.
  - **Centrafrique, Guinée-Bissau, Comores** : non cherchés en profondeur.

  **Conséquence** : l'ordre de travail suit les modèles disponibles. Le Cameroun et le Sénégal passent avant la Côte d'Ivoire. Le modèle officiel ivoirien sera demandé par un expert-comptable local ou à la DGI.
- **Langues de l'interface** : FR, ES, PT, EN. Les libellés de liasse viennent de **dictionnaires officiels**, jamais d'une traduction automatique.
- **Monnaies** : le XOF et le XAF sont à parité fixe avec l'euro (et donc entre eux), mais **ne sont pas interchangeables** : le XOF n'a pas cours en zone CEMAC, ni le XAF en UEMOA. GNF, KMF et CDF sont des monnaies distinctes ; en RDC, il faut prévoir des opérations en USD (écarts de conversion selon l'AUDCIF).

## 17. Intelligence artificielle locale : paquet, matériel, licences ⟲ 15/10

| Niveau | Matériel indicatif | Modèle indicatif | Usage |
|---|---|---|---|
| Sans IA (Standard) | 8 Go de RAM, 4 cœurs | — | Tout le produit sauf l'assistant |
| IA légère | 16 Go de RAM, processeur seul | 3 à 4 milliards de paramètres, quantifié en 4 bits | Palette de commandes, explications courtes ; réponse de 5 à 20 s |
| IA complète | 32 Go de RAM, GPU de 8 à 12 Go | 7 à 14 milliards, quantifié en 4 bits | Chat, rédaction de notes, OCR assisté ; réponse < 5 s |
| Serveur / SaaS | GPU partagé | vLLM, plusieurs modèles | Voix, multi-utilisateurs |

- **Paquet IA séparé** (≈ 6 à 10 Go), signé, téléchargeable ou livré sur support hors ligne. Il contient llama.cpp, les modèles, et en V2.1 Whisper et Piper. L'installeur de base reste ≈ 300 à 600 Mo.
- **Détection de capacité** à l'installation ; à défaut de GPU, bascule sur le processeur, annoncée à l'utilisateur.
- **Les temps de réponse sont promis par niveau, et par écrit.**
- **Registre des licences** (`licences-modeles.json`) : pour chaque modèle et chaque voix, la licence, l'usage commercial autorisé, l'attribution exigée, la source et l'empreinte. La CI refuse un modèle non enregistré.
  - À vérifier à chaque version : la licence communautaire Llama (conditions et attribution), les conditions d'usage Gemma, les licences propres à certaines tailles de Qwen, Mistral sous Apache 2.0, Whisper sous MIT, et **les voix Piper licence par licence**.
- **Qualité** : avant de choisir un modèle, construire un jeu d'évaluation métier FR/ES/PT (comptes SYSCOHADA, questions de révision, rédaction de notes). L'IA ne calcule jamais : elle appelle le moteur et **cite** les textes.

### 17.1 Pile retenue pour Kaem — poste sans GPU, 16 Go de RAM (décisions D4 et D5, 15/10/2026)

| Rôle | Choix par défaut | Licence | Taille (indicative) | Concurrents du banc |
|---|---|---|---|---|
| Compréhension et réponses (LLM) | **Gemma 4 E4B-it**, quantifié en 4 bits (GGUF), via llama.cpp | Apache 2.0 | ≈ 4 à 5 Go sur disque et en mémoire | Qwen3.5 4B (Apache 2.0), Phi-4-mini (MIT), Ministral 3 3B (licence à vérifier) |
| Reconnaissance vocale | **Gemma 4 E4B lui-même** : le modèle accepte l'audio en entrée (reconnaissance de la parole intégrée), **sans second modèle** | Apache 2.0 | inclus | Whisper small ou distil-whisper (MIT), si le banc montre une meilleure précision sur le vocabulaire comptable |
| Voix de Kaem (féminine) | **Kokoro** (82 M de paramètres, rapide sur processeur), voix féminines FR, ES et PT | Apache 2.0 | ≈ 0,3 Go | Piper, licence vérifiée **voix par voix** |
| Embeddings (recherche dans les textes) | Modèle multilingue léger | à enregistrer au registre | ≈ 0,3 à 0,5 Go | — |

**Pourquoi Gemma 4 E4B est un bon choix par défaut** : licence Apache 2.0 (usage commercial libre) ; modèle conçu pour les portables ; plus de 140 langues ; appels d'outils natifs ; contexte de 128 000 jetons ; entrée texte, image et audio. Un seul modèle couvre donc **le chat, la lecture des pièces scannées (OCR assisté) et l'écoute**. Il faut seulement y ajouter la voix de synthèse.

**Ce qu'il ne fera pas bien, et comment on le compense** :
- **Vitesse sur processeur seul** : il faut s'attendre à quelques jetons par seconde (à **mesurer** sur le banc). Une phrase courte prend quelques secondes ; un long commentaire de note, plus de 30 s.
  - Kaem répond donc en **flux continu** : la voix commence dès la première phrase, sans attendre la fin.
  - Les rédactions longues (notes, rapport) deviennent des **tâches de fond** avec une notification à la fin.
- **Mémoire** : le système, PostgreSQL, l'application, le navigateur et le modèle tiennent dans 16 Go, mais sans marge.
  - Le modèle se charge à la première demande et se **libère après 10 min d'inactivité** (réglable).
  - L'installeur refuse le paquet IA sous 16 Go et le dit.
- **Exactitude métier** : le modèle n'est jamais la source d'un chiffre. Il appelle le moteur (catalogue de commandes) et cite le texte de loi ou le compte qu'il utilise.

**Téléchargement** (≈ 5 à 6 Go au total) :
- reprise après coupure ;
- empreinte SHA-256 et signature vérifiées avant activation ;
- **paquet hors ligne** (clé USB) pour les sites à faible débit ;
- l'application reste **pleinement utilisable sans IA** pendant et après le téléchargement.

**Banc d'évaluation Kaem** : à faire **avant** de figer le modèle.
- **Matériel de test** : 3 PC de référence sans GPU, 16 Go de RAM : un processeur Intel ou AMD de bas de gamme récent, un milieu de gamme, et un ancien de 5 ans.
- **Mesures, en FR, ES et PT** :
  - latence avant le premier mot ;
  - jetons par seconde ;
  - taux de réussite des appels d'outils ;
  - précision de la reconnaissance vocale sur 100 phrases comptables ;
  - qualité des notes rédigées, évaluée par un expert.
- **Règle** : le modèle par défaut est celui qui passe **tous** les seuils sur le PC le plus faible. À défaut, Gemma 4 **E2B** devient le niveau de repli.

*Sources consultées le 15/10/2026 : fiche du modèle [google/gemma-4-E4B-it](https://huggingface.co/google/gemma-4-E4B-it) (Apache 2.0, 4,5 milliards de paramètres effectifs, entrée audio) ; [Google AI Edge — Gemma 4](https://developers.google.com/edge/litert-lm/models/gemma-4) ; [Kokoro TTS](https://localaimaster.com/blog/kokoro-tts-local-setup). Toutes les vitesses restent à mesurer ; aucune n'est promise avant le banc.*

## 18. Marque, propriété intellectuelle, contrats ⟲ 15/10

- **Nom** :
  - « Jarvis » est un nom de code, **jamais une marque commerciale** : personnage et marque de l'univers Marvel / Disney, nom déjà très utilisé, d'où un risque d'opposition et une faible distinctivité ;
  - « Facil » étant un mot courant, préférer un signe **composé ou figuratif**.
- **Dépôt** :
  1. recherche d'antériorité ;
  2. **OAPI** (Accord de Bangui : un dépôt couvre ses 17 États membres, qui recoupent largement l'OHADA) ;
  3. **dépôt national en RD Congo**, qui n'est pas membre de l'OAPI ;
  4. système de Madrid si l'on vise l'international ;
  5. noms de domaine associés.
- **Logiciel** :
  - preuve de date (dépôt probatoire du code et de la documentation, horodatage) ;
  - cession des droits par tous les contributeurs ;
  - entiercement du code pour les grands comptes ;
  - protection technique : licence signée hors ligne, packs signés.
- **Documents contractuels**, à rédiger avec un juriste avant la première vente :
  - contrat de licence (édition installée) ;
  - conditions générales et contrat SaaS avec engagement de service (V2) ;
  - accord de traitement des données ;
  - politique de confidentialité ;
  - conditions d'usage de l'IA ;
  - **clause de responsabilité** : outil d'assistance, l'expert-comptable valide et signe, pas de conseil fiscal, plafond de responsabilité ;
  - politique de support et de fin de vie des versions.
- **Licences des composants** : inventaire des dépendances (SBOM) généré en CI. Pas d'AGPL, de SSPL ni de RSAL dans le produit distribué :
  - Valkey plutôt que Redis ≥ 7.4 ;
  - pas de MinIO (AGPL) : système de fichiers ou alternative Apache ;
  - vérification de Grafana et de LiteLLM Enterprise.
- **Données personnelles** : lois nationales sur la protection des données (Côte d'Ivoire 2013, Sénégal 2008, Cameroun 2024, Gabon, etc.), avec déclarations auprès des autorités, localisation des données en SaaS et encadrement des transferts vers un LLM hébergé.
- *Points à faire valider par un juriste ; rien ici n'est un avis juridique.*

## 19. `jarvis_finance.md` : ce qui est repris, ce qui est écarté ⟲ 15/10

- **Repris** (gouvernance) :
  - pare-feu d'outils ;
  - passerelle de confidentialité et coffre de jetons (déjà codés dans `compta-ohada/serveur/confidentialite.py`) ;
  - politique de données par champ ;
  - approbation humaine par action ;
  - journal d'audit chaîné et preuves ;
  - RAG filtré par les droits ;
  - séparation des instructions et des données (défense contre l'injection) ;
  - jobs idempotents ;
  - « le LLM ne calcule pas ».
- **Corrigé** :
  - Keycloak seulement en serveur et en SaaS (trop lourd pour un poste de 8 Go) ;
  - les permissions métier vivent dans l'application, Keycloak ne porte que l'identité ;
  - routage vers un LLM hébergé seulement sur décision du client et après la passerelle ;
  - aucun framework d'agents en V1 : un catalogue de commandes déterministe et des sorties structurées.
- **Écarté ou différé** : le « toujours en éveil » en V1, le multi-agents, l'apprentissage des préférences, Docker Desktop.
- **Défauts du document à ne pas propager** :
  - aucun contenu SYSCOHADA ni pays, exemples en euros ;
  - trois feuilles de route non réconciliées ;
  - choix de pile contradictoires (authentification, framework d'agents) ;
  - aucun dimensionnement matériel ;
  - aucune licence ni aucun contrat ;
  - sources non vérifiées.

  Il sert de **catalogue d'idées de gouvernance**, pas de spécification.