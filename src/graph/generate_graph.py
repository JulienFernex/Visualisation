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

            if not df_dept.empty:
                # Titres et Labels dynamiques
                if selected_col == COL_POPULATION:
                    titre = f"Distribution de la population par commune — {department}"
                    label_y = "Population Totale"
                elif selected_col == COL_RATIO:
                    titre = f"Densité d'établissements (pour 100k hab) par commune — {department}"
                    label_y = "Densité (pour 100k hab)"
                else:
                    titre = f"Distribution du nombre d'établissements par commune — {department}"
                    label_y = "Nombre d'établissements"

                fig = px.scatter(
                    df_dept,
                    x='Libelle_Commune',
                    y=selected_col,
                    size=selected_col if selected_col in df_dept.columns else None, # Taille proportionnelle à la métrique
                    color='Libelle_Commune', # Couleur pour distinguer, mais sans légende car trop nombreux
                    hover_name='Libelle_Commune', # Titre de l'infobulle
                    
                    # Configuration des infobulles des axes
                    labels={selected_col: label_y, 'Libelle_Commune': 'Commune'},
                    hover_data={
                        'Libelle_Commune': False, # Ne pas répéter le nom
                        selected_col: True        # Afficher la valeur
                    },
                    
                    size_max=60,
                    title=titre
                )
                
                # Nettoyage visuel
                fig.update_layout(
                    font_family="Montserrat, sans-serif",
                    template='plotly_white', # Fond blanc épuré
                    title_font_size=18,
                    showlegend=False,
                    margin=dict(l=40, r=40, t=60, b=40), # Marges propres
                    hoverlabel=dict(bgcolor="white", font_size=14)
                )
                fig.update_xaxes(title_text="Commune", showgrid=True, gridcolor='#eee')
                fig.update_yaxes(title_text=label_y, showgrid=True, gridcolor='#eee')
                
                return fig
        except FileNotFoundError:
            pass

    # Par défaut (pas de département ou pas de données communales), rester au niveau département
    try:
        df = pd.read_csv(CLEAN_DATA_PATH)
    except FileNotFoundError:
        return px.scatter(title="Données non trouvées")

    # Définition dynamique du titre et des labels (Niveau National)
    if selected_col == COL_POPULATION:
        titre = "Distribution de la population totale par département"
        label_y = "Population Totale"
    elif selected_col == COL_RATIO:
        titre = "Densité d'établissements de santé (pour 100k hab) par département"
        label_y = "Densité / 100k hab"
    else:
        titre = "Distribution du nombre d'établissements de santé par département"
        label_y = "Nombre d'établissements"

    fig = px.scatter(
        df,
        x='Libelle_Departement',
        y=selected_col,
        size=selected_col if selected_col in df.columns else None,
        color='Libelle_Departement',
        hover_name='Libelle_Departement',
        
        # Configuration des infobulles des axes
        labels={selected_col: label_y, 'Libelle_Departement': 'Département'},
        hover_data={
            'Libelle_Departement': False,
            selected_col: True
        },
        
        size_max=60,
        title=titre
    )
    
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title_text="Département")
    fig.update_yaxes(title_text=label_y)

    return fig