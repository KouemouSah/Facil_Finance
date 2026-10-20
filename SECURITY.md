# Politique de sécurité

## Versions suivies

| Composant | Version | Correctifs de sécurité |
|---|---|---|
| Facil Finance (moteur, packs) | branche `develop` | oui |
| Facil DEF, extension Claude Desktop (`plugin/compta-ohada`) | 0.13.x | oui |
| Versions antérieures de l'extension | < 0.13 | non : réinstaller la dernière |

## Signaler une vulnérabilité

**N'ouvrez pas de ticket public.** Utilisez le signalement privé de GitHub (onglet *Security* → *Report a vulnerability*) ou écrivez à **sah@emacsah.com**, objet « [SÉCURITÉ] Facil Finance ».

Indiquez : le composant et la version, les étapes pour reproduire, l'impact constaté, et si possible une proposition de correction. **N'envoyez jamais de données réelles d'un client** : un exemple synthétique suffit.

| Étape | Délai |
|---|---|
| Accusé de réception | 3 jours ouvrés |
| Première évaluation (gravité, périmètre) | 10 jours ouvrés |
| Correctif ou contournement, gravité critique ou élevée | 30 jours |
| Publication coordonnée | après le correctif, avec mention du découvreur s'il le souhaite |

## Gravité

| Niveau | Exemples |
|---|---|
| Critique | Fuite de données d'un client hors du poste ; exécution de code à distance ; contournement de la validation nominative |
| Élevée | Accès au formulaire local sans jeton ; pack pays non signé accepté ; montant d'une liasse altérable sans trace |
| Moyenne | Session qui ne s'éteint pas ; en-tête de sécurité manquant ; journal incomplet |
| Faible | Information technique exposée sans donnée de client |

## Dans le périmètre

- Le moteur (`facil_moteur/`), les outils de packs, la vérification des signatures Ed25519.
- L'extension Facil DEF : serveur MCP, formulaire local (127.0.0.1, jeton, deux horloges de session), passerelle de confidentialité (pseudonymes, montants masqués, journal des sorties), lecture OCR locale.
- La chaîne de livraison : workflows GitHub Actions, dépendances.

## Hors périmètre

- Les postes et serveurs des clients (durcissement du système, antivirus).
- Claude Desktop et Claude Code eux-mêmes : à signaler à Anthropic.
- Les attaques qui supposent un accès administrateur déjà acquis au poste.

## Mesures en place

- **Données des clients jamais versionnées** : `.gitignore`, purge des classeurs (`outils/purger_classeur.py --verifier`), garde de confidentialité par empreintes HMAC (`outils/garde_confidentialite.py`) exigée en CI, analyse de secrets (gitleaks).
- **Packs pays signés** (Ed25519) ; la clé privée n'est jamais dans le dépôt.
- **Calcul local** : l'IA ne calcule ni ne valide (ADR 0008) ; aucune sortie sans passerelle.
- **Analyse statique** CodeQL et mises à jour Dependabot.
