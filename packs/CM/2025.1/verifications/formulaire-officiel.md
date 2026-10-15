# Formulaire SN : comparaison avec le formulaire officiel de la DGI

Comparé le 16/10/2026 par `outils/comparer_formulaires.py`, `outils/positions_postes.py` et `outils/lignes_notes.py`.

| Contrôle | Résultat |
|---|---|
| Feuilles | 74 dans les deux fichiers ; aucune ajoutée, aucune retirée |
| Position des codes de postes (bilan, compte de résultat, TFT, fiches R1 et R2, note 27B) | **148 postes, 0 écart de position** |
| Libellés des lignes de notes écrites par le moteur (correspondances SN de la couche OHADA) | **241 lignes, 0 libellé différent** (seuil de similarité 0,80) |
| Feuilles identiques en textes et en formules | 13 sur 74 |
| Différences restantes | coquilles de libellés (« Societé », « Revenue », « régions »…) et **absence de formules** dans la version « verrouillée » (note 34 : 50 formules → 5) |

**Conclusion** : le formulaire de la couche OHADA (même origine DGI, avec ses formules) est conforme au formulaire officiel publié, pour tout ce que le moteur écrit et que l'administration lit (positions). Le pack le garde, car l'exigence EX-PROD-6 veut des totaux en formules vivantes.

**À refaire** à chaque nouvelle publication du formulaire par la DGI : relancer les trois outils sur le nouveau fichier ; tout écart de position bloque la publication du pack.
