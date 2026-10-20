"""Calendrier du projet : une source (plans/calendrier.yml), des pages qui en dérivent.

Toute date de planning écrite dans une page « planifiante » est remplacée par une marque
{{cal:...}} que la construction résout. Écrire une date à la main dans ces pages fait échouer
la construction : deux copies d'une même date finissent toujours par diverger.
"""
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

import yaml

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"]

# Pages dont TOUTES les dates de planning viennent du calendrier.
PAGES_PLANIFIANTES = ("tdr.md", "index.md", "plans/roadmap.md", "plans/feuille-de-route.md",
                      "plans/sprints.md", "plans/plan-documentation.md", "plans/couverture-pays.md",
                      "plans/index.md")

# Dates écrites à la main : « 19-23/10 », « 30/11 », « 30/11/2026 », « T2 2027 », « novembre 2026 ».
_DATE_EN_DUR = re.compile(
    r"\b\d{1,2}(?:-\d{1,2})?/\d{2}(?:/\d{4})?\b|\bT[1-4](?:-T[1-4])? 20\d\d\b|\b(?:"
    + "|".join(MOIS) + r") 20\d\d\b", re.IGNORECASE)
_MARQUE = re.compile(r"\{\{cal:([a-z-]+)(?::([A-Za-z0-9_-]+))?\}\}")


class ErreurCalendrier(Exception):
    pass


def _d(valeur) -> dt.date:
    return valeur if isinstance(valeur, dt.date) else dt.date.fromisoformat(str(valeur))


def court(d: dt.date) -> str:
    return f"{d.day:02d}/{d.month:02d}"


def long(d: dt.date) -> str:
    return f"{d.day:02d}/{d.month:02d}/{d.year}"


def periode(debut: dt.date, fin: dt.date) -> str:
    if debut.month == fin.month:
        return f"{debut.day:02d}-{fin.day:02d}/{fin.month:02d}"
    return f"{court(debut)}-{court(fin)}"


