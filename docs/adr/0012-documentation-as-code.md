---
icon: lucide/file-check
---

# 0012 — Documentation as code : Markdown, Mermaid, site hors ligne

Statut : acceptée · Date : 15/10/2026 · Décideur : porteur et architecte

## Contexte
Le porteur demande une documentation en Markdown **et** un site web unifié qu'on ouvre d'un geste, avec schémas, diagrammes et Gantt, à la charte Facil. La documentation doit vivre avec le code, sinon elle meurt à la première itération.

## Options
1. Documents Word et PDF.
2. Wiki en ligne.
3. **Markdown versionné, et un site statique généré** (MkDocs Material), avec les diagrammes en Mermaid.

## Décision
Option 3. Organisation de `projet_doc/` :
- **à plat**, les documents uniques (TDR, PRD, glossaire, risques, architecture) ;
- **en sous-dossiers**, les familles de documents (`adr/`, `plans/`, `specs/`).

Le site est **hors ligne** : Mermaid est stocké sur le poste et la recherche fonctionne sans serveur. Le raccourci `Ouvrir la documentation.cmd` construit puis ouvre le site.

**Une construction est refusée si** :
- un nom de client y figure (échec fermé, même si la liste des noms est absente) ;
- une page manque au menu, ou une entrée du menu n'a pas de page ;
- un lien est cassé (mode strict).

## Conséquences
- `projet.md` et les analyses restent à leur place. Ils sont **copiés en lecture seule** dans *Sources* à chaque construction, jamais dupliqués dans le dépôt.
- Les documents à remettre à l'extérieur (TDR en PDF, par exemple) se produisent avec le plugin `documents-pro`, à partir de ces sources.
- L'outil de construction vit dans un environnement isolé (`projet_doc/.outils/venv`), sans installation globale.

## Liens
[ADR 0001](0001-consigner-les-decisions.md) · [Plan de documentation](../plans/plan-documentation.md)
