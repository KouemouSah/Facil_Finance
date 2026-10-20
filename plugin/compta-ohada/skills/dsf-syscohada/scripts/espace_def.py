# -*- coding: utf-8 -*-
"""DOSSIER DE TRAVAIL de la DEF : automatique d'abord, questions ensuite, validation explicite.

    <racine>\\<Entité>\\<Exercice>\\
        01_sources\\      l'utilisateur y dépose balance, grand livre, DEF précédente (modèle), logo
        02_xls\\          classeurs générés (FR, ES)            — versionnés, jamais écrasés
        03_pdf\\          rapports, annexe balance, contrôle    — versionnés, filigrane « PROJET » avant validation
        04_questions\\    questions.json (ouvertes), reponses.json (réponses), historique des profils effectifs
        manifeste.json   versions : empreintes des sources, réponses appliquées, livrables, statut

Déroulé : `lancer` reconnaît les sources, calcule, produit une version PROJET et consolide TOUTES les questions en une
fois. Seule une balance illisible ou ambiguë arrête avant le calcul (calculer sur une mauvaise lecture fausserait tout).
`repondre` enregistre une réponse ; `lancer` la réinjecte partout (classeurs ET PDF). `valider` produit la version
définitive, seulement quand aucune question obligatoire n'est ouverte, et le trace.

CONFIDENTIALITÉ : la sortie (JSON) ne contient que des statuts, des compteurs, des libellés de questions et des chemins —
jamais d'écritures ni de soldes. C'est ce que Claude lit ; les données comptables restent dans le dossier local.

Usage :
  python espace_def.py init     --entite "ALPHA SARL" --exercice 2025 [--racine DOSSIER]
  python espace_def.py lancer   --entite ... --exercice ... [--racine ...] [--sans-pdf]
  python espace_def.py questions --entite ... --exercice ...
  python espace_def.py repondre --entite ... --exercice ... --id <id> --valeur <valeur>
  python espace_def.py valider  --entite ... --exercice ... --par "<nom>"
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import sys
import time
import unicodedata

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

SOUS = ("01_sources", "02_xls", "03_pdf", "04_questions")
IMAGES = (".png", ".jpg", ".jpeg")
TABLEURS = (".xls", ".xlsx", ".xlsm", ".csv")
# seulement ce qui est LU (page de garde, en-têtes, identification du rapport) ; le sigle, doublon de la raison
# sociale, n'est plus demandé (une réponse déjà saisie reste appliquée)
CHAMPS_IDENTITE = [("raison_sociale", "Dénomination sociale"), ("adresse", "Adresse complète"),
                   ("nif", "Numéro d'identification fiscale (NIF)"), ("rccm", "N° RCCM"), ("forme_juridique", "Forme juridique"),
                   ("activite", "Activité principale"), ("dirigeant", "Dirigeant / signataire des états financiers")]
IDENTITE_OBLIGATOIRE = ("raison_sociale", "nif", "adresse")
OPTIONS_DEF_PRECEDENTE = ("premier exercice", "DEF précédente indisponible")
INTERP_COURT = {"arrondi_base_is": "Base imposable : écarter la fraction inférieure à 1 000 ?",
                "arrondi_is_franc": "Arrondir l'IS au franc ?",
                "base_cmf": "Base de la Cuota Mínima",
                "tf3_iva_deductible": "TF3 : où présenter l'IVA déductible ?",
                "compensation_tresorerie": "Compenser banques créditrices et débitrices ?",
                "notes_neant": "Notes sans montant : omettre ou conserver ?",
                "modele_def": "Modèle de la liasse"}
# liste FERMÉE (règle : une valeur connue d'avance se choisit) : formes de l'Acte uniforme OHADA relatif au droit des
# sociétés commerciales et du GIE (AUSCGIE révisé 2014), plus les entités non sociétaires rencontrées en DEF
CHOIX_IDENTITE = {"forme_juridique": ["SA", "SAS", "SARL", "SNC", "SCS", "GIE", "Succursale", "Entreprise individuelle",
                                      "Établissement public", "Association / ONG"]}


# ---------------------------------------------------------------------------------------------- emplacements
def documents():
    """Dossier « Documents » réel de l'utilisateur (redirigé vers OneDrive le cas échéant)."""
    if os.name == "nt":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders") as k:
                return os.path.expandvars(winreg.QueryValueEx(k, "Personal")[0])
        except OSError:
            pass
    d = os.path.join(os.path.expanduser("~"), "Documents")
    return d if os.path.isdir(d) else os.path.expanduser("~")


def racine_configuree(valeur):
    """Le dossier réglé par l'utilisateur, ou None s'il est absent ou mal transmis.
    Claude Desktop peut transmettre une variable NON REMPLACÉE (« ${DOCUMENTS}/Facil-DEF »,
    « ${user_config.dossier_travail} ») : on ne s'en sert jamais comme chemin (constaté le 16/10/2026)."""
    v = os.path.expandvars((valeur or "").strip().strip('"'))
    if not v or re.search(r"\$\{|%[A-Za-z_]\w*%", v):  # vide, ou variable restée non remplacée
        return None
    return os.path.abspath(os.path.expanduser(v))


def est_synchronise(dossier):
    """Vrai si le dossier est synchronisé vers le cloud (OneDrive) : les données comptables du client
    y quitteraient le poste, contrairement à ce que l'extension promet. Constaté le 17/10/2026."""
    d = os.path.normcase(os.path.abspath(dossier))
    for var in ("OneDrive", "OneDriveConsumer", "OneDriveCommercial"):
        v = os.environ.get(var)
        if v and d.startswith(os.path.normcase(os.path.abspath(v))):
            return True
    return "onedrive" in d


def dossier_par_defaut(documents_):
    r"""Documents\Facil-DEF, SAUF si Documents est synchronisé dans le cloud : alors %USERPROFILE%\Facil-DEF
    (local, non synchronisé). L'utilisateur reste libre de choisir un autre dossier dans le réglage."""
    if est_synchronise(documents_):
        return os.path.join(os.path.expanduser("~"), "Facil-DEF")
    return os.path.join(documents_, "Facil-DEF")


def racine_defaut():
    return racine_configuree(os.environ.get("FACIL_DEF_RACINE")) or dossier_par_defaut(documents())


def slug(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9._ -]+", "", s).strip().replace(" ", "_") or "Entite"


def dossier(racine, entite, exercice):
    return os.path.join(racine or racine_defaut(), slug(entite), str(exercice))


# Un fichier peut être TENU un instant par un autre programme (synchronisation OneDrive, antivirus,
# indexation) : Windows refuse alors lecture ou remplacement (« Accès refusé »). On réessaie.
# Incident du 17/10/2026 : un fichier de réponses tenu par OneDrive était lu comme VIDE, et la réponse
# suivante écrasait toutes les précédentes. Désormais, un fichier qui EXISTE n'est jamais pris pour vide.
ESSAIS, PAUSE = 25, 0.12          # ≈ 3 s au total


class FichierIndisponible(OSError):
    """Le fichier existe mais reste illisible ou non remplaçable après les essais."""


def lire_json(p, defaut):
    if not os.path.exists(p):
        return defaut                                    # absent : c'est le seul cas où l'on rend le défaut
    derniere = None
    for _ in range(ESSAIS):
        try:
            with open(p, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError) as e:               # tenu par un autre programme, ou lu pendant son remplacement
            derniere = e
            time.sleep(PAUSE)
    raise FichierIndisponible(f"{os.path.basename(p)} existe mais reste illisible ({derniere}) ; "
                              "un autre programme le tient peut-être (synchronisation OneDrive, antivirus)")


