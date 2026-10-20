---
icon: lucide/target
---

# De l'outil DEF au produit commercial — analyse critique et feuille de route

*Note de stratégie produit, 15/10/2026. Regard d'un associé de cabinet d'audit et de conseil (« Big 4 ») sur ce qu'il faut pour transformer le plugin actuel en un outil de travail pour une équipe comptable et financière, vendable :*
- *V1 : application autonome, installable sous Linux (toutes distributions, pile embarquée — corrigé le 15/10, voir `projet.md` § 15), utilisable en SSH ;*
- *V2 : SaaS multi-clients.*

*Les chiffres de marché et de coûts sont des **hypothèses à vérifier** ; ils sont signalés comme tels.*

---

## 1. Le verdict, sans complaisance

**Ce qui existe a de la valeur, mais ce n'est pas encore un produit.** C'est un **moteur** remarquable, enveloppé dans un **prototype** :

| Ce qui est solide (et rare) | Ce qui manque pour vendre |
|---|---|
| Moteur déterministe : la balance ou le grand livre donnent une liasse SYSCOHADA complète, contrôlée, adaptée aux données | Une **application** : utilisateurs, rôles, base de données, interface métier, installation serveur |
| Discipline de preuve : gardes, contre-épreuves par mutation, équivalence avec une DEF réelle au franc près | Une **validation à l'échelle** : un seul dossier réel aujourd'hui ; le marché exige des dizaines de dossiers, plusieurs secteurs, plusieurs pays |
| Le calcul ne passe jamais par l'IA ; l'IA orchestre et explique | **Indépendance vis-à-vis de Claude** : aujourd'hui, l'outil ne vit que dans Claude Desktop / Claude Code |
| Confidentialité outillée : pseudonymisation, journal, données locales | Un **périmètre pays** : la Guinée équatoriale seule est un marché trop étroit pour amortir un produit |
| Fiscalité GE paramétrée article par article | Une **veille réglementaire** organisée : lois de finances annuelles, formats DGI, e-filing |

**Conclusion** : la bonne stratégie n'est pas d'« enrichir le plugin ». Il faut **extraire le moteur** et en faire le cœur d'un produit. L'IA y devient une **couche optionnelle** : utile, mais jamais indispensable au calcul ni au dépôt.

---

## 2. Le marché, et pourquoi la Guinée équatoriale seule ne suffit pas

- **Zone OHADA** : 17 États appliquent le même référentiel (SYSCOHADA révisé, AUDCIF 2017). Les états financiers et les notes sont **communs** ; les annexes fiscales et statistiques sont **nationales**. C'est exactement l'architecture déjà construite : un moteur commun, plus des « packs pays ».
- **Cibles**, par ordre de rentabilité probable :
  1. **cabinets d'expertise comptable** : 50 à 500 liasses par an chacun, saisonnalité forte de mars à juin, douleur maximale ;
  2. **directions financières de groupes multi-pays OHADA** : consolidation, homogénéité, contrôle ;
  3. **réseaux et grands cabinets** : exigences d'audit et de qualité (ISQM 1), piste d'audit, revue ;
  4. **PME avec comptable interne** : volume élevé, faible panier, à servir en SaaS.
- **Concurrence** (hypothèse à vérifier par une étude terrain) :
  - modules « liasse » des logiciels comptables locaux ;
  - matrices Excel vendues en ligne ;
  - saisie manuelle sur les portails de télédéclaration des DGI.
  
  Aucun de ces acteurs ne part de la **balance ou du grand livre seuls**, avec **contrôles prouvés**, **multi-pays** et **assistance IA**. C'est le positionnement à défendre.
- **Ordre de grandeur** (hypothèse) : la Guinée équatoriale compte quelques centaines de déclarants au régime normal. La Côte d'Ivoire, le Cameroun et le Sénégal en comptent chacun plusieurs milliers à plusieurs dizaines de milliers. **Le produit doit sortir avec 3 à 4 pays**, sous peine de rester confidentiel.

---

## 3. Les fonctionnalités qui en font un vrai outil de travail

Classées par **valeur pour une équipe de clôture ou d'audit**, et non par facilité technique.

### A. Clôture et révision des comptes (le quotidien de l'équipe)
| Fonction | Pourquoi elle compte |
|---|---|
| **Connecteurs d'import** : Sage 100, SAARI, Perfecto, Odoo, QuickBooks, SAP Business One ; FEC / fichier des écritures | L'import manuel de balances est la première perte de temps ; le moteur sait déjà lire « n'importe quelle » balance |
| **Dossier de révision par cycle** (immobilisations, stocks, clients, fournisseurs, trésorerie, capitaux, impôts, personnel), avec feuilles maîtresses et renvois | C'est le format de travail de tout cabinet ; la liasse en devient la **sortie**, pas le point de départ |
| **Revue analytique** N / N-1 / budget, seuils de signification, explications obligatoires au-delà du seuil | ISA 520 ; elle détecte les anomalies avant le réviseur |
| **Écritures d'inventaire proposées** : amortissements, provisions, CCA/PCA, FNP/FAE, écarts de conversion ; journal des ajustements (AJE/RJE) avec effet sur la liasse | Fait passer de « constater » à « corriger », avec traçabilité |
| **Rapprochements** : banque, TVA / chiffre d'affaires, charges sociales / masse salariale, grand livre / auxiliaires | Les incohérences relevées sur le dossier pilote (IS, versions de balance) relèvent toutes de ce module |

