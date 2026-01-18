"""
Génère un Histogramme (Bar Chart)
"""

import pandas as pd
import plotly.express as px
from src.utils.reference import CLEAN_DATA_PATH, COL_VALUE, COL_POPULATION, COL_RATIO, CLEAN_DATA_COMMUNE_PATH
from src.utils.clean_data import normalize_txt

def create_histogram(selected_col=COL_VALUE, department=None):
    # Choix de l'échelle de couleur
    if selected_col == COL_POPULATION:
        color_scale = 'YlGnBu' 
    elif selected_col == COL_RATIO:
        color_scale = 'PuBuGn'
    else:
        color_scale = 'YlOrRd' 

    # Si un département est sélectionné, afficher histogramme des communes
    if department:
        try:
            df_comm = pd.read_csv(CLEAN_DATA_COMMUNE_PATH)
            dept_norm = normalize_txt(department)
            mask = df_comm['Libelle_Departement'].apply(lambda v: normalize_txt(v) == dept_norm if pd.notna(v) else False)
            df_dept = df_comm[mask]

            if not df_dept.empty:
                df_sorted = df_dept.sort_values(by=selected_col, ascending=True)
                
                # Titres dynamiques
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
                    color=selected_col, # Dégradé de couleur selon la valeur
                    color_continuous_scale=color_scale,
                    hover_name='Libelle_Commune',
                    
                    # Configuration des infobulles des axes
                    labels={selected_col: label_y, 'Libelle_Commune': 'Commune'},
                    hover_data={
                        'Libelle_Commune': False,
                        selected_col: True
                    },
                    
                    title=titre,
                )
                
                fig.update_layout(
                    font_family="Montserrat, sans-serif",
                    template='plotly_white',
                    title_font_size=18,
                    showlegend=False,
                    margin=dict(l=40, r=40, t=60, b=40),
                    hoverlabel=dict(bgcolor="white", font_size=14)
                )
                fig.update_xaxes(title_text="Commune", showgrid=False) # Pas de grille verticale
                fig.update_yaxes(title_text=label_y, showgrid=True, gridcolor='#eee')
                
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
        label_y = "Nombre d'établissements"

    fig = px.bar(
        df_sorted,
        x='Libelle_Departement',
        y=selected_col,
        color=selected_col,
        color_continuous_scale=color_scale,
        hover_name='Libelle_Departement',
        
        # Configuration des infobulles des axes
        labels={selected_col: label_y, 'Libelle_Departement': 'Département'},
        hover_data={
            'Libelle_Departement': False,
            selected_col: True
        },
        
        title=titre
    )
    
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title_text="Département")
    fig.update_yaxes(title_text=label_y)
    
    return fig