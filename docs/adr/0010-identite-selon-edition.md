---
icon: lucide/file-check
---

# 0010 — Identité intégrée en édition installée, Keycloak en SaaS

Statut : acceptée · Date : 15/10/2026 · Décideur : architecte

## Contexte
`jarvis_finance.md` imposait Keycloak dès le départ. Keycloak est un serveur Java qui consomme 0,5 à 1 Go de mémoire : c'est trop sur un poste de 16 Go qui fait déjà tourner PostgreSQL et Kaem. Mais le SaaS (V2) a besoin de fédération d'identité et d'authentification unique.

## Décision
- **Abstraction d'identité** dans l'API.
- **Édition installée** : identité intégrée. Mots de passe conformes à NIST 800-63B (longueur, pas de règles de composition, pas de rotation forcée), double authentification (TOTP), deux horloges de session.
- **SaaS** : Keycloak, ou tout fournisseur OIDC du client.
- **Les droits métier vivent dans l'application et dans la base**, jamais dans le fournisseur d'identité, qui ne porte que l'identité.

## Conséquences
- Le passage au SaaS ne touche pas aux droits.
- La déconnexion passe par le fournisseur d'identité quand c'est lui qui détient la session, et ramène à l'écran de connexion.

## Liens
EX-PLAT-3, EX-PLAT-4
