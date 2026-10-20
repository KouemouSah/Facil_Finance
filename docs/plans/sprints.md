---
icon: lucide/milestone
---

# Plan de sprints — codage avec Claude Code

<span class="statut statut--brouillon">brouillon</span> · Version 0.2 · 15/10/2026

!!! abstract "Le principe"
    Sprints d'**une semaine**, du lundi au vendredi. Claude Code écrit le code. Le développeur responsable **relit, tranche et fusionne** ; le porteur **arbitre** dans la journée.

    Pour chaque sprint : un objectif, des exigences (`EX-…`) et une démonstration le vendredi. On ne planifie en détail que la semaine en cours et la suivante ; au-delà, on planifie par objectif. Toutes les dates viennent de `plans/calendrier.yml`, comme celles du [plan de versions](feuille-de-route.md).

## 1. Une journée type

<div class="facil-etapes facil-etapes--compactes">
  <div class="facil-etape"><span class="facil-etape__num">1</span><span class="facil-etape__icone">:lucide-clipboard-list:</span><span class="facil-etape__titre">Planifier</span><span class="facil-etape__texte">Les tâches du jour, chacune rattachée à une exigence EX-…</span></div>
  <span class="facil-etape__fleche" aria-hidden="true">:lucide-arrow-right:</span>
  <div class="facil-etape"><span class="facil-etape__num">2</span><span class="facil-etape__icone">:lucide-code-xml:</span><span class="facil-etape__titre">Coder</span><span class="facil-etape__texte">Claude Code écrit le code et ses tests</span></div>
  <span class="facil-etape__fleche" aria-hidden="true">:lucide-arrow-right:</span>
  <div class="facil-etape"><span class="facil-etape__num">3</span><span class="facil-etape__icone">:lucide-shield-check:</span><span class="facil-etape__titre">Prouver</span><span class="facil-etape__texte">Gardes et contre-épreuves ; si c'est rouge, retour à l'étape 2</span></div>
  <span class="facil-etape__fleche" aria-hidden="true">:lucide-arrow-right:</span>
  <div class="facil-etape"><span class="facil-etape__num">4</span><span class="facil-etape__icone">:lucide-eye:</span><span class="facil-etape__titre">Relire</span><span class="facil-etape__texte">Un humain : sécurité, SQL, portée, licences</span></div>
  <span class="facil-etape__fleche" aria-hidden="true">:lucide-arrow-right:</span>
  <div class="facil-etape"><span class="facil-etape__num">5</span><span class="facil-etape__icone">:lucide-git-merge:</span><span class="facil-etape__titre">Fusionner</span><span class="facil-etape__texte">Seulement après relecture</span></div>
  <span class="facil-etape__fleche" aria-hidden="true">:lucide-arrow-right:</span>
  <div class="facil-etape"><span class="facil-etape__num">6</span><span class="facil-etape__icone">:lucide-file-pen:</span><span class="facil-etape__titre">Documenter</span><span class="facil-etape__texte">Ce que le changement rend faux est corrigé</span></div>
  <span class="facil-etape__fleche" aria-hidden="true">:lucide-arrow-right:</span>
  <div class="facil-etape"><span class="facil-etape__num">7</span><span class="facil-etape__icone">:lucide-rotate-ccw:</span><span class="facil-etape__titre">Reprise</span><span class="facil-etape__texte">Le prochain geste est écrit dans le plan</span></div>
</div>

**Définition de « terminé »**, la même pour tous les sprints :

1. L'exigence est démontrée par un test **et** par une exécution réelle.
2. Toute garde ajoutée a sa contre-épreuve : une erreur introduite exprès est détectée.
3. Le SQL touché est relu : index sur ce qui filtre, pas de N+1, lectures bornées, verrous.
4. La portée est mesurée : ce qui lit la même table ou appelle la même route a été vérifié.
5. La documentation que le changement rend fausse est corrigée dans la même fusion.
6. Aucune donnée de client dans le code, les tests ou les journaux.

## 2. Les sprints

### Sprint 0 — Cadrage · {{cal:periode:s0}} <span class="statut statut--valide">fait</span>
Termes de référence, PRD, ADR, plans, ce site.

### Sprint 1 — Fondations · {{cal:periode:s1}} <span class="statut statut--valide">fait</span>
**Objectif** : un moteur sans aucune règle propre à un pays, et deux packs qui le prouvent.

