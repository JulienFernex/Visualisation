"""
Génère l'Histogramme de Distribution (répartition par plages de valeurs)
"""

import pandas as pd
import plotly.express as px
import numpy as np
from config import CLEAN_DATA_PATH, CLEAN_DATA_COMMUNE_PATH, COL_VALUE, COL_POPULATION, COL_RATIO
from src.utils.clean_data import normalize_txt

def create_dist_hist(selected_col=COL_POPULATION, department=None):
    """
    Génère un histogramme montrant la distribution des entités (Communes ou Départements)
    selon des plages de valeurs.

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

    df = pd.DataFrame()
    entity_name = "Département"
    
    # Vue Départementale (Communes)
    if department:
        try:
            df_comm = pd.read_csv(CLEAN_DATA_COMMUNE_PATH)
            dept_norm = normalize_txt(department)
            mask = df_comm['Libelle_Departement'].apply(lambda v: normalize_txt(v) == dept_norm if pd.notna(v) else False)
            df = df_comm[mask].copy()
            entity_name = "Commune"
            titre_suffixe = f"par Commune (Département : {department})"
        except FileNotFoundError:
            pass
    
    if df.empty:
        try:
            df = pd.read_csv(CLEAN_DATA_PATH)
            entity_name = "Département"
            titre_suffixe = "par Département"
        except FileNotFoundError:
            return px.bar(title="Données non trouvées")

    # Définition du titre et des labels
    if selected_col == COL_POPULATION:
        titre = f"Distribution de la Population {titre_suffixe}"
        range_label = "Plage de Population"
    elif selected_col == COL_RATIO:
        titre = f"Distribution de la Densité (pour 100k hab) {titre_suffixe}"
        range_label = "Plage de Densité"
    else:
        titre = f"Distribution du Nombre d'Établissements {titre_suffixe}"
        range_label = "Plage d'Établissements"
    
    # Création des plages
    n_bins = 10
    metric_min = df[selected_col].min()
    metric_max = df[selected_col].max()
    
    # Gestion du cas où min == max (ex: une seule commune ou tout à 0)
    if metric_min == metric_max:
         margin = 1 if metric_max == 0 else metric_max * 0.01
    else:
         margin = (metric_max - metric_min) * 0.01

    # Gestion des données
    bins = np.linspace(metric_min, metric_max + margin, n_bins + 1)
    df['Value_Range'] = pd.cut(df[selected_col], bins=bins, labels=False, include_lowest=True)
    dist_data = df.groupby('Value_Range').size().reset_index(name='Compte')
    
    # Création des labels
    range_labels = []
    for i in range(len(bins) - 1):
        min_val = int(bins[i])
        max_val = int(bins[i + 1])
        range_labels.append(f"{min_val:,} - {max_val:,}")
    dist_data['Range_Label'] = dist_data['Value_Range'].apply(lambda x: range_labels[int(x)] if 0 <= x < len(range_labels) else "N/A")
    label_y = f"Nombre de {entity_name}s"

    # Création du Graphique
    fig = px.bar(
        dist_data,
        x='Range_Label',
        y='Compte',
        color='Value_Range',
        color_continuous_scale=color_scale,
        hover_name='Range_Label',
        labels={
            'Range_Label': range_label,
            'Compte': label_y
        },
        hover_data={'Range_Label': False, 'Compte': True, 'Value_Range': False},
        title=titre
    )
    
    # Nettoyage visuel
    fig.update_layout(
        font_family="Montserrat, sans-serif",
        template='plotly_white',
        title_font_size=18,
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=40, r=40, t=60, b=40),
        hoverlabel=dict(bgcolor="white", font_size=14)
    )
    fig.update_xaxes(title_text=range_label, showgrid=False)
    fig.update_yaxes(title_text=label_y, showgrid=True, gridcolor='#eee')
    
    return fig