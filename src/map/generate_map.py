"""
Génère la carte
"""

import pandas as pd
import folium
from folium import Element
import requests
import unicodedata
from src.utils.reference import GEOJSON_URL, JOIN_KEY_DATA, JOIN_KEY_GEOJSON, COL_VALUE, COL_POPULATION, RAW_DATA_PATH, CLEAN_DATA_PATH
from src.utils.geojson import get_departements_geojson
from src.utils.clean_data import clean_etab_to_depart
from src.utils.clean_data import normalize_txt

def create_folium_map(selected_col=COL_VALUE):
    try:
        df_counts = pd.read_csv(CLEAN_DATA_PATH)
    except FileNotFoundError:
        print("Erreur : Le fichier 'clean_data.csv' est introuvable.")
        clean_etab_to_depart(pd.read_csv(RAW_DATA_PATH, sep=';', low_memory=False))
        exit()

    # Préparer les noms des départements pour la jointure avec le GeoJSON
    df_counts['Nom_Departement_Harmonise'] = df_counts['Libelle_Departement'].str.title().str.replace(' ', '-').str.replace('Et', 'et')
    lista=get_departements_geojson()
    
    # Dictionnaire avec pour clé le nom normalisé et valeur le nom du GeoJSON
    geo_mapping = {normalize_txt(nom): nom for nom in lista}

    # Retoure le nom du GeoJson s'il existe, sinon on garde l'ancien nom
    def trouver_nom_officiel(nom_csv):
        nom_norm = normalize_txt(nom_csv)
        return geo_mapping.get(nom_norm, nom_csv)

    # Application du mapping
    df_counts['Nom_Departement_Harmonise'] = df_counts['Libelle_Departement'].apply(trouver_nom_officiel)
    df_counts['Nom_Departement_Harmonise'] = df_counts['Nom_Departement_Harmonise'].str.replace('De ', 'de ').str.replace('Du ', 'du ').str.replace('La ', 'la ')

    # Initialisation centre de la france
    centre_france = [46.603354, 1.888334]
    # Initialiser la carte
    m = folium.Map(location=centre_france, zoom_start=6, tiles="cartodbpositron")

    # Suppression du carré noir qui s'affiche lors du clic sur un département
    style_css = """
    <style>
    .leaflet-interactive { outline: none; }
    </style>
    """

    m.get_root().html.add_child(Element(style_css))

    if selected_col == COL_POPULATION:
        legend_label = "Population Totale"
        color = 'YlGnBu'
    else:
        legend_label = "Nombre d'Établissements"
        color = 'YlOrRd'

    choropleth = folium.Choropleth( 
        geo_data=GEOJSON_URL,
        name='Choropleth',
        data=df_counts,
        columns=[JOIN_KEY_DATA, selected_col],
        key_on=JOIN_KEY_GEOJSON,
        fill_color=color, 
        fill_opacity=0.8,
        line_opacity=0.4,
        legend_name=legend_label,
        highlight=False
    ).add_to(m)

    try:
        geojson_data = requests.get(GEOJSON_URL, timeout=10).json()
    except Exception as e:
        print(f"Impossible de récupérer le GeoJSON pour les popups : {e}")
        geojson_data = None

    if geojson_data:
        value_map = dict(zip(df_counts[JOIN_KEY_DATA], df_counts[selected_col]))

        for feat in geojson_data.get('features', []):
            props = feat.setdefault('properties', {})
            nom = props.get('nom')
            props['valeur_dynamique'] = value_map.get(nom, 0)

        alias_val = "Population" if selected_col == COL_POPULATION else "Nombre établissements"
        popup = folium.features.GeoJsonPopup(fields=['nom', 'valeur_dynamique'], aliases=['Département', alias_val], localize=True)
        tooltip = folium.features.GeoJsonTooltip(fields=['nom'], aliases=['Département'])

        geojson_layer = folium.GeoJson(
            geojson_data,
            name='Informations départements',
            style_function=lambda feature: {
                'fillColor': 'transparent',
                'color': 'grey',
                'weight': 0.5,
                'fillOpacity': 0
            },
            highlight_function=lambda feature: {'weight':1, 'color':'black'},
            tooltip=tooltip,
            popup=popup,
        )
        geojson_layer.add_to(m)
    
    return m