!!! success "Résultat"
    Le code vit dans le dépôt `facil-finance` (commits locaux, un par jour).

    | Livré | Preuve |
    |---|---|
    | Format du pack et outil de validation (`facil_pack.py`) : couches OHADA ← zone ← pays, signature Ed25519, choix du pack en vigueur à la date de clôture | 35 tests, **une contre-épreuve par règle** |
    | Couches communes OHADA et CEMAC, générées depuis le moteur (recette rejouable) | 186 règles « compte → poste », 99 postes, 241 lignes de notes, 6 contrôles communs |
    | Pack Cameroun (préversion, décision D9) : formulaire SN comparé au formulaire officiel de la DGI | **148 postes et 241 lignes de notes identiques** ; seules diffèrent des coquilles et les formules (absentes de la version officielle) |
    | Pack Cameroun : 23 paramètres fiscaux, chacun avec son article (CGI 2026 recoupé avec 2024) | **IS de la SIC (DSF 2025 publiée) reproduit au franc près** : 559 945 947 F |
    | Pack Cameroun : structure du système minimal de trésorerie | relevée sur l'annexe officielle ; correspondance **proposée**, faute de liasse SMT réelle |
    | Noyau du moteur extrait en bibliothèque, source unique publiée vers le plugin | plugin vert : **195 contrôles sur 195** ; garde de parité et sa contre-épreuve |
    | Guinée équatoriale convertie au format pack | paramètres identiques clé par clé ; **calcul fiscal identique** sur 4 balances types |
    | Recette unique `verifier_tout.py`, branchée en crochet de commit | contre-épreuve : un pack cassé refuse le commit |

    **Écarts et apprentissages** :
    - La recherche plaçait l'assiette du minimum de perception sur le CA de l'exercice *précédent*. La DSF déposée de la SIC l'applique au CA de l'**exercice** : c'est ce que retient le pack, avec la divergence inscrite (à confirmer, R14).
    - Chez la SIC, le minimum ne l'emporte pas sur l'IS : ce cas reste à éprouver.
    - La recherche fiscale a pris plus de temps que prévu, car les lois de finances 2025 et 2026 ne sont publiées qu'en scans.

| Jour | Travail | Exigences |
|---|---|---|
| Lundi | Format du pack (manifeste, structure, signature) ; outil de validation des packs | EX-PROD-5, EX-PROD-8 |
| Mardi | Pack Cameroun SN : formulaire officiel comparé à celui embarqué, correspondances | EX-PROD-1 |
| Mercredi | Pack Cameroun : paramètres fiscaux avec leurs articles ; SMT | EX-PROD-2, EX-PROD-5 |
| Jeudi | Extraction du moteur en bibliothèque ; le plugin passe au vert dessus | EX-PROD-6 |
| Vendredi | GE convertie au format pack : **identique au franc près** ; démonstration sur la DSF 2025 publiée de la SIC | EX-PROD-4 |

### Sprint 2 — V1.0 Socle · {{cal:periode:s2}}
**Objectif** : de l'installation à la liasse DÉFINITIVE, sur un serveur Linux et sur un poste Windows.

| Jour | Travail | Exigences |
|---|---|---|
| Lundi | Schéma de la base (écritures immuables, versions, droits, audit) ; migrations | EX-IMP-4, EX-PLAT-2 |
| Mardi | API : import, production, versions ; droits tenus par la base | EX-IMP-1 à 3, EX-PLAT-3 |
| Mercredi | Interface : écrans critiques (import, questions, liasse, validation) ; sessions à deux horloges | EX-REV-1, EX-PLAT-4 |
| Jeudi | Installeurs `.run`, `.deb`, `.rpm` et MSI ; mode `--unattended` ; matrice d'installation en CI | EX-PLAT-5 |
| Vendredi | Pack Sénégal (SN + SMT) ; sauvegarde et restauration exercées ; licence hors ligne | EX-PLAT-6, EX-PLAT-8 |

### Sprint 3 — V1.1 Kaem texte et V1.2 Production · {{cal:periode:s3}}
**Objectif** : Kaem explique et prépare sans jamais calculer ; la saisie écrit dans le même grand livre.

| Période | Travail | Exigences |
|---|---|---|
| {{cal:periode:s3a}} | Paquet IA (téléchargement signé, reprise, détection du matériel) ; llama.cpp + Gemma 4 E4B ; catalogue de commandes ; chat et palette ; journal ; cas d'injection | EX-IA-1 à 4 |
| {{cal:periode:s3b}} | Saisie, extourne, numérotation sans trou ; lettrage ; clôtures et périodes verrouillées ; TVA ; OCR avec validation humaine ; analyse des écritures | EX-CPT-1 à 7, EX-REP-3 |

### Sprint 4 — V2.0 SaaS et V2.1 Voix · {{cal:periode:s4}}
**Objectif** : plusieurs clients isolés par la base ; Kaem parle.

| Période | Travail | Exigences |
|---|---|---|
| {{cal:periode:s4a}} | Isolation au niveau des lignes et banc d'isolation (contre-épreuve) ; Keycloak ; souscription, facturation, restitution des données ; migration aller-retour ; console | EX-SAAS-1 à 7 |
| {{cal:periode:s4b}} | Écoute (Gemma 4) ; voix Kokoro FR, ES, PT ; témoin et coupure du micro ; alertes | EX-VOX-1 à 4 |

