"""
Génère un graphique de type Bubble Chart (Scatter Plot)
"""

import pandas as pd
import plotly.express as px
from src.utils.reference import CLEAN_DATA_PATH, COL_VALUE, COL_POPULATION, COL_RATIO

def create_bubble_chart(selected_col=COL_VALUE):
    # Chargement des données
    try:
        df = pd.read_csv(CLEAN_DATA_PATH)
    except FileNotFoundError:
        return px.scatter(title="Données non trouvées")

    # Définition dynamique du titre et des labels
    if selected_col == COL_POPULATION:
        titre = "Distribution de la population totale par département"
        label_y = "Population COL_RATIO"
    elif selected_col == COL_POPULATION:
        titre = "Densité d'établissements de santé (pour 100k hab) par département"
        label_y = "Densité / 100k hab"    
    else:
        titre = "Distribution du nombre d'établissements de santé par département"
        label_y = "Nb d'établissements"

    # Création du graphique à bulles
    fig = px.scatter(
        df, 
        x='Libelle_Departement',      # Noms des départements
        y=selected_col,               # Nombre d'établissements / Taille population
        size=selected_col,            # Taille de la bulle proportionnelle à la donnée
        color='Libelle_Departement',  # Couleur différente par département
        hover_name='Libelle_Departement',
        labels={selected_col: label_y, 'Libelle_Departement': 'Département'},
        size_max=60,
        title=titre
    )

    # Masquer la légende des couleurs car il y a trop de départements
    # A voir pour changer la représentation des données
    fig.update_layout(showlegend=False)

    return fig