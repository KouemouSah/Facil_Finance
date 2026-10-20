---
icon: lucide/book-open
---

# Manuels et supports de Facil DEF

<span class="statut statut--valide">à jour</span> · Version 0.13.0 · 20/10/2026

Supports de l'extension livrée [Facil DEF](facil-def.md), en français (« DSF ») et en espagnol (« DEF »). Les captures d'écran montrent l'interface française ; le nom du client, ses identifiants et les données personnelles y sont masqués par un aplat.

## Français

| Document | Contenu | Télécharger |
|---|---|---|
| Manuel d'utilisation | 20 pages : installation, configuration, dossier de travail, formulaire, validation, livrables, situations particulières | [PDF](https://kouemousah.github.io/Facil_Finance/manuels/Manuel-utilisation-Facil-DEF.pdf) |
| Présentation commerciale | 6 diapositives : constat, parcours, garanties, fiche produit, appel à l'action | [PDF](https://kouemousah.github.io/Facil_Finance/manuels/Presentation-commerciale-Facil-DEF.pdf) |
| Flyer | une page : démonstration de 15 minutes sur les fichiers du client, analyse des 3 derniers exercices en bonus | [PDF](https://kouemousah.github.io/Facil_Finance/manuels/Flyer-Facil-DEF.pdf) |

## Español

| Documento | Contenido | Descargar |
|---|---|---|
| Manual de uso | 20 páginas | [PDF](https://kouemousah.github.io/Facil_Finance/manuels/es/Manual-de-uso-Facil-DEF.pdf) |
| Presentación comercial | 6 diapositivas | [PDF](https://kouemousah.github.io/Facil_Finance/manuels/es/Presentacion-comercial-Facil-DEF.pdf) |
| Folleto | una página | [PDF](https://kouemousah.github.io/Facil_Finance/manuels/es/Folleto-Facil-DEF.pdf) |

## Reconstruire les supports

Les sources sont dans [`manuel/redaction/`](https://github.com/KouemouSah/Facil_Finance/tree/develop/manuel/redaction) ; les PDF sont versionnés dans `manuel/livrable/` parce que leur rendu fidèle exige Word, PowerPoint et Edge sous Windows.

| Support | Source | Commande (poste Windows, plugin documents-pro) |
|---|---|---|
| Manuel FR / ES | `document.yaml`, `document-es.yaml` | `generer.py construire document.yaml -o ../livrable` |
| Présentation FR / ES | `presentation.yaml`, `presentation-es.yaml` | `generer.py construire presentation.yaml -o ../livrable` |
| Flyer FR / ES | `flyer/construire_flyer.py`, `flyer/textes_es.py` | `python flyer/construire_flyer.py [es]` |

La version espagnole du flyer refuse de se construire si un texte français n'est plus trouvé : une retouche de la version française ne laisse pas de français dans l'espagnole.
