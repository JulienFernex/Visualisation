import dash
from dash import html
import sys
import os

# Importation des modules depuis la racine du projet
repertoireActuel = os.path.dirname(os.path.abspath(__file__))
cheminProjet = os.path.join(repertoireActuel, '..', '..')
sys.path.append(cheminProjet)

# Importation de la fonction générant la carte
from src.map.generate_map import create_folium_map

# Carte Folium
folium_map_obj = create_folium_map()
map_html_string = folium_map_obj.get_root().render()

# Configuration de l'application
app = dash.Dash(__name__)

# Mise en page du dashboard
app.layout = html.Div(children=[
    
    # Entête
    html.H1("DashBoard : Etude de la répartition des établissements de santé", 
            style={'textAlign': 'center', 'color': 'black', 'marginBottom': '10px'}),
    
    html.Div("Cette étude se concentre sur le territoire de France métropolitaine", 
             style={'textAlign': 'center', 'marginBottom': '30px', 'fontSize': '18px', 'color': 'Gray'}),

    # Carte
    html.Div([
        html.H3("Carte des Établissements par Département", style={'textAlign': 'center'}),
        
        # Affichage du HTML de Folium avec le composant Iframe
        html.Iframe(
            id='folium-map',
            srcDoc=map_html_string,  # Injection du HTML de la carte
            style={'width': '100%', 'height': '600px', 'border': 'none'}
        )
    ], style={'width': '98%','marginBottom': '30px', 'boxShadow': '0px 0px 5px #ccc', 'padding': '15px', 'backgroundColor': 'white'}),

    # TODO
    # ZONE AVEC LE GRAPHIQUE ET l'HISTOGRAMME
    html.Div([
        # Colonne Gauche : Graphique
        html.Div([
            html.H3("ZONE DU GRAPHIQUE", style={'textAlign': 'left'}),
            html.Iframe(
            id='folium-map',
            srcDoc=map_html_string,
            style={'width': '100%', 'height': '600px', 'border': 'none'}
        )
        ], style={'width': '47%', 'display': 'inline-block', 'verticalAlign': 'top', 'boxShadow': '0px 0px 5px #ccc', 'padding': '15px', 'backgroundColor': 'white'}),

        # Espace entre les deux zones
        html.Div(style={'width': '2%', 'display': 'inline-block'}),

        # Colonne Droite : Histogramme
        html.Div([
            html.H3("ZONE DE L'HISTOGRAMME", style={'textAlign': 'right'}),
            html.Iframe(
            id='folium-map',
            srcDoc=map_html_string,
            style={'width': '100%', 'height': '600px', 'border': 'none'}
        )
        ], style={'width': '47%', 'display': 'inline-block', 'verticalAlign': 'top', 'boxShadow': '0px 0px 5px #ccc', 'padding': '15px', 'backgroundColor': 'white'})

    ], style={'marginBottom': '30px'}),
])

# Lancement du serveur
if __name__ == '__main__':
    app.run(debug=True)