### Durcissement · {{cal:periode:s5a}}
Revue de sécurité (OWASP ASVS niveau 2 en autocontrôle, OWASP API Top 10), mesures de performance sur des volumes réalistes, matrice d'installation complète, manuels FR, ES et PT.

### Recette · {{cal:periode:recette}} — Livraison le {{cal:jalon-long:livraison}}
Recette métier avec l'expert-comptable et 2 ou 3 pilotes ; banc de Kaem sur les 3 PC de référence ; décision de statut par version ([plan de versions](feuille-de-route.md)).

## 3. Tâches reportées, avec leur échéance

| Tâche | Pourquoi | Échéance |
|---|---|---|
| Gabarit Excel du **SMT** pour le Cameroun (le formulaire officiel n'existe qu'en PDF scanné) | Sans gabarit, le moteur ne peut pas produire le SMT | fin du sprint 2 ({{cal:fin:s2}}) |
| Confirmer la formule G = C − D + E − F du compte de résultat SMT (D et E ne sont pas définis par le formulaire) | Le résultat SMT en dépend | avec un expert inscrit (R14) |
| Éprouver le cas où le **minimum de perception l'emporte** sur l'IS, sur une DSF publiée déficitaire ou peu bénéficiaire | La démonstration SIC ne le couvre pas | fin du sprint 2 ({{cal:fin:s2}}) |
| Clé de signature de **production** des packs (aujourd'hui : clé de développement, hors dépôt) | Un pack publié doit être signé par une clé tenue en exploitation | avant la recette ({{cal:fin:s5a}}) |
| Intitulés espagnols exacts du ministère et de la DGIC (pack GQ) | Un seul fragment trouvé dans le gabarit | avant la recette ({{cal:fin:s5a}}) |
| Assiette du minimum de perception (CA de l'exercice ou de l'exercice précédent) | Divergence entre la recherche et la DSF de la SIC | avec un expert inscrit (R14) |

## 4. Reprise

- **Dépôt du code** : `C:\DSF\facil-finance` (git local, branche `master`). Dernier commit : `git -C C:\DSF\facil-finance log --oneline -1` (fin du sprint 1, rien depuis).
- **Vérifier l'état** : `.venv\Scripts\python.exe outils\verifier_tout.py` (packs, tests, parité avec le plugin). À rejouer AVANT le premier changement du sprint 2 : le noyau publié vers le plugin n'a pas bougé, mais le plugin, lui, a évolué (voir ci-dessous).
- **Dernière tâche close** : sprint 1 (format du pack, packs OHADA, CEMAC, CM et GQ, noyau extrait).
- **Entre le sprint 1 et le sprint 2** (travail hors `facil-finance`) :
    - le plugin `compta-ohada` est passé en 0.13.0 : DSF précédente scannée lue par OCR et prouvée par les formules, analyse financière pluriannuelle (reprise : `C:\DSF\documentation\analyse\plan-plugin-autonome.md`, section Reprise) ;
    - manuel d'utilisation, présentation commerciale et flyer, en français (DSF) et en espagnol (DEF), dans `C:\DSF\manuel\livrable` ;
    - plugin `documents-pro` en 1.1.4 (libellés de mise en page configurables, pour les documents en espagnol).
- **Prochain geste exact** : sprint 2, lundi ({{cal:periode:s2}}). Schéma de la base (écritures immuables, versions, droits, audit) et migrations, dans `facil-finance/`. Les calculs ne se réécrivent pas : le noyau (source unique dans `facil-finance`) et `analyse_financiere.py` (encore dans le plugin seulement, à extraire dans le noyau quand le socle en aura besoin) s'appellent.
- **Question ouverte au porteur** : passer l'interface du plugin en « DSF » en français (boutons « Régénérer la DEF… », options « DEF précédente… ») dans une 0.13.1, avec de nouvelles captures pour le manuel. Tant qu'elle n'est pas tranchée, le manuel français cite ces libellés tels quels.
- **Non commité** : rien dans `facil-finance` (le crochet refuse un commit rouge). `projet_doc`, `compta-ohada` et `manuel` ne sont pas des dépôts git.

## 5. Capacité — l'hypothèse qu'il faut surveiller

!!! warning "Le goulet, c'est la relecture"
    Claude Code produit plus de code qu'un humain ne peut en relire. Le calendrier suppose **un développeur responsable à plein temps** qui relit et fusionne, et **un porteur qui tranche dans la journée**.

    **Indicateur suivi chaque jour** : le nombre de changements en attente de relecture. Au-delà d'une journée de retard, la tâche la moins prioritaire du sprint glisse à la version suivante. Le délai de relecture, lui, n'est jamais raccourci.
