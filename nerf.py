from dash import Dash, html, dcc, Input, Output, State, callback
import dash
import random
import os
import json
import dash_mantine_components as dmc
import numpy as np
filename = 'nerffight.json'

def load_data(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

def save_data(filename, data):
    
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)

def add_player(data, player_name):
    if player_name not in data['players']:
        data['players'][player_name] = {
            "games_played": 0,
            "games_won": 0,
            "game_history": []
        }
    else:
        print(f'Player {player_name} already exists.')

def add_score(data, player_name, game_result, side_played):
    if player_name in data['players']:
        data['players'][player_name]['games_played'] += 1
        data['players'][player_name]['game_history'].append(game_result)
        if game_result == 'win':
            data['players'][player_name]['games_won'] += 1
            data['side'][side_played]['side_win'] += 1
        data['side'][side_played]['side_history'].append(game_result)
    else:
        print(f'Player {player_name} does not exist.')

def add_side_score(side):
    data = load_data('nerffight.json')
    if side == 0: #long
        data['side']['long']['side_history'].append(1)
        wins = data['side']['long']['side_win']
        data['side']['long']['side_win'] = wins+1
        data['side']['islands']['side_history'].append(0)
        
    elif side == 1: #Island
        data['side']['islands']['side_history'].append(1)
        wins = data['side']['islands']['side_win']
        data['side']['islands']['side_win'] = wins+1
        data['side']['long']['side_history'].append(0)

    save_data('nerffight.json', data)


def add_team_score(side, team):
    data = load_data('nerffight.json')
    long = team[0]
    island = team[1]
    data['game']['game'] += 1
    game = data['game']['game']
    

    for player in data['players']: 
        if player in long: # player is in long
            if side == 0: #player is in long and long has won
                data['players'][player]['games_played'] += 1
                data['players'][player]['games_won'] += 1
                data['players'][player]['game_history'].append([0,game])
            else: #player is in long and long lost
                data['players'][player]['games_played'] += 1
                data['players'][player]['game_history'].append([1,game])

        elif player in island:
            if side == 1: #player is in island and island won
                data['players'][player]['games_played'] += 1
                data['players'][player]['games_won'] += 1
                data['players'][player]['game_history'].append([2,game])
            else: #player is in long and long lost
                data['players'][player]['games_played'] += 1
                data['players'][player]['game_history'].append([3,game])

    save_data('nerffight.json', data)

def reset_data():
    # Load the data
    data = load_data('nerffight.json')

    # Reset player statistics and game history
    for player_data in data['players'].values():
        player_data['games_played'] = 0
        player_data['games_won'] = 0
        player_data['game_history'] = []

    # Reset side statistics and game history
    for side_data in data['side'].values():
        side_data['side_win'] = 0
        side_data['side_history'] = []

    # Save the reset data back to the JSON file
    save_data(filename, data)
            

data = load_data('nerffight.json')

players = list(data['players'].keys())


# Create the Dash application
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Define the layout of the application
# Define the layout of the application
app.layout = html.Div(children=[
    
    html.H1(children='Nerf Scoreboard'),
    html.P(children='Welcome to the Nerf Scoreboard! Here you can keep track of player scores and game statistics.'),

    # Input for adding a player
    dcc.Input(id='player-input', type='text', placeholder='Enter a player name...'),
    html.Button('Add Player', id='add-player-button', n_clicks=0),

    # Dropdown for selecting players
    dcc.Dropdown(
        id='player-dropdown',
        options=[{'label': i, 'value': i} for i in players],
        multi=True,
        placeholder="Select players...",
    ),

    # Button for creating a game
    dmc.Button('Make Game', id='make-game-button'),

    # Div for displaying the teams
    html.Div(id='teams-display'),
    dmc.Grid(
        dmc.Col(
            children=[
                dmc.Button('Island Wins', id='island-wins-button'),
                dmc.Button('Long Wins', id='long-wins-button'),
            ],
            id='winning-button'
        ),
    ),

    dmc.Grid(
        dmc.Col(
            children=[
                
            ],
            id='scoreboard'
        ),
    ),
    dcc.Graph(id='win-histogram'),
    dcc.Graph(id='game-history-graph'),
    # Buttons for team wins
    


    dcc.Store(id='team', storage_type='session'),
    dcc.Store(id='island-team-win', storage_type='session'),
    dcc.Store(id='long-team-win', storage_type='session'),
    
])

# Callback for the 'Add Player' button click event
@app.callback(
    Output('player-dropdown', 'options'),
    Input('add-player-button', 'n_clicks'),
    State('player-input', 'value'),
    prevent_initial_call=True
)
def add_player_to_file(n_clicks, player_name):
    data = load_data('nerffight.json')
    if n_clicks > 0 and player_name:
        if player_name in data['players']:
            return[{'label': i, 'value': i} for i in data['players'].keys()]
        else:
            add_player(data, player_name)
            save_data('nerffight.json', data)
            return [{'label': i, 'value': i} for i in data['players'].keys()]