def ecrire_json(p, v):
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(v, f, ensure_ascii=False, indent=1)
        f.flush()
        os.fsync(f.fileno())
    derniere = None
    for _ in range(ESSAIS):
        try:
            os.replace(tmp, p)                           # écriture atomique : jamais de fichier à moitié écrit
            return
        except PermissionError as e:                     # cible tenue un instant par un autre programme
            derniere = e
            time.sleep(PAUSE)
    raise FichierIndisponible(f"{os.path.basename(p)} n'a pas pu être enregistré ({derniere}) ; "
                              "un autre programme le tient peut-être (synchronisation OneDrive, antivirus)")


def empreinte(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


LISEZMOI = """DOSSIER DE TRAVAIL — DEF {exercice} — {entite}

1. Déposez dans 01_sources la BALANCE, ou le GRAND LIVRE, ou les deux — .xls, .xlsx ou .csv, quel que soit le logiciel :
   - les deux : le mieux (la balance fait foi, le grand livre alimente TF3 à TF5, la CMF versée et les contrôles) ;
   - le grand livre seul : la balance en est reconstituée et contrôlée (équilibre) ;
   - la balance seule : TF3 à TF5 et la CMF versée restent à confirmer.
   Facultatif : la DEF de l'exercice précédent (comparatifs N-1 des notes) et le LOGO de l'entité (.png ou .jpg).
2. Lancez la génération (depuis Claude : « prépare la DEF », ou /monter-dsf).
3. Les classeurs arrivent dans 02_xls, les PDF dans 03_pdf. Tant que la version n'est pas VALIDÉE, les fichiers portent
   « projet » dans leur nom et un filigrane.
4. Les questions en suspens sont dans 04_questions\\questions.json ; répondez depuis Claude ou le formulaire local.
   Vos réponses sont réinjectées à chaque génération, dans les classeurs ET les PDF : ne saisissez rien directement dans
   les classeurs générés (une nouvelle version ne reprendrait pas ces saisies).
5. Rien n'est écrasé : chaque génération crée une nouvelle version (v1, v2…) ; manifeste.json en garde la trace
   (empreinte des fichiers sources, réponses appliquées, livrables, validation).
"""


def init(racine, entite, exercice):
    d = dossier(racine, entite, exercice)
    for s in SOUS:
        os.makedirs(os.path.join(d, s), exist_ok=True)
    if not os.path.exists(os.path.join(d, "LISEZMOI.txt")):
        open(os.path.join(d, "LISEZMOI.txt"), "w", encoding="utf-8").write(LISEZMOI.format(entite=entite, exercice=exercice))
    m = os.path.join(d, "manifeste.json")
    if not os.path.exists(m):
        ecrire_json(m, {"entite": entite, "exercice": int(exercice), "cree_le": maintenant(), "versions": []})
    for f in ("questions.json", "reponses.json"):
        p = os.path.join(d, "04_questions", f)
        if not os.path.exists(p):
            ecrire_json(p, [] if f == "questions.json" else {})
    return d


def maintenant():
    return datetime.datetime.now().isoformat(timespec="seconds")


# ---------------------------------------------------------------------------------------------- sources
def score_logo(nom, entite):
    """Une image n'est un logo candidat que si son nom le dit ; celle qui ressemble le plus au nom de l'entité gagne
    (« logo_alpa » ≈ « ALPHA SARL », malgré la faute de frappe). Captures d'écran, photos : ignorées."""
    import difflib
    n = slug(os.path.splitext(nom)[0]).lower()
    if "logo" not in n:
        return 0
    mots_e = [w for w in re.split(r"[_\W]+", slug(entite).lower()) if len(w) >= 3]
    mots_n = [w for w in re.split(r"[_\W]+", n) if len(w) >= 3 and w != "logo"]
    proche = max((difflib.SequenceMatcher(None, a, b).ratio() for a in mots_e for b in mots_n), default=0)
    return 1 + (2 if proche >= 0.8 else 0)


def role_du_fichier(p, entite=""):
    """(rôle, confiance) d'un fichier déposé, reconnu par son CONTENU et non par son nom."""
    import classer_documents as cd
    import identite_sources as ids
    nom = os.path.basename(p)
    ext = os.path.splitext(nom)[1].lower()
    role, conf = "inconnu", 0
    if ext in IMAGES:
        conf = score_logo(nom, entite)
        role = "logo" if conf else "image"
    elif ext in TABLEURS:
        try:
            r = cd.classify(p)
            role, conf = r["role"], r["confiance"]
        except Exception:
            role = "illisible"
        if role in ("inconnu", "illisible") and ids.est_fiche(p):
            role, conf = "fiche_entite", 2
    elif ext in (".txt", ".json") and ids.est_fiche(p):
        role, conf = "fiche_entite", 2
    elif ext == ".pdf":
        role, conf = role_pdf(p)
    return role, conf


MOTS_DEF_PDF = ("bilan", "compte de resultat", "flux de tresorerie", "etats financiers", "declaration statistique",
                "dsf", "def ", "balance general", "activo", "pasivo", "cuenta de resultados", "estados financieros")


def role_pdf(p):
    """Un PDF déposé : DEF lisible (couche texte qui en porte le vocabulaire) ou PDF SCANNÉ (images seules, cas des
    DEF imprimées puis numérisées). Sans OCR, un scan ne se lit pas : il est reconnu et DIT, jamais ignoré en silence."""
    try:
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz
        doc = fitz.open(p)
        pages = doc.page_count
        texte = " ".join(doc[i].get_text() for i in range(min(pages, 6)))
        images = sum(len(doc[i].get_images()) for i in range(min(pages, 3)))
        doc.close()
    except Exception:                                       # noqa: BLE001
        return "illisible", 0
    t = " ".join(unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode().lower().split())
    if len(texte.strip()) < 30 and images:            # images seules : un scan (y compris des seuls états, 2 pages)
        return "pdf_scanne", 1
    # le vocabulaire ne suffit pas (un guide de la DSF le porte aussi) : une DEF porte des dizaines de MONTANTS
    montants = len(re.findall(r"(?<![\d.,])\d{1,3}(?:[ .  ]\d{3})+(?![\d])", texte))
    if sum(1 for m in MOTS_DEF_PDF if m in t) >= 2 and montants >= 30:
        return "def_pdf", 1
    return "inconnu", 0


def _deposes(d):
    src = os.path.join(d, "01_sources")
    return [n for n in sorted(os.listdir(src)) if os.path.isfile(os.path.join(src, n)) and not n.startswith(("~$", "."))]


def inventaire(d, entite=""):
    """Rôle de chaque fichier déposé et son empreinte."""
    src = os.path.join(d, "01_sources")
    out = []
    for nom in _deposes(d):
        p = os.path.join(src, nom)
        role, conf = role_du_fichier(p, entite)
        out.append({"fichier": nom, "role": role, "confiance": conf, "sha256": empreinte(p), **_signature(src, nom)})
    return out


def choisir(inv, role):
    """Le fichier retenu pour un rôle : le plus confiant, puis le plus récent. Les autres sont signalés."""
    c = [x for x in inv if x["role"] == role]
    c.sort(key=lambda x: (x["confiance"], x["modifie_le"]), reverse=True)
    return (c[0] if c else None), c[1:]


ROLES_UTILES = ("balance", "grand_livre", "modele_dsf", "logo", "fiche_entite", "pdf_scanne", "def_pdf")


def _signature(src, nom):
    p = os.path.join(src, nom)
    return {"octets": os.path.getsize(p),
            "modifie_le": datetime.datetime.fromtimestamp(os.path.getmtime(p)).isoformat(timespec="seconds")}


_ROLES = {}


def _role_memo(p, sig, entite):
    """Rôle mémorisé par (chemin, taille, date) : le formulaire interroge à chaque page sans relire les classeurs."""
    k = (p, sig["octets"], sig["modifie_le"])
    if k not in _ROLES:
        _ROLES[k] = role_du_fichier(p, entite)[0]
    return _ROLES[k]


def sources_modifiees(d):
    """Ce qui a changé dans 01_sources depuis la DERNIÈRE version : fichiers utiles ajoutés, remplacés ou retirés.
    Incident du 16/10/2026 : une DEF déposée APRÈS la génération n'était pas vue, la question « premier exercice »
    restait seule proposée et la validation restait bloquée. Une version ne se valide pas sur des sources qu'elle
    n'a pas lues. None tant qu'aucune version n'existe."""
    man = lire_json(os.path.join(d, "manifeste.json"), {})
    vs = man.get("versions") or []
    if not vs:
        return None
    v = vs[-1]
    avant = {x["fichier"]: x for x in (v.get("inventaire") or v.get("sources") or [])}
    src = os.path.join(d, "01_sources")
    presents = _deposes(d)
    out = {"depuis_version": v.get("version"), "ajoutes": [], "remplaces": [], "retires": []}
    for n in presents:
        s = _signature(src, n)
        if n not in avant:              # seul ce qui est NOUVEAU est classé (un classement lit le fichier entier)
            role = _role_memo(os.path.join(src, n), s, man.get("entite", ""))
            if role in ROLES_UTILES:
                out["ajoutes"].append({"fichier": n, "role": role})
        elif (avant[n].get("octets"), avant[n].get("modifie_le")) != (s["octets"], s["modifie_le"]) \
                and avant[n].get("role") in ROLES_UTILES:
            out["remplaces"].append({"fichier": n, "role": avant[n]["role"]})
    out["retires"] = [{"fichier": n, "role": x.get("role")} for n, x in avant.items()
                      if n not in presents and x.get("role") in ROLES_UTILES]
    return out if (out["ajoutes"] or out["remplaces"] or out["retires"]) else {}


def modele_utilisable(p, N):
    """(utilisable, exercice lu, motif) d'une DEF déposée. Elle ne sert que si elle est de l'exercice N (sa colonne
    N-1 donne nos comparatifs) ou N-1 (sa colonne N) : une DEF plus ancienne donnerait de faux comparatifs, en silence."""
    if os.path.splitext(p)[1].lower() not in (".xlsx", ".xlsm"):
        return False, None, "elle est au format .xls ancien — ouvrez-la et enregistrez-la au format .xlsx, puis régénérez"
    try:
        an = exercice_du_modele(p)
    except Exception as e:                                  # noqa: BLE001
        return False, None, f"elle est illisible ({type(e).__name__})"
    if an is not None and an not in (N, N - 1):
        return False, an, f"elle porte l'exercice {an}, ni {N} ni {N - 1}"
    return True, an, ""


def identite_reprise(d, inv, mod):
    """Identité lue dans les sources, avec son origine : fiche entité déposée, puis fiche du dossier de l'entité
    (écrite à la validation d'un exercice), puis page de garde de la DEF précédente. Une PROPOSITION : la réponse
    de l'utilisateur l'emporte toujours."""
    import identite_sources as ids
    valeurs, origines = {}, {}

    def prend(src, origine):
        for k, v in src.items():
            if k == "forme_juridique":              # liste fermée : une valeur hors liste n'est pas reprise, elle est demandée
                v = next((o for o in CHOIX_IDENTITE["forme_juridique"] if ids._norm(o) == ids._norm(v)), None)
            if v and k not in valeurs:
                valeurs[k], origines[k] = v, origine
    fiche, _ = choisir(inv, "fiche_entite")
    if fiche:
        prend(ids.depuis_fiche(os.path.join(d, "01_sources", fiche["fichier"])), f"fiche entité déposée ({fiche['fichier']})")
    f_ent, p_ent = ids.fiche_du_dossier_entite(os.path.dirname(d))
    if f_ent:
        prend(f_ent, f"fiche de l'entité ({os.path.basename(p_ent)})")
    if mod:
        lu = ids.depuis_def(os.path.join(d, "01_sources", mod["fichier"]))
        origine = f"DEF précédente déposée ({mod['fichier']})"
        if lu.get("raison_sociale") and not nom_proche(lu["raison_sociale"], lire_json(os.path.join(d, "manifeste.json"), {}).get("entite", "")):
            # une DEF d'une AUTRE entité (prise pour exemple) ne doit pas donner son identité en silence
            origine += " — ⚠ son nom diffère de celui du dossier : vérifiez que c'est bien la DEF de cette entité"
        prend(lu, origine)
    return valeurs, origines


def nom_proche(a, b):
    """Deux noms d'entité se ressemblent-ils (un mot commun à 75 % près : « ALPHA GE » ≈ « alpa ») ?"""
    import difflib
    ma = [w for w in re.split(r"[_\W]+", slug(a).lower()) if len(w) >= 3]
    mb = [w for w in re.split(r"[_\W]+", slug(b).lower()) if len(w) >= 3]
    return not ma or not mb or max(difflib.SequenceMatcher(None, x, y).ratio() for x in ma for y in mb) >= 0.75


CANAUX = {"formulaire": "saisie au formulaire", "conversation": "réponse donnée dans la conversation"}


def montant_saisi(v):
    """« -1 234 567 », « (1 234 567) », « 1.234.567 » -> entier ; None si ce n'est pas un montant."""
    s = str(v or "").strip()
    if not re.fullmatch(r"[-(]?\s*[\d\s.,  ]+\)?", s) or not re.search(r"\d", s):
        return None
    return (-1 if s.startswith(("-", "(")) else 1) * int(re.sub(r"\D", "", s))


def n1_depuis_scan(d, inv, N, reponses):
    """N-1 tiré d'une DEF précédente SCANNÉE (lecture OCR locale, en arrière-plan, mise en cache).
    Rend (n1_externe | None, montants à vérifier [(code, valeur lue)], état pour le résultat)."""
    import ocr_def
    pdfs = [x for x in inv if x["role"] in ("pdf_scanne", "def_pdf")]
    if not pdfs:
        return None, [], None
    if not ocr_def.disponible():
        return None, [], {"fichier": pdfs[0]["fichier"], "code": "indisponible",
                          "etat": "la lecture des scans n'est pas installée sur ce poste"}
    cache = os.path.join(d, "04_questions", "travail", "ocr")
    # PLUSIEURS scans possibles (DEF N-1, N-2… : constaté chez le porteur) : lus UN À LA FOIS en arrière-plan (la
    # lecture est lourde) ; celui de l'exercice N-1 (à défaut N) donne le N-1 ; tous servent à l'analyse pluriannuelle
    etats = [(x, *ocr_def.etat(os.path.join(d, "01_sources", x["fichier"]), cache)) for x in pdfs]
    en_cours = next(((x, r) for x, st, r in etats if st == "en_cours"), None)
    if not en_cours:
        absent = next((x for x, st, _ in etats if st == "absent"), None)
        if absent:
            ocr_def.lancer_en_fond(os.path.join(d, "01_sources", absent["fichier"]), cache)
            en_cours = (absent, {"avancement": "lecture lancée (environ 10 s par page, en arrière-plan)"})
    lus = [(x, r) for x, st, r in etats if st == "pret"]
    resume = [{"fichier": x["fichier"], "exercice": r.get("exercice"), "pages_etats": r.get("pages_etats"),
               "formules": r.get("formules")} for x, r in lus]
    # exercice non lu (aucune date « 31/12/AAAA » reconnue) : pris pour N-1 en dernier recours, et dit dans la source
    choix = next(((x, r) for cible in (N - 1, N, None) for x, r in lus if r.get("exercice") == cible and r.get("pages_etats")),
                 None)
    if not choix:
        if en_cours:
            return None, [], {"fichier": en_cours[0]["fichier"], "code": "en_cours", "etat": "lecture en cours",
                              "avancement": (en_cours[1] or {}).get("avancement", ""), "scans_lus": resume}
        x, r = (lus or [(None, None)])[0]
        if x and not r.get("pages_etats"):
            return None, [], {"fichier": x["fichier"], "code": "pas_un_etat", "scans_lus": resume,
                              "etat": "aucun bilan ni compte de résultat SYSCOHADA n'y a été trouvé"}
        if x:
            return None, [], {"fichier": x["fichier"], "code": "exercice", "exercice": r.get("exercice"), "scans_lus": resume,
                              "etat": f"elle porte l'exercice {r.get('exercice')}, ni {N} ni {N - 1} : non utilisée"}
        x, _, r = next(((x, st, r) for x, st, r in etats if st == "echec"), (pdfs[0], None, "inconnue"))
        return None, [], {"fichier": x["fichier"], "code": "echec", "etat": f"sa lecture a échoué ({r})"}
    pdf, r = choix
    info = {"fichier": pdf["fichier"], "scans_lus": resume,
            **({"autre_lecture_en_cours": en_cours[0]["fichier"]} if en_cours else {})}
    ex = r.get("exercice")
    champ = "n1" if ex == N else "n"              # DEF N-1 : sa colonne N ; DEF de l'exercice : sa colonne N-1
    valeurs, a_verifier, prouves, confirmes = {}, [], 0, 0
    for code, cols in r["etats"].items():
        x = cols.get(champ)
        if not x:
            continue
        v = None
        if x["prouve"]:
            v, prouves = x["valeur"], prouves + 1
        elif montant_saisi(reponses.get(f"scan.{code}")) is not None:
            v, confirmes = montant_saisi(reponses[f"scan.{code}"]), confirmes + 1
        else:
            a_verifier.append((code, x["valeur"]))
        if v is not None:
            # convention du calcul : charges en négatif (les variations de stocks et les soldes gardent leur signe)
            valeurs[code] = -abs(v) if code[0] == "R" and code not in ("RB", "RD", "RF") else v
    source = (f"DEF {ex or N - 1} scannée « {pdf['fichier']} », lue sur ce poste : {prouves} montant(s) prouvé(s) par les "
              f"formules SYSCOHADA, {confirmes} confirmé(s), {len(a_verifier)} à vérifier (non utilisés)")
    return ({"valeurs": valeurs, "source": source} if valeurs else None), a_verifier, \
        {**info, "code": "lue", "etat": "lue", "exercice": ex, "pages_etats": r.get("pages_etats"), "formules": r.get("formules"),
         "montants_prouves": prouves, "confirmes": confirmes, "a_verifier": len(a_verifier)}


def analyse_pluriannuelle(d, inv, D, N, n1x, reponses, fichiers, chemin, pdf, entite=""):
    """Rapport d'analyse financière (N, N-1, années des DEF scannées lues) + questions FACULTATIVES sur la cause des
    variations significatives. Un échec du rapport ne bloque jamais la DEF : il est dit dans le résultat."""
    import analyse_financiere as af
    import ocr_def
    cache = os.path.join(d, "04_questions", "travail", "ocr")
    scans = []
    for x in inv:
        if x["role"] in ("pdf_scanne", "def_pdf"):
            st, r = ocr_def.etat(os.path.join(d, "01_sources", x["fichier"]), cache)
            if st == "pret":
                scans.append((x["fichier"], r))
    dates = {j.get("id"): j.get("le", "") for j in reponses.get("_journal", [])} if isinstance(reponses.get("_journal"), list) else {}
    causes = {k[len("analyse."):]: {"texte": v, "origine": "réponse de l'entreprise" + (f", le {dates[k][:10]}" if dates.get(k) else "")}
              for k, v in reponses.items() if isinstance(k, str) and k.startswith("analyse.") and isinstance(v, str) and v.strip()}
    annees = af.annees_depuis(D, N, scans, (n1x or {}).get("source"))
    try:
        res = af.construire(D, annees, chemin("analyse_xlsx"), chemin("analyse_pdf") if pdf else None, causes, entite)
    except Exception as e:                                # noqa: BLE001 — dit, jamais bloquant
        return [], {"produite": False, "motif": f"{type(e).__name__} : {e}"}
    fichiers.setdefault("analyse_xlsx", []).append(chemin("analyse_xlsx"))
    if res["pdf"]:
        fichiers.setdefault("analyse_pdf", []).append(chemin("analyse_pdf"))
    qs = []
    for x in res["variations"][:12]:                      # les plus fortes : questions courtes, facultatives
        sens = "hausse" if x["ecart"] > 0 else "baisse"
        pct = f" ({x['pct']:+.0%})" if x["pct"] is not None else ""
        qs.append({"id": f"analyse.{x['ref']}", "categorie": "Analyse financière (facultatif)", "type": "texte",
                   "obligatoire": False, "question": f"Cause de la {sens} de « {x['libelle']} »{pct} ?",
                   "options": [], "impact": "", "defaut": None,
                   "contexte": f"{x['faits']} — À vérifier : {x['verifier']}. Votre réponse figure au rapport d'analyse.",
                   "reponse": reponses.get(f"analyse.{x['ref']}")})
    return qs, {"produite": True, "annees": res["annees"], "variations_significatives": len(res["variations"]),
                "causes_documentees": len(causes)}


def trace_reponses(reponses_eff, origines, anciennes_qs):
    """Chaque réponse appliquée, avec son origine et sa date : ce que le rapport de contrôle doit montrer."""
    lib = {q["id"]: q.get("question") for q in anciennes_qs if isinstance(q, dict)}
    dern = {}
    for j in reponses_eff.get("_journal", []) if isinstance(reponses_eff.get("_journal"), list) else []:
        dern[j.get("id")] = j
    out = []
    for k, v in reponses_eff.items():
        if not isinstance(k, str) or k.startswith("_") or v in (None, ""):
            continue
        j = dern.get(k)
        cle = k.partition(".")[2]
        if j:
            orig, le = CANAUX.get(j.get("canal"), "réponse enregistrée"), j.get("le", "")
        elif k.startswith("identite.") and cle in origines:
            orig, le = "reprise : " + origines[cle], ""
        else:
            orig, le = "réponse enregistrée", ""
        out.append({"id": k, "question": lib.get(k) or k, "reponse": str(v), "origine": orig, "le": le})
    return out


def exercice_du_modele(p):
    """Exercice d'une DEF de référence : l'année la plus fréquente des dates de clôture qu'elle porte."""
    import openpyxl
    from collections import Counter
    wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
    ann = Counter()
    for ws in wb.worksheets[:12]:
        for row in ws.iter_rows(max_row=12, max_col=16, values_only=True):
            for v in row:
                if isinstance(v, (datetime.date, datetime.datetime)) and 2000 < v.year < 2100:
                    ann[v.year] += 1
                elif isinstance(v, str):
                    for y in re.findall(r"\b\d{2}/\d{2}/(20\d{2})\b", v):
                        ann[int(y)] += 1
    wb.close()
    return ann.most_common(1)[0][0] if ann else None


# ---------------------------------------------------------------------------------------------- réponses -> profil
def profil_et_decisions(reponses):
    """Réponses (id -> valeur) -> profil d'entreprise et décisions fiscales EFFECTIFS (conservés à chaque version)."""
    profil = {"identite": {}, "faits": {}, "interpretations": {}, "justifications": {}, "tiers_nif": {}}
    decisions = {"propositions_acceptees": []}
    for k, v in reponses.items():
        if v in (None, "") or not isinstance(k, str):
            continue
        genre, _, cle = k.partition(".")
        if genre == "identite":
            profil["identite"][cle] = v
        elif genre == "fait":
            profil["faits"][cle] = {"oui": True, "non": False}.get(str(v).lower(), v)
        elif genre == "interp" and v != "defaut":
            profil["interpretations"][cle] = {"oui": True, "non": False}.get(str(v).lower(), v)
        elif genre == "reint" and str(v).lower() == "accepter":
            decisions["propositions_acceptees"].append(cle)
        elif genre == "tf5nif" and str(v).lower() not in ("inconnu", "?"):
            profil["tiers_nif"][cle] = v
    return profil, decisions


def questions_apres_calcul(gen, reponses, params, origines=None):
    """Toutes les questions en une fois, après le calcul. Chaque question : id stable, catégorie, libellé, type,
    options, obligatoire (bloque la VALIDATION, jamais le calcul), impact, réponse actuelle. Une identité REPRISE
    d'une source (origines) reste affichée, déjà remplie et avec son origine : elle se relit et se corrige."""
    origines = origines or {}
    import agreger_balance_dsf as agr
    D, f = gen.D, gen.D["fisc"]
    q = []

    def ajoute(id_, cat, texte, typ, obligatoire, options=None, impact="", defaut=None, contexte=""):
        q.append({"id": id_, "categorie": cat, "question": texte, "type": typ, "options": options or [],
                  "obligatoire": obligatoire, "impact": impact, "defaut": defaut, "contexte": contexte,
                  "reponse": reponses.get(id_)})

    ident = D.get("identite") or {}
    for cle, lab in CHAMPS_IDENTITE + [("sigle", "Sigle usuel")]:
        if cle in origines:
            ajoute(f"identite.{cle}", "Identité de l'entité", lab, "choix" if cle in CHOIX_IDENTITE else "texte",
                   cle in IDENTITE_OBLIGATOIRE, CHOIX_IDENTITE.get(cle),
                   contexte=f"Repris : {origines[cle]}." + ("" if "vérifiez" in origines[cle] else " À relire")
                            + " — votre saisie le remplace.")
            q[-1]["origine"] = origines[cle]
        elif not ident.get(cle) and cle != "sigle":
            ajoute(f"identite.{cle}", "Identité de l'entité", lab, "choix" if cle in CHOIX_IDENTITE else "texte",
                   cle in IDENTITE_OBLIGATOIRE, CHOIX_IDENTITE.get(cle),
                   contexte="Saisie une seule fois : reprise en page de garde, dans tous les en-têtes et sur la couverture du rapport.")
    for x in f.get("questions", []):
        ajoute(f"fait.{x['fait']}", "Faits sur l'entreprise", x["question"], "oui_non", True, ["oui", "non"],
               contexte=f"{x['article']}" + (f" — indices dans la balance : {len(x['indices'])} compte(s)" if x.get("indices") else ""))
    taux = f["tf2"][4]
    for p in f.get("propositions", []):
        if p["type"] == "information":
            continue
        impact = f"IS +{round(p['montant'] * taux):,.0f}".replace(",", " ") if p["type"] == "reintegration" else "à examiner"
        ajoute(f"reint.{p['compte']}", "Réintégrations fiscales (TF1)",
               f"Réintégrer {p['montant']:,.0f} du compte {p['compte']} ?".replace(",", " "), "decision", True,
               ["accepter", "refuser"], impact=impact, contexte=f"{p['motif']} ({p['article']})")
    for k, spec in list(params.get("interpretations", {}).items()) + list(agr.INTERPRETATIONS.items()):
        opts = spec.get("choix") or ["oui", "non"]
        lisible = {True: "oui", False: "non"}.get(spec["defaut"], spec["defaut"])        # jamais « True / False » à l'écran
        # libellé COURT à l'écran ; la question complète en contexte (lisible au survol) ; le choix « par défaut (…) »
        # dit déjà la lecture stricte
        ajoute(f"interp.{k}", "Choix d'interprétation (facultatif)", INTERP_COURT.get(k, spec["question"]), "choix", False,
               ["defaut"] + opts, defaut=spec["defaut"],
               contexte=(f"{spec['article']} — " if spec.get("article") else "") + spec["question"])
    ajoute("interp.modele_def", "Choix d'interprétation (facultatif)", INTERP_COURT["modele_def"], "choix", False,
           ["defaut", "syscohada", "ge"], defaut="syscohada",
           contexte="SYSCOHADA système normal : formulaire officiel OHADA complet, adapté aux données (notes sans "
                    "information omises) et aux tableaux fiscaux GE. Format GE : celui de la DEF déposée en exemple, "
                    "bilingue. Mêmes chiffres dans les deux (un seul calcul).")
    ajoute("interp.notes_neant", "Choix d'interprétation (facultatif)", INTERP_COURT["notes_neant"], "choix", False,
           ["defaut", "omettre", "conserver"], defaut="omettre",
           contexte="SYSCOHADA révisé — une note sans montant (N et N-1) n'est pas produite ; elle est signalée dans la "
                    "grille d'analyse des notes. « Conserver » garde toutes les feuilles du formulaire.")
    for x in gen.tf5_lignes:
        if x.get("nom") and not x.get("nif"):
            ajoute(f"tf5nif.{x['nom']}", "Tiers (TF5)", f"NIF du bénéficiaire « {x['nom']} »", "texte", True,
                   contexte="art. 27.2 — répondre « inconnu » si l'entreprise ne le détient pas (signalé au rapport).")
    return q


def ouvertes(qs):
    return [x for x in qs if x["obligatoire"] and x.get("reponse") in (None, "")]


# ---------------------------------------------------------------------------------------------- filigrane
def filigrane(pdf, texte="PROJET - NON VALIDÉ"):          # tiret simple : présent dans la police de base du PDF
    """Filigrane diagonal sur chaque page d'un PDF (PyMuPDF) ; sans PyMuPDF, le nom du fichier suffit à l'annoncer."""
    try:
        try:
            import pymupdf as fitz            # nom actuel de PyMuPDF
        except ImportError:
            import fitz                       # ancien nom (versions < 1.24.3)
    except ImportError:
        return False
    doc = fitz.open(pdf)
    for page in doc:
        r = page.rect
        centre = fitz.Point(r.width / 2, r.height / 2)
        page.insert_text(fitz.Point(r.width * 0.16, r.height * 0.58), texte, fontsize=min(r.width, r.height) / 11,
                         color=(0.85, 0.2, 0.2), fill_opacity=0.16, stroke_opacity=0.16,
                         morph=(centre, fitz.Matrix(-35 if r.height > r.width else -25)))
    tmp = pdf + ".tmp.pdf"
    doc.save(tmp, garbage=3, deflate=True)
    doc.close()
    os.replace(tmp, pdf)
    return True


# ---------------------------------------------------------------------------------------------- génération
def generer(d, definitif=False, pdf=True, par=None):
    import argparse as ap
    from detection_balance import analyse
    import def_modele
    import fiscal_ge
    man = lire_json(os.path.join(d, "manifeste.json"), {})
    N = int(man["exercice"])
    qdir = os.path.join(d, "04_questions")
    reponses = lire_json(os.path.join(qdir, "reponses.json"), {})
    inv = inventaire(d, man.get("entite", ""))
    bal, bal_autres = choisir(inv, "balance")
    gl, _ = choisir(inv, "grand_livre")
    mod, _ = choisir(inv, "modele_dsf")
    logo, logos_autres = choisir(inv, "logo")
    an_mod, mod_ecarte = None, None
    if mod:
        ok_mod, an_mod, motif = modele_utilisable(os.path.join(d, "01_sources", mod["fichier"]), N)
        if not ok_mod:                 # dite, jamais tue : la question « DEF précédente » nomme le fichier et le motif
            mod_ecarte, mod = {"fichier": mod["fichier"], "motif": motif}, None
    anciennes_qs = lire_json(os.path.join(qdir, "questions.json"), [])
    saisies = {k: v for k, v in reponses.items() if v not in (None, "")}
    # réponses EFFECTIVES : l'identité reprise des sources, que toute réponse de l'utilisateur remplace (ses
    # origines ne gardent que ce qui est réellement repris)
    reprise, origines = identite_reprise(d, inv, mod)
    origines = {k: o for k, o in origines.items() if f"identite.{k}" not in saisies}
    reponses = {**{f"identite.{k}": reprise[k] for k in origines}, **saisies}
    res = {"dossier": d, "exercice": N, "sources": {r: (x["fichier"] if x else None) for r, x in
                                                   (("balance", bal), ("grand_livre", gl), ("modele", mod), ("logo", logo))},
           "sources_ignorees": [x["fichier"] for x in inv if x["role"] in ("inconnu", "illisible", "image")]
                               + [x["fichier"] for x in bal_autres + logos_autres]}
    bloquantes = []
    pbal = os.path.join(d, "01_sources", bal["fichier"]) if bal else None
    if not bal and gl:
        # GRAND LIVRE SEUL : la balance (après inventaire, avant clôture) est reconstituée depuis ses écritures,
        # CONTRÔLÉE (équilibre des ouvertures et des mouvements), puis sert au calcul comme une balance déposée
        pbal, ctrl = balance_depuis_grand_livre(os.path.join(d, "01_sources", gl["fichier"]), os.path.join(qdir, "travail"))
        res["balance_reconstituee"] = {k: v for k, v in ctrl.items() if k != "pieces_de_cloture_exclues"}
        res["sources"]["balance"] = "reconstituée depuis le grand livre"
        if not ctrl["equilibree"]:
            bloquantes.append({"id": "sources.grand_livre", "categorie": "Sources", "type": "fichier", "obligatoire": True,
                               "question": "Le grand livre ne s'équilibre pas (ouvertures ou mouvements) : déposez la balance "
                                           "de l'exercice, ou un grand livre complet.", "options": [],
                               "impact": "calcul suspendu (une balance déséquilibrée fausserait toute la DEF)",
                               "defaut": None, "contexte": gl["fichier"], "reponse": None})
            pbal = None
    if not pbal and not bloquantes:
        bloquantes.append({"id": "sources.balance", "categorie": "Sources", "type": "fichier", "obligatoire": True,
                           "question": "Déposez dans 01_sources la balance de l'exercice, ou le grand livre, ou les deux "
                                       "(aucun des deux n'est reconnu).",
                           "options": [], "impact": "calcul impossible", "defaut": None, "contexte": "", "reponse": None})
    elif pbal:
        det = analyse(pbal, reponses.get("balance.gabarit") or None)
        if det["statut"] != "ok":
            rivaux = [r.get("gabarit") or r.get("nom") or str(r) for r in (det.get("rivaux") or [])]
            bloquantes.append({"id": "balance.gabarit", "categorie": "Sources", "type": "choix", "obligatoire": True,
                               "question": "La balance admet plusieurs lectures : laquelle est la bonne ?" if rivaux else
                                           f"Balance illisible : {det.get('raison', '')}", "options": rivaux,
                               "impact": "calcul suspendu (une mauvaise lecture fausserait toute la DEF)", "defaut": None,
                               "contexte": os.path.basename(pbal), "reponse": reponses.get("balance.gabarit")})
    if bloquantes:
        ecrire_json(os.path.join(qdir, "questions.json"), bloquantes)
        res.update({"statut": "bloque_avant_calcul", "questions_ouvertes": len(bloquantes),
                    "questions": [{"id": x["id"], "question": x["question"], "options": x["options"]} for x in bloquantes]})
        return res
    # --- profil et décisions effectifs (tracés)
    profil, decisions = profil_et_decisions(reponses)
    k = len(man.get("versions", [])) + 1
    hist = os.path.join(qdir, "historique")
    os.makedirs(hist, exist_ok=True)
    pp, pdec = os.path.join(hist, f"v{k}_profil.json"), os.path.join(hist, f"v{k}_decisions.json")
    ecrire_json(pp, profil)
    ecrire_json(pdec, decisions)
    col = "N"
    if mod:
        col = "N-1" if an_mod == N else "N"
        res["modele_exercice"] = an_mod
    if mod_ecarte:
        res["modele_ecarte"] = mod_ecarte
    if origines:
        res["identite_reprise"] = sorted(origines)
    suffixe = "" if definitif else "_projet"
    horo = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    base = f"DEF_{N}_v{k}"

    def chemin(nature, lang=None):
        L = f"_{lang.upper()}" if lang else ""
        dos = "02_xls" if nature.endswith("xlsx") else "03_pdf"
        nom = {"xlsx": f"{base}{L}", "pro_xlsx": f"{base}{L}_pro", "excel_pdf": f"{base}{L}_impression",
               "rapport_pdf": f"{base}_rapport{L}", "balance_pdf": f"{base}_annexe-balance{L}",
               "controles_xlsx": f"{base}_controle", "controles_pdf": f"{base}_controle",
               "rapport_abrege_pdf": f"{base}_rapport-abrege", "sn_xlsx": f"{base}_SYSCOHADA{L}",
               "sn_pdf": f"{base}_SYSCOHADA{L}", "analyse_xlsx": f"{base}_analyse-financiere",
               "analyse_pdf": f"{base}_analyse-financiere"}[nature]
        return os.path.join(d, dos, nom + suffixe + (".xlsx" if nature.endswith("xlsx") else ".pdf"))

    # sans DEF déposée : le GABARIT VIERGE embarqué (formulaire officiel complet, structure prouvée) — même DEF,
    # colonne N identique (test_reference_gabarit) ; N-1 des notes vide, bilan N-1 depuis l'ouverture de la balance
    gab = os.path.join(HERE, "..", "templates", "def_ge_gabarit.xlsx")
    # DEF précédente SCANNÉE : lecture locale en arrière-plan ; ses montants PROUVÉS (ou confirmés) donnent le N-1
    n1x, scan_a_verifier, scan_info = (None, [], None) if mod else n1_depuis_scan(d, inv, N, reponses)
    if scan_info:
        res["lecture_scan"] = scan_info
    a = ap.Namespace(modele=os.path.join(d, "01_sources", mod["fichier"]) if mod else gab,
                     balance=pbal,
                     grand_livre=os.path.join(d, "01_sources", gl["fichier"]) if gl else None,
                     exercice=N, profil=pp, decisions=pdec, colonne_precedente=col,
                     logo=os.path.join(d, "01_sources", logo["fichier"]) if logo else None,
                     langues="fr,es", sortie=os.path.join(d, base), pdf=pdf, pdf_excel=False, pro=False,
                     gabarit=not mod, structure=gab[:-5] + ".json" if not mod else None,
                     # modèle de la LIASSE : SYSCOHADA système normal (défaut, décision du porteur du 30/09/2026) ou
                     # format GE ; un seul calcul, deux présentations
                     sn=(reponses.get("interp.modele_def") or "defaut") in ("defaut", "syscohada"),
                     n1_externe=n1x,
                     # traçabilité au rapport de contrôle : chaque réponse appliquée, son origine, sa date, le valideur
                     tracabilite={"statut": "définitive" if definitif else "projet (non validée)",
                                  "valide_par": par if definitif else None,
                                  "valide_le": maintenant() if definitif else None,
                                  "reponses": trace_reponses(reponses, origines, anciennes_qs)})
    if not mod:
        res["modele"] = "gabarit officiel embarqué (aucune DEF déposée)"
    out = def_modele.produire(a, chemin=chemin)
    fichiers = out["fichiers"]
    if a.sn and fichiers.get("sn_xlsx"):
        # la liasse FRANÇAISE est celle du modèle SYSCOHADA : le classeur FR au format GE ferait doublon (il a servi
        # de base au calcul) ; l'ESPAGNOL reste au format GE tant que le modèle SYSCOHADA n'a pas sa traduction
        for x in [x for x in fichiers["xlsx"] if "_FR" in os.path.basename(x).upper()]:
            fichiers["xlsx"].remove(x)
            try:
                os.remove(x)
            except OSError:
                pass
        res["modele_liasse"] = "SYSCOHADA système normal (FR) ; version espagnole au format GE"
    else:
        res["modele_liasse"] = "format GE (FR / ES)"
    res["notes_omises"] = {lang: len(v) for lang, v in out["gen"].notes_omises.items()}
    if out["gen"].notes_absentes:                  # applicables mais sans feuille dans le formulaire : dit, jamais tu
        res["notes_applicables_absentes_du_formulaire"] = sorted(out["gen"].notes_absentes, key=int)
    qs = questions_apres_calcul(out["gen"], reponses, fiscal_ge.load_params(), origines)
    q_analyse, res["analyse_financiere"] = analyse_pluriannuelle(d, inv, out["gen"].D, N, n1x, reponses, fichiers, chemin,
                                                                 pdf, entite=man.get("entite", ""))
    qs += q_analyse
    postes = out["gen"].D.get("postes", {})
    for code, lu in scan_a_verifier:
        # montant lu sur le scan mais NON prouvé par les formules : jamais utilisé sans confirmation de l'utilisateur
        qs.append({"id": f"scan.{code}", "categorie": "DEF précédente scannée — montants à vérifier", "type": "texte",
                   "obligatoire": True, "question": f"{code} — {postes.get(code, {}).get('libelle', '')}".strip(" —"),
                   "options": [], "impact": "colonne N-1", "defaut": None,
                   "proposition": f"{lu:,}".replace(",", " ") if lu is not None else "",   # illisible : à saisir
                   "contexte": f"Lu sur « {scan_info['fichier']} » mais non prouvé par les formules SYSCOHADA : vérifiez sur "
                               "le document papier, corrigez si besoin, puis enregistrez.",
                   "reponse": reponses.get(f"scan.{code}")})
    if not mod and not (scan_info and scan_info.get("code") == "lue"):
        # sans DEF précédente, les comparatifs N-1 des notes manquent : on le DEMANDE. Deux réponses possibles, pour que
        # personne ne reste bloqué (incident du 16/10/2026 : « premier exercice » seul proposé, à une entreprise qui
        # avait une DEF précédente) ; la déposer reste le mieux, et la question disparaît alors à la régénération.
        pdf_def = next((x for x in inv if x["role"] in ("pdf_scanne", "def_pdf")), None)
        if pdf_def and scan_info:                     # le PDF dont on parle est celui que l'état décrit
            pdf_def = next((x for x in inv if x["fichier"] == scan_info["fichier"]), pdf_def)
        if mod_ecarte:
            texte = (f"La DEF déposée « {mod_ecarte['fichier']} » n'est pas utilisée : {mod_ecarte['motif']}. "
                     "Remplacez-la, ou indiquez pourquoi il n'y a pas de DEF précédente.")
        elif pdf_def and scan_info and scan_info.get("code") == "en_cours":
            texte = (f"« {pdf_def['fichier']} » (DEF scannée) est en cours de lecture sur ce poste"
                     + (f" — {scan_info['avancement']}" if scan_info.get("avancement") else "") +
                     ". Régénérez dans quelques minutes : cette question disparaîtra et le compte de résultat N-1 sera "
                     "repris. Si cette DEF n'est pas celle de l'exercice précédent, répondez ci-dessous.")
            res["def_pdf"] = {"fichier": pdf_def["fichier"], "nature": pdf_def["role"]}
        elif pdf_def:
            nature = "un PDF scanné (images seules)" if pdf_def["role"] == "pdf_scanne" else "un PDF"
            motif = scan_info["etat"] if scan_info else "ses chiffres ne sont pas lus"
            texte = (f"« {pdf_def['fichier']} » est {nature} : {motif}. Déposez la DEF précédente au "
                     "format Excel (.xlsx) si vous l'avez — c'est elle qui donne les comparatifs N-1 des notes, le compte "
                     "de résultat N-1 et l'identité ; sinon répondez « DEF précédente indisponible ».")
            res["def_pdf"] = {"fichier": pdf_def["fichier"], "nature": pdf_def["role"]}
        else:
            texte = ("Aucune DEF de l'exercice précédent n'est reconnue dans 01_sources. S'il en existe une, déposez-la "
                     "puis régénérez (elle fournit les comparatifs N-1 des notes et l'identité) ; sinon, indiquez pourquoi.")
        qs.insert(0, {"id": "sources.def_precedente", "categorie": "Sources", "type": "choix", "obligatoire": True,
                      "question": texte, "options": list(OPTIONS_DEF_PRECEDENTE), "impact": "colonnes N-1 des notes vides",
                      "defaut": None, "contexte": "Le bilan N-1 est tiré des soldes d'ouverture de la balance ; seules les "
                                                  "colonnes N-1 des notes restent vides. Une DEF déposée après la génération "
                                                  "n'est lue qu'à la régénération.",
                      "reponse": reponses.get("sources.def_precedente")})
    ecrire_json(os.path.join(qdir, "questions.json"), qs)
    if not definitif:
        for p in (fichiers.get("rapport_pdf", []) + fichiers.get("balance_pdf", []) + fichiers.get("controles_pdf", [])
                  + fichiers.get("sn_pdf", []) + fichiers.get("analyse_pdf", [])):
            filigrane(p)
    ouv = ouvertes(qs)
    version = {"version": k, "horodatage": horo, "statut": "definitive" if definitif else "projet",
               "valide_par": par if definitif else None,
               "sources": [x for x in inv if x["fichier"] in {v for v in res["sources"].values() if v}],
               "valide_le": maintenant() if definitif else None,
               # tout 01_sources tel que lu : une version ne se valide pas sur des sources qu'elle n'a pas lues
               "inventaire": [{k: x[k] for k in ("fichier", "role", "octets", "modifie_le", "sha256")} for x in inv],
               "identite_reprise": origines,
               "reponses_appliquees": reponses, "colonne_precedente": col,
               "livrables": [os.path.relpath(p, d) for ps in fichiers.values() for p in ps],
               "questions_obligatoires_ouvertes": len(ouv)}
    man.setdefault("versions", []).append(version)
    ecrire_json(os.path.join(d, "manifeste.json"), man)
    par_cat = {}
    for x in ouv:
        par_cat[x["categorie"]] = par_cat.get(x["categorie"], 0) + 1
    res.update({"statut": version["statut"], "version": k, "livrables": version["livrables"],
                "questions_obligatoires_ouvertes": len(ouv), "par_categorie": par_cat,
                "questions_facultatives": sum(1 for x in qs if not x["obligatoire"] and x.get("reponse") in (None, ""))})
    return res


def balance_depuis_grand_livre(pgl, dossier):
    """Balance 8 colonnes (CSV) reconstituée depuis le grand livre : (chemin, contrôles). Voir
    grand_livre.balance_reconstituee (à-nouveaux = ouvertures, clôture exclue, comptes centralisés repris)."""
    import csv
    import grand_livre
    lignes, ctrl = grand_livre.balance_reconstituee(grand_livre.lire(pgl))
    os.makedirs(dossier, exist_ok=True)
    p = os.path.join(dossier, "balance_reconstituee_depuis_grand_livre.csv")
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Compte", "Intitulé", "Ouverture D", "Ouverture C", "Mvt D", "Mvt C", "Solde D", "Solde C"])
        for a, lib, o, md, mc in lignes:
            s = round(o + md - mc, 2)
            w.writerow([a, lib, max(o, 0), max(-o, 0), md, mc, max(s, 0), max(-s, 0)])
    return p, ctrl


def repondre(d, id_, valeur, canal=None):
    qs = lire_json(os.path.join(d, "04_questions", "questions.json"), [])
    q = next((x for x in qs if x["id"] == id_), None)
    if q is None and not id_.startswith(("identite.", "tf5nif.", "interp.", "fait.", "reint.", "balance.", "scan.")):
        raise SystemExit(f"Question inconnue : {id_}")
    if id_.startswith("scan.") and montant_saisi(valeur) is None:
        raise SystemExit(f"« {valeur} » n'est pas un montant (chiffres, espaces, signe « - » ou parenthèses)")
    if q and q.get("options") and valeur not in q["options"]:
        raise SystemExit(f"Réponse « {valeur} » hors des choix proposés : {', '.join(q['options'])}")
    p = os.path.join(d, "04_questions", "reponses.json")
    r = lire_json(p, {})
    r[id_] = valeur
    r.setdefault("_journal", []).append({"id": id_, "valeur": valeur, "le": maintenant(),
                                         **({"canal": canal} if canal in CANAUX else {})})
    ecrire_json(p, r)
    return {"enregistre": id_, "a_regenerer": True}


def valider(d, par):
    # d'abord les sources : une DEF déposée après la génération laisse une question périmée ouverte, et le bon geste
    # est de régénérer, pas d'y répondre
    modif = sources_modifiees(d)
    if modif:
        noms = ", ".join(f"{x['fichier']} ({x['role']})" for k in ("ajoutes", "remplaces", "retires") for x in modif[k])
        return {"statut": "refuse", "sources_modifiees": modif,
                "raison": f"01_sources a changé depuis la version {modif['depuis_version']} ({noms}) : régénérez le projet "
                          "et relisez-le avant de valider — une version ne se valide pas sur des fichiers qu'elle n'a pas lus"}
    qs = lire_json(os.path.join(d, "04_questions", "questions.json"), [])
    reponses = lire_json(os.path.join(d, "04_questions", "reponses.json"), {})
    for x in qs:
        x["reponse"] = reponses.get(x["id"], x.get("reponse"))
    ouv = ouvertes(qs)
    if ouv:
        return {"statut": "refuse", "raison": f"{len(ouv)} question(s) obligatoire(s) sans réponse",
                "questions": [{"id": x["id"], "question": x["question"]} for x in ouv]}
    if not par:
        return {"statut": "refuse", "raison": "indiquer qui valide (--par)"}
    res = generer(d, definitif=True, par=par)
    if res.get("statut") == "definitive":
        res["fiche_entite"] = ecrire_fiche_entite(d, par)
    return res


def ecrire_fiche_entite(d, par):
    """Après validation : l'identité RETENUE est posée dans le dossier de l'entité (fiche_entite.json), pour que
    l'exercice suivant ne la redemande pas. Elle reste une proposition, affichée et corrigeable."""
    man = lire_json(os.path.join(d, "manifeste.json"), {})
    v = (man.get("versions") or [{}])[-1]
    ident = {k.partition(".")[2]: val for k, val in (v.get("reponses_appliquees") or {}).items()
             if isinstance(k, str) and k.startswith("identite.") and isinstance(val, str) and val.strip()}
    if not ident:
        return None
    p = os.path.join(os.path.dirname(d), "fiche_entite.json")
    ecrire_json(p, {"identite": ident, "source": f"DEF {man.get('exercice')} validée par {par} le {maintenant()}"})
    return os.path.basename(p)


def main():
    p = argparse.ArgumentParser(description="Dossier de travail de la DEF (automatique d'abord, questions ensuite).")
    p.add_argument("action", choices=["init", "lancer", "questions", "repondre", "valider", "chemin"])
    p.add_argument("--entite", required=True)
    p.add_argument("--exercice", type=int, required=True)
    p.add_argument("--racine")
    p.add_argument("--id")
    p.add_argument("--valeur")
    p.add_argument("--par")
    p.add_argument("--sans-pdf", action="store_true")
    p.add_argument("--brut", action="store_true",
                   help="sortie NON filtrée (usage humain dans un terminal ; jamais depuis un assistant)")
    a = p.parse_args()
    # la ligne de commande est un REPLI du serveur MCP : ce qu'elle affiche peut être lu par un assistant, donc elle
    # passe par la même passerelle de confidentialité (pseudonymes, montants masqués, journal), sauf --brut
    serveur = os.path.join(HERE, "..", "..", "..", "serveur")
    P = None
    if not a.brut and os.path.exists(os.path.join(serveur, "confidentialite.py")):
        sys.path.insert(0, serveur)
        import confidentialite
        P = confidentialite.Passerelle(a.racine or racine_defaut())
        P.apprendre_racine()
        a.entite, a.id = P.entree(a.entite), P.entree(a.id)
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO() if P else sys.stdout):   # affichages internes du calcul : tus
        r = _action(a)
    if P:
        P = confidentialite.Passerelle(a.racine or racine_defaut())
        P.apprendre_racine()
        r = P.sortie("cli:" + a.action, r)
    print(json.dumps(r, ensure_ascii=False, indent=1, default=str))


def _action(a):
    d = init(a.racine, a.entite, a.exercice)
    if a.action in ("init", "chemin"):
        r = {"dossier": d, "sources": os.path.join(d, "01_sources"),
             "a_deposer": "balance (obligatoire), grand livre, DEF de référence, logo"}
    elif a.action == "lancer":
        r = generer(d, pdf=not a.sans_pdf)
    elif a.action == "questions":
        qs = lire_json(os.path.join(d, "04_questions", "questions.json"), [])
        rep = lire_json(os.path.join(d, "04_questions", "reponses.json"), {})
        r = [{k: x[k] for k in ("id", "categorie", "question", "type", "options", "obligatoire", "impact", "contexte")}
             | {"reponse": rep.get(x["id"], x.get("reponse"))} for x in qs]
    elif a.action == "repondre":
        r = repondre(d, a.id, a.valeur)
    else:
        r = valider(d, a.par)
    return r


if __name__ == "__main__":
    main()
