# -*- coding: utf-8 -*-
"""Lecture LOCALE d'une DEF scannée (PDF images seules) : bilan et compte de résultat, colonnes N et N-1.

Rien ne quitte le poste : OCR RapidOCR (onnxruntime) embarqué. Un chiffre lu n'est jamais pris tel quel :
  1. orientation de chaque page (le bilan paysage est numérisé tourné de 90°) — par la GÉOMÉTRIE : codes de ligne à
     gauche de leur libellé (le texte, lui, se lit dans tous les sens : RapidOCR redresse chaque ligne) ;
  2. colonnes = traits verticaux du formulaire ; rangées = codes de ligne (AD, AE…), recalés sur l'ordre OFFICIEL
     quand l'OCR les lit mal (« AO » pour « AD ») ;
  3. décalage vertical des montants MESURÉ (constaté : une demi-ligne sous le libellé) ; le rattachement ambigu
     (ligne du dessus ou du dessous) est tranché par les formules, côté par côté ;
  4. le « - » imprimé à part, trop petit pour l'OCR, est cherché dans les pixels ;
  5. PREUVE par les formules SYSCOHADA (actif = passif, sous-totaux, soldes du compte de résultat, résultat = CJ,
     brut − amortissements = net) ; une case d'une formule fausse est relue seule ; un signe incohérent peut être
     DÉDUIT (marqué tel). Jamais un chiffre calculé à la place d'un chiffre lu.
Chaque montant sort avec son statut : prouvé, ou à vérifier par l'utilisateur.

Mise au point : DEF de test synthétique « scannée » (tests/) et deux DEF réelles numérisées (non versionnées).
Usage : python ocr_def.py <pdf> <sortie.json>     (code 0 = lu ; écrit aussi l'avancement sur la sortie standard)
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time

REF = re.compile(r"^[A-Z]{2}$")
DICO = re.compile(r"[a-záéíóúñç]{5,}", re.I)
SEQUENCES = [s.split() for s in (
    "AD AE AF AG AH AI AJ AK AL AM AN AP AQ AR AS AZ BA BB BG BH BI BJ BK BQ BR BS BT BU BZ",
    "CA CB CD CE CF CG CH CJ CL CM CP DA DB DC DD DF DH DI DJ DK DM DN DP DQ DR DT DV DZ",
    "TA RA RB XA TB TC TD XB TE TF TG TH TI RC RD RE RF RG RH RI RJ XC RK XD TJ RL XE TK TL TM RM RN XF "
    "XG TN TO RO RP XH RQ RS XI")]
REFS_ETATS = {c for s in SEQUENCES for c in s}
# « | » : présentations admises. Les avances sur immobilisations (AP) sont à part du total AI en SYSCOHADA révisé,
# DANS AI sur la DEF de Guinée équatoriale (constaté sur deux DEF déposées).
BILAN = [("BZ", "+DZ"), ("AZ", "+AD+AI+AP+AQ|+AD+AI+AQ"), ("AD", "+AE+AF+AG+AH"),
         ("AI", "+AJ+AK+AL+AM+AN|+AJ+AK+AL+AM+AN+AP"), ("AQ", "+AR+AS"),
         ("BK", "+BA+BB+BG"), ("BG", "+BH+BI+BJ"), ("BT", "+BQ+BR+BS"), ("BZ", "+AZ+BK+BT+BU"),
         ("CP", "+CA-CB+CD+CE+CF+CG+CH+CJ+CL+CM"), ("DD", "+DA+DB+DC"), ("DF", "+CP+DD"),
         ("DP", "+DH+DI+DJ+DK+DM+DN"), ("DT", "+DQ+DR"), ("DZ", "+DF+DP+DT+DV")]
CR = [("XA", "+TA-RA-RB"), ("XB", "+TA+TB+TC+TD"), ("XC", "+XB-RA-RB+TE+TF+TG+TH+TI-RC-RD-RE-RF-RG-RH-RI-RJ"),
      ("XD", "+XC-RK"), ("XE", "+XD+TJ-RL"), ("XF", "+TK+TL+TM-RM-RN"), ("XG", "+XE+XF"), ("XH", "+TN+TO-RO-RP"),
      ("XI", "+XG+XH-RQ-RS"), ("XI", "+CJ")]
FORMULES = BILAN + CR
VARIATIONS = ("RB", "RD", "RF")                         # variations de stocks : leur signe porte le sens
VERSION = 1                                             # change si la lecture change : le cache est alors relu
_OCR = None


def disponible():
    """Le moteur OCR est-il installé (extension complète) ? Vérifié SANS l'importer : le serveur MCP ne doit pas
    charger ces DLL pendant qu'il lit son entrée (blocage constaté) ; la lecture tourne dans un processus à part."""
    import importlib.util
    return all(importlib.util.find_spec(m) is not None for m in ("cv2", "numpy", "rapidocr_onnxruntime"))


