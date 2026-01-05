"""
Génère un Histogramme (Bar Chart)
"""

import pandas as pd
import plotly.express as px
from src.utils.reference import CLEAN_DATA_PATH, COL_VALUE, COL_POPULATION, COL_RATIO, CLEAN_DATA_COMMUNE_PATH
from src.utils.clean_data import normalize_txt

def create_histogram(selected_col=COL_VALUE, department=None):
    # Si un département est sélectionné, essayer d'afficher un histogramme des communes
    if department:
        try:
            df_comm = pd.read_csv(CLEAN_DATA_COMMUNE_PATH)
            dept_norm = normalize_txt(department)
            mask = df_comm['Libelle_Departement'].apply(lambda v: normalize_txt(v) == dept_norm if pd.notna(v) else False)
            df_dept = df_comm[mask]
            if not df_dept.empty and selected_col == COL_VALUE:
                df_sorted = df_dept.sort_values(by=COL_VALUE, ascending=True)
                titre = f"Classement des communes par nombre d'établissements — {department}"
                label_y = "Nb d'établissements"
                fig = px.bar(
                    df_sorted,
                    x='Libelle_Commune',
                    y=COL_VALUE,
                    color=COL_VALUE,
                    labels={COL_VALUE: label_y, 'Libelle_Commune': 'Commune'},
                    title=titre,
                )
                return fig
        except FileNotFoundError:
            pass

    # Par défaut, niveau département
    try:
        df = pd.read_csv(CLEAN_DATA_PATH)
    except FileNotFoundError:
        return px.bar(title="Données non trouvées")

    df_sorted = df.sort_values(by=selected_col, ascending=True)

    # Définition dynamique du titre et des labels
    if selected_col == COL_POPULATION:
        titre = "Classement des départements par population totale"
        label_y = "Population Totale"
    elif selected_col == COL_RATIO:
        titre = "Classement par densité d'établissements (pour 100k hab)"
        label_y = "Densité / 100k hab"
    else:
        titre = "Classement des départements par nombre d'établissements"
        label_y = "Nb d'établissements"

    fig = px.bar(
        df_sorted,
        x='Libelle_Departement',
        y=selected_col,
        color=selected_col,
        labels={selected_col: label_y, 'Libelle_Departement': 'Département'},
        title=titre,
    )

    return fig