---
icon: lucide/map
---

# Roadmap — de la livraison à la couverture des 17 États

<span class="statut statut--brouillon">brouillon</span> · Version 0.2 · 15/10/2026

!!! info "Une seule source pour toutes les dates"
    La frise, le tableau ci-dessous, le [plan de versions](feuille-de-route.md), le [plan de sprints](sprints.md) et la [couverture des pays](couverture-pays.md) sont **générés** depuis `plans/calendrier.yml`. Ils ne peuvent pas diverger : une date écrite à la main dans l'une de ces pages fait échouer la construction du site.

## 1. Trois niveaux de planification

<div class="facil-etapes">
  <div class="facil-etape">
    <span class="facil-etape__icone">:lucide-map:</span>
    <span class="facil-etape__titre">Roadmap</span>
    <span class="facil-etape__texte"><strong>Pourquoi</strong> et <strong>vers quoi</strong> : thèmes, résultats, marchés. Par trimestre, avec un degré de confiance.</span>
    <span class="facil-etape__meta">Horizon : 18 mois</span>
  </div>
  <span class="facil-etape__fleche" aria-hidden="true">:lucide-arrow-right:</span>
  <a class="facil-etape" href="feuille-de-route.html">
    <span class="facil-etape__icone">:lucide-calendar-range:</span>
    <span class="facil-etape__titre">Plan de versions</span>
    <span class="facil-etape__texte"><strong>Quoi</strong> et à quel critère : contenu, statut, preuves restantes. Par semaine.</span>
    <span class="facil-etape__meta">Jusqu'au {{cal:jalon-long:livraison}}</span>
  </a>
  <span class="facil-etape__fleche" aria-hidden="true">:lucide-arrow-right:</span>
  <a class="facil-etape" href="sprints.html">
    <span class="facil-etape__icone">:lucide-milestone:</span>
    <span class="facil-etape__titre">Plan de sprints</span>
    <span class="facil-etape__texte"><strong>Comment</strong> et par qui : tâches, exigences, démonstration. Par jour.</span>
    <span class="facil-etape__meta">La semaine en cours et la suivante</span>
  </a>
</div>

Plus l'horizon est lointain, plus la précision baisse. Une date au jour près dans 18 mois serait une fausse promesse.

## 2. Vue d'ensemble

{{cal:roadmap-frise}}

## 3. Par trimestre

{{cal:roadmap-tableau}}

## 4. Ce qui fait avancer ou reculer cette roadmap

<div class="facil-colonnes">
  <div class="facil-colonne facil-colonne--plus">
    <span class="facil-colonne__icone">:lucide-rocket:</span>
    <span class="facil-colonne__titre">Accélère</span>
    <ul>
      <li>:lucide-user-check: Un expert-comptable local disponible</li>
      <li>:lucide-file-check: Des liasses réelles fournies par les pilotes</li>
      <li>:lucide-download: Un modèle officiel téléchargeable (Cameroun, Sénégal, Togo)</li>
    </ul>
  </div>
  <div class="facil-colonne facil-colonne--moins">
    <span class="facil-colonne__icone">:lucide-hourglass:</span>
    <span class="facil-colonne__titre">Ralentit</span>
    <ul>
      <li>:lucide-search-x: Un modèle officiel introuvable (Côte d'Ivoire, Congo, Niger, Tchad, RDC)</li>
      <li>:lucide-scroll-text: Une loi de finances qui change en cours d'exercice</li>
      <li>:lucide-shield-check: L'attente de l'audit de sécurité avant d'ouvrir le SaaS</li>
    </ul>
  </div>
  <div class="facil-colonne facil-colonne--neutre">
    <span class="facil-colonne__icone">:lucide-scale:</span>
    <span class="facil-colonne__titre">Ne dépend pas du code</span>
    <ul>
      <li>:lucide-check-check: Après la livraison, le rythme est fixé par les <strong>preuves</strong> : experts, liasses, audits</li>
      <li>:lucide-gavel: La marque et les contrats suivent le calendrier du juriste et de l'OAPI</li>
      <li>:lucide-bot: Claude Code accélère le code, pas la validation</li>
    </ul>
  </div>
</div>

## 5. Revue

La roadmap est revue **chaque mois** à la démonstration de fin de sprint, et chaque trimestre avec le porteur. Un trimestre décalé se modifie **dans `plans/calendrier.yml`**, avec sa raison dans le message de modification : toutes les pages suivent d'elles-mêmes.
