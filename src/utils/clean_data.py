"""
Convertit un fichier CSV brut en données utilisables
"""

import pandas as pd
import os
import unicodedata

# Pour supprimer le warning lors de la création du csv
import warnings
warnings.simplefilter("ignore", UserWarning)

try:
    from .reference import CLEAN_DATA_PATH, RAW_DATA_PATH, RAW_POPULATION_PATH, COL_VALUE, COL_POPULATION
except ImportError:
    try:
        from src.utils.reference import CLEAN_DATA_PATH, RAW_DATA_PATH, RAW_POPULATION_PATH, COL_VALUE, COL_POPULATION
    except ImportError:
        ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        if ROOT not in __import__('sys').path:
            __import__('sys').path.insert(0, ROOT)
        from src.utils.reference import CLEAN_DATA_PATH, RAW_DATA_PATH, RAW_POPULATION_PATH, COL_VALUE, COL_POPULATION

# Suppressions des majuscules, accents, tirets et apostrophes du texte
def normalize_txt(text):
    if not isinstance(text, str):
        return str(text)
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
    text = text.upper().replace('-', ' ').replace("'", ' ')
    return " ".join(text.split())

# Nettoie le fichier pour ne faire apapparaître que les départements avec leurs nombres d'établissements sanitaires
def clean_etab_to_depart(document_etab):
    df_counts = document_etab.groupby('Libelle_Departement').size().reset_index(name=COL_VALUE)     # Compte les établissements par département par ordre alphabétique
    df_counts['join_key'] = df_counts['Libelle_Departement'].apply(normalize_txt)                   # Création d'une colonne temporaire pour la jointure
    df_pop = pd.read_excel(RAW_POPULATION_PATH, sheet_name='Départements', skiprows=7)              # Les données dans l'onglet département du fichier avec les populations commencent à la ligne 7
    df_pop['join_key'] = df_pop['Nom du département'].apply(normalize_txt)      # Normalisation pour la jointure
    df_pop = df_pop.rename(columns={'Population totale': COL_POPULATION})
    df_pop = df_pop[['join_key', COL_POPULATION]]                               # Sélection des colonnes utiles
    df_final = pd.merge(df_counts, df_pop, on='join_key', how='left')           # Fusion des données, le how est nécessaire pour certains département, cf la Vienne
    df_final[COL_POPULATION] = df_final[COL_POPULATION].fillna(0)               # Rempli les NaN par 0, nécessaire à cause de départements d'outre mer
    df_final = df_final.drop(columns=['join_key'])                              # Nettoyage de la colonne intermédiaire 
    df_final.to_csv(CLEAN_DATA_PATH, index=False)                               # Sauvegarde
    print("Données nettoyées sauvegardées.")

# Permet de simplement lancer le clean_data sans lancer tout le programme
if __name__ == "__main__":
    df = pd.read_csv(RAW_DATA_PATH, sep=';', low_memory=False)
    clean_etab_to_depart(df)