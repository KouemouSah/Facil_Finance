"""Noyau du moteur : modules sans aucune règle propre à un pays.

  detection_balance   lecture de toute balance (1 à 8 colonnes, avec ou sans en-tête), par invariants comptables
  grand_livre         lecture du grand livre, balance reconstituée et rapprochée
  formules_xl         évaluation des formules Excel des gabarits (rendu sans Excel)
  rendu_pdf           PDF natifs des classeurs

SOURCE UNIQUE. Le plugin compta-ohada en reçoit des copies par outils/publier_vers_plugin.py ;
la garde de parité (publier_vers_plugin.py --check, tests/test_noyau.py) rougit si une copie diverge.
Ne jamais corriger une copie du plugin : corriger ici, puis publier.
"""
