"""
Génère un Histogramme (Bar Chart)
"""

import pandas as pd
import plotly.express as px
from src.utils.reference import CLEAN_DATA_PATH, COL_VALUE

def create_histogram():

    # Chargement des données
    # Les mêmes que pour la carte (pour l'instant ?)
    try:
        df = pd.read_csv(CLEAN_DATA_PATH)
    except FileNotFoundError:
        return px.bar(title="Données non trouvées")

    # Trie par nombre d'établissements croissant, pour des questions de lisibilité
    df_sorted = df.sort_values(by=COL_VALUE, ascending=True)

    # Création de l'histogramme
    fig = px.bar(
        df_sorted, 
        x='Libelle_Departement',  # Noms des départements
        y=COL_VALUE,              # Nombre d'établissements
        color=COL_VALUE,          # Couleur différente selon le nombre d'établissements
        labels={COL_VALUE: "Nb d'établissements", 'Libelle_Departement': 'Département'},
        title="Classement des départements par nombre d'établissements de santé",
        height=400
    )

    return fig