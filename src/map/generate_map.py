import pandas as pd
import folium
import numpy as np
import requests
from src.utils.reference import GEOJSON_URL, JOIN_KEY_DATA, JOIN_KEY_GEOJSON, COL_VALUE, RAW_DATA_PATH, CLEAN_DATA_PATH, OUTPUT_MAP
from src.utils.geojson import get_departements_geojson
from src.utils.clean_data import clean_etab_to_depart

try:
    df_counts = pd.read_csv(CLEAN_DATA_PATH)
except FileNotFoundError:
    print("Erreur : Le fichier 'clean_data.csv' est introuvable.")
    clean_etab_to_depart(pd.read_csv(RAW_DATA_PATH, sep=';', low_memory=False))
    exit()

# Préparer les noms des départements pour la jointure avec le GeoJSON
df_counts['Nom_Departement_Harmonise'] = df_counts['Libelle_Departement'].str.title().str.replace(' ', '-').str.replace('Et', 'et')
i = 0
lista=get_departements_geojson()
for value in df_counts['Libelle_Departement']:
    if(i<101):
        df_counts.loc[df_counts['Libelle_Departement'] == value, 'Nom_Departement_Harmonise'] = lista[i]
        i+=1
df_counts['Nom_Departement_Harmonise'] = df_counts['Nom_Departement_Harmonise'].str.replace('De ', 'de ').str.replace('Du ', 'du ').str.replace('La ', 'la ')


# Initialisation centre de la france
centre_france = [46.603354, 1.888334]
# Initialiser la carte
m = folium.Map(location=centre_france, zoom_start=6, tiles="cartodbpositron")

choropleth = folium.Choropleth( 
    geo_data=GEOJSON_URL,
    name='Établissements par Département',
    data=df_counts,
    columns=[JOIN_KEY_DATA, COL_VALUE],
    key_on=JOIN_KEY_GEOJSON,
    fill_color='YlOrRd', 
    fill_opacity=0.8,
    line_opacity=0.4,
    legend_name="Nombre d'Établissements",
    highlight=False
).add_to(m)

try:
    geojson_data = requests.get(GEOJSON_URL, timeout=10).json()
except Exception as e:
    print(f"Impossible de récupérer le GeoJSON pour les popups : {e}")
    geojson_data = None

if geojson_data:
    value_map = dict(zip(df_counts[JOIN_KEY_DATA], df_counts[COL_VALUE]))

    for feat in geojson_data.get('features', []):
        props = feat.setdefault('properties', {})
        nom = props.get('nom')
        props[COL_VALUE] = value_map.get(nom, 0)

    popup = folium.features.GeoJsonPopup(fields=['nom', COL_VALUE], aliases=['Département', 'Nombre établissements'], localize=True)
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
    
m.save(OUTPUT_MAP)
print("\nCarte générée avec succès ! Ouvrez le fichier 'carte_etablissements_par_departement.html' dans votre navigateur pour l'afficher.")