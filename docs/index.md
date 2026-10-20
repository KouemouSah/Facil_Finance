---
icon: lucide/house
hide:
  - toc
---

<div class="facil-banniere" markdown>
<span class="facil-badge">:lucide-file-check: Documentation projet · brouillon v0.1</span>

# Facil Finance — la liasse SYSCOHADA, juste et prouvée

<p class="facil-banniere__chapo">Une plateforme de production financière pour les 17 États de l'OHADA. Elle importe la balance, le grand livre ou les écritures du logiciel de l'entreprise, puis produit la révision, les états financiers (système normal et système minimal), la liasse fiscale de chaque pays et le reporting. Elle fonctionne toujours en mode serveur, sous Windows et sous toutes les distributions Linux, sans dépendance à installer, avec une assistante locale, Kaem.</p>
</div>

<div class="facil-chiffres">
  <div class="facil-chiffre"><span class="facil-chiffre__icone">:lucide-globe:</span><span class="facil-chiffre__valeur">{{NB_PAYS}}</span><span class="facil-chiffre__libelle">États couverts à terme</span></div>
  <div class="facil-chiffre"><span class="facil-chiffre__icone">:lucide-milestone:</span><span class="facil-chiffre__valeur">{{NB_VERSIONS}}</span><span class="facil-chiffre__libelle">Versions, V1.0 à V2.1</span></div>
  <div class="facil-chiffre"><span class="facil-chiffre__icone">:lucide-list-checks:</span><span class="facil-chiffre__valeur">{{NB_EXIGENCES}}</span><span class="facil-chiffre__libelle">Exigences tracées</span></div>
  <div class="facil-chiffre"><span class="facil-chiffre__icone">:lucide-scale:</span><span class="facil-chiffre__valeur">{{NB_ADR}}</span><span class="facil-chiffre__libelle">Décisions d'architecture</span></div>
  <div class="facil-chiffre"><span class="facil-chiffre__icone">:lucide-triangle-alert:</span><span class="facil-chiffre__valeur">{{NB_RISQUES}}</span><span class="facil-chiffre__libelle">Risques suivis</span></div>
</div>

## Parcourir la documentation

