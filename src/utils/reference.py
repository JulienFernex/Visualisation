"""
Contient les constantes du projet
"""

import os

GEOJSON_URL = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-avec-outre-mer.geojson"
JOIN_KEY_DATA = 'Nom_Departement_Harmonise'
JOIN_KEY_GEOJSON = 'properties.nom'
COL_VALUE = 'Nombre_Etablissements'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, '..')
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, 'datas', 'raw_data.csv')
CLEAN_DATA_PATH = os.path.join(PROJECT_ROOT, 'datas', 'clean_data.csv')

OUTPUT_MAP = os.path.join(PROJECT_ROOT, 'output', 'carte_etablissement_par_departement.html')