@echo off
chcp 65001 >nul
rem Construit puis ouvre la documentation (hors ligne). Fichier fourni par le plugin doc-projet.
rem Premier lancement : crée l'environnement isolé .outils\venv (aucune installation globale).
setlocal
cd /d "%~dp0"
if not exist ".outils\venv\Scripts\python.exe" (
  echo Préparation de l'outil de documentation, une seule fois...
  python -m venv ".outils\venv" || goto :erreur
  ".outils\venv\Scripts\python.exe" -m pip install -q "mkdocs-material==9.*" || goto :erreur
)
".outils\venv\Scripts\python.exe" "outils\construire_site.py" --ouvrir || goto :erreur
exit /b 0
:erreur
echo.
echo La documentation n'a pas pu être construite. Le message ci-dessus indique pourquoi.
pause
exit /b 1
