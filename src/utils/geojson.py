"""
Récupère les données géographiques 
"""

import requests
import os
import sys
import pandas as pd

try:
    # Quand importé en tant que package
    from .reference import GEOJSON_URL
except ImportError:
    try:
        # Essaie de l'importation absolue (si la racine du projet se trouve dans PYTHONPATH)
        from src.utils.reference import GEOJSON_URL
    except ImportError:
        # Fallback: ajouter la racine du projet à sys.path puis importer
        ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        if ROOT not in sys.path:
            sys.path.insert(0, ROOT)
        from src.utils.reference import GEOJSON_URL

def get_departements_geojson(return_df=False):

    try:
        response = requests.get(GEOJSON_URL, timeout=10)
        response.raise_for_status()
        geojson_data = response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléchargement du GeoJSON : {e}")
        exit()

    if return_df:
        # Convertir lses propriétés GeoJSON en DataFrame pour la jointure
        features = geojson_data['features']
        data = [{'code': f['properties']['code'], 'nom': f['properties']['nom']} for f in features]
        return pd.DataFrame(data)
    
    # Retourne la liste triée
    noms_departements = []
    for feature in geojson_data['features']:
        nom = feature['properties']['nom']
        noms_departements.append(nom)

    noms_departements = sorted(noms_departements)
    return noms_departements