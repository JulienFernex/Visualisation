"""
Génère l'Histogramme principal de classement (Bar Chart)Z
"""

import pandas as pd
import plotly.express as px
from config import CLEAN_DATA_PATH, CLEAN_DATA_COMMUNE_PATH, COL_VALUE, COL_POPULATION, COL_RATIO
from src.utils.clean_data import normalize_txt

def create_bar_chart(selected_col=COL_VALUE, department=None):
    """
    Génère un histogramme classant les entités (Communes ou Départements).

    Args:
        selected_col: Métrique analysée.
        department: Filtre départemental (optionnel).
    Returns:
        Figure Plotly.
    """

    # Choix de l'échelle de couleur
    if selected_col == COL_POPULATION:
        color_scale = 'YlGnBu' 
    elif selected_col == COL_RATIO:
        color_scale = 'PuBuGn'
    else:
        color_scale = 'YlOrRd' 

    # Vue Départementale (Communes)
    if department:
        try:
            df_comm = pd.read_csv(CLEAN_DATA_COMMUNE_PATH)
            dept_norm = normalize_txt(department)
            # Filtre insensible à la casse/accents
            mask = df_comm['Libelle_Departement'].apply(lambda v: normalize_txt(v) == dept_norm if pd.notna(v) else False)
            df_dept = df_comm[mask]

            if not df_dept.empty:
                df_sorted = df_dept.sort_values(by=selected_col, ascending=True)
                
                # Définition du titre et des labels
                if selected_col == COL_POPULATION:
                    titre = f"Classement des communes par population — {department}"
                    label_y = "Population Totale"
                elif selected_col == COL_RATIO:
                    titre = f"Classement par densité (pour 100k hab) — {department}"
                    label_y = "Densité (pour 100k hab)"
                else:
                    titre = f"Classement des communes par nombre d'établissements — {department}"
                    label_y = "Nombre d'établissements"

                fig = px.bar(
                    df_sorted,
                    x='Libelle_Commune',
                    y=selected_col,
                    color=selected_col,
                    color_continuous_scale=color_scale,
                    hover_name='Libelle_Commune',
                    labels={selected_col: label_y, 'Libelle_Commune': 'Commune'},
                    hover_data={'Libelle_Commune': False, selected_col: True},
                    title=titre,
                )
                
                # Nettoyage visuel
                fig.update_layout(
                    font_family="Montserrat, sans-serif",
                    template='plotly_white',
                    title_font_size=18,
                    showlegend=False,
                    margin=dict(l=40, r=40, t=60, b=40),
                    hoverlabel=dict(bgcolor="white", font_size=14)
                )
                fig.update_xaxes(title_text="Commune", showgrid=False)
                fig.update_yaxes(title_text=label_y, showgrid=True, gridcolor='#eee')
                
                return fig
        except FileNotFoundError:
            pass

    # Vue Nationale par défaut (Départements)
    try:
        df = pd.read_csv(CLEAN_DATA_PATH)
    except FileNotFoundError:
        return px.bar(title="Données non trouvées")

    df_sorted = df.sort_values(by=selected_col, ascending=True)

    # Définition du titre et des labels
    if selected_col == COL_POPULATION:
        titre = "Classement des départements par population totale"
        label_y = "Population Totale"
    elif selected_col == COL_RATIO:
        titre = "Classement par densité d'établissements (pour 100k hab)"
        label_y = "Densité / 100k hab"
    else:
        titre = "Classement des départements par nombre d'établissements"
        label_y = "Nombre d'établissements"

    fig = px.bar(
        df_sorted,
        x='Libelle_Departement',
        y=selected_col,
        color=selected_col,
        color_continuous_scale=color_scale,
        hover_name='Libelle_Departement',
        labels={selected_col: label_y, 'Libelle_Departement': 'Département'},
        hover_data={'Libelle_Departement': False, selected_col: True},
        title=titre
    )
    
    fig.update_layout(
        font_family="Montserrat, sans-serif",
        template='plotly_white',
        showlegend=False,
        title_font_size=18,
        margin=dict(l=40, r=40, t=60, b=40),
        hoverlabel=dict(bgcolor="white", font_size=14)
    )
    fig.update_xaxes(title_text="Département")
    fig.update_yaxes(title_text=label_y)
    
    return fig