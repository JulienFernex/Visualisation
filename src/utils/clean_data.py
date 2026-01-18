"""
Convertit un fichier CSV brut en données utilisables
"""

import pandas as pd
import os
import unicodedata
import re

# Pour supprimer le warning lors de la création du csv
import warnings
warnings.simplefilter("ignore", UserWarning)

try:
    from .reference import CLEAN_DATA_PATH, RAW_DATA_PATH, RAW_POPULATION_PATH, COL_VALUE, COL_POPULATION, COL_RATIO, CLEAN_DATA_COMMUNE_PATH
except ImportError:
    try:
        from src.utils.reference import CLEAN_DATA_PATH, RAW_DATA_PATH, RAW_POPULATION_PATH, COL_VALUE, COL_POPULATION, COL_RATIO, CLEAN_DATA_COMMUNE_PATH
    except ImportError:
        ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        if ROOT not in __import__('sys').path:
            __import__('sys').path.insert(0, ROOT)
        from src.utils.reference import CLEAN_DATA_PATH, RAW_DATA_PATH, RAW_POPULATION_PATH, COL_VALUE, COL_POPULATION, COL_RATIO, CLEAN_DATA_COMMUNE_PATH

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
    
    # Calcul du ratio
    df_final[COL_RATIO] = (df_final[COL_VALUE] / df_final[COL_POPULATION]) * 100000     # Ratio pour 100k habitants
    df_final.loc[df_final[COL_POPULATION] <= 0, COL_RATIO] = 0                          # Correction des NaN par des 0
    df_final[COL_RATIO] = df_final[COL_RATIO].round(2)                                  # Arrondi de la valeur
    
    df_final = df_final.drop(columns=['join_key'])                              # Nettoyage de la colonne intermédiaire 
    df_final.to_csv(CLEAN_DATA_PATH, index=False)                               # Sauvegarde
    print("Données nettoyées sauvegardées.")


def clean_libelle_commune(text):
    if not isinstance(text, str):
        return ""
    
    # Enlève code postal au début
    parts = text.split(' ', 1)
    if len(parts) > 1 and parts[0].isdigit():
        text = parts[1]
    
    text = text.upper()
    
    # Standardisation ST / STE
    text = re.sub(r'\bST\b', 'SAINT', text)
    text = re.sub(r'\bST\s', 'SAINT ', text)
    text = re.sub(r'\bSTE\b', 'SAINTE', text)
    text = re.sub(r'\bSTE\s', 'SAINTE ', text)
    
    text = re.sub(r'\s+CED.*$', '', text)  # Enlève le CEDEX et tout ce qui suit
        
    return text.strip()

def clean_etab_to_commune(document_etab):
    df = document_etab.copy()
    #  On nettoie d'abord pour identifier les mêmes communes
    df['cleaned_name'] = df['Libelle_Commune'].apply(clean_libelle_commune)   
    
    # On trie pour garder le label le plus court en premier
    df['name_len'] = df['Libelle_Commune'].astype(str).str.len()
    df = df.sort_values(by=['Libelle_Departement', 'cleaned_name', 'name_len'])
    df = df.drop(columns=['name_len'])

    # On regroupe par nom nettoyé, en sommant les établissements
    df_counts = df.groupby(['Libelle_Departement', 'cleaned_name']).agg(
        Libelle_Commune=('Libelle_Commune', 'first'),
        Nombre_Etablissements=('Libelle_Commune', 'count') # Somme tout
    ).reset_index()

    # Chargement références Population
    df_ref_dept = pd.read_excel(RAW_POPULATION_PATH, sheet_name='Départements', skiprows=7)
    code_to_name = dict(zip(df_ref_dept['Code département'].astype(str), df_ref_dept['Nom du département']))

    df_pop = pd.read_excel(RAW_POPULATION_PATH, sheet_name='Communes', skiprows=7)
    df_pop['Dept_Name'] = df_pop['Code département'].astype(str).map(code_to_name)
    
    # Normalisation
    df_pop['nom_dept_norm'] = df_pop['Dept_Name'].apply(normalize_txt)
    df_pop['nom_commune_norm'] = df_pop['Nom de la commune'].apply(normalize_txt)
    
    # Dictionnaires de recherche
    # Exact : Dept, Commune -> Pop
    pop_lookup = dict(zip(zip(df_pop['nom_dept_norm'], df_pop['nom_commune_norm']), df_pop['Population totale']))
    
    # Par Département pour recherche floue : Dept -> {Commune: Pop}
    dept_lookup = {}
    for _, row in df_pop.iterrows():
        d, c, p = row['nom_dept_norm'], row['nom_commune_norm'], row['Population totale']
        if pd.isna(d) or pd.isna(c): continue
        if d not in dept_lookup: dept_lookup[d] = {}
        dept_lookup[d][c] = p

    # Préparation données Etablissements
    df_counts['clean_comm'] = df_counts['Libelle_Commune'].apply(clean_libelle_commune)
    df_counts['d_norm'] = df_counts['Libelle_Departement'].apply(normalize_txt)
    df_counts['c_norm'] = df_counts['clean_comm'].apply(normalize_txt)
    
    def get_population(row):
        d, c = row['d_norm'], row['c_norm']
        
        # Nom exact
        if (d, c) in pop_lookup:
            return pop_lookup[(d, c)]
        
        # Nom par inclusion
        if d in dept_lookup:
            candidates = dept_lookup[d]
            for real_name, pop in candidates.items():
                if c in real_name or real_name in c:
                    return pop
        return 0

    df_counts[COL_POPULATION] = df_counts.apply(get_population, axis=1)

    # Calcul Ratio
    df_counts[COL_RATIO] = (df_counts[COL_VALUE] / df_counts[COL_POPULATION]) * 100000
    df_counts.loc[df_counts[COL_POPULATION] <= 0, COL_RATIO] = 0
    df_counts[COL_RATIO] = df_counts[COL_RATIO].round(2)

    df_counts = df_counts.drop(columns=['cleaned_name', 'clean_comm', 'd_norm', 'c_norm'])
    df_counts.to_csv(CLEAN_DATA_COMMUNE_PATH, index=False)
    print("Données nettoyées (communes) sauvegardées.")

# Permet de simplement lancer le clean_data sans lancer tout le programme
if __name__ == "__main__":
    df = pd.read_csv(RAW_DATA_PATH, sep=';', low_memory=False)
    clean_etab_to_depart(df)
    clean_etab_to_commune(df)