# Callback for the 'Make Game' button click event
@app.callback(
    Output('team', 'data'),
    Input('make-game-button', 'n_clicks'),
    State('player-dropdown', 'value'),
    prevent_initial_call=True
)
def make_game(n_clicks, selected_players):
    if n_clicks > 0:
        random.shuffle(selected_players)
        num_players = len(selected_players)
        half = num_players // 2

        # If there's an odd number of players, randomly add the extra player to 'long' or 'islands'
        if num_players % 2 == 1:
            extra = random.choice([0, 1])
            half += extra

        team_long = selected_players[:half]
        team_islands = selected_players[half:]

        return [team_long, team_islands]
@app.callback(
    Output('teams-display', 'children'),
    Input('team', 'data'),
    prevent_initial_call=True
)
def display_teams(teams):
    if teams == None:
        dash.no_update
    else:
        team_long = teams[0]
        team_islands = teams[1]
        if team_long and team_islands:
            return html.Div([
                html.H2('Long:'),
                html.P(', '.join(team_long)),
                html.H2('Islands:'),
                html.P(', '.join(team_islands)),
            ])
        else:
            return None

# Callbacks for the team win buttons click event
@app.callback(
    Output('island-team-win', 'data'),
    Input('island-wins-button', 'n_clicks'),
    State('island-team-win', 'data'),
    State('team', 'data'),
    prevent_initial_call=True
)
def team_wins(n_clicks_island, island_wins,teams):
    if island_wins == None:
        island_wins = 0
    island_wins += 1
    add_team_score(1, teams)
    add_side_score(1)

    return island_wins

@app.callback(
    Output('long-team-win', 'data'),
    Input('long-wins-button', 'n_clicks'),
    State('long-team-win', 'data'),
    State('team', 'data'),
    prevent_initial_call=True
)
def team_wins(n_clicks_long, long_wins,teams):
    if long_wins == None:
        long_wins = 0
    #print(n_clicks_long)
    add_side_score(0)
    add_team_score(0, teams)

    long_wins += 1
    return long_wins


@app.callback(
    Output('scoreboard', 'children'),
    Input('team', 'data'),
    State('long-team-win', 'data'),
    State('island-team-win', 'data'),
    prevent_initial_call=True
)
def display_teams(teams,init_long, init_island):
    if teams is None:
        return dash.no_update
    else:
        # Load the data from the JSON file
        data = load_data('nerffight.json')

        # Create a list to hold the scoreboard children
        children = []

        # Add a header to the scoreboard
        children.append(html.H2('Scoreboard'))

        # Add player scores to the scoreboard
        for player, player_data in data['players'].items():
            children.append(html.P(f"{player}: {player_data['games_won']} wins"))

        # Add side scores to the scoreboard
        for side, side_data in data['side'].items():
            children.append(html.P(f"{side.capitalize()}: {side_data['side_win']} wins"))

        return children
    

@app.callback(
    Output('win-histogram', 'figure'),
    Input('team', 'data'),  # Trigger the callback whenever the team data is updated
    prevent_initial_call=True
)
def update_histogram(teams):
    if teams is None:
        return dash.no_update
    else:
        # Load the data from the JSON file
        data = load_data('nerffight.json')

        # Create a list of player names and their number of wins
        player_names = list(data['players'].keys())
        player_wins = [player_data['games_won'] for player_data in data['players'].values()]

        # Create a histogram using Plotly
        figure = {
            'data': [{
                'type': 'bar',
                'x': player_names,
                'y': player_wins,
            }],
            'layout': {
                'title': 'Player Wins',
                'xaxis': {'title': 'Player'},
                'yaxis': {'title': 'Wins'},
            },
        }

        return figure
    
@app.callback(
    Output('game-history-graph', 'figure'),
    Input('team', 'data'),  # Trigger the callback whenever the team data is updated
    prevent_initial_call=True
)
def update_game_history_graph(teams):
    if teams is None:
        return dash.no_update
    else:
        # Load the data from the JSON file
        data = load_data('nerffight.json')

        # Create a trace for each side
        traces = []
        for side, side_data in data['side'].items():
            # Calculate the cumulative win count
            win_count = np.cumsum(side_data['side_history'])

            # Create a trace for this side
            trace = {
                'type': 'scatter',
                'x': list(range(1, len(win_count) + 1)),
                'y': win_count.tolist(),
                'name': side,
            }
            traces.append(trace)

        # Create the figure using Plotly
        figure = {
            'data': traces,
            'layout': {
                'title': 'Game History',
                'xaxis': {'title': 'Game Count'},
                'yaxis': {'title': 'Cumulative Wins'},
            },
        }

        return figure

# Run the application
if __name__ == '__main__':
    app.run_server(debug=True, port=8060)
