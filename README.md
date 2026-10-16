# Facil Finance — moteur et packs pays

Documentation projet : `C:\DSF\projet_doc` (ouvrir `Ouvrir la documentation.cmd`). Décisions : ADR 0005 (moteur extrait), 0006 (packs pays), 0013 (codage avec Claude Code).

## Contenu

| Dossier | Rôle |
|---|---|
| `facil_moteur/noyau/` | Lecture des balances et grands livres, formules Excel, rendu PDF — **sans règle de pays**, source unique publiée vers le plugin `compta-ohada` |
| `facil_moteur/packs/` | Format des packs pays : validation, signature Ed25519, résolution des couches OHADA ← zone ← pays, pack en vigueur à la date de clôture |
| `facil_moteur/adaptateurs.py` | Rend aux calculs nationaux encore dans le plugin leurs paramètres lus dans un pack |
| `packs/` | `ohada/2017.1`, `cemac/2025.1`, `CM/2025.1` (préversion), `GQ/2025.1` |
| `outils/` | `facil_pack.py` (valider, signer, résoudre), recettes de conversion, comparaison de formulaires, lecture de DSF publiées en PDF, `verifier_tout.py` |
| `tests/` | Une contre-épreuve par garde ; démonstration sur la DSF publiée de la SIC (Cameroun) |

## Commandes

```
python -m venv .venv && .venv\Scripts\python.exe -m pip install pyyaml cryptography openpyxl pytest pymupdf
.venv\Scripts\python.exe outils\verifier_tout.py             # packs + tests + parité (aussi en crochet de commit)
.venv\Scripts\python.exe outils\facil_pack.py resoudre CM 2025-12-31 --atelier
.venv\Scripts\python.exe outils\publier_vers_plugin.py         # noyau → plugin compta-ohada
```

## Règles

- **Aucune règle de pays dans le moteur** : taux, libellés, lignes et contrôles viennent des packs.
- **Aucun taux sans article** : la validation refuse un paramètre sans article ni source.
- **Le noyau se corrige ici, jamais dans le plugin** : la garde de parité rougit sinon.
- **La clé privée de signature n'est jamais dans le dépôt** : `~/.facil/cles/`.
