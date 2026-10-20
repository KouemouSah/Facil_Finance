---
icon: lucide/network
---

# Architecture — vue d'ensemble

<span class="statut statut--brouillon">brouillon</span> · Version 0.1 · 15/10/2026

Cette page donne les vues C4 (contexte, conteneurs), le déploiement et le flux de production d'une liasse. Chaque choix renvoie à son [ADR](adr/index.md).

## 1. Contexte (C4 — niveau 1)

```mermaid
flowchart LR
    compta["Comptable / chef de mission<br/>(navigateur)"]
    admin["Administrateur<br/>(navigateur, SSH)"]
    expert["Expert-comptable valideur"]
    ff(["<b>Facil Finance</b><br/>serveur local ou réseau"])
    logiciel["Logiciel comptable du client<br/>(Sage, logiciel local, Excel…)"]
    dgi["Administration fiscale<br/>(dépôt ou télédéclaration)"]
    maj["Canal de mises à jour Facil<br/>(application, packs pays, modèles IA — signés)"]

    logiciel -- "balance, grand livre, écritures (fichiers)" --> ff
    compta -- "importe, répond, valide" --> ff
    admin -- "installe, sauvegarde, met à jour" --> ff
    ff -- "liasse PDF / Excel" --> expert
    expert -- "liasse signée" --> dgi
    maj -. "téléchargements signés (optionnels, hors ligne possible)" .-> ff
```

**Ce qui ne figure pas sur ce schéma est voulu** : aucun service d'IA externe. Kaem fonctionne en local ([ADR 0007](adr/0007-kaem-ia-locale.md)). Un appel externe ne peut être activé que par le client, à travers la passerelle de confidentialité.

## 2. Conteneurs (C4 — niveau 2)

```mermaid
flowchart TB
    subgraph poste["Navigateur"]
        ui["Interface web<br/>(fichiers statiques)"]
    end
    subgraph serveur["Serveur Facil Finance — /opt/facil-finance ou Program Files"]
        proxy["Caddy<br/>TLS, fichiers statiques"]
        api["API métier<br/>FastAPI · Python embarqué"]
        moteur["Moteur de production<br/>(bibliothèque, sans règle propre à un pays)"]
        packs[("Packs pays<br/>signés, datés")]
        worker["Travailleurs de fond<br/>(générations longues)"]
        kaem["Kaem<br/>llama.cpp + Gemma 4 E4B<br/>(paquet optionnel)"]
        passerelle["Passerelle de<br/>confidentialité"]
        db[("PostgreSQL embarqué<br/>grand livre, versions, droits, audit")]
        file[("Valkey<br/>file de tâches")]
        fichiers[("Fichiers<br/>sources, liasses, sauvegardes")]
    end
    ui -- HTTPS --> proxy --> api
    api --> moteur
    moteur --> packs
    api --> db
    api --> file --> worker --> moteur
    worker --> fichiers
    api -- "commandes du catalogue" --> kaem
    kaem -- "appels d'outils (lecture)" --> api
    api -. "seule sortie possible" .-> passerelle
```

| Conteneur | Rôle | Décision |
|---|---|---|
| Caddy | TLS (certificat automatique ou autorité locale), fichiers statiques | [ADR 0009](adr/0009-pile-serveur.md) |
| API métier | Droits, orchestration, contrats OpenAPI | [ADR 0009](adr/0009-pile-serveur.md) |
| Moteur | Lecture des balances, agrégation, états, contrôles, rendu Excel et PDF | [ADR 0005](adr/0005-reutiliser-le-moteur-def.md) |
| Packs pays | Tout ce qui dépend du pays | [ADR 0006](adr/0006-packs-pays-declaratifs.md) |
| PostgreSQL | Grand livre immuable, versions de liasse, droits, journal d'audit | [ADR 0004](adr/0004-erp-entree-par-la-production.md) |
| Kaem | Assistante locale | [ADR 0007](adr/0007-kaem-ia-locale.md), [ADR 0008](adr/0008-ia-ne-calcule-ni-ne-valide.md) |

## 3. Déploiement

```mermaid
flowchart LR
    subgraph mono["Monoposte — même logiciel"]
        n1["Navigateur"] --> s1["Service Facil Finance<br/>écoute 127.0.0.1"]
    end
    subgraph lan["Réseau du cabinet"]
        n2["Postes (navigateur)"] --> s2["Serveur Facil Finance<br/>Linux ou Windows"]
        adm["Admin (SSH)"] -- "tunnel ssh -L / CLI" --> s2
    end
    subgraph saas["V2 — SaaS"]
        n3["Clients"] --> lb["Frontal régional"] --> s3["Instances Facil Finance<br/>isolation au niveau des lignes"]
    end
```

**Le même logiciel** sert ces trois cas ([ADR 0002](adr/0002-toujours-en-mode-serveur.md)). Seules l'adresse d'écoute et la configuration changent.

## 4. Flux : de la balance à la liasse

```mermaid
sequenceDiagram
    autonumber
    actor C as Comptable
    participant API as API
    participant M as Moteur
    participant P as Pack pays
    participant DB as Base
    C->>API: dépose la balance et/ou le grand livre
    API->>M: reconnaître et contrôler
    M-->>API: format détecté, équilibre, ambiguïtés
    API->>DB: écritures et soldes importés (immuables, horodatés)
    C->>API: produire la liasse (pays, exercice)
    API->>P: pack valide pour le pays et la date de clôture
    API->>M: agréger → états → notes → tableaux fiscaux → contrôles
    M-->>API: liasse PROJET + grille de couverture + questions
    API->>DB: version n (jamais écrasée)
    C->>API: répond aux questions
    API->>M: régénérer (idempotent)
    C->>API: valider
    API->>DB: version DÉFINITIVE, signée et horodatée
```

## 5. Principes non négociables

1. **Le moteur ne contient aucune règle propre à un pays** : chaque taux, libellé, ligne et contrôle vient d'un pack.
2. **Une liasse se prouve** : chaque poste est relié à ses comptes ; chaque contrôle est consigné ; chaque écart est expliqué.
3. **Rien n'est écrasé** : écritures importées, versions de liasse et réponses sont horodatées et conservées.
4. **Les droits sont tenus par la base**, pas seulement par l'écran.
5. **Aucune sortie sans passerelle** : tout ce qui quitte le serveur est pseudonymisé, contrôlé et journalisé.
