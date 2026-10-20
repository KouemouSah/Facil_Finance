# -*- coding: utf-8 -*-
"""Construit le GABARIT VIERGE embarqué de la DEF GE depuis une DEF réellement déposée (dossier pilote).

Le formulaire officiel (51 feuilles, lignes, libellés, mise en forme) est conservé ; toute donnée de l'entité est
purgée : identité (remplacée par des repères que le générateur relie à la page de garde), fiches R1-R3, actionnaires
(note 13), bénéficiaires du TF5, feuille balance, montants (mis à 0 : la cellule reste un repère de montant).
La STRUCTURE DES TOTAUX, qu'un gabarit à zéro ne peut plus prouver, est prouvée ICI sur les montants réels puis figée
dans le fichier annexe (.json) : le générateur la relit en mode gabarit.

Contrôle final bloquant : aucun texte purgé ne subsiste dans le gabarit, ni dans le reste du plugin (hors dist/).
Outil de mainteneur : il lit les fichiers du dossier pilote, qui ne sont PAS dans le plugin.

Usage : python tools/construire_gabarit.py --modele DEF.xlsx --balance B.xls [--grand-livre GL.xls] --exercice 2025
"""
import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import warnings

warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "dsf-syscohada", "scripts")
sys.path.insert(0, SCRIPTS)
import def_modele as dm  # noqa: E402

SORTIE = os.path.join(ROOT, "skills", "dsf-syscohada", "templates")
REPERES = {"D13": "[DENOMINATION SOCIALE]", "D16": "[SIGLE]", "D17": "[ADRESSE]", "D18": "[NIF]"}
A_SAISIR = "[A SAISIR]"
FICHES = ("fiche r1", "fiche r2", "fiche r3")
LIBELLES_COURTS = {"DU", "AU", "E-MAIL", "RCCM", "TOTAL"}


def structure_prouvee(a):
    """Génère une fois sur le modèle RÉEL : chaque total est prouvé par ses montants ; la trace est la structure."""
    g = dm.Generateur(a)
    g.rendre("fr", os.path.join(tempfile.mkdtemp(), "trace.xlsx"))
    return g.trace


def purger(modele, exercice, i18n):
    import openpyxl
    wb = openpyxl.load_workbook(modele)                  # valeurs collées (le modèle n'a pas de formules), styles gardés
    G = dm.Generateur.__new__(dm.Generateur)
    pg = next(w for w in wb.worksheets if dm.norm(w.title) == "page garde")
    ident = {dm.norm(pg[c].value): rep for c, rep in REPERES.items() if isinstance(pg[c].value, str) and pg[c].value.strip()}
    # textes PROPRES À L'ENTITÉ : « noms » (entité, personnes, tiers, adresses, n° de compte) contrôlés partout ;
    # « attributs » (nationalité, catégorie d'actions) contrôlés dans le gabarit seulement : ce sont des mots génériques.
    # La balance, purgée à part, porte surtout des libellés génériques du plan de comptes : non tracée.
    purges = {"noms": set(), "attributs": set()}
    a_saisir = []

    def efface(cell, remplacement=None, trace="noms", vide=False):
        v = cell.value
        if trace and isinstance(v, str) and v.strip():
            purges[trace].add(v.strip())
        cell.value = remplacement if isinstance(v, str) else (0 if dm.num(v) and not vide else None)

    for ws in wb.worksheets:
        t = dm.norm(ws.title)
        # feuilles reconstruites EN ENTIER par le générateur : balance (depuis la balance de l'entité) ; réintégrations
        # (depuis le calcul fiscal ; le modèle n'y donne que l'ordre des comptes) -> vidées, rien n'y sert de repère
        if t.startswith("bg ") or t == "reintegraciones":
            for row in ws.iter_rows(min_row=1 if t.startswith("bg ") else 3):
                for c in row:
                    if type(c).__name__ != "MergedCell" and c.value is not None:
                        efface(c, trace=None, vide=True)
            if t.startswith("bg "):
                ws.title = "BG BALANCE"
            continue
        c0, r0, c1, r1, pa = G.zone(ws)
        h0, h1 = G.entetes(ws, r0, r1)
        roles = dm.roles_colonnes(ws, h0, h1, exercice)
        extra = t in dm.EXTRA_COMPTABLES or t == "note 13"
        # TF5 : une ligne de BÉNÉFICIAIRE (nom en colonne A, absent du dictionnaire du formulaire) est vidée en entier ;
        # les en-têtes et les lignes « nombre / total » restent
        lignes_tf5 = {r for r in range(h1 + 1, ws.max_row + 1) if t == "tf5" and isinstance(ws.cell(r, 1).value, str)
                      and ws.cell(r, 1).value.strip() not in i18n
                      and not dm.norm(ws.cell(r, 1).value).startswith(("nombre", "total"))}
        for row in ws.iter_rows():
            for c in row:
                if type(c).__name__ == "MergedCell" or c.value is None:
                    continue
                v, r = c.value, c.row
                if isinstance(v, str):
                    s = v.strip()
                    if dm.norm(s) in ident:                                   # identité : repère partout
                        purges["noms"].add(s)
                        c.value = ident[dm.norm(s)]
                    elif t in FICHES and (G.cellule_identite(t, c.coordinate) or (
                            s not in i18n and not re.fullmatch(r"Z[A-Z]", s) and s.upper() not in LIBELLES_COURTS
                            and not re.fullmatch(r"\d{2}/\d{2}/\d{4}", s))):
                        efface(c, A_SAISIR)
                    elif t == "note 13" and r > h1 and c.column >= 2 and not dm.ligne_total(s):
                        efface(c, trace="noms" if c.column == 2 else "attributs")   # actionnaires ; nationalité, catégorie
                    elif r in lignes_tf5:
                        efface(c)                                             # bénéficiaire, adresse, NIF
                elif dm.num(v) and not isinstance(v, bool):
                    if (extra and r > 4) or r in lignes_tf5:
                        c.value = 0
                    elif r > h1 and roles.get(c.column):
                        c.value = 0                                           # montant calculé -> repère à zéro
                    elif abs(v) >= 1000 and c.column > 2 and not (r <= h1 and 1990 <= v <= 2100):
                        # montant NON calculé (recopié du modèle), y compris au-dessus de l'en-tête détecté ; les
                        # colonnes 1-2 (codes, n° de compte) et les années d'en-tête restent -> à saisir, fond ambre
                        c.value = 0
                        a_saisir.append(f"{t}|{c.coordinate}")
    for ws in wb.worksheets:                                                  # les fiches : zones d'identité vidées même
        t = dm.norm(ws.title)                                                 # quand la cellule portait un nombre
        if t in FICHES:
            for row in ws.iter_rows():
                for c in row:
                    if type(c).__name__ != "MergedCell" and G.cellule_identite(t, c.coordinate) and dm.num(c.value):
                        c.value = 0
    return wb, purges, a_saisir