def _ocr():
    global _OCR
    if _OCR is None:
        from rapidocr_onnxruntime import RapidOCR
        _OCR = RapidOCR()
    return _OCR


# ------------------------------------------------------------------------------------------------- page
def geo(b):
    xs, ys = [p[0] for p in b], [p[1] for p in b]
    return {"x0": min(xs), "x1": max(xs), "y": (min(ys) + max(ys)) / 2, "h": max(ys) - min(ys)}


def jetons(r):
    return [dict(geo(b), txt=t.strip(), conf=float(c)) for b, t, c in (r or [])]


def refs_de(T):
    """Codes de ligne : deux majuscules d'un état SYSCOHADA, avec un libellé à leur DROITE sur la même ligne."""
    libs = [t for t in T if len(t["txt"]) >= 6 and DICO.search(t["txt"])]
    return [t for t in T if REF.match(t["txt"]) and t["txt"] in REFS_ETATS
            and any(abs(l["y"] - t["y"]) < t["h"] * 0.8 and 0 <= l["x0"] - t["x1"] < 450 for l in libs)]


def image(page, dpi=300):
    import numpy as np
    pix = page.get_pixmap(dpi=dpi)
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]


def orienter(img):
    """Sens de lecture (0, 90, 270, 180°) : boîtes horizontales et codes à gauche de leur libellé."""
    import numpy as np

    def essai(k):
        im = np.ascontiguousarray(np.rot90(img, k))
        T = jetons(_ocr()(im)[0])
        return k, im, T, len(refs_de(T)), sum(1 for t in T if t["x1"] - t["x0"] > t["h"]) / max(len(T), 1)
    # texte HORIZONTAL : page droite ou à l'envers (0° / 180°) ; texte VERTICAL : 90° ou 270° — deux essais au plus
    e0 = essai(0)
    candidats = [e0] + ([essai(2)] if e0[3] < 3 else []) if e0[4] > 0.6 else [essai(1), essai(3)]
    k, im, T, _, _ = max(candidats, key=lambda e: (e[3], e[4]))
    return k, im, T


