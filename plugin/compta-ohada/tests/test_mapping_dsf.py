# -*- coding: utf-8 -*-
"""Garde de la correspondance comptes -> postes de la DEF (mapping v2 + agreger_balance_dsf).

Les montants ATTENDUS sont calculés À LA MAIN (voir commentaires), jamais par le code testé.
Balance jouet équilibrée : chaque règle délicate y figure une fois.
Lancer : python tests/test_mapping_dsf.py      (code 0 = conforme)
"""
import csv
import json
import os
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGREGER = os.path.join(ROOT, "skills", "dsf-syscohada", "scripts", "agreger_balance_dsf.py")
MAPPING = os.path.join(ROOT, "skills", "dsf-syscohada", "references", "mapping-comptes-dsf.json")

# soldes D - C ; Σ = 0 (le 57 porte le solde d'équilibre : +620)
BALANCE = {
    "10130000": -1000, "11100000": -100,
    "12100000": 50,        # report à nouveau DÉBITEUR (déficitaire) -> CH négatif
    "13100000": -30,       # résultat antérieur non affecté (balance non clôturée) -> CH
    "24100000": 600, "24500000": 300, "28410000": -200, "28450000": -100,
    "40110001": -250,
    "40110002": 20,        # fournisseur DÉBITEUR -> BH (avance versée), pas en déduction de DJ
    "41110001": 400,
    "41110002": -60,       # client CRÉDITEUR -> DI (avance reçue)
    "44100000": -80, "44520000": 15,
    "52110000": 90,
    "52120000": -40,       # banque CRÉDITRICE -> DR (pas de compensation avec l'autre banque)
    "56100000": -70, "57110000": 620,
    "60440000": 300, "60331000": 10, "61100000": 7, "62200000": 50, "64100000": 3,
    "66100000": 100, "68130000": 20,
    "70510000": -610, "78100000": -5, "84100000": -40,
}
# Résultat = -(Σ classes 6-8) = -(300+10+7+50+3+100+20-610-5-40) = 165
ATTENDU = {
    # passif (C - D)
    "CA": 1000, "CF": 100, "CG": 0,
    "CH": -20,             # 12 : -50 ; 13 : +30
    "CJ": 165,
    "CP": 1245,            # 1000 + 100 - 20 + 165
    "DI": 60, "DJ": 250, "DK": 80, "DR": 110,   # DR = 40 (52 créditeur) + 70 (56)
    "DP": 390, "DT": 110, "DZ": 1745,
    # actif net (brut - amort)
    "AM": 400, "AN": 200, "AI": 600, "AZ": 600,
    "BH": 20, "BI": 400, "BJ": 15, "BG": 435, "BK": 435,
    "BS": 710,             # 90 + 620 (la banque créditrice n'est PAS compensée)
    "BT": 710, "BZ": 1745,
    # compte de résultat (C - D : charges négatives)
    "TC": 610, "XB": 610,
    "RE": -300, "RF": -10, "RG": -7, "RH": -50, "RI": -3, "RK": -100, "RL": -20,
    "TI": 5, "TO": 40,
    "XC": 245,             # 610 - 300 - 10 - 7 - 50 - 3 + 5
    "XD": 145, "XE": 125, "XG": 125, "XH": 40, "XI": 165,
}
BRUT_AMORT = {"AM": (600, 200), "AN": (300, 100)}
# Codes FAUX de la v1 qui ne doivent plus jamais réapparaître
INTERDITS = {"RG_fin", "RH_hao", "RW", "RZ"}


def run(path, *extra):
    cp = subprocess.run([sys.executable, AGREGER, "--balance", path, "--json", *extra],
                        capture_output=True, text=True, encoding="utf-8")
    if cp.returncode:
        raise SystemExit(cp.stderr)
    return json.loads(cp.stdout)


def write(path, bal):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Compte", "Solde débit", "Solde crédit"])
        for a, s in bal.items():
            w.writerow([a, max(s, 0), max(-s, 0)])


