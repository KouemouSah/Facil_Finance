# -*- coding: utf-8 -*-
"""Génère references/mapping-comptes-dsf.md DEPUIS mapping-comptes-dsf.json (source unique).

La v1 avait une doc et un JSON divergents (la doc disait une chose, le script en exécutait
une autre). La doc est désormais DÉRIVÉE : ne jamais l'éditer à la main.
  python tools/gen_mapping_md.py          régénère
  python tools/gen_mapping_md.py --check  code 1 si la doc n'est pas à jour (appelé par package.py)
"""
import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(ROOT, "skills", "dsf-syscohada", "references")
SRC = os.path.join(REF, "mapping-comptes-dsf.json")
DST = os.path.join(REF, "mapping-comptes-dsf.md")


def render():
    m = json.load(open(SRC, encoding="utf-8"))
    meta, postes = m["_meta"], m["postes"]
    out = [
        "# Correspondance comptes SYSCOHADA → postes de la DEF/DSF",
        "",
        "> **FICHIER GÉNÉRÉ** depuis `mapping-comptes-dsf.json` par `tools/gen_mapping_md.py` — ne pas éditer.",
        f"> Version {meta['version']} ({meta['date']}). {meta['reference']}",
        "",
        "## Conventions",
        "",
    ]
    out += [f"- **{k}** : {v}" for k, v in meta["conventions"].items()]
    for etat, titre in (("actif", "Bilan — actif"), ("passif", "Bilan — passif"), ("resultat", "Compte de résultat")):
        out += ["", f"## {titre}", "", "| REF | Poste | Note | Comptes (préfixes) |", "|---|---|---|---|"]
        for ref, p in postes.items():
            if p["etat"] != etat:
                continue
            if "total" in p:
                comptes = "= " + " + ".join(p["total"])
            else:
                parts = []
                for r in m["regles"]:
                    if r.get("ref") == ref:
                        parts.append(r["prefixe"] + (" (amort./dépréc.)" if r.get("nature") == "amort" else ""))
                    if r.get("debiteur") == ref:
                        parts.append(r["prefixe"] + " si débiteur")
                    if r.get("crediteur") == ref:
                        parts.append(r["prefixe"] + " si créditeur")
                comptes = ", ".join(parts) or "—"
            lib = f"**{p['libelle']}**" if "total" in p else p["libelle"]
            out.append(f"| {ref} | {lib} | {p.get('note', '')} | {comptes} |")
    hors = [r["prefixe"] for r in m["regles"] if r.get("nature") == "hors_etats"]
    out += ["", "## Hors des états", "", f"Classes/préfixes signalés sans être agrégés : {', '.join(hors)}.", "",
            "## Limites connues", "",
            "- L'éclatement par signe se fait au niveau du **compte**. Un tiers débiteur logé dans un compte collectif "
            "créditeur (ex. avances fournisseurs) n'est reclassé qu'avec une **balance auxiliaire**.",
            "- Le N-1 d'une DEF vient de la DEF précédente déposée, pas de la balance N (sauf balance comparative).",
            "- Validé au franc près contre la DEF GE 2025 déposée du dossier pilote, écarts expliqués : "
            "la garde de référence du dossier pilote (hors plugin).", ""]
    return "\n".join(out)


def main(check):
    txt = render()
    cur = open(DST, encoding="utf-8").read() if os.path.exists(DST) else ""
    if check:
        if cur != txt:
            print("  [DIVERGENCE] mapping-comptes-dsf.md n'est pas à jour — lancer tools/gen_mapping_md.py")
            return 1
        print("  mapping-comptes-dsf.md : conforme au JSON")
        return 0
    open(DST, "w", encoding="utf-8").write(txt)
    print(f"  écrit : {os.path.relpath(DST, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
