"""
Génère un graphique de type Bubble Chart (Scatter Plot)
"""

import pandas as pd
import plotly.express as px
from src.utils.reference import CLEAN_DATA_PATH, COL_VALUE

def create_bubble_chart():

    # Chargement des données
    # Les mêmes que pour la carte (pour l'instant ?)
    try:
        df = pd.read_csv(CLEAN_DATA_PATH)
    except FileNotFoundError:
        return px.scatter(title="Données non trouvées")

    # Création du graphique à bulles
    fig = px.scatter(
        df, 
        x='Libelle_Departement',  # Noms des départements
        y=COL_VALUE,              # Nombre d'établissements
        size=COL_VALUE,           # Taille de la bulle proportionnelle au nombre d'établissements
        color='Libelle_Departement',  # Couleur différente par département
        hover_name='Libelle_Departement',
        labels={COL_VALUE: "Nb d'établissements", 'Libelle_Departement': 'Département'},
        size_max=60,
        title="Distribution du nombre d'établissements de santé par département"
    )

    # Masquer la légende des couleurs car il y a trop de départements
    # A voir pour changer la représentation des données
    fig.update_layout(showlegend=False)

    return fig