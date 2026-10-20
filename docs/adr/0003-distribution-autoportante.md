---
icon: lucide/file-check
---

# 0003 — Distribution autoportante : Windows et Linux toutes distributions, sans Docker

Statut : acceptée · Date : 15/10/2026 · Décideur : porteur et architecte (arbitrage A4)

## Contexte
Le porteur exige un produit installable sur **toute** distribution Linux, et sous Windows, **avec sa pile et ses outils embarqués**. Les deux documents d'origine proposaient Docker Compose. Docker suppose un outil installé et administré, parfois interdit en entreprise. Sous Windows, Docker Desktop est payant pour les entreprises au-delà de certains seuils.

## Options
1. Docker Compose partout.
2. Paquets natifs par distribution (`.deb`, `.rpm`), dépendant des bibliothèques du système.
3. **Un contenu autoportant unique**, compilé sur une base ancienne de la glibc, livré dans plusieurs enveloppes.

## Décision
Option 3.
- **Compatibilité** : glibc 2.28 (norme `manylinux_2_28`), architectures x86_64 et aarch64.
- **Contenu embarqué** : Python autonome relocalisable, binaires PostgreSQL relocalisables, Valkey, Caddy, interface statique, et llama.cpp dans le paquet IA.
- **Enveloppes** : `.run` autoextractible et signé (interactif, ou `--unattended --config` pour le SSH) ; `.deb` / `.rpm` minces publiés dans un dépôt signé ; image OCI optionnelle ; MSI sous Windows.

## Conséquences
- Couvre Debian 10+, Ubuntu 20.04+, RHEL / Alma / Rocky 8+, SUSE 15+ et Fedora. Alpine (musl) n'est servie que par l'image OCI.
- **Ne s'embarquent pas** : le noyau et les pilotes GPU.
- Le service est porté par systemd, ou par un superviseur intégré quand systemd est absent (conteneur, WSL). L'installeur traite SELinux, AppArmor et le pare-feu.
- Une **matrice de recette** (installation, mise à jour, retour arrière, désinstallation) tourne en CI sur Debian 12, Ubuntu 22.04 et 24.04, Rocky 9, openSUSE 15, Fedora, Windows 10 et 11.
- **Précédent** : le runtime Python embarqué sous Windows est déjà en production dans le plugin, ce qui prouve le principe.

## Liens
EX-PLAT-5 · R7 · [projet.md § 15](../sources/projet.md)
