---
icon: lucide/search-check
---

# Analyse critique croisée — `projet.md` (Facil Gestion) × `jarvis_finance.md` × l'existant

*15/10/2026. Regard d'associé de cabinet d'audit et de conseil. Sources :*
- *`projet.md` (443 lignes), lu en entier ;*
- *`jarvis_finance.md` (6 439 lignes), lu en entier par un agent dont la synthèse donne les numéros de ligne cités ici ;*
- *le plugin existant ;*
- *les demandes du porteur du 15/10/2026.*

*Les décisions qui en découlent sont reportées dans `projet.md`, § 0 et §§ 14 à 19.*

---

## 1. Verdict d'ensemble

| Document | Ce qu'il vaut | Son défaut principal |
|---|---|---|
| **`projet.md`** | Un vrai cadrage produit, métier et design. Il est rigoureux sur la conformité (« le SYSCOHADA n'est pas une fonctionnalité, c'est un invariant »), sur l'IA (« l'IA propose, l'humain dispose ») et sur l'ergonomie comptable. | Il vise un **ERP comptable complet** construit de zéro, ce qui représente 12 à 24 mois-homme de son propre aveu. Il ignore l'actif déjà construit, et ses choix d'installation Linux contredisent l'exigence « tout embarqué ». |
| **`jarvis_finance.md`** | Une excellente **couche de gouvernance de l'IA**, de niveau grande entreprise : sécurité des outils, passerelle de confidentialité, preuves, approbation humaine, audit chaîné, IA qui ne calcule jamais. | C'est une **conversation d'IA mise bout à bout**, pas un document de projet. Il n'y a **aucune ligne sur le SYSCOHADA**, et les exemples sont en euros (l. 896, 1055). On y trouve trois feuilles de route, quatre positions sur le framework d'agents (l. 3942, 5869, 6378, 6431) et trois sur l'authentification (l. 553, 4040, 5509). Aucun dimensionnement matériel. Les sources tierces portent `utm_source=chatgpt.com` et ne sont pas vérifiées. |
| **L'existant (plugin)** | Le **seul actif prouvé** : liasse SYSCOHADA à partir de la balance ou du grand livre, contrôles qui prouvent chaque chiffre, passerelle de confidentialité **déjà codée**, Python embarqué, discipline de gardes et de contre-épreuves. | Il est lié à Claude, il n'a pas de base de données ni d'utilisateurs, et il n'est validé que sur un dossier. |

**Le risque majeur du projet n'est pas technique : c'est la dispersion.** Additionner l'ERP de `projet.md`, le « Jarvis » de `jarvis_finance.md`, 17 pays et un SaaS, c'est vouloir livrer un SAP africain doté d'une IA. Sans arbitrage, on obtient 50 mois-homme et aucun client. La suite propose ces arbitrages.

---

## 2. Contradictions entre les deux documents, et l'arbitrage proposé

| Sujet | `projet.md` | `jarvis_finance.md` | Arbitrage |
|---|---|---|---|
| Contenu de la V2 | V2 = assistant vocal local (§ 3.2) | V1 inclut déjà agents et LLM (l. 5240) | **V2 = SaaS multi-clients** (demande du porteur). L'assistant suit une **piste IA continue** : texte en V1.x, voix en V2 (§ 15 de `projet.md`) |
| Moteur financier | ERP de zéro, saisie et journaux (§ 3.1) | « Financial Engine » générique, en euros | **Le moteur DEF existant devient le cœur** : clôture, états financiers et liasse ; la saisie complète vient ensuite (§ 3 ci-dessous) |
| Installation Linux | Docker Compose, `.deb` / AppImage (§ 6.2, § 6.4) | Docker Compose, Docker Desktop sous Windows (l. 1439) | **Paquet autoportant multi-distributions**, sans Docker requis ; Docker reste une option (§ 14 de `projet.md`) |
| Matériel cible | 8 Go de RAM, 4 cœurs (§ 4) | LLM + VLM + Whisper + Keycloak + Docker Desktop sur un « PC peu puissant » (l. 2707) | **Éditions** : Standard sans IA (8 Go) ; IA (32 Go et GPU recommandés) ; Serveur (§ 15) |
| Authentification | Sessions + JWT + TOTP (§ 7) | Keycloak dès le départ (l. 5509) | **Abstraction d'identité** : intégrée en édition autonome, Keycloak en serveur et en SaaS. Keycloak (Java, 0,5 à 1 Go de RAM) est trop lourd pour un poste de 8 Go |
| LLM | 100 % local (§ 1.3, OB10) | Routage vers le cloud par LiteLLM (l. 3344) | **Local par défaut**. Cloud en option, **par client et par donnée**, derrière la passerelle de confidentialité (déjà codée dans le plugin) |
| Framework d'agents | — | Indécis (LangGraph ou PydanticAI) | **Aucun en V1.** Un catalogue de commandes déterministe (palette Ctrl+K du § 12.6) ; le LLM choisit une commande en sortie structurée. Comparatif PydanticAI / LangGraph en V2 |
| Rôles | Rôle × module × action × société, en base | Keycloak + tables locales, sans dire qui fait foi (l. 6376) | **Les permissions métier vivent dans l'application** (la base fait foi) ; Keycloak ne porte que l'identité |
| Licence du produit | Open source type LGPL « à décider » (§ 11.5) | Absente | **Propriétaire**, avec entiercement du code pour les grands comptes (§ 18). Sous LGPL, les packs fiscaux, qui sont la valeur, seraient copiables |

