"""
Récupère les données géographiques 
"""

import requests
import os
import sys
import json
import pandas as pd

try:
    # Lorsque importé en tant que package
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

def get_departements_geojson(return_df=False, return_geojson=False):

    # Emplacement du cache local (src/output/departements_geojson.json)
    cache_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output'))
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, 'departements_geojson.json')

    # Charger depuis le cache si disponible
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as fh:
                geojson_data = json.load(fh)
        except Exception as e:
            print(f"Erreur lors du chargement du GeoJSON depuis le cache : {e}")
            geojson_data = None
    else:
        try:
            response = requests.get(GEOJSON_URL, timeout=10)
            response.raise_for_status()
            geojson_data = response.json()
            # Sauvegarde dans le cache pour usages futurs
            try:
                with open(cache_path, 'w', encoding='utf-8') as fh:
                    json.dump(geojson_data, fh)
            except Exception:
                # Ne pas bloquer l'exécution si l'écriture échoue
                pass
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors du téléchargement du GeoJSON : {e}")
            exit()

    if return_df:
        # Convertir les propriétés GeoJSON en DataFrame pour la jointure
        features = geojson_data['features']
        data = [{'code': f['properties'].get('code'), 'nom': f['properties'].get('nom')} for f in features]
        return pd.DataFrame(data)

    # Retourne la liste triée ou l'objet GeoJSON complet si demandé
    if return_geojson:
        return geojson_data

    noms_departements = [f['properties'].get('nom') for f in geojson_data.get('features', [])]
    noms_departements = sorted([n for n in noms_departements if n])
    return noms_departements