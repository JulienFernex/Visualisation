# Visualisation

Ce dépôt contient un tableau de bord interactif de visualisation de données.

## User Guide

- **Prérequis**: Python 3.10+ (ou 3.8+ selon votre environnement), `pip`.
- **Installer les dépendances**:

	```bash
	python -m venv .venv
	.venv\Scripts\activate    # Windows
	pip install --upgrade pip
	pip install -r requirements.txt
	```

- **Lancer le dashboard** :

	```bash
	python main.py
	```

- **Accéder** : ouvrir http://127.0.0.1:8050 dans un navigateur.

- **Déployer sur une autre machine** :
	- Copier le dépôt via un zip ou cloner le repo.
	- Reproduire les étapes d'installation ci-dessus.

## Data

Les fichiers de données se trouvent dans le dossier `src/datas/` :

- `raw_data.csv` : dump initial des données brutes.
- `clean_data.csv` et `clean_data_commune.csv` : versions nettoyées et prêtes à l'utilisation.

Description générale : les jeux de données contiennent les informations d'établissements (localisation, département, type d'établissement, et autres informations utiles à l'histogramme aux graphiques et à notre carte). Pour toute informations, ouvrir `src/utils/clean_data.py` qui contient la logique de nettoyage du fichier.

Remarque : les fichiers GeoJSON utilisés pour la cartographie de notre map sont dans `src/output/departements_geojson.json`.

## Developer Guide

Architecture principale :

- `src/main.py` : point d'entrée qui lance le serveur Dash.
- `src/dashboard/app.py` : définition de l'application Dash (layout, pages, callbacks).
- `src/graph/generate_graph.py` : fonctions pour générer graphiques/figures.
- `src/hist/generate_hist.py` : génération d'histogrammes spécifiques.
- `src/map/generate_map.py` : génération de la carte interactive.
- `src/utils/` : utilitaires (nettoyage, gestion GeoJSON, références).

Ajouter une page au dashboard :

1. Ouvrir `src/dashboard/app.py` et repérer la structure des pages et du `layout`.
2. Créer une nouvelle fonction de layout qui retourne le composant Dash souhaité.
3. Ajouter une route/page dans la navigation.
4. Si la page nécessite des callbacks, définir les callbacks dans `src/dashboard/app.py` ou dans un module dédié et les enregistrer avec `@app.callback`.

Ajouter un graphique :

1. Implémenter une fonction qui crée la figure (plotly) dans `src/graph/generate_graph.py`. La fonction doit accepter les paramètres nécessaires (données, filtres) et retourner un objet.
2. Importer cette fonction dans `src/dashboard/app.py` et insérer la figure dans le layout via `dcc.Graph(figure=...)`.
3. Connecter les `Input`/`Output` nécessaires via des callbacks pour rendre le graphique interactif.

Conseils : garder la logique de préparation des données dans `src/utils/` pour séparer présentation et traitement.

## Rapport d'analyse

Principales conclusions (résumé qualitatif) :

- Les établissements se concentrent principalement dans les zones urbaines et certains départements présentent une densité notablement plus élevée.
- Les visualisations cartographiques met en évidence des disparités territoriales qui peuvent guider des analyses plus fines (par commune, par tranche d'effectifs, etc.).

- C'est un premier pas. On pourrait maintenant croiser ces données avec d'autres variables ou analyser leur évolution dans le temps.

## Copyright / Déclaration d'originalité

Je déclare sur l'honneur que le code fourni a été produit par moi / nous-même, à l'exception des lignes ci-dessous :

- Ligne(s) / groupe(s) de lignes empruntée(s) :
	- Référence de la source : (indiquer URL ou auteur)
	- Explication : (quelle portion de code a été reprise et pourquoi, et comment elle est utilisée)

Toute ligne non déclarée ci-dessus est réputée être produite par l'auteur (ou les auteurs) du projet. L'absence ou l'omission de déclaration sera considérée comme du plagiat.

