# -*- coding: utf-8 -*-
"""Garde du moteur de détection des balances et de ses deux consommateurs.

Vérité = balance SYNTHÉTIQUE générée ici de façon déterministe (écritures en partie double,
donc équilibrée par construction). Aucune donnée client n'est embarquée dans le plugin.
Chaque variante présente la MÊME comptabilité dans un format différent ; la garde exige :
  - soldes identiques à la vérité, compte par compte (par classe si les comptes sont tronqués) ;
  - équilibre ; statut attendu (« ambigu » quand — et seulement quand — c'est indécidable) ;
  - N-1 / ouverture restitués quand le format les porte.
Balance réelle facultative : DSF_BALANCE_REELLE=<chemin> DSF_RESULTAT_REEL=<résultat attendu>.

Lancer : python tests/test_detection_balance.py      (code 0 = tout conforme)
"""
import csv
import json
import os
import random
import subprocess
import sys
import tempfile
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "lib"))
from detection_balance import analyse  # noqa: E402

AGREGER = os.path.join(ROOT, "skills", "dsf-syscohada", "scripts", "agreger_balance_dsf.py")
REVISION = os.path.join(ROOT, "skills", "revision-comptes-ohada", "scripts", "dossier_revision.py")
CLASSER = os.path.join(ROOT, "skills", "dsf-syscohada", "scripts", "classer_documents.py")

# --------------------------------------------------------------------------- vérité synthétique
COMPTES = {
    "10130000": "Capital souscrit appelé versé", "11100000": "Réserve légale", "12100000": "Report à nouveau",
    "16200000": "Emprunts bancaires", "24110000": "Matériel industriel", "24500000": "Matériel de transport",
    "28410000": "Amort. matériel industriel", "28450000": "Amort. matériel de transport",
    "32100000": "Matières premières", "40110001": "Fournisseurs locaux", "40110002": "Fournisseurs étrangers",
    "41110001": "Clients", "41141000": "Clients État", "42200000": "Personnel, rémunérations dues",
    "43130000": "Caisse de sécurité sociale", "44100000": "État, impôt sur les bénéfices",
    "44320000": "TVA facturée", "44520000": "TVA récupérable",
    # 47100000 / 47100010 : une fois tronqués (variante 5), « 471000 » devient un compte PARENT
    # portant son propre solde, sous la ligne de cumul « 471 » — cas qui exige de résoudre
    # les parents du plus long au plus court.
    "47100000": "Débiteurs divers", "47100010": "Débiteurs divers - avances chantier", "52110000": "Banque A", "52120000": "Banque B",
    "57110000": "Caisse siège", "60420000": "Carburants", "60440000": "Matériaux de construction",
    "61100000": "Transports sur achats", "62200000": "Locations", "63100000": "Frais bancaires",
    "64100000": "Impôts et taxes", "66100000": "Rémunérations du personnel", "68130000": "Dotations amortissements",
    "70510000": "Travaux facturés", "70600000": "Services vendus", "77100000": "Intérêts reçus",
    "84100000": "Produits HAO", "89100000": "Impôt sur les bénéfices",
}


def verite():
    rnd = random.Random(20260928)
    ouv, mvt = defaultdict(lambda: [0.0, 0.0]), defaultdict(lambda: [0.0, 0.0])

    def ecr(book, d, c, m):
        book[d][0] += m; book[c][1] += m

    # à-nouveaux : bilan seulement (classes 1-5), équilibrés par construction
    for d, c, m in [("24110000", "10130000", 900e6), ("24500000", "16200000", 450e6), ("52110000", "11100000", 120e6),
                    ("41110001", "40110001", 300e6), ("32100000", "28410000", 80e6), ("12100000", "28450000", 60e6),
                    ("41141000", "44100000", 210e6), ("57110000", "40110002", 15e6)]:
        ecr(ouv, d, c, m)
    flux = [("41110001", "70510000"), ("41141000", "70510000"), ("41110001", "70600000"), ("52110000", "41110001"),
            ("52120000", "41141000"), ("60420000", "40110001"), ("60440000", "40110002"), ("61100000", "40110001"),
            ("40110001", "52110000"), ("40110002", "52120000"), ("62200000", "52110000"), ("63100000", "52120000"),
            ("66100000", "42200000"), ("42200000", "52110000"), ("66100000", "43130000"), ("43130000", "52120000"),
            ("64100000", "57110000"), ("57110000", "52110000"), ("44520000", "40110001"), ("41110001", "44320000"),
            ("44320000", "44520000"), ("68130000", "28410000"), ("68130000", "28450000"), ("52110000", "77100000"),
            ("52120000", "84100000"), ("89100000", "44100000"), ("44100000", "52110000"),
            ("47100000", "52110000"), ("47100010", "52120000")]
    for _ in range(400):
        d, c = rnd.choice(flux)
        ecr(mvt, d, c, round(rnd.uniform(1e5, 5e7), rnd.choice([0, 0, 2])))
    t = {}
    for a in COMPTES:
        o, m = ouv[a], mvt[a]
        s = (o[0] - o[1]) + (m[0] - m[1])
        t[a] = dict(od=max(o[0] - o[1], 0), ok=max(o[1] - o[0], 0), md=m[0], mk=m[1],
                    cd=o[0] + m[0], ck=o[1] + m[1], sd=max(s, 0), sk=max(-s, 0), solde=s, ouverture=o[0] - o[1])
    return t


