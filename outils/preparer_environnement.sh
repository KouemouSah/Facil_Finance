#!/usr/bin/env bash
# Prépare une session Claude Code WEB (Linux) : environnement virtuel et dépendances du moteur, du plugin et de la doc.
# Lancé par le crochet SessionStart de .claude/settings.json quand CLAUDE_CODE_REMOTE=true. Idempotent.
set -euo pipefail
cd "${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi
PY=.venv/bin/python
$PY -m pip install --quiet --upgrade pip
$PY -m pip install --quiet -r requirements-dev.txt
$PY -m pip install --quiet -r plugin/compta-ohada/serveur/requirements.txt
$PY -m pip install --quiet --no-deps rapidocr_onnxruntime==1.4.4
$PY -m pip install --quiet -r docs/requirements.txt

# L'environnement virtuel devient le Python des commandes suivantes de la session.
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export VIRTUAL_ENV=$PWD/.venv" >> "$CLAUDE_ENV_FILE"
  echo "export PATH=$PWD/.venv/bin:\$PATH" >> "$CLAUDE_ENV_FILE"
fi
echo "Environnement prêt : $($PY --version), moteur + plugin + documentation."