def main():
    assert sum(BALANCE.values()) == 0, "balance jouet déséquilibrée"
    d = tempfile.mkdtemp()
    ok = []

    def check(nom, cond, detail=""):
        ok.append(cond)
        print(f"  {'OK   ' if cond else 'ÉCHEC'} {nom}" + ("" if cond else f"  — {detail}"))

    p = os.path.join(d, "jouet.csv"); write(p, BALANCE)
    r = run(p)
    pr = r["par_ref"]
    print("== Postes (valeurs calculées à la main)")
    for ref, v in ATTENDU.items():
        check(f"{ref} = {v}", abs(pr[ref]["montant"] - v) < 0.01, f"obtenu {pr[ref]['montant']}")
    for ref, (b, a) in BRUT_AMORT.items():
        check(f"{ref} brut {b} / amort {a}", pr[ref]["brut"] == b and pr[ref]["amort"] == a,
              f"obtenu {pr[ref].get('brut')} / {pr[ref].get('amort')}")
    print("== Contrôles")
    check("actif = passif", r["controles"]["actif_egal_passif"]["ok"], str(r["controles"]))
    check("CJ = XI", r["controles"]["resultat_bilan_egal_cr"]["ok"], str(r["controles"]))
    check("aucun compte non mappé", r["nb_non_mappes"] == 0, str(r["non_mappes"]))
    check("éclatements tracés (40110002 -> BH, 41110002 -> DI, 52120000 -> DR)",
          {("40110002", "BH"), ("41110002", "DI"), ("52120000", "DR")}
          <= {(e["compte"], e["poste"]) for e in r["eclatements"]}, str(r["eclatements"]))
    check("résultat antérieur non affecté signalé", any("non affecté" in w for w in r["avertissements"]))
    mp = json.load(open(MAPPING, encoding="utf-8"))
    codes = {x.get("ref") for x in mp["regles"]} | {x.get(k) for x in mp["regles"] for k in ("debiteur", "crediteur")}
    check("aucun code inventé de la v1", not (codes & INTERDITS), str(codes & INTERDITS))
    check("tous les postes produits sont définis", all(c in mp["postes"] for c in codes if c), str(codes - set(mp["postes"])))

    print("== Balance clôturée (classes 6-8 soldées, résultat viré au 13)")
    clo = {a: s for a, s in BALANCE.items() if a[0] not in "678"}
    clo["13100000"] = -30 - 165
    p2 = os.path.join(d, "cloturee.csv"); write(p2, clo)
    r2 = run(p2)
    check("CJ = 195 (13 entier) et CH = -50", r2["par_ref"]["CJ"]["montant"] == 195 and r2["par_ref"]["CH"]["montant"] == -50,
          f"CJ {r2['par_ref']['CJ']['montant']} CH {r2['par_ref']['CH']['montant']}")
    check("clôture détectée et signalée", r2["controles"]["balance_cloturee"]
          and any("CLÔTURÉE" in w for w in r2["avertissements"]))
    check("actif = passif (clôturée)", r2["controles"]["actif_egal_passif"]["ok"])

    print("== Profil : compensation de trésorerie (interprétation d'entreprise)")
    pf = os.path.join(d, "profil.json")
    json.dump({"interpretations": {"compensation_tresorerie": True}}, open(pf, "w", encoding="utf-8"))
    r3 = run(p, "--profil", pf)
    # 52120000 créditeur (40) compensé : BS = 710 - 40 = 670 ; DR = 70 (le 56 n'est jamais compensé)
    check("BS = 670, DR = 70 (56 non compensé)", r3["par_ref"]["BS"]["montant"] == 670 and r3["par_ref"]["DR"]["montant"] == 110 - 40,
          (r3["par_ref"]["BS"]["montant"], r3["par_ref"]["DR"]["montant"]))
    check("actif = passif maintenu", r3["controles"]["actif_egal_passif"]["ok"])
    check("compensation signalée et chiffrée (40,00)",
          any("compensation_tresorerie" in w and "40.00" in w for w in r3["avertissements"]), r3["avertissements"][:2])

    print("== Intégration de l'IS (balance sans impôt)")
    sys.path.insert(0, os.path.dirname(AGREGER))
    import agreger_balance_dsf as agr
    mp = agr.load_mapping(MAPPING)
    b2, info = agr.avec_impot(list(BALANCE.items()), 40)
    r4 = agr.aggregate(b2, mp)["par_ref"]
    # résultat avant impôt 165 -> RS = -40, XI = CJ = 125 ; DK = 80 + 40 = 120 ; actif = passif maintenu (1745)
    check("écriture simulée signalée", info["mode"] == "ecriture_simulee" and "À passer" in info["message"], info)
    check("RS = -40, XI = CJ = 125, DK = 120",
          (r4["RS"]["montant"], r4["XI"]["montant"], r4["CJ"]["montant"], r4["DK"]["montant"]) == (-40, 125, 125, 120),
          (r4["RS"]["montant"], r4["XI"]["montant"], r4["CJ"]["montant"], r4["DK"]["montant"]))
    check("bilan toujours équilibré (DZ = BZ = 1745)", r4["DZ"]["montant"] == r4["BZ"]["montant"] == 1745)
    b3, info3 = agr.avec_impot(b2, 50)       # impôt déjà en 89 (40) : rien ajouté, écart signalé
    check("IS déjà comptabilisé : pas de double, écart -10 signalé", len(b3) == len(b2) and info3["ecart"] == -10, info3)

    print(f"\n{sum(ok)}/{len(ok)} contrôles conformes")
    sys.exit(0 if all(ok) else 1)


if __name__ == "__main__":
    main()
