"""
Génère la carte interactive des départements (Folium)
"""

import pandas as pd
import folium
from folium import Element
from functools import lru_cache
from config import JOIN_KEY_DATA, JOIN_KEY_GEOJSON, COL_VALUE, COL_POPULATION, COL_RATIO, RAW_DATA_PATH, CLEAN_DATA_PATH, METRIC_COLORS
from src.utils.geojson import get_departements_geojson
from src.utils.clean_data import clean_etab_to_depart
from src.utils.clean_data import normalize_txt


@lru_cache(maxsize=1)
def load_geojson():
    """
    Charge le fichier GeoJSON des départements en mémoire cache pour 
    éviter de relire le fichier à chaque refresh.
    """
    return get_departements_geojson(return_geojson=True)


@lru_cache(maxsize=1)
def load_df_counts():
    """
    Charge les données statistiques des départements : si le fichier nettoyé n'existe pas, 
    tente de le régénérer depuis les données brutes.
    """
    try:
        return pd.read_csv(CLEAN_DATA_PATH)
    except FileNotFoundError:
        clean_etab_to_depart(pd.read_csv(RAW_DATA_PATH, sep=';', low_memory=False))
        return pd.read_csv(CLEAN_DATA_PATH)

def create_folium_map(selected_col=COL_VALUE, department=None):
    """
    Crée une carte choroplèthe interactive Folium..

    Args:
        selected_col: Colonne de données à visualiser.
        department: Si donné, la carte zoome et ne montre que ce département.
    Returns:
        Carte Folium.
    """

    # Charger les données nettoyées et le GeoJSON (mis en cache)
    df_counts = load_df_counts().copy()
    geojson_data = load_geojson()

    # Jointure des départements avec le GeoJSON
    noms_departements = sorted([f.get('properties', {}).get('nom') for f in geojson_data.get('features', []) if f.get('properties', {}).get('nom')])
    geo_mapping = {normalize_txt(nom): nom for nom in noms_departements}
    df_counts['join_key'] = df_counts['Libelle_Departement'].apply(normalize_txt)
    df_counts[JOIN_KEY_DATA] = df_counts['join_key'].apply(lambda k: geo_mapping.get(k, k))
    df_counts[JOIN_KEY_DATA] = df_counts[JOIN_KEY_DATA].astype(str).str.replace('De ', 'de ').str.replace('Du ', 'du ').str.replace('La ', 'la ')

    # Initialisation centre de la france
    centre_france = [46.603354, 1.888334]
    m = folium.Map(location=centre_france, zoom_start=6, tiles="cartodbpositron")

    # Suppression du carré noir qui s'affiche lors du clic sur un département
    style_css = """
    <style>
    .leaflet-interactive { outline: none; }
    </style>
    """

    m.get_root().html.add_child(Element(style_css))

    # Définition du titre et des labels
    if selected_col == COL_POPULATION:
        legend_label = "Population Totale"
    elif selected_col == COL_RATIO:
        legend_label = "Densité (établissements / 100k hab)"
    else:
        legend_label = "Nombre d'Établissements"
    color = METRIC_COLORS.get(selected_col, 'YlOrRd')

    # Filtrage (Si un département est sélectionné)
    if department:
        filtered_features = [f for f in geojson_data.get('features', []) if f.get('properties', {}).get('nom') == department]
        geojson_data_filtered = {'type': 'FeatureCollection', 'features': filtered_features}
    else:
        geojson_data_filtered = geojson_data

    key_on = JOIN_KEY_GEOJSON if str(JOIN_KEY_GEOJSON).startswith('feature') else f'feature.{JOIN_KEY_GEOJSON}'

    # Calcul des bornes min/max sur l'ensemble des données
    vmin = df_counts[selected_col].min()
    vmax = df_counts[selected_col].max()

    choropleth = folium.Choropleth( 
        geo_data=geojson_data_filtered,
        name='Choropleth',
        data=df_counts,
        columns=[JOIN_KEY_DATA, selected_col],
        key_on=key_on,
        fill_color=color, 
        fill_opacity=0.8,
        line_opacity=0.4,
        legend_name=legend_label,
        highlight=False,
        vmin=vmin,
        vmax=vmax, 
    ).add_to(m)
    
    # Propriétés dynamiques pour les popups en utilisant l'objet GeoJSON en mémoire
    value_map = dict(zip(df_counts[JOIN_KEY_DATA], df_counts[selected_col]))
    if selected_col == COL_POPULATION:
        alias_val = "Population"
    elif selected_col == COL_RATIO:
        alias_val = "Densité / 100k hab"
    else:
        alias_val = "Nombre établissements"
    popup = folium.features.GeoJsonPopup(fields=['nom', 'valeur_dynamique'], aliases=['Département', alias_val], localize=True)
    tooltip = folium.features.GeoJsonTooltip(fields=['nom'], aliases=['Département'])

    for feat in geojson_data_filtered.get('features', []):
        props = feat.setdefault('properties', {})
        nom = props.get('nom')
        if nom:
            props['valeur_dynamique'] = value_map.get(nom, 0)

    geojson_layer = folium.GeoJson(
        geojson_data_filtered,
        name='Informations départements',
        style_function=lambda feature: {
            'fillColor': 'transparent',
            'color': 'grey',
            'weight': 0.5,
            'fillOpacity': 0
        },
        tooltip=tooltip,
        popup=popup,
        zoom_on_click=True
    )
    geojson_layer.add_to(m)
    
    return m