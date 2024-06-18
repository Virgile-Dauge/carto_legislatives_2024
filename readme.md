# Cartographie des Législatives 2024

Ce projet permet de traiter et de visualiser les résultats électoraux par département pour les élections législatives de 2024. Il comprend des scripts pour séparer les données par département, calculer des caractéristiques spécifiques et générer des cartes interactives.

## Fonctionnalités

### 1. Séparation des Données par Département

Les fichiers de résultats et de géométries sont initialement fournis sous forme de gros fichiers. Pour optimiser le temps de chargement, ces fichiers sont séparés par département à l'aide du notebook `split.ipynb`.

### 2. Calcul des Caractéristiques et Génération des Cartes

Le script `skeleton.py` permet de calculer des caractéristiques spécifiques pour chaque bureau de vote et de générer des cartes interactives pour une liste de départements ou pour tous les départements présents dans le dossier `départements` si aucun département n'est spécifié.

- **skeleton.py** : Script principal pour traiter les données et générer les cartes.

## Utilisation

### Séparation des Données par Département

Pour séparer les données par département, utilise le notebook `split.ipynb` 

### Calcul des Caractéristiques et Génération des Cartes

Pour calculer les caractéristiques et générer les cartes, utilise le script `skeleton.py`.

#### Arguments

- `-d`, `--departments`: Liste des numéros de départements à traiter. Si aucun département n'est spécifié, tous les départements présents dans le dossier `./départements` seront traités.

#### Exemple de commande

```bash
python skeleton.py -d 13 14 18
```
## Où contribuer 

### Réconciliation des bureaux
Les identifiants des bureaux dans le fichier `bureaux_votes_gpkg` ne correspondent pas totalement à celui dans les données des européénnes (colonne `bv_id` dans le fichier `source_data/européennes_2024/resultats_fr_par_bureau.xlsx`). 

But du jeu = construire une colone `bv_id` dans `bureaux_votes_gpkg` avec des identifiant corrigés

### Générer des nouveaux départements

### Documenter et Affiner les features 
Cf fichier `features.py`
### Utiliser les projections pour le calcul du Coude à coude
En attente, des projections plus fiables seront dispo vers le 20/06
