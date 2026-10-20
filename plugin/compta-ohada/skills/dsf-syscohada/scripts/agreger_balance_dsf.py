# -*- coding: utf-8 -*-
"""Agrège une balance générale SYSCOHADA vers les postes (REF) de la DEF/DSF.

1. LECTURE par invariants comptables (detection_balance.py) : balances à 8, 6, 4, 2 ou
   1 colonne, avec ou sans en-tête, .xls/.xlsx/.csv. En cas d'AMBIGUÏTÉ (ex. soldes N-1
   et N côte à côte sans en-tête), le script s'arrête (code 2) : relancer avec --gabarit.
2. CORRESPONDANCE comptes -> postes (references/mapping-comptes-dsf.json, v2, plus long
   préfixe) avec les conventions de signe de la DEF :
     actif    brut = D - C ; amortissements / dépréciations = C - D ; net = brut - amort
     passif   C - D
     résultat C - D (produits positifs, charges négatives)
   - comptes à éclatement (40, 41, 42-47, 48, 52-58) : le SIGNE du solde du compte choisit
     le poste (ex. client créditeur -> DI, banque créditrice -> DR). Niveau COMPTE seulement :
     l'éclatement tiers par tiers exige une balance auxiliaire ;
   - compte 13 : résultat ANTÉRIEUR non affecté tant que la balance n'est pas clôturée
     (classes 6-8 non soldées) -> présenté en CH ; CJ = résultat calculé des classes 6 à 8.
3. TOTAUX (AZ, BZ, CP, DZ, XA à XI…) et CONTRÔLES : actif = passif ; CJ = XI.
   Les comptes non mappés sont listés, jamais ignorés.

Usage :
  python agreger_balance_dsf.py --balance balance.xls
  python agreger_balance_dsf.py --balance b.xlsx --gabarit "4 col. (soldes N-1, soldes N)" --json
"""
import argparse
import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from detection_balance import LAYOUTS, analyse, rapport  # noqa: E402

DEFAULT_MAPPING = os.path.join(HERE, "..", "references", "mapping-comptes-dsf.json")


def read_balance(path, gabarit=None):
    """(lignes N [(compte, solde D-C)], lignes N-1 ou None, détection). Code 2 si illisible ou ambiguë."""
    res = analyse(path, gabarit)
    print(rapport(res), file=sys.stderr)
    if res["statut"] == "illisible":
        raise SystemExit(2)
    if res["statut"] == "ambigu":
        print("Gabarits possibles : " + " | ".join([res["gabarit"]] + res["rivaux"]), file=sys.stderr)
        raise SystemExit(2)
    n = sorted(res["soldes"].items())
    n1 = sorted(res["soldes_n1"].items()) if res.get("soldes_n1") else None
    return n, n1, res


