<div align="center">

<img src="docs/assets/logo.png" alt="Facil" height="72">

# Facil Finance

**De la balance à la liasse fiscale validée — SYSCOHADA révisé, 17 États de l'OHADA.**
Calculée sur le poste ou le serveur du client, prouvée chiffre par chiffre, validée par une personne nommée.

[![CI](https://github.com/KouemouSah/Facil_Finance/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/KouemouSah/Facil_Finance/actions/workflows/ci.yml)
[![Documentation](https://github.com/KouemouSah/Facil_Finance/actions/workflows/documentation.yml/badge.svg?branch=develop)](https://kouemousah.github.io/Facil_Finance/)
[![CodeQL](https://github.com/KouemouSah/Facil_Finance/actions/workflows/securite.yml/badge.svg?branch=develop)](https://github.com/KouemouSah/Facil_Finance/actions/workflows/securite.yml)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)
![SYSCOHADA](https://img.shields.io/badge/SYSCOHADA-r%C3%A9vis%C3%A9-468C00?style=flat-square)
![Licence](https://img.shields.io/badge/licence-propri%C3%A9taire-555?style=flat-square)

[**Portail et documentation**](https://kouemousah.github.io/Facil_Finance/) · [Architecture](https://kouemousah.github.io/Facil_Finance/documentation/architecture.html) · [Plan de sprints](https://kouemousah.github.io/Facil_Finance/documentation/plans/sprints.html) · [Tâches](https://github.com/KouemouSah/Facil_Finance/issues) · [Jalons](https://github.com/KouemouSah/Facil_Finance/milestones)

</div>

---

## Sommaire

1. [Ce qu'est Facil Finance](#1-ce-quest-facil-finance)
2. [Où en est le projet](#2-où-en-est-le-projet)
3. [Architecture cible](#3-architecture-cible)
4. [Carte du dépôt](#4-carte-du-dépôt)
5. [Démarrer](#5-démarrer)
6. [Reprendre la construction avec Claude Code web](#6-reprendre-la-construction-avec-claude-code-web)
7. [Chaîne d'intégration et de livraison](#7-chaîne-dintégration-et-de-livraison)
8. [Sécurité et confidentialité](#8-sécurité-et-confidentialité)
9. [Documentation](#9-documentation)
10. [Contribuer, licence](#10-contribuer-licence)

---

## 1. Ce qu'est Facil Finance

Une **plateforme de production financière** pour les cabinets d'expertise comptable et les services comptables des entreprises de l'espace OHADA. Elle lit la balance et le grand livre tels qu'ils sortent du logiciel comptable, produit la **liasse SYSCOHADA** (états, notes, tableaux fiscaux du pays), pose **une seule fois** les questions qu'aucun fichier ne tranche, puis fait **valider** la version définitive par une personne nommée. Rien n'est écrasé, chaque chiffre est relié à ses comptes.

| Principe | Ce qu'il impose |
|---|---|
| **Automatique d'abord, questions ensuite** | La liasse complète est calculée avant la première question |
| **Aucune règle de pays dans le moteur** | Taux, libellés, lignes et contrôles viennent d'un **pack pays** signé et daté |
| **Une liasse se prouve** | Chaque poste relié à ses comptes ; « calculé » ≠ « déclaré » ≠ « prouvé » |
| **Rien n'est écrasé** | Écritures importées, versions de liasse, réponses : horodatées, conservées |
| **Les données restent chez le client** | Serveur local ou réseau ; l'IA (Kaem) est locale ; aucune sortie sans passerelle |
| **L'IA ne calcule ni ne valide** | Kaem explique et prépare ; le moteur calcule ; une personne valide |

**Facil DEF**, déjà livré, en est le premier produit : une extension Claude Desktop qui produit la DSF de Guinée équatoriale (`plugin/compta-ohada`, v0.13.0). Son moteur est la référence métier que Facil Finance réutilise ([ADR 0005](docs/adr/0005-reutiliser-le-moteur-def.md)).

> **Vocabulaire.** En français : **DSF**, Déclaration statistique et fiscale. En espagnol : **DEF**, Declaración Estadística y Fiscal. La marque « Facil DEF » reste telle quelle.

## 2. Où en est le projet

| Livrable | État |
|---|---|
| Cadrage : TDR, PRD (exigences `EX-…`), 14 ADR, registre des risques | fait |
| **Sprint 1 — Fondations** : format du pack pays (validation, signature Ed25519, couches), packs OHADA, CEMAC, Cameroun (préversion), Guinée équatoriale ; noyau du moteur extrait ; IS de la SIC 2025 reproduit au franc près | fait |
| **Facil DEF 0.13.0** : DSF de Guinée équatoriale, lecture **OCR locale** des DSF scannées prouvée par les formules SYSCOHADA, **analyse financière pluriannuelle**, formulaire local, passerelle de confidentialité | livré |
| **Sprint 2 — V1.0 Socle** : base, API, droits, sessions, interface, installeurs, pack Sénégal | [à faire](https://github.com/KouemouSah/Facil_Finance/milestone/1) |

<!-- gantt:debut -->
```mermaid
%%{init: {"gantt": {"barHeight": 26, "barGap": 6, "fontSize": 13, "sectionFontSize": 13, "leftPadding": 170, "topPadding": 40, "gridLineStartPadding": 40, "numberSectionStyles": 2}, "themeVariables": {"taskBkgColor": "#7CC242", "taskBorderColor": "#397004", "taskTextColor": "#1d3502", "taskTextLightColor": "#1d3502", "taskTextOutsideColor": "#1d3502", "activeTaskBkgColor": "#498E03", "activeTaskBorderColor": "#2b5503", "doneTaskBkgColor": "#c9c9c9", "doneTaskBorderColor": "#8a8a8a", "critBkgColor": "#e0a030", "critBorderColor": "#9a5b00", "sectionBkgColor": "#eef6e6", "altSectionBkgColor": "#ffffff", "gridColor": "#dddddd", "todayLineColor": "#c62828", "fontSize": "13px"}}}%%
gantt
    title Facil Finance — livraison le 30/11/2026
    dateFormat YYYY-MM-DD
    axisFormat %d/%m
    tickInterval 1week

    section Cadrage
    Documentation (TDR, PRD, ADR, plans) :done, s0a, 2026-10-15, 2026-10-17
    section Sprint 1 · Fondations
    Format du pack, pack Cameroun (étalon) :done, s1a, 2026-10-19, 2026-10-23
    Moteur extrait, GE convertie au franc près :done, s1b, 2026-10-19, 2026-10-23
    section Sprint 2 · V1.0
    Base, API, droits, sessions, interface :active, s2a, 2026-10-26, 2026-10-30
    Installeurs Windows et Linux, pack Sénégal :s2b, 2026-10-26, 2026-10-30
    Code V1.0 terminé :milestone, m_v10, 2026-10-30, 0d
    section Sprint 3 · V1.1 et V1.2
    Kaem texte, catalogue, paquet IA :s3a, 2026-11-02, 2026-11-06
    Saisie, lettrage, clôtures, TVA, OCR :s3b, 2026-11-02, 2026-11-13
    Code V1.1 terminé :milestone, m_v11, 2026-11-06, 0d
    Code V1.2 terminé :milestone, m_v12, 2026-11-13, 0d
    section Sprint 4 · V2.0 et V2.1
    SaaS — isolation, Keycloak, facturation :s4a, 2026-11-09, 2026-11-20
    Voix, écoute, veille :s4b, 2026-11-16, 2026-11-20
    Code V2.0 et V2.1 terminé :milestone, m_v20, 2026-11-20, 0d
    section Durcissement et recette
    Sécurité, performance, matrice d'installation :crit, s5a, 2026-11-16, 2026-11-20
    Recette métier avec l'expert et les pilotes :crit, recette, 2026-11-23, 2026-11-27
    Livraison :milestone, m_livraison, 2026-11-30, 0d
```
<!-- gantt:fin -->

Bloc généré depuis la source unique des dates : [`docs/plans/calendrier.yml`](docs/plans/calendrier.yml).

## 3. Architecture cible

Choix arrêtés dans les [ADR](docs/adr/index.md) ; détail dans [l'architecture](docs/architecture.md).

### 3.1 Contexte

```mermaid
flowchart LR
    compta["Comptable / chef de mission<br/>(navigateur)"]
    admin["Administrateur<br/>(navigateur, SSH)"]
    expert["Expert-comptable<br/>valideur"]
    ff(["<b>Facil Finance</b><br/>serveur local ou réseau"])
    logiciel["Logiciel comptable du client<br/>(Sage, Excel, autre)"]
    dgi["Administration fiscale"]
    maj["Canal de mises à jour Facil<br/>application, packs pays, modèles IA<br/>(signés)"]

    logiciel -- "balance, grand livre, écritures" --> ff
    compta -- "importe, répond, valide" --> ff
    admin -- "installe, sauvegarde, met à jour" --> ff
    ff -- "liasse PDF / Excel" --> expert
    expert -- "liasse signée" --> dgi
    maj -. "téléchargements signés<br/>(hors ligne possible)" .-> ff
```

Aucun service d'IA externe : **Kaem** tourne en local ([ADR 0007](docs/adr/0007-kaem-ia-locale.md)).

### 3.2 Conteneurs

```mermaid
flowchart TB
    subgraph poste["Navigateur"]
        ui["Interface web<br/>application monopage<br/>(fichiers statiques)"]
    end
    subgraph serveur["Serveur Facil Finance — un seul contenu autoportant (Linux glibc 2.28+, Windows)"]
        proxy["Caddy<br/>TLS, fichiers statiques"]
        api["API métier<br/>FastAPI · SQLAlchemy 2 · Pydantic 2<br/>Python embarqué"]
        moteur["Moteur de production<br/><code>facil_moteur</code><br/>(aucune règle de pays)"]
        packs[("Packs pays<br/>signés Ed25519, datés")]
        worker["Travailleurs de fond<br/>(générations longues, OCR)"]
        kaem["Kaem<br/>llama.cpp + Gemma 4 E4B<br/>(paquet optionnel)"]
        passerelle["Passerelle de<br/>confidentialité"]
        db[("PostgreSQL embarqué<br/>grand livre immuable, versions,<br/>droits (RLS), audit")]
        file[("Valkey<br/>file de tâches")]
        fichiers[("Fichiers<br/>sources, liasses, sauvegardes")]
    end
    ui -- HTTPS --> proxy --> api
    api --> moteur --> packs
    api --> db
    api --> file --> worker --> moteur
    worker --> fichiers
    api -- "commandes du catalogue" --> kaem
    kaem -- "appels d'outils (lecture seule)" --> api
    api -. "seule sortie possible" .-> passerelle
```

| Brique | Choix | Écarté, et pourquoi | ADR |
|---|---|---|---|
| API | FastAPI, SQLAlchemy 2, Alembic, Pydantic 2 | — (le moteur est en Python) | [0009](docs/adr/0009-pile-serveur.md) |
| Base | PostgreSQL embarqué | SQLite : ni multi-utilisateurs, ni sécurité au niveau des lignes | [0009](docs/adr/0009-pile-serveur.md) |
| File | Valkey (BSD) | Redis ≥ 7.4 (RSAL/SSPL, incompatible produit fermé) | [0009](docs/adr/0009-pile-serveur.md) |
| Frontal | Caddy | Nginx : TLS manuel | [0009](docs/adr/0009-pile-serveur.md) |
| Interface | Application monopage exportée en statique | Rendu côté serveur : Node.js à l'exécution | [0009](docs/adr/0009-pile-serveur.md) |
| Identité | Intégrée (NIST 800-63B, TOTP) ; Keycloak / OIDC en SaaS | Keycloak partout : 0,5 à 1 Go de mémoire | [0010](docs/adr/0010-identite-selon-edition.md) |
| IA | Gemma 4 E4B local, llama.cpp, sur processeur, 16 Go | IA hébergée : données hors du pays | [0007](docs/adr/0007-kaem-ia-locale.md) |
| Distribution | Contenu autoportant : `.run`, `.deb`, `.rpm`, MSI | Docker obligatoire | [0003](docs/adr/0003-distribution-autoportante.md) |

### 3.3 Packs pays : tout ce qui dépend du pays

```mermaid
flowchart LR
    subgraph couches["Résolution d'un pack (date de clôture)"]
        ohada["<b>ohada/2017.1</b><br/>plan de comptes, états,<br/>correspondances, contrôles"]
        zone["<b>cemac/2025.1</b> · uemoa/…<br/>règles de zone"]
        pays["<b>CM/2025.1</b> · <b>GQ/2025.1</b> · SN/…<br/>gabarit officiel, fiscalité,<br/>libellés, mentions"]
    end
    ohada --> zone --> pays --> resolu(["Pack résolu<br/>en vigueur à la clôture"])
    resolu --> moteur["Moteur"]
    sig["Signature Ed25519<br/>+ article et source<br/>pour chaque taux"] -. "vérifiée au chargement" .-> resolu
```

Format : [spécification du pack pays](docs/specs/pack-pays.md) ([ADR 0006](docs/adr/0006-packs-pays-declaratifs.md)). Un taux sans article est refusé par la validation.

### 3.4 Flux : de la balance à la liasse validée

```mermaid
sequenceDiagram
    autonumber
    actor C as Comptable
    participant API as API
    participant M as Moteur
    participant P as Pack pays
    participant DB as Base
    actor V as Valideur
    C->>API: dépose balance et/ou grand livre
    API->>M: reconnaître (par le contenu) et contrôler
    M-->>API: format, équilibre, ambiguïtés
    API->>DB: écritures et soldes (immuables, horodatés, empreinte de la source)
    C->>API: produire la liasse (pays, exercice)
    API->>P: pack en vigueur à la date de clôture
    API->>M: agréger → états → notes → tableaux fiscaux → contrôles
    M-->>API: liasse PROJET + couverture + questions
    API->>DB: version n (jamais écrasée)
    C->>API: répond (une seule fois)
    API->>M: régénérer (idempotent)
    V->>API: valider (nommément)
    API->>DB: version DÉFINITIVE, signée, horodatée, tracée à l'audit
```

### 3.5 Modèle de données cible

Premier livrable du sprint 2 ([EX-IMP-4, EX-PLAT-2](docs/prd.md)) ; ce schéma est le **point de départ**, il s'arrête dans une migration Alembic relue.

```mermaid
erDiagram
    ORGANISATION ||--o{ ENTITE : "regroupe (cabinet ou client SaaS)"
    ENTITE ||--o{ EXERCICE : "déclare"
    EXERCICE ||--o{ IMPORT : "reçoit"
    IMPORT ||--o{ ECRITURE : "apporte (immuable)"
    IMPORT ||--o{ SOLDE : "apporte (immuable)"
    EXERCICE ||--o{ LIASSE : "produit"
    PACK ||--o{ LIASSE : "règle"
    LIASSE ||--o{ VERSION_LIASSE : "versionne (jamais écrasée)"
    VERSION_LIASSE ||--o{ QUESTION : "pose"
    QUESTION ||--o{ REPONSE : "reçoit (historisée)"
    UTILISATEUR ||--o{ AFFECTATION : "reçoit"
    ROLE ||--o{ AFFECTATION : "définit"
    ENTITE ||--o{ AFFECTATION : "porte"
    UTILISATEUR ||--o{ SESSION : "ouvre"
    UTILISATEUR ||--o{ JOURNAL_AUDIT : "agit"

    IMPORT { uuid id PK
             text empreinte_sha256 "source, unique par exercice"
             text format_detecte
             timestamptz recu_le }
    ECRITURE { bigint id PK
               uuid import_id FK
               date date_piece
               text compte
               numeric debit
               numeric credit
               text piece }
    VERSION_LIASSE { uuid id PK
                     int numero "1, 2, 3…"
                     text statut "projet | definitive"
                     jsonb empreintes_sources
                     uuid validee_par FK
                     timestamptz validee_le }
    REPONSE { uuid id PK
              jsonb valeur
              text origine "saisie | reprise | proposition"
              uuid auteur FK
              timestamptz horodatage }
    PACK { text pays
           text version
           date en_vigueur_du
           text signature_ed25519 }
    JOURNAL_AUDIT { bigint id PK
                    text action
                    text objet
                    text empreinte_precedente "chaînage"
                    timestamptz horodatage }
    SESSION { uuid id PK
              timestamptz derniere_activite "inactivité 15 min"
              timestamptz ouverte_le "durée absolue 12 h" }
```

Règles portées **par la base**, pas seulement par l'écran : sécurité au niveau des lignes par organisation (prépare le SaaS), écritures et versions définitives en ajout seul (déclencheurs qui refusent `UPDATE` et `DELETE`), journal d'audit chaîné.

### 3.6 Déploiement : un seul logiciel, trois usages

```mermaid
flowchart LR
    subgraph mono["Monoposte"]
        n1["Navigateur"] --> s1["Service Facil Finance<br/>écoute 127.0.0.1"]
    end
    subgraph lan["Réseau du cabinet"]
        n2["Postes (navigateur)"] --> s2["Serveur Facil Finance<br/>Linux ou Windows"]
        adm["Admin"] -- "tunnel SSH / CLI" --> s2
    end
    subgraph saas["V2 — SaaS"]
        n3["Clients"] --> lb["Frontal régional"] --> s3["Instances Facil Finance<br/>isolation par lignes, Keycloak"]
    end
```

Toujours en mode serveur, même seul ([ADR 0002](docs/adr/0002-toujours-en-mode-serveur.md)) : on change l'adresse d'écoute, on ne réinstalle rien.

### 3.7 Kaem et la frontière de confidentialité

```mermaid
flowchart LR
    u["Utilisateur"] -- "question, voix" --> kaem["Kaem (local)<br/>Gemma 4 E4B"]
    kaem -- "commande du catalogue<br/>(lecture)" --> api["API"]
    api --> moteur["Moteur<br/>seul à calculer"]
    api -- "données réelles" --> kaem
    kaem -- "explique, prépare<br/>ne valide jamais" --> u
    api -. "sortie externe activée<br/>par le client seulement" .-> gw["Passerelle<br/>pseudonymes, montants masqués,<br/>journal, échec fermé"]
    gw -.-> ext["Service externe"]
```

## 4. Carte du dépôt

```text
Facil_Finance/
├── facil_moteur/            moteur : noyau (source unique), format et résolution des packs, adaptateurs
├── packs/                   packs pays : ohada/2017.1, cemac/2025.1, CM/2025.1, GQ/2025.1
├── outils/                  verifier_tout, facil_pack, garde_confidentialite, purger_classeur, portail, conversions
├── tests/                   tests du moteur et des packs (une contre-épreuve par garde)
├── plugin/compta-ohada/     Facil DEF : extension Claude Desktop (skills, serveur MCP, formulaire, OCR, tests)
│                            — runtime/ et dist/ (extension construite) ne sont pas versionnés
├── docs/                    documentation projet (MkDocs) : cadrage, PRD, architecture, ADR, specs, plans
├── manuel/                  manuel, présentation, flyer de Facil DEF (FR « DSF », ES « DEF ») : sources et PDF
├── travaux/                 relevés et recherches de travail (données publiées seulement)
├── .github/                 CI/CD, formulaires de tickets, CODEOWNERS, Dependabot
├── .claude/settings.json    préparation automatique des sessions Claude Code web
└── CLAUDE.md                consignes pour Claude Code (poste et web)
```

Catalogue détaillé : [Catalogue des modules](https://kouemousah.github.io/Facil_Finance/documentation/catalogue-modules.html).

## 5. Démarrer

Prérequis : Python 3.13, git. Jamais de `pip install` dans le Python du système.

```bash
git clone https://github.com/KouemouSah/Facil_Finance.git && cd Facil_Finance
python -m venv .venv && . .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements-dev.txt
python outils/installer_crochets.py                   # crochet pre-commit (vérification + confidentialité)

python outils/verifier_tout.py                        # packs + tests + parité noyau ↔ plugin
python outils/facil_pack.py resoudre CM 2025-12-31 --atelier

# Facil DEF (plugin)
pip install -r plugin/compta-ohada/serveur/requirements.txt
pip install --no-deps --ignore-requires-python rapidocr_onnxruntime==1.4.4     # OCR, version figée
python plugin/compta-ohada/tools/gardes_ci.py

# Documentation
pip install -r docs/requirements.txt
python docs/outils/construire_site.py                 # site dans docs/site/
```

L'extension `.mcpb` se construit sous Windows (`plugin/compta-ohada/tools/construire_extension.py`) ; elle n'est **pas** publiée dans ce dépôt.

## 6. Reprendre la construction avec Claude Code web

Le dépôt est conçu pour qu'une session [Claude Code sur le web](https://claude.ai/code) reprenne le travail sans rien redécouvrir.

1. Ouvrir **claude.ai/code**, choisir le dépôt `KouemouSah/Facil_Finance`, branche `develop`.
2. Au démarrage, `.claude/settings.json` lance [`outils/preparer_environnement.sh`](outils/preparer_environnement.sh) : environnement virtuel, dépendances du moteur, du plugin et de la documentation.
3. Claude lit [`CLAUDE.md`](CLAUDE.md) (règles, carte, commandes), puis la section **Reprise** de [`docs/plans/sprints.md`](docs/plans/sprints.md).
4. Demander, par exemple : *« Prends le ticket #… du jalon Sprint 2, fais-le jusqu'à la clôture, ouvre une demande de fusion vers develop. »*
5. La CI rejoue tout ; la demande de fusion porte la preuve en exécution et ce qui n'a pas été vérifié.

```mermaid
flowchart LR
    t["Ticket du sprint<br/>(jalon, exigence EX-…)"] --> s["Session Claude Code web<br/>branche claude/…"]
    s --> p["preparer_environnement.sh"]
    p --> c["CLAUDE.md + Reprise"]
    c --> d["Code + gardes + falsification"]
    d --> pr["Demande de fusion → develop"]
    pr --> ci{"CI verte ?"}
    ci -- non --> d
    ci -- oui --> r["Relecture humaine (CODEOWNERS)"] --> m["Fusion, Pages republiées"]
```

Limites déclarées en session web : pas d'Excel ni de Windows (rendu PDF natif, `FACIL_PDF=natif`), pas de construction de l'extension `.mcpb`, et **la garde nominative de confidentialité ne joue qu'avec la clé** (secret de CI) : en session web, c'est la CI qui la tient.

## 7. Chaîne d'intégration et de livraison

```mermaid
flowchart LR
    push["push / demande de fusion"] --> conf["Confidentialité<br/>empreintes HMAC, classeurs purgés,<br/>gitleaks"]
    push --> lint["Lint<br/>ruff"]
    push --> mot["Moteur et packs<br/>Ubuntu + Windows"]
    push --> plug["Facil DEF<br/>gardes du plugin<br/>Windows + Ubuntu"]
    push --> codeql["CodeQL<br/>Python, JavaScript"]
    develop["push sur develop"] --> doc["Documentation<br/>MkDocs strict, parité du menu,<br/>hors ligne, garde de confidentialité"]
    doc --> pages["GitHub Pages<br/>portail + documentation + manuels"]
```

| Workflow | Déclencheurs | Rôle |
|---|---|---|
| [`ci.yml`](.github/workflows/ci.yml) | push, demande de fusion | confidentialité, lint, moteur (Ubuntu, Windows), plugin (Windows, Ubuntu) |
| [`documentation.yml`](.github/workflows/documentation.yml) | push sur `develop`, chaque lundi, manuel | construit et publie le portail et la documentation |
| [`securite.yml`](.github/workflows/securite.yml) | push, demande de fusion, chaque lundi | CodeQL |
| [`dependabot.yml`](.github/dependabot.yml) | chaque semaine | actions et dépendances Python (l'OCR reste figé) |

Branches : `develop` (par défaut, intégration) et `main` (versions `vX.Y.Z`), toutes deux protégées. Détail : [CONTRIBUTING](CONTRIBUTING.md).

## 8. Sécurité et confidentialité

- **Aucune donnée de client dans ce dépôt public.** La liste des noms confidentiels reste hors dépôt ; seules ses **empreintes HMAC** y sont, inexploitables sans la clé (secret de CI). Classeurs purgés de leurs liaisons externes et de leurs auteurs ([`outils/purger_classeur.py`](outils/purger_classeur.py)).
- **Packs signés** Ed25519 ; la clé privée n'est jamais dans le dépôt.
- **Facil DEF** : formulaire local `127.0.0.1` protégé par jeton, sessions à deux horloges (15 min, 12 h), passerelle de confidentialité (pseudonymes, montants masqués, journal des sorties).
- Signaler une vulnérabilité : [SECURITY.md](SECURITY.md), jamais en ticket public.

## 9. Documentation

| Où | Quoi |
|---|---|
| [Portail](https://kouemousah.github.io/Facil_Finance/) | Tableau de bord (jalons, tâches), accès, manuels |
| [Documentation projet](https://kouemousah.github.io/Facil_Finance/documentation/) | Cadrage, PRD, architecture, ADR, spécifications, plans, catalogue des modules, Facil DEF, exploitation |
| [`docs/`](docs/) | Sources Markdown du site |
| [`manuel/livrable/`](manuel/livrable/) | Manuel d'utilisation, présentation, flyer de Facil DEF (FR et ES) |

## 10. Contribuer, licence

- [CONTRIBUTING](CONTRIBUTING.md) : branches, commits, définition de « fait ». [Code de conduite](CODE_OF_CONDUCT.md).
- **Licence propriétaire** ([LICENSE](LICENSE)) : le dépôt est public pour la transparence ; il ne vaut pas licence d'utilisation ([ADR 0011](docs/adr/0011-licence-proprietaire.md)).

<sub>© Emac SAH — Facil - AI Solutions Architect · SIRET 108 750 407 00018 · Paris, France · sah@emacsah.com</sub>
