"""
Génère le Camembert de Distribution (Pie Chart)
"""

import pandas as pd
import plotly.express as px
import numpy as np
from config import CLEAN_DATA_PATH, CLEAN_DATA_COMMUNE_PATH, COL_VALUE, COL_POPULATION, COL_RATIO, METRIC_COLORS
from src.utils.clean_data import normalize_txt

def create_pie_chart(selected_col=COL_POPULATION, department=None):
    """
    Génère un graphique en camembert (Pie Chart) montrant la répartition des entités
    par plages de valeurs.

    Args:
        selected_col: Métrique analysée.
        department: Filtre départemental (optionnel).
    Returns:
        Figure Plotly.
    """

    # Choix de l'échelle de couleur
    color_scale = METRIC_COLORS.get(selected_col, 'YlOrRd')
    
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
            titre_suffixe = f"Communes (Département : {department})"
        except FileNotFoundError:
            pass

    # Vue Nationale par défaut (Départements)      
    if df.empty:
        try:
            df = pd.read_csv(CLEAN_DATA_PATH)
            entity_name = "Département"
            titre_suffixe = "Départements"
        except FileNotFoundError:
            return px.pie(title="Données non trouvées")
    
    # Définition du titre et des labels
    if selected_col == COL_POPULATION:
        titre = f"Répartition du nombre de {titre_suffixe} par Plage de Population"
        range_label = "Plage de Population"
    elif selected_col == COL_RATIO:
        titre = f"Répartition du nombre de {titre_suffixe} par Plage de Densité"
        range_label = "Plage de Densité"
    else:
        titre = f"Répartition du nombre de {titre_suffixe} par Plage d'Établissements"
        range_label = "Plage d'Établissements"
    
    n_bins = 10
    metric_min = df[selected_col].min()
    metric_max = df[selected_col].max()
    
    if metric_min == metric_max:
         margin = 1 if metric_max == 0 else metric_max * 0.01
    else:
         margin = (metric_max - metric_min) * 0.01

    bins = np.linspace(metric_min, metric_max + margin, n_bins + 1)
    
    df['Value_Range'] = pd.cut(df[selected_col], bins=bins, labels=False, include_lowest=True)
    dist_data = df.groupby('Value_Range').size().reset_index(name='Compte')
    dist_data = dist_data.sort_values('Value_Range')
    
    range_labels = []
    for i in range(len(bins) - 1):
        min_val = int(bins[i])
        max_val = int(bins[i + 1])
        range_labels.append(f"{min_val:,} - {max_val:,}")
    
    dist_data['Range_Label'] = dist_data['Value_Range'].apply(lambda x: range_labels[int(x)] if 0 <= x < len(range_labels) else "N/A")
    
    label_count = f"Nombre de {entity_name}s"

    colors = px.colors.sample_colorscale(color_scale, [i/n_bins for i in dist_data['Value_Range']])

    # Création du graphique
    fig = px.pie(
        dist_data,
        values='Compte',
        names='Range_Label',
        labels={
            'Range_Label': range_label,
            'Compte': label_count
        },
        hover_data={'Compte': True},
        title=titre
    )
    fig.update_traces(marker=dict(colors=colors))
    fig.update_layout(
        font_family="Montserrat, sans-serif",
        template='plotly_white',
        title_font_size=18,
        margin=dict(l=40, r=40, t=60, b=40),
        hoverlabel=dict(bgcolor="white", font_size=14)
    )
    
    return fig