### B. Fiscalité (le cœur de valeur actuel, à étendre)
- **Packs pays** : liasse, passage du résultat comptable au résultat fiscal, IS / IMF / CMF, acomptes et échéancier ; d'abord GE, CI, CM, SN, puis le reste de la zone.
- **TVA** : déclarations mensuelles, réconciliation annuelle TVA / chiffre d'affaires, retenues à la source.
- **Calendrier fiscal** par entité, avec alertes ; **simulation** de l'IS avant clôture.
- **Télédéclaration** : export au format attendu par chaque DGI (XML, EDI ou formulaire) là où elle existe. C'est l'argument commercial le plus fort après l'automatisation, et un **verrou** : il faut l'agrément ou la conformité au format officiel.

### C. Audit et assurance (ce qui fera adopter le produit par les grands cabinets)
- **Analyse des écritures** (ISA 240) : écritures manuelles, le week-end, en fin de période, montants ronds, doublons, loi de Benford, utilisateurs inhabituels. Le grand livre est déjà lu ligne à ligne.
- **Échantillonnage** statistique (ISA 530, sondage en unités monétaires) et **circularisations** (clients, fournisseurs, banques), avec suivi des réponses.
- **Liste de pièces à fournir (PBC)** partagée avec le client, statut par pièce.
- **Notes de revue**, avec statut (préparé / revu / validé) par feuille et signature du réviseur : c'est la piste exigée par ISQM 1.

### D. Consolidation et reporting de gestion (montée en gamme)
- Multi-entités, multi-pays, **retraitements SYSCOHADA ↔ IFRS** (IFRS 16, 9, 15) : les filiales de groupes internationaux en ont besoin chaque année.
- Tableaux de bord : BFR, endettement, marges, trésorerie prévisionnelle ; budget / réel ; liasse de reporting groupe.

### E. Collaboration, contrôle interne, conformité (indispensable pour vendre)
- Comptes utilisateurs, **rôles** (préparateur, réviseur, associé, client en lecture), délégation, piste d'audit **inaltérable**.
- **Workflow** de dossier : ouvert → en préparation → en revue → validé → déposé → archivé ; verrouillage après validation, réouverture motivée.
- **Signature électronique** de la liasse et du rapport ; **archivage légal** sur 10 ans ; réversibilité (export complet).

### F. La couche IA, à sa juste place
- **Ce qu'elle fait bien** :
  - expliquer un écart ;
  - rédiger la note 2 (méthodes) et les commentaires de notes, à partir des chiffres ;
  - répondre sur la loi fiscale **en citant l'article** ;
  - proposer une affectation de compte inhabituel ;
  - résumer un dossier pour l'associé.
- **Ce qu'elle ne doit jamais faire** : calculer un montant, décider seule d'une réintégration, déposer. C'est déjà le principe du plugin ; il faut le **garder comme règle de produit**, et le dire dans la documentation commerciale.
- **Commercialement** : l'IA est une **option** facturée à part, qu'on peut désactiver. Certains clients (banques, administrations, filiales de groupes) refuseront tout envoi de données hors de leur infrastructure. La pseudonymisation actuelle est un atout de vente, mais pas une garantie suffisante pour eux. Il faut une offre **« sans IA »** et, à terme, une offre « IA hébergée localement ».

---

## 4. Architecture V1 : autonome, Linux toutes distributions, SSH

> ⟲ 15/10 : « Debian » se lit désormais « **toute distribution Linux** ». La solution retenue est un contenu autoportant (glibc ≥ 2.28, x86_64 et aarch64, PostgreSQL, Valkey et Caddy embarqués), livré en `.run` avec des enveloppes `.deb` / `.rpm` / OCI. Elle remplace le « Nginx » et le PostgreSQL système ci-dessous. Détail : `projet.md` § 15.

