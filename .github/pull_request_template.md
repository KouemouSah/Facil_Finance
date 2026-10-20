## Résumé

<!-- Ce qui change et pourquoi. Lien vers le ticket : « Ferme #… ». -->

## Type

- [ ] Fonctionnalité  - [ ] Correction  - [ ] Documentation  - [ ] CI / outillage  - [ ] Refonte  - [ ] Pack pays

## Preuve en exécution

<!-- Sortie RÉELLE des commandes (extraits). « Ça devrait marcher » n'est pas une preuve. -->

```text
python outils/verifier_tout.py
```

## Clôture

- [ ] Gardes ajoutées falsifiées (une mutation par garde, et elle rougit)
- [ ] SQL relu : filtre indexé, pas de N+1, lecture bornée, verrou (ou « sans SQL »)
- [ ] Portée mesurée : qui d'autre lit cette table, appelle cette route, dépend de ce nom
- [ ] Documentation que ce changement rend fausse : corrigée dans cette demande
- [ ] **Aucune donnée de client** (la garde de confidentialité est verte)
- [ ] Ce qui n'est pas fait est inscrit en ticket daté, pas en commentaire

## Ce qui n'a PAS été vérifié

<!-- Une suite non rejouée, une limite de poste, une plateforme non essayée : le dire. -->