def residus(wb, purges, i18n_brut):
    """Textes purgés (≥ 4 caractères, normalisés) qui subsisteraient : dans le gabarit, dans le dictionnaire, dans
    tout fichier texte du plugin. Une présence = échec (le gabarit n'est pas écrit)."""
    def propres(xs):
        c = {dm.norm(p) for p in xs if len(dm.norm(p)) >= 4 and not re.fullmatch(r"[\d\W]+", dm.norm(p))}
        c -= {dm.norm(x) for x in REPERES.values()} | {dm.norm(A_SAISIR)} | {dm.norm(x) for x in LIBELLES_COURTS}
        return c - {dm.norm(k) for k in json.loads(i18n_brut)["es"]}
    noms = propres(purges["noms"])
    cibles = noms | propres(purges["attributs"])
    trouves = []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and dm.norm(c.value) in cibles:
                    trouves.append(f"gabarit {ws.title}!{c.coordinate} « {c.value.strip()[:40]} »")
    texte_i18n = dm.norm(i18n_brut)
    trouves += [f"i18n-def.json : « {x[:12]}… »" for x in noms if len(x) >= 6 and x in texte_i18n]
    return trouves


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--modele", required=True)
    p.add_argument("--balance", required=True)
    p.add_argument("--grand-livre")
    p.add_argument("--exercice", type=int, required=True)
    p.add_argument("--sortie", default=SORTIE)
    x = p.parse_args()
    a = argparse.Namespace(modele=x.modele, balance=x.balance, grand_livre=x.grand_livre, exercice=x.exercice,
                           profil=None, decisions=None, colonne_precedente="N-1", logo=None, langues="fr",
                           sortie=None, pdf=False, pdf_excel=False, pro=False)
    print("== Structure prouvée sur les montants réels")
    trace = structure_prouvee(a)
    print(f"  {len(trace['totaux'])} totaux, {len(trace['refs'])} lignes d'état sans REF")
    print("== Purge des données de l'entité")
    brut = open(dm.I18N, encoding="utf-8").read()
    i18n = json.loads(brut)["es"]
    wb, purges, a_saisir = purger(x.modele, x.exercice, i18n)
    print(f"  {len(purges['noms'])} noms et {len(purges['attributs'])} attributs purgés (identité, fiches R, actionnaires, TF5, balance)")
    reste = residus(wb, purges, brut)
    if reste:
        print("ÉCHEC — données de l'entité encore présentes :")
        for r in reste[:20]:
            print("  ", r)
        return 1
    os.makedirs(x.sortie, exist_ok=True)
    xl = os.path.join(x.sortie, "def_ge_gabarit.xlsx")
    wb.save(xl)
    meta = {"annee": x.exercice, "feuilles": len(wb.worksheets),
            "origine": "DEF GE déposée d'un dossier pilote, purgée ; structure des totaux prouvée sur ses montants",
            "empreinte_gabarit": hashlib.sha256(open(xl, "rb").read()).hexdigest(),
            "totaux": trace["totaux"], "refs": trace["refs"], "a_saisir": sorted(a_saisir)}
    json.dump(meta, open(os.path.join(x.sortie, "def_ge_gabarit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"  → {xl} ({len(wb.worksheets)} feuilles) + def_ge_gabarit.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
