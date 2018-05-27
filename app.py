# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import data_handler


teams = ['Atlanta Hawks',
         'Boston Celtics',
         'Brooklyn Nets',
         'Charlotte Hornets',
         'Chicago Bulls',
         'Cleveland Cavaliers',
         'Dallas Mavericks',
         'Denver Nuggets',
         'Detroit Pistons',
         'Golden State Warriors',
         'Houston Rockets',
         'Indiana Pacers',
         'Los Angeles Clippers',
         'Los Angeles Lakers',
         'Memphis Grizzlies',
         'Miami Heat',
         'Milwaukee Bucks',
         'Minnesota Timberwolves',
         'New Orleans Pelicans',
         'New York Knicks',
         'Oklahoma City Thunder',
         'Orlando Magic',
         'Philadelphia 76ers',
         'Phoenix Suns',
         'Portland Trail Blazers',
         'Sacramento Kings',
         'San Antonio Spurs',
         'Toronto Raptors',
         'Utah Jazz',
         'Washington Wizards']
team_dropdown_options = []
for team in teams:
    team_dropdown_options.append({'label': team, 'value': team})
    

features = ['ELO', 'TotalWins', 'TotalLosses', 'AvgSpread', 'AvgPTS']
feature_dropdown_options = []
for feature in features:
    feature_dropdown_options.append({'label': feature, 'value': feature})


app = dash.Dash()

app.layout = html.Div(children=[
    html.H1(children='NBA Predictor'),

    html.Div(children='''
        Symbol to Graph:
    '''),
        
    dcc.Dropdown(
        id='team_dropdown',
        options=team_dropdown_options,
        multi=True,
        value=['Toronto Raptors']
    ),
    
    dcc.Dropdown(
        id='feature_dropdown',
        options=feature_dropdown_options,
        multi=True,
        value=['ELO']
    ),
        
    html.Div(id='output-graph'),
    
    dcc.Slider(
        id='season_input',
        min=2000,
        max=2018,
        marks={i: i for i in range(2001, 2018)},
        value=2017
    )
    
])
        
        
@app.callback(
        Output(component_id='output-graph', component_property='children'),
        [Input(component_id='season_input', component_property='value'),
         Input(component_id='team_dropdown', component_property='value'),
         Input(component_id='feature_dropdown', component_property='value')]
        )
def update_graph(season, teams, features):
    data_list = []
    for team in teams:
        for feature in features:
            df = data_handler.load_feature_data(season, team, feature)
            data_list.append({'x': df.Date, 'y': df[feature], 'type': 'line', 'name': '{} {}'.format(team, feature)})
    
    return dcc.Graph(
        id='feature-graph',
        figure={
            'data': data_list,
            'layout': {
                'title': 'NBA Data Features'
            }
        }
    )


if __name__ == '__main__':
    app.run_server(debug=True)