def load_mapping(path):
    """(règles triées par préfixe décroissant, postes). Refuse l'ancien format v1."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if "postes" not in data:
        raise SystemExit(f"{path} : mapping v1 (sans « postes ») — format obsolète et faux, utiliser la v2.")
    return sorted(data["regles"], key=lambda r: len(r["prefixe"]), reverse=True), data["postes"]


def match_rule(compte, regles):
    c = str(compte).strip()
    return next((r for r in regles if c.startswith(r["prefixe"])), None)


INTERPRETATIONS = {
    # défaut = lecture stricte ; un profil d'entreprise peut s'en écarter, l'écart est chiffré
    "compensation_tresorerie": {"defaut": False, "question":
        "Compenser les banques/caisses créditrices avec les débitrices (au lieu de les porter en DR) ? "
        "Contraire au principe de non-compensation du SYSCOHADA ; pratiqué par certaines DEF."},
}


def aggregate(balance, mapping, profil=None):
    """balance : [(compte, solde D-C)] ; mapping : (règles, postes) ; profil : {"interpretations": {...}}.
    Montants au format DEF."""
    regles, postes = mapping
    pi = (profil or {}).get("interpretations", {})
    interp = {k: pi.get(k, v["defaut"]) for k, v in INTERPRETATIONS.items()}
    compense = 0.0
    brut, amort, montant = {}, {}, {}
    non_mappes, eclatements, hors_etats, anterieur = [], [], [], 0.0
    detail = []                                   # (compte, poste, colonne, valeur) : base des notes annexes
    _add = lambda d, k, v: d.__setitem__(k, round(d.get(k, 0.0) + v, 2))
    _col = {id(brut): "brut", id(amort): "amort", id(montant): "montant"}

    def add(d, k, v, compte=None):
        _add(d, k, v)
        if compte is not None:
            detail.append((compte, k, _col[id(d)], round(v, 2)))
    gestion = [s for a, s in balance if a[:1] in "678"]
    cloturee = all(abs(s) < 1 for s in gestion)

    for compte, solde in balance:
        r = match_rule(compte, regles)
        if r is None:
            non_mappes.append({"compte": compte, "solde": round(solde, 2)})
            continue
        if ("debiteur" in r and interp["compensation_tresorerie"] and r["debiteur"] == "BS"
                and r["crediteur"] == "DR" and not r["prefixe"].startswith("56") and solde < 0):
            add(brut, "BS", solde, compte)            # interprétation d'entreprise : compensée dans BS
            compense += -solde
            continue
        if "debiteur" in r:                           # éclatement par le signe du solde
            if solde > 0:
                add(brut, r["debiteur"], solde, compte)
                ref = r["debiteur"]
            else:
                add(montant, r["crediteur"], -solde, compte)
                ref = r["crediteur"]
            if abs(solde) >= 1:
                eclatements.append({"compte": compte, "poste": ref, "solde": round(solde, 2)})
            continue
        nature = r["nature"]
        if nature == "actif":
            add(brut, r["ref"], solde, compte)
        elif nature == "amort":
            add(amort, r["ref"], -solde, compte)
        elif nature in ("passif", "gestion"):
            add(montant, r["ref"], -solde, compte)
        elif nature == "resultat":
            if cloturee:
                add(montant, "CJ", -solde, compte)
            else:                                     # résultat antérieur non affecté
                add(montant, "CH", -solde, compte)
                anterieur += -solde
        elif nature == "hors_etats":
            hors_etats.append({"compte": compte, "solde": round(solde, 2)})

    if not cloturee:
        montant["CJ"] = round(sum(v for k, v in montant.items() if postes.get(k, {}).get("etat") == "resultat"), 2)

    # postes de base -> valeurs ; puis totaux (récursifs)
    par_ref = {}

    def valeur(ref):
        if ref in par_ref:
            return par_ref[ref]
        p = postes.get(ref, {"etat": "?", "libelle": ref})
        if "total" in p:
            parts = [valeur(x) for x in p["total"]]
            v = {"montant": round(sum(x["montant"] for x in parts), 2)}
            if p["etat"] == "actif":
                v["brut"] = round(sum(x.get("brut", 0) for x in parts), 2)
                v["amort"] = round(sum(x.get("amort", 0) for x in parts), 2)
        elif p["etat"] == "actif":
            b, am = brut.get(ref, 0.0), amort.get(ref, 0.0)
            v = {"brut": b, "amort": am, "montant": round(b - am, 2)}
        else:
            v = {"montant": montant.get(ref, 0.0)}
        v.update(libelle=p.get("libelle", ref), note=p.get("note", ""), etat=p.get("etat"))
        par_ref[ref] = v
        return v

    for ref in postes:
        valeur(ref)
    inconnus = sorted((set(brut) | set(amort) | set(montant)) - set(postes))
    par_note = {}
    for ref, v in par_ref.items():
        if v["note"] and "total" not in postes.get(ref, {}):
            par_note[v["note"]] = round(par_note.get(v["note"], 0.0) + v["montant"], 2)

    actif, passif = par_ref["BZ"]["montant"], par_ref["DZ"]["montant"]
    controles = {
        "actif_egal_passif": {"actif": actif, "passif": passif, "ecart": round(actif - passif, 2),
                              "ok": abs(actif - passif) < 1},
        "resultat_bilan_egal_cr": {"CJ": par_ref["CJ"]["montant"], "XI": par_ref["XI"]["montant"],
                                   "ok": cloturee or abs(par_ref["CJ"]["montant"] - par_ref["XI"]["montant"]) < 1},
        "balance_cloturee": cloturee,
    }
    avert = []
    if compense:
        just = (profil or {}).get("justifications", {}).get("compensation_tresorerie")
        avert.append(f"INTERPRÉTATION D'ENTREPRISE (compensation_tresorerie) : {compense:,.2f} de banques/caisses "
                     "créditrices compensés dans BS au lieu d'être portés en DR (lecture stricte : non-compensation). "
                     + (f"Justification : {just}" if just else "Aucune justification consignée."))
    if cloturee:   # classes 6-8 soldées OU absentes : dans les deux cas, pas de compte de résultat
        avert.append("Balance CLÔTURÉE (classes 6-8 soldées ou absentes) : le compte de résultat ne peut pas être "
                     "reconstitué depuis cette balance ; CJ vient du compte 13.")
    if anterieur:
        avert.append(f"Compte 13 : {anterieur:,.2f} de résultat(s) antérieur(s) non affecté(s), présenté(s) en CH. "
                     "Vérifier que l'affectation votée en AG a bien été comptabilisée.")
    if non_mappes:
        avert.append(f"{len(non_mappes)} compte(s) non mappé(s) : à rattacher (les totaux sont incomplets).")
    if inconnus:
        avert.append(f"Postes produits par le mapping mais absents de « postes » : {inconnus}")
    avert.append("Éclatement au niveau COMPTE : sans balance auxiliaire, un tiers débiteur logé dans un compte "
                 "collectif créditeur n'est pas reclassé (ex. avances fournisseurs BH).")
    return {"par_ref": par_ref, "par_note": par_note, "non_mappes": non_mappes, "eclatements": eclatements,
            "interpretations": interp, "detail": detail,
            "hors_etats": hors_etats, "controles": controles, "avertissements": avert,
            "nb_comptes": len(balance), "nb_non_mappes": len(non_mappes)}


def avec_impot(balance, impot, compte_charge="89100000", compte_dette="44100000"):
    """Intègre l'impôt sur le résultat quand la balance ne le porte pas encore (cas du dossier pilote : IS calculé
    dans la DEF, comptabilisé après). Écriture SIMULÉE, non comptabilisée : D 891 / C 441 = impôt dû.
    Si des comptes 89 portent déjà un solde, l'impôt est réputé comptabilisé : rien n'est ajouté et
    l'écart éventuel avec le calcul est signalé. Retourne (balance, info)."""
    deja = round(sum(s for a, s in balance if a.startswith("89")), 2)
    if abs(deja) >= 1:
        ecart = round(deja - impot, 2)
        return list(balance), {"mode": "deja_comptabilise", "montant_balance": deja, "montant_calcule": impot,
                               "ecart": ecart,
                               "message": ("IS déjà comptabilisé en 89 : " + f"{deja:,.2f}"
                                           + ("" if abs(ecart) < 1 else f" ≠ IS calculé {impot:,.2f} (écart {ecart:+,.2f}) : à rapprocher"))}
    if abs(impot) < 1:
        return list(balance), {"mode": "aucun", "montant_calcule": impot, "message": "Aucun impôt à intégrer."}
    b = list(balance) + [(compte_charge, round(impot, 2)), (compte_dette, -round(impot, 2))]
    return b, {"mode": "ecriture_simulee", "montant_calcule": impot, "comptes": [compte_charge, compte_dette],
               "message": (f"IS intégré par ÉCRITURE SIMULÉE (non comptabilisée) : débit {compte_charge} / crédit "
                           f"{compte_dette} = {impot:,.2f}. À passer en comptabilité AVANT la clôture.")}