# --------------------------------------------------------------------------- formats
def fr(x):
    s = f"{abs(x):,.2f}".replace(",", " ").replace(".", ",")
    return f"({s})" if x < 0 else s


def es(x):
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def xlsx(path, rows, extra_sheets=()):
    from openpyxl import Workbook
    wb = Workbook(); ws = wb.active; ws.title = "Balance"
    for r in rows:
        ws.append(r)
    for name, rr in extra_sheets:
        w2 = wb.create_sheet(name, 0)
        for r in rr:
            w2.append(r)
    wb.save(path)


def csvf(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        csv.writer(f, delimiter=";").writerows(rows)


def cumul_lines(t, level, shift, net_only):
    """Lignes de cumul « à la Sage » : code tronqué, libellé en colonne décalée, solde des soldes."""
    out = {}
    for a, v in t.items():
        g = out.setdefault(a[:level], defaultdict(float))
        for k2 in ("od", "ok", "md", "mk", "cd", "ck"):
            g[k2] += v[k2]
        g["s"] += v["solde"]
    rows = {}
    for code, g in out.items():
        vals = [g["od"], g["ok"], g["md"], g["mk"], g["cd"], g["ck"], max(g["s"], 0), max(-g["s"], 0)]
        rows[code] = [code, f"CUMUL {code}"] + vals if shift else [code, "", f"CUMUL {code}"] + vals
    return rows


def variantes(t, d):
    V = []
    # 1) 8 colonnes hiérarchique, SANS en-tête, cumuls décalés d'une colonne, date d'édition parasite
    rows = [["Balance générale 8 colonnes"], [46210.0, "EDITEUR", 0.41]]
    c3 = cumul_lines(t, 3, True, True); c2 = cumul_lines(t, 2, True, True)
    last3 = last2 = None
    for a in sorted(t):
        if last3 and a[:3] != last3:
            rows.append(c3[last3])
        if last2 and a[:2] != last2:
            rows.append(c2[last2])
        v = t[a]; last3, last2 = a[:3], a[:2]
        rows.append([a, "", COMPTES[a], v["od"], v["ok"], v["md"], v["mk"], v["cd"], v["ck"], v["sd"], v["sk"]])
    rows += [c3[last3], c2[last2], ["Total bilan", 1, 2, 3]]
    V.append(("8 col. hiérarchique sans en-tête, cumuls décalés", "v1.xlsx", rows, xlsx, "ok", "exact"))
    # 2) 6 colonnes, en-tête sur 2 lignes, zéros vides, balance en 2e feuille (1re = page de garde)
    rows = [["", "", "Solde d'ouverture", "", "Mouvements", "", "Solde de clôture", ""],
            ["Compte", "Intitulé", "Débit", "Crédit", "Débit", "Crédit", "Débit", "Crédit"]]
    for a in sorted(t):
        v = t[a]
        rows.append([a, COMPTES[a]] + [x or None for x in (v["od"], v["ok"], v["md"], v["mk"], v["sd"], v["sk"])])
    V.append(("6 col. xlsx, zéros vides, 2e feuille", "v2.xlsx", rows,
              lambda p, r: xlsx(p, r, [("Garde", [["SOCIETE X"], ["Exercice 2025"]])]), "ok", "exact"))
    # 3) 4 colonnes CSV, en-têtes espagnols, montants texte 1.234.567,89
    rows = [["Cuenta", "Descripción", "Debe", "Haber", "Saldo deudor", "Saldo acreedor"]]
    rows += [[a, COMPTES[a], es(t[a]["cd"]), es(t[a]["ck"]), es(t[a]["sd"]), es(t[a]["sk"])] for a in sorted(t)]
    V.append(("4 col. CSV espagnol, montants texte", "v3.csv", rows, csvf, "ok", "exact"))
    # 4) 2 colonnes, compte+libellé dans une cellule, totaux de classe intercalés
    rows = [["SOLDES AU 31/12/2025"], ["Compte", "Débit", "Crédit"]]; cur = None; td = tc = 0
    for a in sorted(t):
        if cur and a[0] != cur:
            rows.append([f"Total classe {cur}", td, tc]); td = tc = 0
        cur = a[0]; td += t[a]["sd"]; tc += t[a]["sk"]
        rows.append([f"{a} {COMPTES[a]}", t[a]["sd"], t[a]["sk"]])
    rows.append([f"Total classe {cur}", td, tc])
    V.append(("2 col. compte+libellé collés, totaux", "v4.xlsx", rows, xlsx, "ok", "exact"))
    # 5) 1 colonne signée, parenthèses, sans en-tête, cumuls à 3 chiffres, comptes tronqués (6 chiffres)
    rows = [["Etat imprimé le 07/07/2026"], []]; seen = set()
    for a in sorted(t):
        if a[:3] not in seen:
            seen.add(a[:3])
            rows.append([a[:3], "cumul", fr(sum(t[b]["solde"] for b in t if b[:3] == a[:3]))])
        rows.append([a[:6] + a[6:].rstrip("0"), COMPTES[a], fr(t[a]["solde"])])
    V.append(("1 col. signée, parenthèses, sans en-tête, tronqués", "v5.csv", rows, csvf, "ok", "classe"))
    # 6) 4 colonnes ouverture + soldes sans en-tête : tranchable (classes 6-7 nulles à l'ouverture)
    rows = [[a, COMPTES[a], t[a]["od"], t[a]["ok"], t[a]["sd"], t[a]["sk"]] for a in sorted(t)]
    V.append(("4 col. ouverture+soldes sans en-tête", "v6.xlsx", rows, xlsx, "ok", "exact"))
    # 7) soldes N-1 + N sans en-tête : INDÉCIDABLE -> ambigu
    n1 = {a: (t[a]["ouverture"] if a[0] not in "678" else t[a]["solde"] * 0.5) for a in t}
    n1["12100000"] -= sum(v for a, v in n1.items() if a[0] in "678")
    rows = [[a, COMPTES[a], max(n1[a], 0), max(-n1[a], 0), t[a]["sd"], t[a]["sk"]] for a in sorted(t)]
    V.append(("soldes N-1 + N sans en-tête (piège)", "v7.xlsx", rows, xlsx, "ambigu", "exact"))
    for name, fn, rows, w, exp, cmp in V:
        w(os.path.join(d, fn), rows)
    return V, n1


def by_class(s):
    d = defaultdict(float)
    for a, x in s.items():
        d[a[0]] += x
    return {k: round(v, 2) for k, v in d.items()}


def run(script, *args):
    cp = subprocess.run([sys.executable, script, *args, "--json"], capture_output=True, text=True, encoding="utf-8")
    return cp.returncode, (json.loads(cp.stdout) if cp.returncode == 0 else None), cp.stderr


def main():
    t = verite()
    truth = {a: v["solde"] for a, v in t.items()}
    assert abs(sum(truth.values())) < 1e-3, "fixture déséquilibrée"
    d = os.environ.get("VARIANTES_DIR") or tempfile.mkdtemp()
    os.makedirs(d, exist_ok=True)
    V, n1 = variantes(t, d)
    checks = []

    def check(nom, ok, detail=""):
        checks.append(ok)
        print(f"  {'OK   ' if ok else 'ÉCHEC'} {nom}" + (f"  — {detail}" if detail and not ok else ""))

    print("== Détection (lib/detection_balance.py)")
    for name, fn, rows, w, exp, cmp in V:
        r = analyse(os.path.join(d, fn))
        s = r.get("soldes", {})
        same = (all(abs(s.get(a, 0) - x) < 0.01 for a, x in truth.items()) and len(s) == len(truth)) if cmp == "exact" \
            else by_class(s) == by_class(truth)
        check(f"{name:52s} -> {r.get('gabarit', '-')}, {r['statut']}",
              same and r["statut"] == exp and abs(r.get("equilibre", 1)) < 1,
              f"statut={r['statut']} attendu={exp} équilibre={r.get('equilibre')} soldes_ok={same}")
    r = analyse(os.path.join(d, "v7.xlsx"), gabarit="4 col. (soldes N-1, soldes N)")
    check("ambiguïté levée par --gabarit : N et N-1 exacts", r["statut"] == "ok"
          and all(abs(r["soldes"][a] - truth[a]) < .01 and abs(r["soldes_n1"][a] - n1[a]) < .01 for a in truth))
    r = analyse(os.path.join(d, "v2.xlsx"))
    check("ouverture restituée (6 col.)", r.get("feuille") == "Balance"
          and all(abs(r["soldes_ouverture"][a] - t[a]["ouverture"]) < .01 for a in t))

    print("== Consommateurs")
    code, out, err = run(AGREGER, "--balance", os.path.join(d, "v1.xlsx"))
    check(f"agreger_balance_dsf : 8 col. lue, {len(t)} comptes", code == 0 and out["nb_comptes"] == len(t), err[-200:])
    r = analyse(os.path.join(d, "v5.csv"))
    check("compte parent à solde propre gardé (471000), cumul 471 écarté",
          "471000" in r["parents_avec_solde_propre"] and "471" not in r["soldes"], str(r.get("parents_avec_solde_propre")))
    code, out, err = run(AGREGER, "--balance", os.path.join(d, "v7.xlsx"))
    check("agreger_balance_dsf : ambiguïté -> arrêt (code 2), jamais de choix silencieux", code == 2, f"code={code}")
    code, out, err = run(AGREGER, "--balance", os.path.join(d, "v7.xlsx"), "--gabarit", "4 col. (soldes N-1, soldes N)")
    check("agreger_balance_dsf : --gabarit -> N-1 agrégé", code == 0 and out["n1"] is not None, err[-200:])
    code, out, err = run(REVISION, "--balance", os.path.join(d, "v7.xlsx"), "--gabarit", "4 col. (soldes N-1, soldes N)")
    check("dossier_revision : N-1 tiré des soldes N-1", code == 0 and out["source_n1"] == "soldes N-1", err[-200:])
    code, out, err = run(REVISION, "--balance", os.path.join(d, "v2.xlsx"))
    gest = [l for c in (out or {}).get("cycles", {}).values() for l in c["lignes"] if l["compte"][0] in "67"]
    check("dossier_revision : N-1 = ouverture, gestion N-1 déclarée inconnue",
          code == 0 and out["source_n1"] == "ouverture" and gest and all(l["solde_n1"] is None and not l["alerte"] for l in gest),
          err[-200:])
    code, out, err = run(CLASSER, "--fichiers", os.path.join(d, "v1.xlsx"))
    check("classer_documents : balance SANS en-tête reconnue par invariants",
          code == 0 and out["documents"][0]["role"] == "balance", str(out)[:200])
    # grand livre : porte « Débit / Crédit / Solde » comme une balance, mais ses lignes sont des écritures datées
    gl = [["Grand-livre général"], ["Date", "Journal", "Pièce", "Libellé", "Débit", "Crédit", "Solde débiteur"]]
    for i, a in enumerate(sorted(t)):
        gl.append([a, COMPTES[a]])
        gl.append([45688.0 + i, "ODG", f"ODG-{i:04d}", "Écriture", t[a]["md"], t[a]["mk"], None])
        gl.append([a, "Total compte au", 46022.0, t[a]["md"], t[a]["mk"]])
    xlsx(os.path.join(d, "gl.xlsx"), gl)
    code, out, err = run(CLASSER, "--fichiers", os.path.join(d, "gl.xlsx"))
    check("classer_documents : grand livre classé grand_livre, pas balance",
          code == 0 and out["documents"][0]["role"] == "grand_livre", str(out)[:300])
    # balance PARTIELLE (classes 1 à 4 seulement) : déséquilibrée, mais reste une balance
    part = [["Compte", "Intitulé", "Solde débit", "Solde crédit"]]
    part += [[a, COMPTES[a], t[a]["sd"], t[a]["sk"]] for a in sorted(t) if a[0] in "1234"]
    xlsx(os.path.join(d, "partielle.xlsx"), part)
    code, out, err = run(CLASSER, "--fichiers", os.path.join(d, "partielle.xlsx"))
    check("classer_documents : balance partielle (déséquilibrée) reste une balance",
          code == 0 and out["documents"][0]["role"] == "balance", str(out)[:300])

    reel = os.environ.get("DSF_BALANCE_REELLE")
    if reel:
        print("== Balance réelle (facultatif)")
        r = analyse(reel)
        res = -sum(x for a, x in r["soldes"].items() if a[0] in "678")
        attendu = float(os.environ.get("DSF_RESULTAT_REEL", "nan"))
        check(f"{os.path.basename(reel)} -> {r['gabarit']}, résultat {res:,.2f}",
              r["statut"] == "ok" and abs(r["equilibre"]) < 1 and abs(res - attendu) < 1, f"attendu {attendu:,.2f}")

    print(f"\n{sum(checks)}/{len(checks)} contrôles conformes")
    sys.exit(0 if all(checks) else 1)


if __name__ == "__main__":
    main()