def traits_verticaux(img):
    import cv2
    import numpy as np
    g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    b = cv2.adaptiveThreshold(g, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 25, 15)
    H = b.shape[0]
    ver = cv2.morphologyEx(b, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (1, H // 40)))
    prof = ver.sum(axis=0) / 255
    # seuil RELATIF au trait le plus net (un scan entrecoupe les traits : 10 % de la hauteur au mieux, constaté), et
    # le plus petit des deux seuils (un cadre épais ne doit pas masquer les traits fins des colonnes)
    idx = np.where(prof > max(min(prof.max() * 0.5, H * 0.10), H * 0.03))[0]
    out = []
    for i in idx:
        if out and i - out[-1][-1] <= 6:
            out[-1].append(i)
        else:
            out.append([i])
    return [int(np.mean(g)) for g in out]


def recaler(marques):
    """Codes mal lus : alignement global (programmation dynamique) des marques lues sur la séquence OFFICIELLE des
    lignes. Une marque parasite ou un code non lu ne décale pas le reste."""
    lus = [m["txt"].upper() for m in marques]
    seq = max(SEQUENCES, key=lambda s: sum(1 for c in lus if c in s))

    def sim(a, b):                                      # « AO » ~ « AD », « C6 » ~ « CG »
        return 3 if a == b else 1 if len(a) == 2 and (a[0] == b[0] or a[1] == b[1]) else -1
    n, m_, TROU = len(lus), len(seq), -1
    S = [[0] * (m_ + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        S[i][0] = S[i - 1][0] + TROU
    for j in range(1, m_ + 1):
        S[0][j] = S[0][j - 1] + TROU
    for i in range(1, n + 1):
        for j in range(1, m_ + 1):
            S[i][j] = max(S[i - 1][j - 1] + sim(lus[i - 1], seq[j - 1]), S[i - 1][j] + TROU, S[i][j - 1] + TROU)
    i, j = n, m_
    while i > 0 and j > 0:
        if S[i][j] == S[i - 1][j - 1] + sim(lus[i - 1], seq[j - 1]):
            marques[i - 1]["code"] = seq[j - 1]
            i, j = i - 1, j - 1
        elif S[i][j] == S[i - 1][j] + TROU:
            i -= 1
        else:
            j -= 1
    return [m for m in marques if m.get("code")]


def signe_moins(img, x_case, x_chiffres, yc, h):
    """Le « - » imprimé à part, entre le trait de la case et les chiffres, cherché dans les pixels À LA HAUTEUR DES
    CHIFFRES, traits verticaux effacés. Mesuré à 300 dpi : tiret de 8 × 5 px pour un texte de 39 px, isolé. Un trait
    de séparation de ligne (2 px, qui part du bord gauche de la zone) n'en est pas un."""
    import cv2
    import numpy as np
    x0, x1 = max(int(x_case) - int(h), 0), int(x_chiffres) - 2
    y0, y1 = int(yc - h * 0.45), int(yc + h * 0.45)
    if x1 - x0 < 6 or y1 - y0 < 4:
        return False
    b = (cv2.cvtColor(img[max(y0, 0):y1, x0:x1], cv2.COLOR_RGB2GRAY) < 140).astype(np.uint8)
    b = cv2.subtract(b, cv2.morphologyEx(b, cv2.MORPH_OPEN,
                                         cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(int(h * 0.8), 3)))))
    n, _, st, cen = cv2.connectedComponentsWithStats(b, 8)
    for k in range(1, n):
        x, y, w, hh, _ = st[k]
        if x > 0 and hh >= 3 and h * 0.15 <= w <= h * 1.6 and hh <= max(h * 0.25, 3) and w >= 1.3 * hh \
                and abs(cen[k][1] - (yc - y0)) < h * 0.3:
            return True
    return False


def relire(img, x0, x1, y0, y1):
    """Texte d'une case seule, découpée entre ses traits et agrandie ('' = vide ; None = rien de lisible)."""
    import cv2
    c = img[max(y0, 0):y1, x0 + 4:x1 - 3]
    if c.size == 0:
        return None
    if (cv2.cvtColor(c, cv2.COLOR_RGB2GRAY) < 120).mean() < 0.003:
        return ""
    c = cv2.resize(c, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    c = cv2.copyMakeBorder(c, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    r, _ = _ocr()(c)
    return texte_case(sorted(jetons(r), key=lambda t: t["x0"])) if r else None   # même garde : deux montants = illisible


def ncols(code):
    return 4 if code[0] in "AB" else 2                  # actif : brut, amort, net N, net N-1 ; sinon N, N-1


ILLISIBLE = "‖"                                         # case qui porte DEUX montants (colonnes non séparées)


def texte_case(fs):
    """Texte d'une case depuis ses morceaux. Deux groupes de chiffres séparés par un LARGE blanc sont deux montants
    (trait de colonne non vu) : ILLISIBLE. Constaté sur la DEF de test : N et N-1 lus « 1 160 000 800 000 » — et les
    formules, linéaires, restaient justes avec des montants ainsi collés. Jamais additionner deux colonnes."""
    chif = [f for f in fs if re.search(r"\d", f["txt"])]
    for a, b in zip(chif, chif[1:]):
        if b["x0"] - a["x1"] > 2.5 * max(a["h"], b["h"]):
            return ILLISIBLE
    return " ".join(f["txt"] for f in fs)


def cases(img, T, sens=0):
    """Contenu des cases de chaque ligne à code. sens 0 / 1 : les deux rattachements d'un décalage d'une demi-ligne."""
    xs = traits_verticaux(img)
    # bord droit du tableau non vu (trait fin près du bord de la page, constaté) : borne virtuelle après le texte le
    # plus à droite, sinon la dernière colonne n'existe pas et ses montants seraient perdus (ou déclarés illisibles)
    if T and xs and max(t["x1"] for t in T) > xs[-1] + 30:
        xs.append(int(max(t["x1"] for t in T)) + 8)
    col = lambda x: next((j for j in range(len(xs) - 1) if xs[j] <= x < xs[j + 1]), None)   # noqa: E731
    cotes0 = sorted({col((r["x0"] + r["x1"]) / 2) for r in refs_de(T)} - {None})
    par_cote = {}
    for jr in cotes0:
        marques = [dict(t) for t in T if col((t["x0"] + t["x1"]) / 2) == jr and 1 <= len(t["txt"]) <= 3]
        # un code non lu DU TOUT ne laisse aucune marque : son libellé en tient lieu (sinon le montant glisse)
        for t in T:
            if col((t["x0"] + t["x1"]) / 2) == jr + 1 and len(t["txt"]) >= 4 and re.search(r"[A-Za-z]{3}", t["txt"]) \
                    and not any(abs(m["y"] - t["y"]) < t["h"] * 0.6 for m in marques):
                marques.append(dict(t, txt="?"))
        marques.sort(key=lambda t: t["y"])
        uniques = []
        for m in marques:
            if not (uniques and abs(m["y"] - uniques[-1]["y"]) < m["h"] * 0.5):
                uniques.append(m)
        for m in recaler(uniques):
            m["txt"] = m["code"]
            par_cote.setdefault(jr, []).append(m)
    cotes = sorted(par_cote)
    out = {}
    for jr in cotes:
        fin = next((c for c in cotes if c > jr), len(xs) - 1)
        rs = sorted(par_cote[jr], key=lambda r: r["y"])
        ecarts = sorted(b["y"] - a["y"] for a, b in zip(rs, rs[1:]))
        pas = ecarts[len(ecarts) // 2] if ecarts else 40
        dans = lambda t: any(xs[j] <= (t["x0"] + t["x1"]) / 2 < xs[j + 1] for j in range(max(fin - 4, jr + 1), fin))  # noqa: E731
        # DÉCALAGE des montants, MESURÉ : médiane des écarts au code le plus proche, ramenée dans [-pas/2, pas/2)
        res_ = sorted(((t["y"] - min(rs, key=lambda q: abs(q["y"] - t["y"]))["y"] + pas / 2) % pas - pas / 2)
                      for t in T if re.search(r"\d{3}", t["txt"]) and dans(t))
        delta = res_[len(res_) // 2] if res_ else 0
        if sens == 1:
            delta = delta - pas if delta > 0 else delta + pas
        for r in rs:
            ligne = []
            k = ncols(r["txt"])
            # colonnes ATTENDUES : libellé, note, puis les k montants. Moins de cases = traits de colonnes non vus :
            # les montants seraient collés ou décalés — toute la ligne est ILLISIBLE (échec fermé)
            if fin - jr - 1 < k + 2:
                out[r["txt"]] = {"cases": [ILLISIBLE] * k, "geom": [], "colonnes": fin - jr - 1}
                continue
            for j in range(jr + 1, fin):
                fs = sorted([t for t in T if xs[j] <= (t["x0"] + t["x1"]) / 2 < xs[j + 1] and t is not r
                             and min(rs, key=lambda q: abs(q["y"] + delta - t["y"])) is r
                             and abs(r["y"] + delta - t["y"]) < pas * 0.5], key=lambda t: t["x0"])
                ligne.append(texte_case(fs))
                chif = [f for f in fs if re.search(r"\d", f["txt"])]
                if chif and ligne[-1] != ILLISIBLE and not re.search(r"[-(]", ligne[-1]) and j >= fin - k:
                    hh = sorted(f["h"] for f in chif)[len(chif) // 2]
                    if signe_moins(img, xs[j], min(f["x0"] for f in chif), sum(f["y"] for f in chif) / len(chif), hh):
                        ligne[-1] = "-" + ligne[-1]
            geom = [[xs[j], xs[j + 1], int(r["y"] + delta - pas * 0.45), int(r["y"] + delta + pas * 0.45)]
                    for j in range(max(fin - k, jr + 1), fin)]
            out[r["txt"]] = {"cases": ligne, "geom": geom}
    return out, len(xs)


# ------------------------------------------------------------------------------------------------- preuve
def nombre(c):
    """Montant d'une case ; 0 si vide ou tiret ; None si ILLISIBLE (jamais utilisé, jamais prouvé)."""
    if c == ILLISIBLE:
        return None
    c = (c or "").replace("O", "0").replace("o", "0").replace("（", "(").replace("）", ")")
    if not re.search(r"\d", c):
        return 0                                          # vide ou tiret
    return (-1 if ("(" in c or c.strip().startswith("-")) else 1) * int(re.sub(r"\D", "", c))


def idx(code, an):
    return (2 + an) if code[0] in "AB" else an


def evaluer(E, tot, expr, an, tolerance=1):
    """(juste ?, cases). Trois conventions d'impression constatées : charges en valeur absolue (soustraites) ;
    charges imprimées avec leur signe (tout s'additionne) ; mixte (variations de stocks avec leur signe)."""
    if "|" in expr:                                      # présentations admises : la première juste l'emporte
        # la présentation EXACTEMENT juste d'abord : sinon « à l'unité près » retiendrait une présentation où un
        # montant parasite de 1 comble l'écart (constaté sur la DEF de test : AP « 1 » déclaré prouvé)
        exactes = [evaluer(E, tot, x, an, 0) for x in expr.split("|")]
        res = [evaluer(E, tot, x, an, tolerance) for x in expr.split("|")]
        juste = next((r for r in exactes if r[0]), None) or next((r for r in res if r[0]), None)
        return juste or next((r for r in res if r[0] is False), res[0])
    parts = re.findall(r"([+-])([A-Z]{2})", expr)
    cs = [(tot, idx(tot, an))] + [(c, idx(c, an)) for _, c in parts]
    if any(c not in E or i >= len(E[c]["vals"]) or E[c]["vals"][i] is None for c, i in cs):
        return None, cs
    a = E[tot]["vals"][idx(tot, an)]
    s_abs = s_sig = s_mix = 0
    for sgn, c in parts:
        v = E[c]["vals"][idx(c, an)]
        s_abs += (-abs(v) if c[0] == "R" else -v) if sgn == "-" else v
        s_sig += (v if c[0] == "R" else -v) if sgn == "-" else v
        s_mix += ((v if c in VARIATIONS else -abs(v)) if c[0] == "R" else -v) if sgn == "-" else v
    return any(abs(a - s) <= tolerance or abs(abs(a) - abs(s)) <= tolerance for s in (s_abs, s_sig, s_mix)), cs


def lignes_actif(E):
    """Actif, exercice N, ligne par ligne : brut − amortissements = net."""
    return [(c, abs(abs(x["vals"][0]) - abs(x["vals"][1]) - x["vals"][2]) <= 1) for c, x in E.items()
            if c[0] in "AB" and len(x["vals"]) == 4 and None not in x["vals"][:3] and any(x["vals"][:3])]


def score(E):
    """Formules justes NON TRIVIALES (au moins un montant non nul) + lignes d'actif justes."""
    n = 0
    for tot, expr in FORMULES:
        for an in (0, 1):
            ok, cs = evaluer(E, tot, expr, an)
            n += bool(ok and any(E[c]["vals"][i] for c, i in cs))
    return n + sum(1 for _, ok in lignes_actif(E) if ok)


def resoudre(E, images):
    """Réparer par les formules : relecture d'une case d'une formule fausse, gardée seulement si le nombre de formules
    justes augmente ; puis signe inversé aux mêmes conditions (« signe déduit »). Enfin, statut de preuve."""
    relues = set()
    for _ in range(3):
        progres = False
        for tot, expr in FORMULES:
            for an in (0, 1):
                ok, cs = evaluer(E, tot, expr, an)
                if ok is not False:
                    continue
                for c, i in cs:
                    if (c, i) in relues:
                        continue
                    relues.add((c, i))
                    g = E[c]["geom"]
                    j = i - (len(E[c]["vals"]) - len(g))
                    if not (0 <= j < len(g)):
                        continue
                    t = relire(images[E[c]["page"]], *g[j])
                    if t is None:
                        continue
                    avant, s0 = E[c]["vals"][i], score(E)
                    v_ = nombre(t)
                    if v_ is None:
                        continue
                    E[c]["vals"][i] = -v_ if v_ > 0 and (avant or 0) < 0 else v_   # le signe vu dans les pixels reste acquis
                    if score(E) > s0:
                        E[c]["source"][i] = "relu"
                        progres = True
                        if evaluer(E, tot, expr, an)[0]:
                            break
                    else:
                        E[c]["vals"][i] = avant
        if not progres:
            break
    # plusieurs signes manqués dans une même formule (constaté : −1 et −22 côte à côte) : on continue jusqu'à ce
    # que plus aucune inversion n'améliore le compte de formules justes
    for _ in range(4):
        progres = False
        for tot, expr in FORMULES:
            for an in (0, 1):
                ok, cs = evaluer(E, tot, expr, an)
                if ok is not False:
                    continue
                for c, i in cs:
                    v = E[c]["vals"][i]
                    if not v:
                        continue
                    s0 = score(E)
                    E[c]["vals"][i] = -v
                    if score(E) > s0:
                        E[c]["source"][i] = "signe déduit"
                        progres = True
                        if evaluer(E, tot, expr, an)[0]:
                            break
                    else:
                        E[c]["vals"][i] = v
        if not progres:
            break
    for tot, expr in FORMULES:
        for an in (0, 1):
            ok, cs = evaluer(E, tot, expr, an)
            if ok and not any(E[c]["vals"][i] for c, i in cs):
                continue                          # 0 = 0 + 0 : ne prouve RIEN (des montants non lus donnent aussi 0)
            if ok:
                # tolérance d'une unité (arrondis des DEF réelles) : une formule juste « à l'unité près » ne prouve PAS
                # ses montants de 0 ou ±1 — l'écart d'arrondi pourrait être eux (constaté : « 1 » lu pour un vide)
                exacte = evaluer(E, tot, expr, an, tolerance=0)[0]
                for c, i in cs:
                    if exacte or abs(E[c]["vals"][i]) > 1:
                        E[c]["prouve"][i] = True
    for c, ok in lignes_actif(E):
        if ok and E[c]["prouve"][2]:
            E[c]["prouve"][0] = E[c]["prouve"][1] = True
    return E


# ------------------------------------------------------------------------------------------------- document
def lire(pdf, journal=print):
    """Lit tout le PDF ; rend les états (code -> valeurs, statut de preuve), l'exercice lu et le bilan de la preuve."""
    import pymupdf
    t0 = time.time()
    doc = pymupdf.open(pdf)
    E, images, pages, annees = {}, {}, [], {}
    import numpy as np
    for n in range(1, doc.page_count + 1):
        t = time.time()
        # repérage RAPIDE à 150 dpi (sens de lecture, page d'état ou non, dates) ; seules les pages d'états sont
        # relues à 300 dpi, où les chiffres se lisent sûrement
        k, _, T = orienter(image(doc[n - 1], dpi=150))
        for x in T:                                       # exercice : dates de clôture lues
            for y in re.findall(r"31\s*/\s*12\s*/\s*(20\d\d)", x["txt"]):
                annees[int(y)] = annees.get(int(y), 0) + 1
        if len(refs_de(T)) < 3:
            pages.append({"page": n, "etat": False})
            journal(f"page {n}/{doc.page_count} lue ({time.time() - t:.0f}s)")
            continue
        im = np.ascontiguousarray(np.rot90(image(doc[n - 1]), k))
        T = jetons(_ocr()(im)[0])
        if len(refs_de(T)) < 8:
            pages.append({"page": n, "etat": False})
            journal(f"page {n}/{doc.page_count} lue ({time.time() - t:.0f}s)")
            continue
        essais = []
        for sens in (0, 1):
            c, nx = cases(im, T, sens)
            essais.append((sens, {code: {"vals": [nombre(v) for v in x["cases"][-ncols(code):]], "geom": x["geom"],
                                         "page": n} for code, x in c.items()}))
        # rattachement choisi PAR CÔTÉ (constaté : actif « dessous », passif « dessus » sur la même page)
        Ep, choix = {}, {}
        for groupe in ("AB", "CD", "RTX"):
            sens, meilleur = max(essais, key=lambda e: score({k_: v for k_, v in e[1].items() if k_[0] in groupe}))
            choix[groupe] = sens
            Ep.update({k_: v for k_, v in meilleur.items() if k_[0] in groupe})
        images[n] = im
        for code, x in Ep.items():
            if code not in E:                             # premier état lu : la page « paysage » ne double rien
                E[code] = {**x, "source": ["lu"] * len(x["vals"]), "prouve": [False] * len(x["vals"])}
        pages.append({"page": n, "etat": True, "rotation": k * 90, "codes": len(Ep), "rattachement": choix})
        journal(f"page {n}/{doc.page_count} : état SYSCOHADA, {len(Ep)} lignes ({time.time() - t:.0f}s)")
    resoudre(E, images)
    verifiables = [evaluer(E, tot, expr, an)[0] for tot, expr in FORMULES for an in (0, 1)]
    lignes = lignes_actif(E)
    etats = {}
    for c, x in E.items():
        v, p, s = x["vals"], x["prouve"], x["source"]
        # colonnes nommées depuis la DROITE (les montants finissent la ligne ; une ligne tronquée perd celles de tête)
        champs = (("brut", "amort", "n", "n1") if ncols(c) == 4 else ("n", "n1"))[-len(v):] if v else ()
        etats[c] = {ch: {"valeur": v[i], "prouve": p[i], "source": s[i]} for i, ch in enumerate(champs)}
    exercice = max(annees, key=annees.get) if annees else None
    return {"version": VERSION, "fichier": os.path.basename(pdf), "pages": len(pages),
            "pages_etats": [p["page"] for p in pages if p.get("etat")], "exercice": exercice, "etats": etats,
            "formules": {"justes": sum(1 for x in verifiables if x), "verifiables": sum(1 for x in verifiables if x is not None),
                         "total": len(verifiables)},
            "lignes_actif": {"justes": sum(1 for _, ok in lignes if ok), "total": len(lignes)},
            "montants": {"prouves": sum(1 for e in etats.values() for x in e.values() if x["prouve"]),
                         "total": sum(len(e) for e in etats.values())},
            "duree_s": round(time.time() - t0)}


# ------------------------------------------------------------------------------------------------- cache et fond
def empreinte(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def chemins(pdf, dossier_cache):
    e = empreinte(pdf)[:24]
    return os.path.join(dossier_cache, f"ocr_{e}.json"), os.path.join(dossier_cache, f"ocr_{e}.en_cours")


def etat(pdf, dossier_cache):
    """('pret', resultat) · ('en_cours', avancement) · ('echec', motif) · ('absent', None)."""
    res, marque = chemins(pdf, dossier_cache)
    if os.path.exists(res):
        try:
            r = json.load(open(res, encoding="utf-8"))
            if r.get("version") == VERSION:
                return ("echec", r["echec"]) if r.get("echec") else ("pret", r)
        except (OSError, ValueError):
            pass
    if os.path.exists(marque):
        try:
            m = json.load(open(marque, encoding="utf-8"))
            vivant = time.time() - os.path.getmtime(marque) < 600   # avancement écrit à chaque page (< 2 min)
            if vivant:
                return "en_cours", m
        except (OSError, ValueError):
            pass
    return "absent", None


def lancer_en_fond(pdf, dossier_cache):
    """Lecture en arrière-plan (≈ 10 s par page) : un processus détaché écrit le résultat dans le cache. Sans effet
    si la lecture est déjà prête ou en cours."""
    st, _ = etat(pdf, dossier_cache)
    if st in ("pret", "en_cours"):
        return st
    os.makedirs(dossier_cache, exist_ok=True)
    res, marque = chemins(pdf, dossier_cache)
    with open(marque, "w", encoding="utf-8") as f:
        json.dump({"debut": time.strftime("%Y-%m-%dT%H:%M:%S"), "page": 0}, f)
    drapeaux = 0
    if os.name == "nt":
        drapeaux = 0x00000008 | 0x00000200 | 0x08000000   # DETACHED_PROCESS | NEW_PROCESS_GROUP | NO_WINDOW
    subprocess.Popen([sys.executable, os.path.abspath(__file__), pdf, res, marque], creationflags=drapeaux,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
    return "lance"


def main():
    pdf, sortie = sys.argv[1], sys.argv[2]
    marque = sys.argv[3] if len(sys.argv) > 3 else None

    def journal(m):
        if marque:
            try:
                json.dump({"avancement": m, "maj": time.strftime("%H:%M:%S")}, open(marque, "w", encoding="utf-8"))
            except OSError:
                pass
        else:
            print(m, flush=True)
    try:
        r = lire(pdf, journal)
    except Exception as e:                                # noqa: BLE001 — l'échec s'écrit, il ne se tait pas
        r = {"version": VERSION, "fichier": os.path.basename(pdf), "echec": f"{type(e).__name__} : {e}"}
    tmp = sortie + ".tmp"
    json.dump(r, open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
    os.replace(tmp, sortie)
    if marque and os.path.exists(marque):
        os.remove(marque)
    return 0 if not r.get("echec") else 1


if __name__ == "__main__":
    sys.exit(main())