def _ligne(ref, v):
    if v["etat"] == "actif":
        return (f"  {ref}  {v['libelle'][:44]:44s} brut {v.get('brut', 0):>18,.2f}  amort {v.get('amort', 0):>18,.2f}"
                f"  net {v['montant']:>18,.2f}")
    return f"  {ref}  {v['libelle'][:44]:44s} {v['montant']:>18,.2f}"


def main():
    p = argparse.ArgumentParser(description="Balance -> postes de la DEF/DSF (lecture par invariants, mapping v2).")
    p.add_argument("--balance", required=True)
    p.add_argument("--mapping", default=DEFAULT_MAPPING)
    p.add_argument("--gabarit", default=None, choices=list(LAYOUTS),
                   help="impose la lecture des colonnes (après ambiguïté signalée)")
    p.add_argument("--profil", default=None, help="profil d'entreprise (interprétations, faits, justifications)")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    n, n1, det = read_balance(a.balance, a.gabarit)
    mapping = load_mapping(a.mapping)
    profil = json.load(open(a.profil, encoding="utf-8")) if a.profil else None
    res = aggregate(n, mapping, profil)
    res["n1"] = aggregate(n1, mapping, profil) if n1 else None
    res["detection"] = {k: det[k] for k in ("gabarit", "confiance", "feuille", "cumuls_prouves",
                                             "parents_avec_solde_propre", "a_confirmer", "equilibre")}
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=2)); return
    print(f"Comptes lus : {res['nb_comptes']} | non mappés : {res['nb_non_mappes']}"
          + (" | N-1 disponible" if n1 else " | N-1 : absent de cette balance (à reprendre de la DEF précédente)"))
    for etat, titre in (("actif", "BILAN — ACTIF"), ("passif", "BILAN — PASSIF"), ("resultat", "COMPTE DE RÉSULTAT")):
        print(f"\n{titre}")
        for ref, v in res["par_ref"].items():
            if v["etat"] == etat and (abs(v["montant"]) >= 0.5 or abs(v.get("brut", 0)) >= 0.5):
                print(_ligne(ref, v))
    c = res["controles"]
    print(f"\nContrôles : actif = passif {'OK' if c['actif_egal_passif']['ok'] else 'ÉCART ' + format(c['actif_egal_passif']['ecart'], ',.2f')}"
          f" | CJ = XI {'OK' if c['resultat_bilan_egal_cr']['ok'] else 'ÉCART'}")
    for w in res["avertissements"]:
        print("⚠ " + w)
    for x in res["non_mappes"][:20]:
        print(f"   non mappé : {x['compte']:12s} {x['solde']:>18,.2f}")


if __name__ == "__main__":
    main()
