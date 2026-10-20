# -*- coding: utf-8 -*-
"""Construit le RUNTIME EMBARQUÉ du plugin : Python officiel « embeddable » pour Windows + dépendances précompilées,
dans <plugin>/runtime/. L'utilisateur n'a RIEN à installer : ni Python, ni paquet ; rien n'est écrit dans le registre
ni dans un Python existant. Le serveur MCP, le formulaire, le hook et la ligne de commande tournent sur ce runtime.

Étapes (outil de MAINTENEUR, réseau requis une fois) :
  1. télécharge python-<V>-embed-amd64.zip depuis python.org (HTTPS), en contrôle l'empreinte après téléchargement
     et la consigne dans runtime/RUNTIME.json ;
  2. l'extrait dans runtime/, déclare Lib\\site-packages dans le fichier ._pth ;
  3. installe serveur/requirements.txt dans runtime/Lib/site-packages en ROUES BINAIRES seulement, pour cp<V>/win_amd64
     (pip d'un Python de construction, jamais dans son propre environnement) ;
  4. vérifie : le runtime importe openpyxl, xlrd, PIL, pymupdf, mcp, et le moteur OCR (cv2, numpy, rapidocr).
Pourquoi pas un exécutable « figé » (PyInstaller) : les scripts du plugin trouvent leurs données (gabarit, dictionnaire,
paramètres fiscaux) à côté d'eux ; figés, ces chemins cassent. Ici, les scripts tournent tels quels.

Usage : python tools/construire_runtime.py [--version 3.13.7] [--forcer]
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNTIME = os.path.join(ROOT, "runtime")
REQ = os.path.join(ROOT, "serveur", "requirements.txt")
REQ_OCR = os.path.join(ROOT, "serveur", "requirements-ocr.txt")
VERIF = ("import openpyxl, xlrd, PIL, pymupdf, mcp, json, cv2, numpy, rapidocr_onnxruntime; "
         "print(json.dumps({'ok': True}))")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--version", default="3.13.7")
    p.add_argument("--forcer", action="store_true")
    a = p.parse_args()
    V = a.version
    court = "".join(V.split(".")[:2])                      # 3.13.7 -> 313
    etat = os.path.join(RUNTIME, "RUNTIME.json")
    req_sha = hashlib.sha256((sha256(REQ) + sha256(REQ_OCR)).encode()).hexdigest()   # les deux listes
    if not a.forcer and os.path.exists(etat):
        e = json.load(open(etat, encoding="utf-8"))
        if e.get("version") == V and e.get("requirements_sha256") == req_sha:
            print(f"runtime à jour (Python {V}, dépendances inchangées)")
            return 0
    if os.path.isdir(RUNTIME):
        shutil.rmtree(RUNTIME)
    os.makedirs(RUNTIME)
    url = f"https://www.python.org/ftp/python/{V}/python-{V}-embed-amd64.zip"
    zp = os.path.join(RUNTIME, "..", f"python-{V}-embed-amd64.zip")
    print(f"== Téléchargement {url}")
    urllib.request.urlretrieve(url, zp)
    empreinte = sha256(zp)
    with zipfile.ZipFile(zp) as z:
        z.extractall(RUNTIME)
    os.remove(zp)
    pth = os.path.join(RUNTIME, f"python{court}._pth")
    lignes = open(pth, encoding="utf-8").read().splitlines()
    if "Lib\\site-packages" not in lignes:
        lignes.insert(lignes.index(".") if "." in lignes else len(lignes), "Lib\\site-packages")
    # « import site » : traite les .pth de site-packages (pywin32, requis par mcp sous Windows, s'y déclare)
    lignes = ["import site" if l.strip() == "#import site" else l for l in lignes]
    open(pth, "w", encoding="utf-8").write("\n".join(lignes) + "\n")
    sp = os.path.join(RUNTIME, "Lib", "site-packages")
    os.makedirs(sp)
    print("== Dépendances (roues binaires cp%s / win_amd64)" % court)
    cmd = [sys.executable, "-m", "pip", "install", "--no-cache-dir", "--disable-pip-version-check", "--target", sp,
           "--python-version", V, "--implementation", "cp", "--platform", "win_amd64", "--only-binary=:all:", "-r", REQ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-2000:] + r.stderr[-2000:])
        print("ÉCHEC : dépendances non installables en roues binaires")
        return 1
    # moteur OCR : paquet en Python pur figé, installé sans dépendances (déjà là) et sans le contrôle de version
    # Python qu'il déclare à tort (voir serveur/requirements-ocr.txt) — la preuve est test_ocr_def.py sur ce runtime
    r = subprocess.run(cmd[:cmd.index("-r")] + ["--no-deps", "--ignore-requires-python", "-r", REQ_OCR],
                       capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-2000:] + r.stderr[-2000:])
        print("ÉCHEC : moteur OCR non installable")
        return 1
    for base, dirs, _ in os.walk(sp):                      # caches de compilation : régénérés au besoin
        for d in list(dirs):
            if d == "__pycache__":
                shutil.rmtree(os.path.join(base, d), ignore_errors=True)
                dirs.remove(d)
    py = os.path.join(RUNTIME, "python.exe")
    v = subprocess.run([py, "-c", VERIF], capture_output=True, text=True)
    if v.returncode or '"ok": true' not in v.stdout:
        print(v.stdout + v.stderr)
        print("ÉCHEC : le runtime n'importe pas ses dépendances")
        return 1
    taille = sum(os.path.getsize(os.path.join(b, f)) for b, _, fs in os.walk(RUNTIME) for f in fs)
    json.dump({"version": V, "source": url, "zip_sha256": empreinte, "requirements_sha256": req_sha,
               "taille_octets": taille}, open(etat, "w", encoding="utf-8"), indent=1)
    print(f"  → runtime/ : Python {V}, {taille / 1e6:.0f} Mo, dépendances importables")
    return 0


if __name__ == "__main__":
    sys.exit(main())
