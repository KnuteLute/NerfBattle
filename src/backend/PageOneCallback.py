import dash
from dash import html, dcc, Input, Output, State, callback, ALL, MATCH
import dash_mantine_components as dmc
import pandas as pd
import json
import random
import time

json_file = 'nerffight.json'
def load_data(filename):
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
            if 'side' not in data or 'players' not in data:
                time.sleep(1)
                
                load_data(filename)
    except json.JSONDecodeError:
        data = {}  # or set to a default value
    return data


@callback(
    Output('page1-names', 'children'),  # Output to display the name or a confirmation message
    [Input('submit-player-btn', 'n_clicks')],  # Button click as trigger
    [State('Add_player_bar', 'value')]  # Input value at the time of the button click
)
def add_player(n_clicks, player_name):
    data = load_data(json_file)
    if n_clicks is not None and player_name:
        if player_name not in data['players']:
            data['players'][player_name] = {
                "games_played": 0,
                "games_won": 0,
                "game_history": []
            }
        else:
            print(f'Player {player_name} already exists.')
        return f"Player {player_name} added successfully!"
    return ""