class Calendrier:
    def __init__(self, chemin: Path, produit: str = "Projet", couleurs: dict | None = None):
        self.produit = produit
        # Couleurs de la charte (doc-projet.yml) ; valeurs Facil par défaut.
        c = {"principale": "#397004", "decor": "#498E03", "claire": "#7CC242", "nuit": "#2b5503", "voile": "#eef6e6",
             "pale": "#c6e3a4", "encre": "#1d3502", "forte": "#a8d67a", "legere": "#e6f2d9"}
        c.update({k: v for k, v in (couleurs or {}).items() if v})
        self.c = c
        self.donnees = yaml.safe_load(chemin.read_text(encoding="utf-8"))
        self.jalons = {k: _d(v) for k, v in self.donnees["jalons"].items()}
        self.preuves = {k: _d(v) for k, v in (self.donnees.get("preuves") or {}).items()}
        self.periodes: dict[str, tuple[dt.date, dt.date]] = {}
        for e in self.donnees["etapes"]:
            self.periodes[e["id"]] = (_d(e["debut"]), _d(e["fin"]))
            for t in e.get("taches", []):
                if ":" in t["libelle"]:
                    raise ErreurCalendrier(f"tâche {t['id']} : « : » interdit dans un libellé (Mermaid le lit comme séparateur)")
                self.periodes[t["id"]] = (_d(t["debut"]), _d(t["fin"]))
                if not (_d(e["debut"]) <= _d(t["debut"]) <= _d(t["fin"]) <= _d(e["fin"])):
                    raise ErreurCalendrier(f"tâche {t['id']} hors de son étape {e['id']}")
        self.pays_trimestre = {}
        for tri in self.donnees["trimestres"]:
            for code in tri.get("pays", []):
                if code in self.pays_trimestre:
                    raise ErreurCalendrier(f"pays {code} dans deux trimestres")
                self.pays_trimestre[code] = tri["libelle"]
        # Le suivi par pays (ou par lot) est facultatif : un projet sans « pays_noms » n'en a pas.
        self.noms = self.donnees.get("pays_noms") or {}
        manquants = set(self.noms) - set(self.pays_trimestre)
        if manquants:
            raise ErreurCalendrier("pays sans trimestre de disponibilité : " + ", ".join(sorted(manquants)))
        if max(self.jalons.values()) != self.jalons["livraison"]:
            raise ErreurCalendrier("un jalon tombe après la livraison")

    # -- résolution des marques ------------------------------------------------------------
    def resoudre(self, genre: str, cle: str | None) -> str:
        try:
            if genre == "periode":
                return periode(*self.periodes[cle])
            if genre == "fin":
                return court(self.periodes[cle][1])
            if genre == "jalon":
                return court(self.jalons[cle])
            if genre == "jalon-long":
                return long(self.jalons[cle])
            if genre == "preuve":
                return long(self.preuves[cle])
            if genre == "mois":
                d = self.jalons.get(cle) or self.preuves[cle]
                return f"{MOIS[d.month - 1]} {d.year}"
            if genre == "pays":
                return self.pays_trimestre[cle]
            if genre == "gantt":
                return self.gantt()
            if genre == "roadmap-frise":
                return self.frise()
            if genre == "roadmap-tableau":
                return self.tableau_roadmap()
        except KeyError:
            raise ErreurCalendrier(f"marque inconnue : {{{{cal:{genre}:{cle}}}}}") from None
        raise ErreurCalendrier(f"genre de marque inconnu : {genre}")

    def appliquer(self, texte: str) -> str:
        # Deux passes : un bloc généré (frise) peut contenir lui-même des marques.
        for _ in range(2):
            texte = _MARQUE.sub(lambda m: self.resoudre(m.group(1), m.group(2)), texte)
        return texte

    # -- blocs générés ------------------------------------------------------------------------
    def gantt(self) -> str:
        c = self.c
        init = "%%{init: " + json.dumps({
            "gantt": {"barHeight": 26, "barGap": 6, "fontSize": 13, "sectionFontSize": 13, "leftPadding": 170,
                      "topPadding": 40, "gridLineStartPadding": 40, "numberSectionStyles": 2},
            "themeVariables": {"taskBkgColor": c["claire"], "taskBorderColor": c["principale"], "taskTextColor": c["encre"],
                               "taskTextLightColor": c["encre"], "taskTextOutsideColor": c["encre"],
                               "activeTaskBkgColor": c["decor"], "activeTaskBorderColor": c["nuit"],
                               "doneTaskBkgColor": "#c9c9c9", "doneTaskBorderColor": "#8a8a8a",
                               "critBkgColor": "#e0a030", "critBorderColor": "#9a5b00", "sectionBkgColor": c["voile"],
                               "altSectionBkgColor": "#ffffff", "gridColor": "#dddddd", "todayLineColor": "#c62828",
                               "fontSize": "13px"}}, ensure_ascii=False) + "}%%"
        lignes = ["```mermaid", init, "gantt",
                  f"    title {self.produit} — livraison le {long(self.jalons['livraison'])}",
                  "    dateFormat YYYY-MM-DD", "    axisFormat %d/%m", "    tickInterval 1week", ""]
        for e in self.donnees["etapes"]:
            lignes.append(f"    section {e['nom']}")
            for t in e.get("taches", []):
                etat = f"{t['etat']}, " if t.get("etat") else ""
                lignes.append(f"    {t['libelle']} :{etat}{t['id']}, {t['debut']}, {t['fin']}")
            for j in e.get("jalons", []):
                lignes.append(f"    {j['libelle']} :milestone, m_{j['id']}, {self.jalons[j['id']]}, 0d")
        lignes.append("```")
        return "\n".join(lignes)

    def frise(self) -> str:
        c = self.c
        init = "%%{init: " + json.dumps({"theme": "base", "themeVariables": {
            "fontSize": "14px", "cScale0": c["forte"], "cScaleLabel0": c["encre"], "cScalePeer0": c["principale"],
            "cScale1": c["pale"], "cScaleLabel1": c["encre"], "cScalePeer1": c["decor"],
            "cScale2": c["legere"], "cScaleLabel2": c["encre"], "cScalePeer2": c["claire"],
            "cScaleInv0": c["principale"], "cScaleInv1": c["decor"], "cScaleInv2": c["claire"],
            "git0": c["principale"], "git1": c["decor"], "git2": c["claire"]}}, ensure_ascii=False) + "}%%"
        lignes = ["```mermaid", init, "timeline",
                  f"    title {self.produit} — roadmap (confiance décroissante vers la droite)"]
        annee_courante = None
        for tri in self.donnees["trimestres"]:
            annee = tri["libelle"].split()[-1]
            if annee != annee_courante:
                lignes.append(f"    section {annee}")
                annee_courante = annee
            elements = list(tri["resultats"])
            if tri.get("pays"):
                elements.append("Packs disponibles · " + ", ".join(self.noms.get(c, c) for c in tri["pays"]))
            # Dans une frise Mermaid, « : » sépare les éléments : on n'en met jamais dans un texte.
            for el in elements:
                if ":" in _MARQUE.sub("", el):
                    raise ErreurCalendrier(f"« : » interdit dans un résultat de la roadmap : {el}")
            lignes.append(f"        {tri['libelle']} : " + " : ".join(elements))
        lignes.append("```")
        return "\n".join(lignes)

    def tableau_roadmap(self) -> str:
        lignes = ["| Trimestre | Thème | Résultats attendus | Packs pays disponibles | Confiance |",
                  "|---|---|---|---|---|"]
        for tri in self.donnees["trimestres"]:
            pays = ", ".join(self.noms.get(c, c) for c in tri.get("pays", [])) or "—"
            lignes.append(f"| **{tri['libelle']}** | {tri['theme']} | " + " ; ".join(tri["resultats"])
                          + f" | {pays} | {tri['confiance']} |")
        return "\n".join(lignes)


def verifier_dates_en_dur(pages: dict[str, str]) -> None:
    """Aucune date de planning écrite à la main dans les pages planifiantes. Exceptions : la ligne
    de statut d'un document (sa date de rédaction) et les constats datés marqués « constaté le »."""
    fautes = []
    for rel, texte in pages.items():
        for n, ligne in enumerate(texte.splitlines(), 1):
            if 'class="statut' in ligne or "constaté le" in ligne:
                continue
            m = _DATE_EN_DUR.search(_MARQUE.sub("", ligne))
            if m:
                fautes.append(f"{rel}:{n} « {m.group(0)} »")
    if fautes:
        raise ErreurCalendrier("date de planning écrite à la main (utiliser {{cal:…}}) :\n  " + "\n  ".join(fautes[:15]))
