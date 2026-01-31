"""
Charge les données géographiques depuis data/raw/
"""
import os
import sys
import json
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import GEOJSON_PATH

def get_departements_geojson(return_df=False, return_geojson=False):
    if os.path.exists(GEOJSON_PATH):
        try:
            with open(GEOJSON_PATH, 'r', encoding='utf-8') as fh:
                geojson_data = json.load(fh)
        except Exception as e:
            print(f"Erreur lors de la lecture du GeoJSON : {e}")
            return [] if not return_geojson else None
    else:
        print(f"Attention: GeoJSON introuvable dans {GEOJSON_PATH}. Veuillez lancer python src/utils/get_data.py")
        return [] if not return_geojson else None

    if return_df:
        features = geojson_data['features']
        data = [{'code': f['properties'].get('code'), 'nom': f['properties'].get('nom')} for f in features]
        return pd.DataFrame(data)

    if return_geojson:
        return geojson_data

    noms_departements = [f['properties'].get('nom') for f in geojson_data.get('features', [])]
    noms_departements = sorted([n for n in noms_departements if n])
    return noms_departements