---

## 3. Le choix stratégique que les deux documents ne posent pas

**Être un ERP comptable complet, ou une couche de production et de contrôle au-dessus des logiciels existants ?**

- **ERP complet** (`projet.md`) : saisie, journaux, lettrage, clôture.
  - Le marché est occupé (Sage, logiciels locaux, Odoo).
  - Faire migrer un client coûte cher (§ 11.2 le reconnaît).
  - Le délai de mise sur le marché est long.
- **Couche de production** : importer la balance, le grand livre et les écritures du logiciel du client, puis produire la révision, la liasse, les contrôles, le reporting, et l'IA par-dessus.
  - C'est **exactement l'actif existant**.
  - Il n'y a pas de migration : on vend aux cabinets **sans changer le logiciel de leurs clients**.
  - On peut être partenaire des éditeurs d'ERP plutôt que leur concurrent.

**Recommandation** : V1 = couche de production (import → révision → états → liasse → contrôles → reporting). La **saisie comptable complète** devient un module ultérieur, si le marché la demande. Le § 3.1 de `projet.md` reste la cible à terme, mais pas la porte d'entrée.

---

## 4. « Jarvis » : bonne idée, mauvais nom, mauvais ordre

**Ce qui est juste** :
- un assistant qui comprend la demande métier et déclenche des traitements sûrs ;
- qui explique un écart, rédige le commentaire d'une note, prépare le rapport au conseil d'administration ;
- et qui le fait sous l'identité et les droits de l'utilisateur, avec preuves et approbation.