<div class="facil-cartes">
  <a class="facil-carte" href="tdr.html">
    <span class="facil-carte__icone">:lucide-file-text:</span>
    <span class="facil-carte__titre">Termes de référence</span>
    <span class="facil-carte__texte">Ce qui est livré, quand, comment on le reçoit. Le document à remettre à un financeur ou à un partenaire.</span>
    <span class="facil-carte__action">Lire :lucide-arrow-right:</span>
  </a>
  <a class="facil-carte facil-carte--nuit" href="prd.html">
    <span class="facil-carte__icone">:lucide-list-checks:</span>
    <span class="facil-carte__titre">Exigences produit</span>
    <span class="facil-carte__texte">Personas, exigences numérotées par domaine et par version, critères d'acceptation et mesures de succès.</span>
    <span class="facil-carte__action">Explorer :lucide-arrow-right:</span>
  </a>
  <a class="facil-carte facil-carte--clair" href="architecture.html">
    <span class="facil-carte__icone">:lucide-network:</span>
    <span class="facil-carte__titre">Architecture</span>
    <span class="facil-carte__texte">Vues C4, déploiement et flux de production d'une liasse, avec les principes non négociables.</span>
    <span class="facil-carte__action">Visualiser :lucide-arrow-right:</span>
  </a>
  <a class="facil-carte" href="adr/index.html">
    <span class="facil-carte__icone">:lucide-scale:</span>
    <span class="facil-carte__titre">Décisions (ADR)</span>
    <span class="facil-carte__texte">Chaque choix structurant, avec les options écartées et ses conséquences.</span>
    <span class="facil-carte__action">Consulter :lucide-arrow-right:</span>
  </a>
  <a class="facil-carte facil-carte--ambre" href="specs/pack-pays.html">
    <span class="facil-carte__icone">:lucide-package:</span>
    <span class="facil-carte__titre">Format du pack pays</span>
    <span class="facil-carte__texte">Tout ce qui dépend d'un pays, déclaré en données signées et datées. Le moteur ne connaît aucun pays.</span>
    <span class="facil-carte__action">Spécifier :lucide-arrow-right:</span>
  </a>
  <a class="facil-carte facil-carte--nuit" href="plans/feuille-de-route.html">
    <span class="facil-carte__icone">:lucide-calendar-range:</span>
    <span class="facil-carte__titre">Plan de versions</span>
    <span class="facil-carte__texte">Cinq versions codées en un mois avec Claude Code, livrées le {{cal:jalon-long:livraison}} : statut de chacune et preuves qui restent à obtenir.</span>
    <span class="facil-carte__action">Planifier :lucide-arrow-right:</span>
  </a>
  <a class="facil-carte facil-carte--clair" href="plans/roadmap.html">
    <span class="facil-carte__icone">:lucide-map:</span>
    <span class="facil-carte__titre">Roadmap</span>
    <span class="facil-carte__texte">Les 18 mois après la livraison, trimestre par trimestre, jusqu'à la couverture des 17 États.</span>
    <span class="facil-carte__action">Voir :lucide-arrow-right:</span>
  </a>
  <a class="facil-carte facil-carte--nuit" href="demarrer.html">
    <span class="facil-carte__icone">:lucide-rocket:</span>
    <span class="facil-carte__titre">Démarrer</span>
    <span class="facil-carte__texte">Poste de développement, vérifications, et reprise du travail par Claude Code sur le web.</span>
    <span class="facil-carte__action">Installer :lucide-arrow-right:</span>
  </a>
  <a class="facil-carte facil-carte--clair" href="facil-def.html">
    <span class="facil-carte__icone">:lucide-file-check:</span>
    <span class="facil-carte__titre">Facil DEF, l'extension livrée</span>
    <span class="facil-carte__texte">La DSF de Guinée équatoriale : OCR des DSF scannées prouvé par les formules, analyse financière pluriannuelle.</span>
    <span class="facil-carte__action">Découvrir :lucide-arrow-right:</span>
  </a>
  <a class="facil-carte" href="modele-donnees.html">
    <span class="facil-carte__icone">:lucide-database:</span>
    <span class="facil-carte__titre">Modèle de données cible</span>
    <span class="facil-carte__texte">Grand livre immuable, versions, droits tenus par la base, audit chaîné : le point de départ du sprint 2.</span>
    <span class="facil-carte__action">Concevoir :lucide-arrow-right:</span>
  </a>
  <a class="facil-carte facil-carte--ambre" href="chaine-livraison.html">
    <span class="facil-carte__icone">:lucide-workflow:</span>
    <span class="facil-carte__titre">Chaîne de livraison</span>
    <span class="facil-carte__texte">CI/CD, gardes et leurs contre-épreuves, publication sur GitHub Pages, confidentialité du dépôt public.</span>
    <span class="facil-carte__action">Vérifier :lucide-arrow-right:</span>
  </a>
</div>

## Par où commencer

| Si vous êtes… | Commencez par |
|---|---|
| Financeur, partenaire, client grand compte | [Termes de référence](tdr.md) |
| Responsable produit, expert-comptable valideur | [Exigences produit](prd.md), puis [Couverture des pays](plans/couverture-pays.md) |
| Architecte, développeur | [Démarrer](demarrer.md), [Architecture](architecture.md), puis les [ADR](adr/index.md), le [catalogue des modules](catalogue-modules.md) et le [format du pack pays](specs/pack-pays.md) |
| Session Claude Code web | `CLAUDE.md` du dépôt, puis la reprise du [plan de sprints](plans/sprints.md) |
| Utilisateur de Facil DEF | Les [manuels](manuels.md) (français, espagnol) |
| Nouvel arrivant | Le [glossaire](glossaire.md), puis la [feuille de route](plans/feuille-de-route.md) |

!!! note "Règles de cette documentation"
    - **Une seule source par fait.** Un document renvoie à un autre ; il ne le recopie pas. Les chiffres ci-dessus sont recalculés à chaque construction à partir des documents eux-mêmes.
    - **Chaque document porte son statut** (<span class="statut statut--brouillon">brouillon</span> ou <span class="statut statut--valide">validé</span>), avec sa date et sa version.
    - **Ce qui n'est pas prouvé se dit** : les durées, tailles et performances non mesurées sont marquées *hypothèse*.
    - **Aucune donnée de client** : la construction échoue si un nom de client apparaît.
    - **Code et tâches** : dépôt [KouemouSah/Facil_Finance](https://github.com/KouemouSah/Facil_Finance), [tickets par sprint](https://github.com/KouemouSah/Facil_Finance/milestones).
