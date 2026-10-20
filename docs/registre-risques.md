---
icon: lucide/triangle-alert
---

# Registre des risques

<span class="statut statut--brouillon">brouillon</span> · Version 0.1 · 15/10/2026 · Revu à chaque jalon

Probabilité (P) et impact (I) sont notés de 1 à 3. **Criticité = P × I** ; un risque de criticité 6 ou plus a un propriétaire et une échéance.

| ID | Risque | P | I | Criticité | Réponse | Signal d'alerte |
|---|---|---|---|---|---|---|
| R1 | Liasse non conforme au format officiel d'un pays | 2 | 3 | **6** | Pack validé par un expert local ; reproduction de liasses réelles ; gardes de non-régression | Écart non expliqué sur le banc |
| R2 | Dispersion du périmètre : ERP, IA, 17 pays et SaaS en même temps | 3 | 3 | **9** | Feuille de route par versions ; une version n'ouvre qu'après la fermeture de la précédente ([ADR 0004](adr/0004-erp-entree-par-la-production.md)) | Deux versions en cours en parallèle |
| R3 | Kaem trop lent sur processeur seul | 2 | 2 | 4 | Banc sur 3 PC de référence ; réponses en flux continu ; repli sur Gemma 4 E2B ([ADR 0007](adr/0007-kaem-ia-locale.md)) | Premier mot au-delà de 3 s sur le PC le plus faible |
| R4 | Modèle officiel introuvable (Côte d'Ivoire, Congo, Niger, Tchad, RDC) | 3 | 2 | **6** | Expert local ou demande à l'administration ; le pays recule dans l'ordre de couverture | Pas de modèle 2 mois avant la saison de dépôt |
| R5 | Conflit de marque sur « Kaem » (KAEM Technologies, Inde, éditeur de « KAEM Accounts ») | 2 | 2 | 4 | Recherche d'antériorité à l'OAPI ; Kaem n'est utilisé qu'à l'intérieur du produit ; variante « Kaem by Facil » | Opposition, ou antériorité trouvée |
| R6 | Fuite de données de clients (dans le produit, la documentation ou les journaux) | 1 | 3 | 3 | Passerelle de confidentialité ; garde des noms à l'empaquetage et dans ce site ; pas de télémétrie sans accord | Garde rouge |
| R7 | Licence incompatible dans une dépendance ou un modèle | 2 | 3 | **6** | Inventaire des dépendances (SBOM) et registre des licences en CI ; Valkey plutôt que Redis | Nouvelle dépendance non enregistrée |
| R8 | Changement fiscal en cours d'exercice (loi de finances) | 3 | 2 | **6** | Packs datés par exercice, avec une date de validité ; veille par pays | Loi de finances publiée |
| R9 | Matériel client sous le minimum (moins de 16 Go de RAM pour Kaem) | 2 | 1 | 2 | Kaem refusé et l'utilisateur prévenu ; le produit reste complet sans lui | — |
| R10 | Dépendance à une seule personne pour le moteur | 2 | 3 | **6** | Documentation as code ; ADR ; tests de référence ; entiercement du code | Une seule personne capable de modifier le moteur |
| R11 | Coupures électriques en cours de production | 3 | 1 | 3 | Transactions atomiques ; versions jamais écrasées ; reprise sur incident de la base | — |
| R12 | La relecture humaine n'absorbe pas le volume de code produit par Claude Code | 3 | 3 | **9** | Un développeur responsable à plein temps ; changements petits ; gardes et contre-épreuves à chaque fusion ; la tâche la moins prioritaire glisse ; le délai de relecture n'est jamais raccourci ([ADR 0013](adr/0013-developpement-avec-claude-code.md)) | Plus d'une journée de changements en attente de relecture |
| R14 | Pack pays validé sans expert-comptable humain (décision D9 : Claude fait office d'expert à partir des textes officiels et des liasses publiées) : une erreur d'interprétation fiscale n'est relevée par personne, et aucune signature n'engage un professionnel | 2 | 3 | **6** | Chaque taux cité avec son article et son URL ; reproduction de liasses réelles publiées ; écarts tous expliqués ; statut « préversion » tant qu'aucun expert inscrit n'a signé ; **signature obligatoire avant la première vente** dans le pays | Un écart que la loi de finances n'explique pas |
| R13 | Confondre « code livré » et « version disponible » : vendre une version sans ses preuves externes | 2 | 3 | **6** | Deux dates par version dans le [plan de versions](plans/feuille-de-route.md) ; statut « préversion » affiché dans le produit ; aucune donnée réelle en SaaS avant l'audit | Une demande commerciale sur une préversion |
