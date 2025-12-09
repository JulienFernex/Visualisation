"""
Génère un Histogramme (Bar Chart)
"""

import pandas as pd
import plotly.express as px
from src.utils.reference import CLEAN_DATA_PATH, COL_VALUE, COL_POPULATION, COL_RATIO

def create_histogram(selected_col=COL_VALUE):
    # Chargement des données
    try:
        df = pd.read_csv(CLEAN_DATA_PATH)
    except FileNotFoundError:
        return px.bar(title="Données non trouvées")

    # Trie par nombre d'établissements croissant, pour des questions de lisibilité
    df_sorted = df.sort_values(by=selected_col, ascending=True)

    # Définition dynamique du titre et des labels
    if selected_col == COL_POPULATION:
        titre = "Classement des départements par population totale"
        label_y = "Population Totale"
    elif selected_col == COL_POPULATION:
        titre = "Classement par densité d'établissements (pour 100k hab)"
        label_y = "Densité / 100k hab"    
    else:
        titre = "Classement des départements par nombre d'établissements"
        label_y = "Nb d'établissements"

    # Création de l'histogramme
    fig = px.bar(
        df_sorted, 
        x='Libelle_Departement',
        y=selected_col,
        color=selected_col,
        labels={selected_col: label_y, 'Libelle_Departement': 'Département'},
        title=titre,
    )

    return fig