"""
Contient les constantes du projet
"""
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Structure des dossiers
DATA_DIR = os.path.join(ROOT_DIR, 'data')
RAW_DIR = os.path.join(DATA_DIR, 'raw')
CLEANED_DIR = os.path.join(DATA_DIR, 'cleaned')

# Chemins des fichiers
RAW_DATA_PATH = os.path.join(RAW_DIR, 'raw_data.csv')
RAW_POPULATION_PATH = os.path.join(RAW_DIR, 'raw_data_population.xlsx')
GEOJSON_PATH = os.path.join(RAW_DIR, 'departements-avec-outre-mer.geojson')

CLEAN_DATA_PATH = os.path.join(CLEANED_DIR, 'clean_data.csv')
CLEAN_DATA_COMMUNE_PATH = os.path.join(CLEANED_DIR, 'clean_data_commune.csv')

# URLs
GEOJSON_URL = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-avec-outre-mer.geojson"
DATA_URL = "https://www.data.gouv.fr/api/1/datasets/r/98f3161f-79ff-4f16-8f6a-6d571a80fea2" 
POPULATION_URL = "https://www.insee.fr/fr/statistiques/fichier/8290591/ensemble.xlsx"

# Constantes
COL_VALUE = 'Nombre_Etablissements'
COL_POPULATION = 'Population_Totale'
COL_RATIO = 'Ratio_100k'
JOIN_KEY_DATA = 'Nom_Departement_Harmonise'
JOIN_KEY_GEOJSON = 'properties.nom'