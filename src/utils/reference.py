"""
Contient les constantes du projet
"""

import os

GEOJSON_URL = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-avec-outre-mer.geojson"
JOIN_KEY_DATA = 'Nom_Departement_Harmonise'
JOIN_KEY_GEOJSON = 'properties.nom'

# Colonnes de données
COL_VALUE = 'Nombre_Etablissements'
COL_POPULATION = 'Population_Totale'
COL_RATIO = 'Ratio_100k'

# Chemin
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, '..')

# Chemins vers les données
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, 'datas', 'raw_data.csv')
RAW_POPULATION_PATH = os.path.join(PROJECT_ROOT, 'datas', 'raw_data_population.xlsx')
CLEAN_DATA_PATH = os.path.join(PROJECT_ROOT, 'datas', 'clean_data.csv')
CLEAN_DATA_COMMUNE_PATH = os.path.join(PROJECT_ROOT, 'datas', 'clean_data_commune.csv')