### 4.1 Le principe : un cœur, plusieurs façades
```
facil-core (Python)           moteur actuel : lecture, agrégation, fiscalité, liasses, contrôles, PDF
   ├── facil-cli              ligne de commande (usage SSH, automatisation, intégration)
   ├── facil-web              application web (FastAPI + interface) : le produit que voit l'équipe
   ├── facil-mcp (option)     l'adaptateur Claude actuel, devenu une façade parmi d'autres
   └── facil-worker           générations longues en tâche de fond (file de travaux)
stockage : PostgreSQL (dossiers, versions, réponses, piste d'audit) + fichiers (sources, livrables)
```
Le moteur actuel est déjà séparé en modules propres et sans dépendance à Claude. L'**extraction est réaliste** ; c'est le premier chantier.

### 4.2 Installation et exploitation
| Besoin | Réponse V1 |
|---|---|
| Debian / Ubuntu | paquet **.deb** (environnement Python embarqué, comme le runtime Windows actuel), service **systemd**, Nginx en frontal, PostgreSQL ou SQLite pour une petite structure |
| Windows (la majorité des comptables) | installeur **MSI** reprenant le runtime embarqué existant |
| Mode SSH | `facil-cli` complet (générer, contrôler, exporter) + interface web accessible par **tunnel SSH**, sans port public |
| Hors ligne, faible bande passante | fonctionnement **100 % local** ; seules les mises à jour (moteur, paramètres fiscaux) se téléchargent, **signées** |
| Licence | clé de licence **signée** (Ed25519), vérifiable **hors ligne** : nombre de postes ou de dossiers, pays, date de fin |
| Sécurité | comptes locaux + annuaire (LDAP / Active Directory), double authentification, rôles, chiffrement des sauvegardes, journal d'accès |
| Mises à jour réglementaires | « packs pays » versionnés et signés, indépendants du moteur : une loi de finances ne doit pas imposer une réinstallation |

### 4.3 Ce qui doit changer dans le code actuel
- Les **fichiers JSON** (manifeste, questions, réponses) deviennent des **tables**. La piste d'audit devient une table en ajout seul.
- Le **formulaire local** devient l'**application web** : même logique d'étapes, mais avec comptes et rôles.
- La **passerelle de confidentialité** est conservée telle quelle pour la façade IA.
- Les **gardes et contre-épreuves** deviennent la **chaîne d'intégration continue** : c'est la meilleure assurance qualité du projet, elle doit le rester.

---

## 5. Architecture V2 : SaaS multi-clients

