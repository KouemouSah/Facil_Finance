---
icon: lucide/file-check
---

# 0007 — Kaem : IA locale sur processeur, Gemma 4 E4B téléchargé à l'installation

Statut : acceptée sous réserve du banc d'évaluation · Date : 15/10/2026 · Décideur : porteur (décisions D3, D4, D5) et architecte

## Contexte
Le porteur veut une assistante, **Kaem**, à voix féminine, qui fonctionne **en local** sur des PC **sans carte graphique, avec au moins 16 Go de RAM**, et qui se télécharge à l'installation. Les données financières ne doivent pas quitter le poste.

## Options
| Option | Pour | Contre |
|---|---|---|
| Modèle dans l'installeur de base | Rien à télécharger | Installeur de 5 à 6 Go, imposé même à qui n'en veut pas |
| **Modèle téléchargé à l'installation, optionnel** | Installeur léger ; choix du client ; version hors ligne sur clé USB | Un téléchargement de 5 à 6 Go |
| LLM hébergé (cloud) | Rapide, sans matériel | Données hors du pays ; dépendance au réseau |

## Décision
Modèle local **téléchargé à l'installation** (ou fourni sur clé USB), vérifié par empreinte et signature.

| Rôle | Choix par défaut | Licence |
|---|---|---|
| LLM | **Gemma 4 E4B-it**, quantifié en 4 bits (≈ 4 à 5 Go), via llama.cpp | Apache 2.0 |
| Écoute | Gemma 4 E4B lui-même (il accepte l'audio en entrée) ; Whisper (MIT) si le banc le justifie | Apache 2.0 |
| Voix | Kokoro, voix féminines FR, ES et PT | Apache 2.0 |

**Banc d'évaluation obligatoire avant de figer le choix** :
- **Matériel** : 3 PC de référence sans GPU, 16 Go de RAM.
- **Mesures, en FR, ES et PT** : latence avant le premier mot ; jetons par seconde ; réussite des appels d'outils ; précision de l'écoute sur 100 phrases comptables ; qualité des rédactions, notée par un expert.
- **Concurrents** : Qwen3.5 4B (Apache 2.0) et Phi-4-mini (MIT).
- **Repli** : Gemma 4 E2B.

## Conséquences
- Réponses **en flux continu**. Les rédactions longues partent en tâche de fond, avec une notification.
- Le modèle se charge à la première demande et se libère après 10 min d'inactivité.
- Le paquet IA est refusé sous 16 Go de RAM, avec un message clair. Le produit reste complet sans lui.
- **Registre des licences** des modèles et des voix, tenu en CI.
- **Marque** : un logiciel de comptabilité nommé « KAEM Accounts » existe déjà (KAEM Technologies, Inde). Kaem reste un nom **dans le produit** jusqu'à la recherche d'antériorité (R5).

## Liens
EX-IA-1, EX-IA-3, EX-IA-5 · R3, R5, R9 · [ADR 0008](0008-ia-ne-calcule-ni-ne-valide.md)

*Sources consultées le 15/10/2026 : [fiche Gemma 4 E4B-it](https://huggingface.co/google/gemma-4-E4B-it), [Google AI Edge — Gemma 4](https://developers.google.com/edge/litert-lm/models/gemma-4). Les vitesses ne sont pas mesurées : aucune n'est promise avant le banc.*