La gouvernance de `jarvis_finance.md` (pare-feu d'outils, passerelle, approbation humaine, journal chaîné) est la bonne. Il faut la reprendre.

**Ce qui doit changer** :
1. **Le nom.** « JARVIS » est un personnage et une marque de l'univers Marvel (Disney), et de nombreux logiciels portent déjà ce nom. Le déposer comme marque commerciale exposerait à une opposition, ou à un refus pour défaut de distinctivité. Il faut le garder comme **nom de code interne** et déposer un nom propre (§ 17 de `projet.md`).
2. **L'ordre : le texte d'abord, la voix ensuite.**
   - Dans un bureau comptable partagé, la voix est bruyante, peu discrète et peu fiable sur le vocabulaire comptable en FR, ES et PT avec les accents locaux.
   - La **palette de commandes** et le **chat texte** apportent 80 % de la valeur pour 20 % du coût.
   - La voix vient en V2, sur le serveur ou le SaaS, où un GPU la rend fluide.
3. **« Toujours en éveil »** : un navigateur ne peut pas écouter en permanence (autorisation du micro par onglet, mise en veille).
   - L'écoute permanente exige une **application de bureau** (Tauri par exemple) avec un détecteur de mot d'éveil **local**.
   - Elle pose un sujet de consentement et de vie privée **au bureau** : témoin d'écoute, coupure physique, politique écrite.
   - Le niveau 2 du document (veille côté serveur, alertes) offre l'essentiel de la « proactivité » sans micro ouvert. C'est lui qu'il faut faire en premier.
4. **Le périmètre des actions.** En V1, l'assistant **lit, explique et prépare**. Il ne valide ni n'écrit d'écriture comptable. Cela suit la règle d'or du § 6.6 de `projet.md`, et c'est aussi ce qui limite la responsabilité de l'éditeur.

---

## 5. Embarquer un modèle local dans l'installeur : oui, mais pas dans le même paquet

| Question | Constat | Recommandation |
|---|---|---|
| Taille | LLM 7 à 8 milliards de paramètres quantifié en 4 bits ≈ 4,5 à 5 Go. Reconnaissance vocale (Whisper medium/large) ≈ 1,5 à 3 Go. Synthèse vocale ≈ 0,1 Go par voix. Embeddings ≈ 0,5 Go | **Paquet IA séparé** (6 à 10 Go), téléchargé ou livré sur support hors ligne, **signé**. L'application de base reste légère (≈ 300 à 600 Mo) |
| Matériel | Sur un processeur seul, un modèle de 7 à 8 milliards donne quelques mots par seconde : une réponse prend 10 à 30 s. L'objectif « < 5 s » de `projet.md` (OB10) exige un **GPU de 8 à 12 Go** ou un modèle de 3 à 4 milliards | **Détection de capacité** à l'installation, et 3 niveaux : *sans IA* ; *IA légère* (modèle de 3 à 4 milliards sur processeur, 16 Go de RAM) ; *IA complète* (7 à 14 milliards sur GPU, 32 Go). Annoncer honnêtement les temps de réponse par niveau |
| Pilotes | Les pilotes GPU (NVIDIA, AMD) **ne s'embarquent pas** : ils font partie du système | L'installeur **détecte** le pilote. À défaut, il bascule sur le processeur et le dit |
| Moteur d'inférence | `llama.cpp` (MIT) : un serveur en un seul binaire, compatible processeur, CUDA et Vulkan, **embarquable sans dépendance**. Ollama est pratique mais ajoute une couche. vLLM convient au serveur GPU et au SaaS | **llama.cpp** en autonome ; **vLLM** en serveur et en SaaS ; LiteLLM (MIT) devant l'ensemble |
| Licences des modèles | **Point bloquant pour la vente** : licences très variables. Llama impose une licence communautaire avec conditions et attribution. Gemma impose ses conditions d'usage. Parmi les Qwen 2.5, la plupart sont sous Apache 2.0, mais certaines tailles ont une licence propre. Mistral 7B est sous Apache 2.0. Whisper est sous MIT. Les **voix Piper ont chacune leur licence, parfois non commerciale** | **Registre des licences** de chaque modèle et de chaque voix, audité avant distribution ; préférer Apache 2.0 et MIT. À **revérifier à chaque version** : les licences changent |
| Qualité | Les modèles généralistes se trompent sur le SYSCOHADA (comptes, régimes) et sur l'espagnol ou le portugais administratifs | Ne jamais leur faire calculer ni décider. Leur fournir des **outils** (le moteur) et une **recherche dans les textes officiels** (AUDCIF, lois de finances), avec citation obligatoire. Construire un **jeu d'évaluation métier** avant de choisir un modèle |
| Mises à jour | Un modèle se remplace comme un composant : version, empreinte, retour arrière | Registre local des modèles (déjà esquissé l. 5146), canal signé, test d'évaluation avant activation |

---

## 6. Linux : la correction demandée, et pourquoi Docker ne suffit pas

L'exigence réelle est **« installable sur toute distribution Linux, avec ses outils et sa pile embarqués »**. Docker Compose, retenu par les deux documents, **ne la satisfait pas** :
- il suppose Docker installé, administré, et parfois interdit en entreprise ;
- sous Windows, **Docker Desktop** est payant pour les entreprises au-delà de certains seuils de taille ou de chiffre d'affaires. Le proposer comme « option simple » (`jarvis_finance.md` l. 1439) crée un coût caché chez le client.

**L'approche professionnelle** est un **paquet autoportant**, installé dans `/opt/<produit>` et compilé une fois pour toutes les distributions :
- **référence de compatibilité** : glibc 2.28 (norme `manylinux_2_28`). Cela couvre Debian 10+, Ubuntu 18.10+ / 20.04+, RHEL / AlmaLinux / Rocky 8+, SUSE 15+ et Fedora récent ;
- **architectures** : x86_64 et aarch64 (serveurs ARM, Raspberry Pi 5) ;
- **Alpine** (musl) : servi par l'image conteneur ;
- **contenu embarqué** : Python autonome (comme le runtime Windows actuel du plugin), PostgreSQL compilé et relocalisable, Valkey (fork BSD de Redis), Caddy (serveur web en un seul binaire, TLS automatique), interface web en fichiers statiques (sans Node.js à l'exécution) et `llama.cpp` dans le paquet IA ;
- **installeur** : un script autoextractible (`.run`), en mode interactif ou sans assistance (`--unattended`, idéal en SSH). Il crée les services systemd, ou un superviseur intégré quand systemd est absent (conteneurs, WSL). Il gère les politiques de sécurité SELinux et AppArmor et ouvre le pare-feu ;
- **variantes de confort** : paquets `.deb` et `.rpm` minces (dépôt signé) qui enveloppent le même contenu, et image conteneur (Docker / Podman) pour qui la préfère. **Un seul contenu, plusieurs enveloppes.**
- **mode SSH** :
  - ligne de commande complète (`<produit> dossier`, `generer`, `controler`, `exporter`) et interface texte ;
  - interface web par tunnel (`ssh -L`), sans port public ;
  - installation et mise à jour sans assistance.

Sous Windows, le même principe s'applique : runtime embarqué (c'est déjà fait), installeur MSI ou InnoSetup, et **aucun Docker requis**.

---

## 7. Les 17 États du SYSCOHADA : ce que « tous les pays » implique vraiment

| Zone | États | Monnaie | Langue officielle de la liasse |
|---|---|---|---|
| UEMOA | Bénin, Burkina Faso, Côte d'Ivoire, Guinée-Bissau, Mali, Niger, Sénégal, Togo | XOF | FR ; **PT** pour la Guinée-Bissau |
| CEMAC | Cameroun, Centrafrique, Congo, Gabon, Guinée équatoriale, Tchad | XAF | FR ; **ES** pour la Guinée équatoriale ; **EN** au Cameroun (régions anglophones) |
| Hors zones monétaires | Comores, Guinée, RD Congo | KMF, GNF, CDF (USD courant en RDC) | FR (et arabe aux Comores) |

Conséquences rarement anticipées :
- **Quatre langues de liasse**, et non deux : FR, ES, PT, EN. Il faut une i18n par **dictionnaire de libellés officiels** (déjà en place pour FR→ES dans le plugin), pas par traduction automatique.
- **17 administrations fiscales**. Chacune a sa liasse (DSF ou équivalent), ses annexes, ses taux (IS, impôt minimum, TVA) et ses portails de télédéclaration.
  - C'est le **principal coût récurrent** du produit, et aussi la barrière qui le protège.
  - L'harmonisation par zone (directives UEMOA et CEMAC) ne supprime pas les spécificités nationales.
- **Méthode** : un « pack pays » est un **jeu de données versionné et signé** (gabarit, correspondances, paramètres fiscaux cités article par article, comme `parametres_fiscaux_ge.json`). Il est validé par un expert local et mis à l'épreuve d'au moins 10 liasses réelles déposées.
  - Vouloir les 17 pays à la V1 est irréaliste.
  - **Ordre recommandé** : GE (fait) ; puis Cameroun, Côte d'Ivoire et Sénégal (marchés les plus larges) ; puis Gabon et Congo (CEMAC, proches de la GE) ; puis le reste de l'UEMOA ; enfin RDC, Guinée et Comores.
- **Le système minimal de trésorerie (SMT)** doit exister dans chaque pack : il concerne la masse des très petites entités.

---

## 8. Protéger la marque et contracter : ce qui manque entièrement

Absent des deux documents ; détaillé au § 17 de `projet.md`.
- **Marque** :
  - un **seul dépôt à l'OAPI** (Accord de Bangui) protège la marque dans ses 17 États membres. Ceux-ci recoupent largement l'OHADA, mais **pas entièrement** : la RD Congo n'est pas membre de l'OAPI et exige un dépôt national, tandis que la Mauritanie est à l'OAPI sans être à l'OHADA ;
  - pour l'Europe ou l'international, le système de Madrid ;
  - **recherche d'antériorité avant tout dépôt** ;
  - « Facil » est un terme courant, donc faiblement distinctif : un signe composé ou figuratif se défendra mieux.
- **Logiciel** : il est protégé par le droit d'auteur dès sa création. Il faut se constituer une **preuve de date** (dépôt probatoire, horodatage), prévoir un **entiercement du code** pour les grands comptes, et vérifier que **Facil détient tous les droits** (contrats de développement, contributions).
- **Contrats** :
  - contrat de licence pour l'installation locale ;
  - conditions générales et contrat SaaS avec engagement de service ;
  - **accord de traitement des données** ;
  - politique de confidentialité ;
  - conditions d'usage de l'IA ;
  - clauses de responsabilité : outil d'assistance, l'expert-comptable valide et signe, plafond de responsabilité, pas de conseil fiscal.
- **Licences des briques** :
  - inventaire de toutes les dépendances (SBOM) ;
  - éviter d'embarquer des composants AGPL ou SSPL dans un produit fermé distribué. Par exemple, **Redis ≥ 7.4** (préférer **Valkey**, sous BSD) et **MinIO**, sous AGPL (préférer le système de fichiers, ou une alternative Apache) ;
  - vérifier Docker Desktop, LiteLLM Enterprise, Grafana, ainsi que les modèles et les voix.
- **Données personnelles** : lois nationales (Côte d'Ivoire 2013, Sénégal 2008, Cameroun 2024, Gabon, etc.), avec déclarations auprès des autorités, localisation des données et transferts vers des LLM hébergés hors du pays.

---

## 9. Ce qu'il faut reprendre de chaque document

| Reprendre de `projet.md` | Reprendre de `jarvis_finance.md` | Reprendre de l'existant |
|---|---|---|
| Invariants comptables (immuabilité, extourne, verrouillage), packs pays pilotés par les données, i18n dès le premier jour, design system et composants métier (§ 12.6), corpus de recette, « l'IA propose, l'humain dispose » | Pare-feu d'outils, passerelle de confidentialité et coffre de jetons, Data Policy par champ, approbation humaine par action, audit chaîné, preuves (Evidence), RAG filtré par les droits, défense contre l'injection, jobs idempotents, « le LLM ne calcule pas » | Moteur DEF (états, liasse, contrôles « note = poste »), lecture de toute balance et de tout grand livre, gabarits SYSCOHADA et GE, passerelle de confidentialité, runtime embarqué, discipline de gardes et de contre-épreuves |

**À écarter ou différer** :
- dans `jarvis_finance.md` : l'agent proactif « toujours en éveil » en V1, le multi-agents, l'apprentissage des préférences, le routage automatique vers le cloud ;
- dans `projet.md` : la promesse de mise à jour « à chaud » en monoposte (déjà nuancée par le document lui-même).

---

## 10. Feuille de route unifiée proposée

| Version | Contenu | Matériel | Critère de sortie |
|---|---|---|---|
| **V1.0 Socle** | Moteur extrait du plugin ; application web + ligne de commande ; base PostgreSQL ; comptes, rôles, droits par société ; import balance / grand livre / écritures ; révision et contrôles ; états financiers et liasse GE + 3 pays ; paquets Linux autoportants et Windows ; licence hors ligne ; sessions à deux horloges | 8 Go, sans IA | 30 liasses réelles par pays au franc près ; installation sans assistance < 30 min |
| **V1.1 Assistant texte** | Palette de commandes ; chat sur le catalogue de commandes ; explications d'écarts ; rédaction de notes ; pare-feu d'outils ; passerelle ; journal ; paquet IA optionnel (llama.cpp) | 16 à 32 Go | Jeu d'évaluation métier ≥ 90 % ; aucune action d'écriture par l'IA |
| **V1.2 Production** | Ingestion OCR (§ 6.6 de `projet.md`), révision avancée, analyse des écritures (ISA 240), TVA, télédéclaration là où elle existe | — | Corpus documentaire ≥ 90 % des champs |
| **V2.0 SaaS** | Multi-clients (isolation au niveau des lignes, clé par client), Keycloak, facturation, hébergement régional, trajectoire ISO 27001 | Serveurs GPU partagés | Audit de sécurité externe ; premiers clients SaaS |
| **V2.1 Voix et proactivité** | Voix (Whisper / Piper) sur le serveur ; veille et alertes (niveau 2) ; application de bureau pour le mot d'éveil (niveau 1), en option | GPU serveur | 10 parcours vocaux < 5 s |

**Effort** (hypothèse) : V1.0 à V1.2 ≈ 25 à 35 mois-homme ; V2.x ≈ 20 à 30 de plus.
- Ces chiffres dépassent l'estimation de `projet.md` (12 à 24), qui ne comptait ni l'IA gouvernée, ni le multi-pays, ni le SaaS.
- Les 17 pays s'étalent sur toute la période : environ 1 à 2 mois-homme par pack, plus un expert local.

---

## 11. Les cinq décisions qui conditionnent tout le reste

1. **Positionnement** : couche de production au-dessus des logiciels existants (recommandé), ou ERP complet ?
2. **Nom commercial** : abandonner « Jarvis » comme marque, choisir un nom, faire la recherche d'antériorité, déposer à l'OAPI.
3. **Licence du produit** : propriétaire avec entiercement (recommandé), ou open source ?
4. **Ordre des pays** après la GE : Cameroun, Côte d'Ivoire et Sénégal sont proposés ; le choix dépend de l'accès à des liasses réelles et à un expert local.
5. **Éditions et matériel** : Standard sans IA, IA locale, Serveur. Il faut annoncer **par écrit** les temps de réponse de l'IA selon le matériel, pour ne pas vendre une promesse que le PC du client ne tiendra pas.

*Toutes les durées, tailles et estimations de marché ci-dessus sont des hypothèses à vérifier. Les licences et les textes cités (OAPI, lois sur les données) sont à **revérifier auprès d'un juriste** avant tout dépôt ou contrat.*