| Sujet | Recommandation | Point critique |
|---|---|---|
| Isolation des clients | PostgreSQL avec **isolation au niveau des lignes** (RLS) et identifiant de client partout ; **schéma dédié** pour les grands comptes | Une fuite entre cabinets tue le produit : tests d'isolation automatiques, revue de sécurité externe |
| Chiffrement | clé **par client** (KMS) ; fichiers chiffrés au repos | Rotation, révocation, réversibilité à la résiliation |
| Hébergement | régions Afrique (Afrique du Sud, Nigeria) et / ou Europe ; option « cloud privé » pour les grands comptes | **Lois nationales de protection des données** (Sénégal, Côte d'Ivoire, Cameroun, Gabon…) : localisation et déclarations aux autorités |
| Identité | OpenID Connect (Keycloak ou équivalent), SSO entreprise, double authentification obligatoire | Comptes clients (lecture, PBC) distincts des comptes cabinet |
| IA | fournisseurs sous **accord sans conservation** ; passerelle de pseudonymisation **côté serveur** ; option désactivable par client | Transparence contractuelle : quelles données partent, où, combien de temps |
| Facturation | abonnement + consommation (dossiers), paiement par carte, **virement** et **mobile money** | Facturation en XAF / XOF, TVA locale du fournisseur |
| Conformité | trajectoire **ISO 27001** puis **SOC 2** : les grands cabinets l'exigeront de leurs fournisseurs | Coût et délai : 12 à 18 mois, à anticiper dès la V1 (politique de sécurité, journalisation) |
| Exploitation | supervision, sauvegardes testées (restauration **exercée**), plan de continuité, engagement de service | La saisonnalité (mars-juin) impose une montée en charge contrôlée |

**Ne pas abandonner l'installation locale en V2.** En Afrique centrale et de l'Ouest, une part du marché (banques, grandes entreprises, administrations, connectivité faible) restera sur site. L'architecture « un cœur, plusieurs façades » permet de servir les deux avec un seul code.

---

## 6. Les risques à traiter avant de vendre

1. **Responsabilité professionnelle.** Une liasse fausse entraîne un redressement ; or le client se retournera contre l'éditeur. Il faut :
   - des conditions générales claires : le produit **assiste**, l'expert-comptable **valide et signe** ;
   - une assurance responsabilité civile professionnelle d'éditeur ;
   - la traçabilité de chaque choix (déjà en place : réponses, interprétations, versions).
2. **Validation insuffisante.** Un seul dossier réel. Avant toute vente :
   - **30 à 50 dossiers** par pays lancé, plusieurs secteurs (négoce, BTP, services, industrie), avec et sans grand livre ;
   - un **banc de non-régression** sur ces dossiers, rejoué à chaque version (le lot L5 prévu).
3. **Veille réglementaire.** Chaque loi de finances et chaque nouveau formulaire DGI exigent une mise à jour. Sans **fiscaliste OHADA** dans l'équipe, le produit vieillit en un an. C'est un coût récurrent, mais c'est aussi la **barrière à l'entrée** qui protège l'éditeur.
4. **Dépendance à un fournisseur d'IA.** Le moteur n'en dépend pas, et c'est voulu : il faut que cela reste vrai. Prix, disponibilité et conditions d'usage des données doivent pouvoir changer sans casser le produit.
5. **Équipe.** Un projet porté par une seule personne, même rigoureuse, n'est pas un actif vendable. Les clients d'audit demanderont la continuité de service et l'entiercement du code source.
6. **Agrément et formats officiels.** Certaines administrations publient des formats imposés ou agréent les logiciels de télédéclaration. Il faut s'en informer **pays par pays** avant de promettre le dépôt en ligne.

---

## 7. Modèle économique (hypothèses à valider auprès de 10 cabinets)

| Offre | Pour qui | Principe de prix (hypothèse) |
|---|---|---|
| **Licence sur site V1** | cabinets, groupes | licence annuelle par nombre de dossiers + maintenance (veille fiscale incluse) |
| **Au dossier** | petits cabinets, PME | prix par liasse produite et validée, dégressif selon le volume |
| **SaaS V2** | tous | abonnement par utilisateur + quota de dossiers ; option IA en sus |
| **Packs pays** | tous | inclus par pays souscrit ; nouveau pays = extension facturée |
| **Services** | grands comptes | paramétrage, reprise de l'historique, formation, connecteurs spécifiques |

**Canaux** :
- les **ordres nationaux d'experts-comptables** : formation continue, recommandation ;
- les **revendeurs de logiciels comptables** déjà implantés ;
- un **cabinet pilote de référence** par pays.

La crédibilité vient de références nommées et d'un taux d'erreur mesuré ; la publicité n'y suffira pas.

---

## 8. Feuille de route proposée

| Étape | Durée (hypothèse) | Contenu | Critère de sortie |
|---|---|---|---|
| **0. Preuve de marché** | 3 mois | banc de validation sur 30 dossiers GE + 1 pays majeur ; 3 cabinets pilotes (payants, même modestement) ; grille de prix testée | ≥ 95 % des postes identiques aux liasses déposées, écarts tous expliqués ; 3 lettres d'intention |
| **1. V1 autonome** | 6 mois | extraction de `facil-core` ; application web + CLI ; .deb + MSI ; comptes et rôles ; workflow de dossier ; licence hors ligne ; 3 à 4 pays ; 3 connecteurs | 10 clients payants ; installation sans intervention de l'éditeur |
| **1.5 Révision et audit** | 4 à 6 mois | dossier de révision par cycle, revue analytique, analyse des écritures (ISA 240), PBC, notes de revue, TVA | adoption par un cabinet de taille moyenne pour sa saison |
| **2. SaaS** | 9 à 12 mois | multi-clients, SSO, facturation, hébergement régional, trajectoire ISO 27001 | premiers clients SaaS ; audit de sécurité externe passé |

**Équipe minimale (hypothèse)** :
- 2 développeurs Python ;
- 1 développeur d'interface ;
- 1 expert-comptable « produit » ;
- 1 fiscaliste OHADA (à temps partiel au début) ;
- 1 personne support / mise en service en saison.

---

## 9. Les décisions à prendre maintenant

1. **Choisir le deuxième pays** (Côte d'Ivoire, Cameroun ou Sénégal) selon l'accès à des dossiers réels et à un cabinet pilote. Sans lui, pas de marché.
2. **Réunir 30 dossiers réels** (balance, grand livre, liasse déposée) pour le banc de validation. C'est l'actif le plus précieux du projet, plus que le code.
3. **Décider de l'extraction du moteur** hors du plugin, avant d'ajouter des fonctions. Chaque fonction ajoutée au plugin devra sinon être refaite.
4. **Fixer la règle de produit** : le calcul est déterministe et prouvé, l'IA reste optionnelle et n'est jamais décisionnaire. Elle doit apparaître dans les contrats et le discours commercial.
5. **Protéger** : marque, conditions générales, assurance, propriété du code (l'actuel est-il entièrement propriété de Facil ?).

*Ce qui est déjà acquis, et qui distingue ce projet de la plupart des outils du marché :*
- *un moteur qui part de la balance ou du grand livre seuls ;*
- *une liasse officielle adaptée aux données ;*
- *des contrôles qui prouvent chaque chiffre ;*
- *une culture de la preuve (gardes, contre-épreuves).*

*C'est une base solide. Ce qui manque relève de la mise en produit, du marché et de l'organisation, plus que de la technique.*
