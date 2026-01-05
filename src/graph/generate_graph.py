"""
Génère un graphique de type Bubble Chart (Scatter Plot)
"""

import pandas as pd
import plotly.express as px
from src.utils.reference import CLEAN_DATA_PATH, COL_VALUE, COL_POPULATION, COL_RATIO, CLEAN_DATA_COMMUNE_PATH
from src.utils.clean_data import normalize_txt

def create_bubble_chart(selected_col=COL_VALUE, department=None):
    # Si un département est sélectionné, tenter d'afficher les données par commune
    if department:
        try:
            df_comm = pd.read_csv(CLEAN_DATA_COMMUNE_PATH)
            dept_norm = normalize_txt(department)
            mask = df_comm['Libelle_Departement'].apply(lambda v: normalize_txt(v) == dept_norm if pd.notna(v) else False)
            df_dept = df_comm[mask]
            if not df_dept.empty and selected_col == COL_VALUE:
                titre = f"Distribution du nombre d'établissements par commune — {department}"
                label_y = "Nb d'établissements"
                fig = px.scatter(
                    df_dept,
                    x='Libelle_Commune',
                    y=COL_VALUE,
                    size=COL_VALUE,
                    color='Libelle_Commune',
                    hover_name='Libelle_Commune',
                    labels={COL_VALUE: label_y, 'Libelle_Commune': 'Commune'},
                    size_max=40,
                    title=titre
                )
                fig.update_layout(showlegend=False)
                return fig
        except FileNotFoundError:
            # Pas de fichier communes : on retombera sur le niveau département
            pass

    # Par défaut (pas de département ou pas de données communales), rester au niveau département
    try:
        df = pd.read_csv(CLEAN_DATA_PATH)
    except FileNotFoundError:
        return px.scatter(title="Données non trouvées")

    # Définition dynamique du titre et des labels
    if selected_col == COL_POPULATION:
        titre = "Distribution de la population totale par département"
        label_y = "Population"
    elif selected_col == COL_RATIO:
        titre = "Densité d'établissements de santé (pour 100k hab) par département"
        label_y = "Densité / 100k hab"
    else:
        titre = "Distribution du nombre d'établissements de santé par département"
        label_y = "Nb d'établissements"

    fig = px.scatter(
        df,
        x='Libelle_Departement',
        y=selected_col,
        size=selected_col if selected_col in df.columns else None,
        color='Libelle_Departement',
        hover_name='Libelle_Departement',
        labels={selected_col: label_y, 'Libelle_Departement': 'Département'},
        size_max=60,
        title=titre
    )
    fig.update_layout(showlegend=False)
    return fig