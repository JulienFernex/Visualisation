import dash
from dash import html, dcc, Input, Output
import sys
import os

# Importation des modules depuis la racine du projet
repertoireActuel = os.path.dirname(os.path.abspath(__file__))
cheminProjet = os.path.join(repertoireActuel, '..', '..')
sys.path.append(cheminProjet)

# Importation des fonctions et données générérant les représentations de données
from src.map.generate_map import create_folium_map
from src.graph.generate_graph import create_bubble_chart
from src.hist.generate_hist import create_histogram
from src.utils.reference import COL_VALUE, COL_POPULATION

# Configuration de l'application
app = dash.Dash(__name__)

# Mise en page du dashboard
app.layout = html.Div(children=[
    
    # Entête
    html.H1("DashBoard : Etude de la répartition des établissements de santé", 
            style={'textAlign': 'center', 'color': 'black', 'marginBottom': '10px'}),
    
    html.Div("Cette étude se concentre sur le territoire de France métropolitaine (bien qu'en l'état certains départements d'outre mer sont pris en compte)", 
             style={'textAlign': 'center', 'marginBottom': '30px', 'fontSize': '18px', 'color': 'Gray'}),

    html.Div([
        html.Label("Choisir la métrique à visualiser :", style={'fontWeight': 'bold', 'marginRight': '10px'}),
        dcc.RadioItems(
            id='metric-selector',
            options=[
                {'label': ' Volume Total', 'value': COL_VALUE},
                {'label': ' Densité (pour 100k hab)', 'value': 'Ratio_100k'},
                {'label': ' Population Totale', 'value': COL_POPULATION}
            ],
            value=COL_VALUE,
            inline=True,
            labelStyle={'display': 'inline-block', 'marginRight': '15px', 'cursor': 'pointer'}
        )
    ], style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#f9f9f9', 'marginBottom': '20px'}),

    # Carte
    html.Div([
        html.H3("Carte des Établissements par Département", style={'textAlign': 'center'}),
        
        # Affichage du HTML de Folium avec le composant Iframe
        html.Iframe(
            id='folium-map',
            srcDoc=create_folium_map(COL_VALUE).get_root().render(),  # Injection du HTML de la carte
            style={'width': '100%', 'height': '600px', 'border': 'none'}
        )
    ], style={'width': '98%','marginBottom': '30px', 'boxShadow': '0px 0px 5px #ccc', 'padding': '15px', 'backgroundColor': 'white'}),

    # ZONE AVEC LE GRAPHIQUE ET l'HISTOGRAMME
    html.Div([
        # Colonne Gauche : Graphique
        html.Div([
            html.H3("Graphique à bulles", style={'textAlign': 'center'}),
            dcc.Graph(   # dcc.Graph pour Plotly
                id='bubble-chart',
                figure=create_bubble_chart(COL_VALUE),
                style={'height': '600px'}
            )
        ], style={'width': '47%', 'display': 'inline-block', 'verticalAlign': 'top', 'boxShadow': '0px 0px 5px #ccc', 'padding': '15px', 'backgroundColor': 'white'}),

        # Espace entre les deux zones
        html.Div(style={'width': '2%', 'display': 'inline-block'}),

        # Colonne Droite : Histogramme
        html.Div([
            html.H3("Histogramme", style={'textAlign': 'center'}),
            
            # Intégration de l'histogramme ici
            dcc.Graph(
                id='histogram-chart',
                figure=create_histogram(COL_VALUE),
                style={'height': '600px'}
            )
        ], style={'width': '47%', 'display': 'inline-block', 'verticalAlign': 'top', 'boxShadow': '0px 0px 5px #ccc', 'padding': '15px', 'backgroundColor': 'white'})

    ], style={'marginBottom': '30px'}),
])

# Quand le RadioItems change, tout se met à jour
@app.callback(
    [Output('folium-map', 'srcDoc'),
     Output('bubble-chart', 'figure'),
     Output('histogram-chart', 'figure')],
    [Input('metric-selector', 'value')]
)
def update_dashboard(selected_metric):    # Appellée automatiquement quand le metric-selector a une valeur, soit quand on clique dessus
    map_obj = create_folium_map(selected_metric)
    map_html = map_obj.get_root().render()
    bubble_fig = create_bubble_chart(selected_metric)
    hist_fig = create_histogram(selected_metric)
    
    return map_html, bubble_fig, hist_fig

# Lancement du serveur
if __name__ == '__main__':
    app.run(debug=True)