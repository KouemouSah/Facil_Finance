---
icon: lucide/file-check
---

# 0002 — Toujours en mode serveur, même en monoposte

Statut : acceptée · Date : 15/10/2026 · Décideur : porteur (décision D1)

## Contexte
Le produit vise à la fois le comptable seul sur son PC et le cabinet en réseau. `projet.md` prévoyait deux topologies. Le risque est d'avoir deux produits à maintenir, et un client monoposte qui doit tout réinstaller le jour où il embauche.

## Options
1. Une application de bureau monoposte, plus une édition serveur.
2. **Un seul mode : un service serveur**, accessible par navigateur, comme Odoo.

## Décision
Option 2. En monoposte, le service écoute `127.0.0.1`. Pour partager, on change l'adresse d'écoute dans l'interface d'administration ; on ne réinstalle rien.

## Conséquences
- Un seul code, un seul installeur, une seule matrice de tests ; le passage à plusieurs utilisateurs est immédiat.
- Le service tourne en permanence (systemd ou service Windows) : l'installeur doit le déclarer proprement et la désinstallation le retirer.
- Les **sessions** (deux horloges) et les **droits** s'appliquent même à un utilisateur seul : c'est voulu, puisqu'un poste partagé est le cas le plus courant.
- **Mise à jour** : un redémarrage du service, de moins d'une minute, avec migration transactionnelle. On ne promet pas une mise à jour « à chaud ».

## Liens
EX-PLAT-1, EX-PLAT-4 · [ADR 0003](0003-distribution-autoportante.md) · [Architecture § 3](../architecture.md#3-deploiement)
