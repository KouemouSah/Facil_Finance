#!/usr/bin/env sh
# Construit puis ouvre la documentation (hors ligne), sous Linux et macOS. Fourni par le plugin doc-projet.
# Premier lancement : crée l'environnement isolé .outils/venv (aucune installation globale).
set -e
cd "$(dirname "$0")"
if [ ! -x ".outils/venv/bin/python" ]; then
  echo "Préparation de l'outil de documentation, une seule fois..."
  python3 -m venv .outils/venv
  .outils/venv/bin/python -m pip install -q "mkdocs-material==9.*"
fi
.outils/venv/bin/python outils/construire_site.py --ouvrir
