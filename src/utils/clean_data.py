"""
Nettoie les données brutes et les exporte dans data/cleaned/
"""
import pandas as pd
import os
import sys
import unicodedata
import re
import warnings

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import (
    CLEANED_DIR,
    CLEAN_DATA_PATH, 
    RAW_DATA_PATH, 
    RAW_POPULATION_PATH, 
    COL_VALUE, 
    COL_POPULATION, 
    COL_RATIO, 
    CLEAN_DATA_COMMUNE_PATH
)

warnings.simplefilter("ignore", UserWarning)
warnings.simplefilter("ignore", pd.errors.DtypeWarning)

# Liste des 32 colonnes du CSV
NEW_COLUMN_NAMES = [
    "Type_Ligne", "FINESS_ET", "FINESS_EJ", "Raison_Sociale", "Raison_Sociale_Longue",
    "Complement_Raison_Sociale", "Complement_Distribution", "Numero_Voie", "Type_Voie",
    "Libelle_Voie", "Complement_Voie", "Lieu_Dit_BP", "Code_Postal", "Code_Commune",
    "Libelle_Departement", "Libelle_Commune", "Telephone", "Telecopie",
    "Categorie_Etablissement", "Libelle_Categorie_Etablissement", "Categorie_Agrement_Etablissement",
    "Libelle_Categorie_Agrement_Etablissement", "SIRET", "Code_APE", "Nature_Etablissement",
    "Libelle_Nature_Etablissement", "Statut_Juridique", "Libelle_Statut_Juridique",
    "Date_Ouverture", "Date_Autorisation", "Date_Maj_Structure", "Numero_UAI"
]

def normalize_txt(text):
    if not isinstance(text, str):
        return str(text)
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
    text = text.upper().replace('-', ' ').replace("'", ' ')
    return " ".join(text.split())

def load_and_rename_raw_data():
    """
    Charge le CSV en forçant les 32 colonnes et en filtrant les lignes inutiles.
    """
    print(f"Chargement de {RAW_DATA_PATH}...")
    
    # On force les noms de colonnes (names=...) pour que Pandas n'utilise pas la première ligne (qui n'en a que 4)
    try:
        df = pd.read_csv(
            RAW_DATA_PATH, 
            sep=';', 
            encoding='iso-8859-1', 
            header=None,           # Indique que la première ligne n'est pas l'entête
            names=NEW_COLUMN_NAMES, 
            low_memory=False,
            on_bad_lines='skip' # Ignore les lignes mal formées
        )
    except UnicodeDecodeError:
        df = pd.read_csv(
            RAW_DATA_PATH, 
            sep=';', 
            encoding='utf-8', 
            header=None, 
            names=NEW_COLUMN_NAMES, 
            low_memory=False,
            on_bad_lines='skip'
        )

    # Filtrage : On ne garde que les lignes qui commencent par 'structureet'
    # Cela élimine la première ligne (finess;etalab...) et les lignes de géolocalisation
    if 'Type_Ligne' in df.columns:
        df = df[df['Type_Ligne'] == 'structureet'].copy()
        print(f"Données filtrées : {len(df)} établissements trouvés.")
    
    return df

def clean_etab_to_depart(document_etab):
    print("Nettoyage des données départementales...")
    
    df_counts = document_etab.groupby('Libelle_Departement').size().reset_index(name=COL_VALUE)
    df_counts['join_key'] = df_counts['Libelle_Departement'].apply(normalize_txt)
    
    # Chargement Population
    try:
        df_pop = pd.read_excel(RAW_POPULATION_PATH, sheet_name='Départements', skiprows=7)
    except ValueError:
        try:
             df_pop = pd.read_excel(RAW_POPULATION_PATH, sheet_name='DEP', skiprows=7)
        except:
             print("Erreur: Impossible de trouver l'onglet 'Départements' ou 'DEP' dans le fichier population.")
             return

    df_pop['join_key'] = df_pop['Nom du département'].apply(normalize_txt)
    df_pop = df_pop.rename(columns={'Population totale': COL_POPULATION})
    df_pop = df_pop[['join_key', COL_POPULATION]]
    
    # Fusion
    df_final = pd.merge(df_counts, df_pop, on='join_key', how='left')
    df_final[COL_POPULATION] = df_final[COL_POPULATION].fillna(0)
    
    # Ratios
    df_final[COL_RATIO] = (df_final[COL_VALUE] / df_final[COL_POPULATION]) * 100000
    df_final.loc[df_final[COL_POPULATION] <= 0, COL_RATIO] = 0
    df_final[COL_RATIO] = df_final[COL_RATIO].round(2)
    
    df_final = df_final.drop(columns=['join_key'])
    
    # Sauvegarde
    os.makedirs(CLEANED_DIR, exist_ok=True)
    df_final.to_csv(CLEAN_DATA_PATH, index=False)
    print(f"Sauvegardé : {CLEAN_DATA_PATH}")

