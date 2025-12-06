"""
Convertit un fichier CSV brut en données utilisables
"""

import pandas as pd
import os

try:
    from .reference import CLEAN_DATA_PATH, RAW_DATA_PATH
except ImportError:
    try:
        from src.utils.reference import CLEAN_DATA_PATH, RAW_DATA_PATH
    except ImportError:
        ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        if ROOT not in __import__('sys').path:
            __import__('sys').path.insert(0, ROOT)
        from src.utils.reference import CLEAN_DATA_PATH, RAW_DATA_PATH

# Nettoie le fichier pour ne faire aparaître que les départements avec leurs nombres d'établissements sanitaires
def clean_etab_to_depart(document):
    df_counts = document.groupby('Libelle_Departement').size().reset_index(name='Nombre_Etablissements')
    df_counts.to_csv(CLEAN_DATA_PATH, index=False)

# Charger le fichier
df = pd.read_csv(
    RAW_DATA_PATH,
    sep=';',
    low_memory=False
)