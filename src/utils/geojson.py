import requests
import os
import sys
import pandas as pd

try:
    # When imported as a package (recommended)
    from .reference import GEOJSON_URL
except ImportError:
    try:
        # Try absolute import (if project root is on PYTHONPATH)
        from src.utils.reference import GEOJSON_URL
    except ImportError:
        # Fallback: add project root to sys.path then import
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
    
    # Reste du code si vous avez besoin de la liste triée
    noms_departements = []
    for feature in geojson_data['features']:
        nom = feature['properties']['nom']
        noms_departements.append(nom)

    noms_departements = sorted(noms_departements)
    return noms_departements