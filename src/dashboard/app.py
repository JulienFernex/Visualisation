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
from src.hist.generate_hist import create_histogram, create_population_distribution_histogram, create_population_distribution_pie
from src.utils.reference import COL_VALUE, COL_POPULATION, COL_RATIO
from src.utils.geojson import get_departements_geojson

# Importation de la police Google Fonts
external_stylesheets = ['https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;700&display=swap']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Styles CSS
# Style pour les Cartes : Blocs blancs avec ombre et arrondis
STYLE_CARD = {
    'backgroundColor': 'white',
    'borderRadius': '15px',
    'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
    'padding': '20px',
    'border': '1px solid #f0f0f0'
}

# Style du conteneur principal : Fond gris clair
STYLE_CONTAINER = {
    'fontFamily': 'Montserrat, sans-serif',
    'backgroundColor': '#f8f9fa',
    'padding': '30px',
    'minHeight': '100vh',
    'color': '#333'
}

# Mise en page du dashboard
app.layout = html.Div(children=[
    
    # En tête
    html.Div([
        html.H1("Répartition des Établissements de Santé", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '10px', 'fontWeight': '700'}),
        
        html.Div("Analyse territoriale : France métropolitaine et DROM", 
                 style={'textAlign': 'center', 'marginBottom': '0px', 'fontSize': '16px', 'color': '#7f8c8d'}),
    ], style={**STYLE_CARD, 'marginBottom': '30px'}),

    # Bloc cartes et sélecteurs
    html.Div([
        
        # Zone des sélecteurs (Gauche)
        html.Div([
            html.H3("Contrôles", style={'marginTop': '0', 'color': '#2c3e50'}),
            html.Label("Métrique :", style={'fontWeight': 'bold', 'display': 'block', 'marginBottom': '10px'}),
            dcc.RadioItems(
                id='metric-selector',
                options=[
                    {'label': "Nombre d'établissements", 'value': COL_VALUE},
                    {'label': 'Population Totale', 'value': COL_POPULATION},
                    {'label': "Densité (pour 100k hab)", 'value': COL_RATIO}
                ],
                value=COL_VALUE,
                labelStyle={'display': 'block', 'marginBottom': '8px', 'cursor': 'pointer'}
            ),
            
            html.Br(),
            
            html.Label("Département :", style={'fontWeight': 'bold', 'display': 'block', 'marginBottom': '10px'}),
            dcc.Dropdown(
                id='department-selector',
                # Récupère directement la liste des noms (déjà triée par get_departements_geojson)
                options=[{'label': d, 'value': d} for d in get_departements_geojson()],
                placeholder="Sélectionnez un département",
                style={'width': '100%'}
            ),
            
            html.Div("Sélectionnez un département pour voir le détail par commune.", style={'fontSize': '12px', 'color': 'grey', 'marginTop': '10px'})

        ], style={**STYLE_CARD, 'width': '28%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '2%'}),

        # Zone Carte (Droite)
        html.Div([
            dcc.Loading(
                id='loading-map',
                type='dot',
                color='#3498db',
                children=html.Iframe(
                    id='folium-map', 
                    srcDoc=create_folium_map().get_root().render(), 
                    width='100%', 
                    height='600',
                    style={'border': 'none', 'borderRadius': '15px'} 
                ),
                style={'height': '600px'} # Assure que le loading est centré dans la zone
            )
        ], style={**STYLE_CARD, 'width': '66%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '0px'}),

    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '30px'}),

    # Bloc des graphiques
    html.Div([
        
        # Graphique à bulles
        html.Div([
            dcc.Loading(
                id='loading-bubble',
                type='dot',
                color='#3498db',
                children=dcc.Graph(
                    id='bubble-chart',
                    figure=create_bubble_chart(COL_VALUE),
                    style={'height': '600px'}
                ),
                style={'height': '600px'}
            )
        ], style={**STYLE_CARD, 'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '2%'}),

        # Histogramme
        html.Div([
            dcc.Loading(
                id='loading-hist',
                type='dot',
                color='#3498db',
                children=dcc.Graph(
                    id='histogram-chart',
                    figure=create_histogram(COL_VALUE),
                    style={'height': '600px'}
                ),
                style={'height': '600px'}
            )
        ], style={**STYLE_CARD, 'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})

    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '30px'}),

    # Bloc de l'histogramme et camembert de distribution
    html.Div([
        
        # Histogramme de distribution
        html.Div([
            dcc.Loading(
                id='loading-dist-hist',
                type='dot',
                color='#3498db',
                children=dcc.Graph(
                    id='distribution-histogram-chart',
                    figure=create_population_distribution_histogram(),
                    style={'height': '600px'}
                ),
                style={'height': '600px'}
            )
        ], style={**STYLE_CARD, 'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '2%'}),

        # Camembert de distribution
        html.Div([
            dcc.Loading(
                id='loading-dist-pie',
                type='dot',
                color='#3498db',
                children=dcc.Graph(
                    id='distribution-pie-chart',
                    figure=create_population_distribution_pie(),
                    style={'height': '600px'}
                ),
                style={'height': '600px'}
            )
        ], style={**STYLE_CARD, 'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})

    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '30px'}),

], style=STYLE_CONTAINER)


# Quand le RadioItems change, tout se met à jour
@app.callback(
    [Output('folium-map', 'srcDoc'),
     Output('bubble-chart', 'figure'),
     Output('histogram-chart', 'figure'),
     Output('distribution-histogram-chart', 'figure'),
     Output('distribution-pie-chart', 'figure')],
    [Input('metric-selector', 'value'),
     Input('department-selector', 'value')]
)
def update_dashboard(selected_metric, selected_department):
    # Si aucun département sélectionné (None ou ''), on affiche tous
    dept = selected_department if selected_department else None
    
    # Génération des mises à jour
    map_obj = create_folium_map(selected_metric, department=dept)
    map_html = map_obj.get_root().render()
    
    bubble_fig = create_bubble_chart(selected_metric, department=dept)
    hist_fig = create_histogram(selected_metric, department=dept)
    dist_hist_fig = create_population_distribution_histogram(selected_metric)
    dist_pie_fig = create_population_distribution_pie(selected_metric)
    
    return map_html, bubble_fig, hist_fig, dist_hist_fig, dist_pie_fig

# Lancer l'application
if __name__ == '__main__':
    app.run(debug=True)