def clean_libelle_commune(text):
    if not isinstance(text, str):
        return ""
    parts = text.split(' ', 1)
    if len(parts) > 1 and parts[0].isdigit():
        text = parts[1]
    text = text.upper()
    text = re.sub(r'\bST\b', 'SAINT', text)
    text = re.sub(r'\bST\s', 'SAINT ', text)
    text = re.sub(r'\bSTE\b', 'SAINTE', text)
    text = re.sub(r'\bSTE\s', 'SAINTE ', text)
    text = re.sub(r'\s+CED.*$', '', text)
    return text.strip()

def clean_etab_to_commune(document_etab):
    print("Nettoyage des données communales...")
    df = document_etab.copy()
    
    df = df.dropna(subset=['Libelle_Commune'])
    
    df['cleaned_name'] = df['Libelle_Commune'].apply(clean_libelle_commune)   
    
    df['name_len'] = df['Libelle_Commune'].astype(str).str.len()
    df = df.sort_values(by=['Libelle_Departement', 'cleaned_name', 'name_len'])
    df = df.drop(columns=['name_len'])

    df_counts = df.groupby(['Libelle_Departement', 'cleaned_name']).agg(
        Libelle_Commune=('Libelle_Commune', 'first'),
        Nombre_Etablissements=('Libelle_Commune', 'count')
    ).reset_index()

    try:
        df_ref_dept = pd.read_excel(RAW_POPULATION_PATH, sheet_name='Départements', skiprows=7)
        df_pop = pd.read_excel(RAW_POPULATION_PATH, sheet_name='Communes', skiprows=7)
    except ValueError:
        df_ref_dept = pd.read_excel(RAW_POPULATION_PATH, sheet_name='DEP', skiprows=7)
        df_pop = pd.read_excel(RAW_POPULATION_PATH, sheet_name='COM', skiprows=7)

    code_to_name = dict(zip(df_ref_dept['Code département'].astype(str), df_ref_dept['Nom du département']))

    df_pop['Dept_Name'] = df_pop['Code département'].astype(str).map(code_to_name)
    
    df_pop['nom_dept_norm'] = df_pop['Dept_Name'].apply(normalize_txt)
    df_pop['nom_commune_norm'] = df_pop['Nom de la commune'].apply(normalize_txt)
    
    pop_lookup = dict(zip(zip(df_pop['nom_dept_norm'], df_pop['nom_commune_norm']), df_pop['Population totale']))
    
    dept_lookup = {}
    for _, row in df_pop.iterrows():
        d, c, p = row['nom_dept_norm'], row['nom_commune_norm'], row['Population totale']
        if pd.isna(d) or pd.isna(c): continue
        if d not in dept_lookup: dept_lookup[d] = {}
        dept_lookup[d][c] = p

    df_counts['clean_comm'] = df_counts['Libelle_Commune'].apply(clean_libelle_commune)
    df_counts['d_norm'] = df_counts['Libelle_Departement'].apply(normalize_txt)
    df_counts['c_norm'] = df_counts['clean_comm'].apply(normalize_txt)
    
    def get_population(row):
        d, c = row['d_norm'], row['c_norm']
        if (d, c) in pop_lookup:
            return pop_lookup[(d, c)]
        if d in dept_lookup:
            candidates = dept_lookup[d]
            for real_name, pop in candidates.items():
                if c in real_name or real_name in c:
                    return pop
        return 0

    df_counts[COL_POPULATION] = df_counts.apply(get_population, axis=1)

    df_counts[COL_RATIO] = (df_counts[COL_VALUE] / df_counts[COL_POPULATION]) * 100000
    df_counts.loc[df_counts[COL_POPULATION] <= 0, COL_RATIO] = 0
    df_counts[COL_RATIO] = df_counts[COL_RATIO].round(2)

    df_counts = df_counts.drop(columns=['cleaned_name', 'clean_comm', 'd_norm', 'c_norm'])
    
    os.makedirs(CLEANED_DIR, exist_ok=True)
    df_counts.to_csv(CLEAN_DATA_COMMUNE_PATH, index=False)
    print(f"Sauvegardé : {CLEAN_DATA_COMMUNE_PATH}")

if __name__ == "__main__":
    if os.path.exists(RAW_DATA_PATH):
        df = load_and_rename_raw_data()
        
        clean_etab_to_depart(df)
        clean_etab_to_commune(df)
    else:
        print(f"Erreur : Le fichier source {RAW_DATA_PATH} est introuvable. Lancez get_data.py d'abord.")