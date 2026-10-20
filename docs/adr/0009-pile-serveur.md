---
icon: lucide/file-check
---

# 0009 — Pile serveur : FastAPI, PostgreSQL, Valkey, Caddy

Statut : acceptée · Date : 15/10/2026 · Décideur : architecte

## Contexte
`projet.md` (§ 6.2) a acté Python et FastAPI. Le moteur existant est en Python. Il fallait compléter ces choix en tenant compte de la licence et de l'embarquabilité.

## Décision
| Brique | Choix | Raison | Écartée |
|---|---|---|---|
| API | FastAPI, SQLAlchemy 2, Alembic, Pydantic 2 | Le moteur est déjà en Python ; contrat OpenAPI généré | — |
| Base | PostgreSQL relocalisable, embarqué | Transactions, MVCC, sécurité au niveau des lignes (prépare le SaaS) | SQLite : ni multi-utilisateurs sérieux, ni sécurité au niveau des lignes |
| File de tâches | **Valkey** (BSD) | Embarquable, licence compatible avec un produit fermé | Redis ≥ 7.4 (licences RSAL / SSPL) |
| Serveur web | **Caddy** | Un seul binaire, TLS automatique ou autorité locale | Nginx : configuration TLS manuelle |
| Interface | Application monopage **exportée en fichiers statiques** | Pas de Node.js à l'exécution | Next.js avec rendu côté serveur |
| Stockage de fichiers | Système de fichiers | Simple, sauvegardable | MinIO (AGPL) |

## Conséquences
- Toute la pile tient dans le contenu autoportant de l'[ADR 0003](0003-distribution-autoportante.md).
- Toute nouvelle dépendance passe par l'inventaire des licences (R7).

## Liens
[Architecture § 2](../architecture.md#2-conteneurs-c4-niveau-2)
