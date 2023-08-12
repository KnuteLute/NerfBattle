from dash import Dash, html, dcc, Input, Output, State, callback, ALL, ctx
import dash
import random
import os
import json
import dash_mantine_components as dmc
import numpy as np
import time
from plotly.subplots import make_subplots
import plotly.graph_objects as go

filename = 'nerffight.json'


def load_data(filename):
    try:
        with open('nerffight.json', 'r') as f:
            data = json.load(f)
            if 'side' not in data or 'players' not in data:
                time.sleep(1)
                
                load_data(filename)
    except json.JSONDecodeError:
        data = {}  # or set to a default value
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
    if side == 0:  # long
        data['side']['long']['side_history'].append(1)
        wins = data['side']['long']['side_win']
        data['side']['long']['side_win'] = wins + 1
        data['side']['islands']['side_history'].append(0)

    elif side == 1:  # Island
        data['side']['islands']['side_history'].append(1)
        wins = data['side']['islands']['side_win']
        data['side']['islands']['side_win'] = wins + 1
        data['side']['long']['side_history'].append(0)

    save_data('nerffight.json', data)


def add_team_score(side, team):
    data = load_data('nerffight.json')
    long = team[0]
    island = team[1]
    data['game']['game'] += 1
    game = data['game']['game']

    for player in data['players']:
        if player in long:  # player is in long
            if side == 0:  # player is in long and long has won
                data['players'][player]['games_played'] += 1
                data['players'][player]['games_won'] += 1
                data['players'][player]['game_history'].append([0, game])
            else:  # player is in long and long lost
                data['players'][player]['games_played'] += 1
                data['players'][player]['game_history'].append([1, game])

        elif player in island:
            if side == 1:  # player is in island and island won
                data['players'][player]['games_played'] += 1
                data['players'][player]['games_won'] += 1
                data['players'][player]['game_history'].append([2, game])
            else:  # player is in long and long lost
                data['players'][player]['games_played'] += 1
                data['players'][player]['game_history'].append([3, game])

    save_data('nerffight.json', data)


def load_guns():
    data = load_data('nerffight.json')
    guns = []
    for gun in data['guns']:
        guns.append(gun)

    return guns


def give_player_gun(player_gun):
    # player_gun is a list where everyother element is either a player or a gun. # ex: [player, gun, player, gun]
    data = load_data('nerffight.json')
    increment = 1
    while increment/2 <= len(player_gun)/2:
        for player in data['players']:
            if player == player_gun[increment-1]:
                player_data = data['players'][player]
                game_number = data['game']['game']
                gun_info = data['guns'][player_gun[increment]]
                if 'game_gun' not in player_data:
                    player_data['game_gun'] = []
                
                player_data['game_gun'].append({'gun_name' : [player_gun[increment]], 'gun': gun_info, 'game': game_number})
                save_data('nerffight.json', data)
        increment += 2
        


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
app.layout = html.Div(
    children=[
        dmc.Grid([
            dmc.Col([                
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
                dmc.Grid([
                    dmc.Col(
                        children=[
                            dmc.Button('MakeGame', id='make-game-button',style={'background-color': 'green', 'color': 'white'}),
                        ], span=3,
                    ),
                    dmc.Col(
                        children=[
                            dmc.Button('Filp Side', id='flip-side-button',style={'background-color': 'orange', 'color': 'white'}),
                        ],
                        span=6,
                    ),
                    dmc.Col(
                        children=[
                            html.Div(id='teams-display'),
                        ],
                        span=12,
                    ),
                    dmc.Col(
                        children=[
                            dmc.Button('Island Wins', id='island-wins-button',style={'background-color': 'orange', 'color': 'white'}),
                            dmc.Button('Long Wins', id='long-wins-button',style={'background-color': 'blue', 'color': 'white'}),
                        ],
                        id='winning-button'
                    ),
                ]),
            ],span=6),
            dmc.Col([
                # Div for displaying the teams
                dmc.Grid([
                    dmc.Col(
                        children=[

                        ], span=6,
                        id='scoreboard'
                    ),
                    dmc.Col(
                        children=[

                        ],
                        id='gun_choice',
                        span=6,
                    ),
                    

                ]),
            ],span=6),

            dmc.Col([
                # Column for the game history graph

                dmc.Grid([
                    dmc.Col(
                        children=[
                            dcc.Graph(id='win-histogram'),
                        ], span=12,
                    ),
                    dmc.Col(
                        children=[
                            dcc.Graph(id='player_donut-chart'),
                        ], span=12,
                        style={
                            'margin-bottom': '0px',
                        }  # Adjust the value as needed
                    ),
                    dmc.Col(
                        children=[
                            dcc.Graph(id='player_side_donut-chart'),
                        ], span=12,
                        style={
                            'margin-top': '0px',
                        }  # Adjust the value as needed
                    ),
                    # Column for the game history graph
                    dmc.Col([
                        dcc.Graph(id='game-history-graph'),
                    ], span=6),  # Set the width to 6 (out of 12) for a 50% width column

                    # Column for the donut chart
                    dmc.Col([
                        dcc.Graph(id='donut-chart'),
                    ], span=6),  # Set the width to 6 (out of 12) for a 50% width column
                    dmc.Col(
                        children=[

                        ], id='dummy-output'
                    )
                ]),  # Set the width to 6 (out of 12) for a 50% width column
            ],span=12),
            
            # Buttons for team wins

            dcc.Store(id='team', storage_type='session'),
            dcc.Store(id='island-team-win', storage_type='session'),
            dcc.Store(id='long-team-win', storage_type='session'),
        ])
    ],
    style={
        "background-color": "lightblue",
        "margin-left" : "0px",
        "margin-right" : "0px",
        "border-left" : "0px",
        "border-right" : "0px",
    }
)


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
            return [{'label': i, 'value': i} for i in data['players'].keys()]
        else:
            add_player(data, player_name)
            save_data('nerffight.json', data)
            return [{'label': i, 'value': i} for i in data['players'].keys()]


# Callback for the 'Make Game' button click event
@app.callback(
    Output('team', 'data'),
    Input('make-game-button', 'n_clicks'),
    Input('flip-side-button','n_clicks'),
    State('player-dropdown', 'value'),
    prevent_initial_call=True
)
def make_game(make_game, flip_side, selected_players):
    button_id = ctx.triggered_id if not None else 'No clicks yet'
    if button_id == "make-game-button":
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

    if button_id == "flip-side-button":

        team_long = []
        team_islands = []

        data = load_data('nerffight.json')
        target_game = data['game']['game']
        players_in_target_game = []
        players_side_in_game = []
        for player, player_data in data['players'].items():
            for game_history in player_data['game_history']:
                if game_history[-1] == target_game:
                    players_in_target_game.append(player)
                    players_side_in_game.append(player_data['game_history'][-1][0])
                    break 
        
        for player, side in zip(players_in_target_game, players_side_in_game):
            
            if side == 0 or side == 1:
                team_islands.append(player)
            else:
                team_long.append(player)

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
                html.H1('Long:', style={'color': 'blue'}),
                html.H2(', '.join(team_long), style={'color': 'blue'}),
                html.H1('Islands:', style={'color': 'orange'}),
                html.H2(', '.join(team_islands),style={'color': 'orange'}),
            ])
        else:
            return None


# Callbacks for the team win buttons click event
@app.callback(
    Output('island-team-win', 'data'),
    Input('island-wins-button', 'n_clicks'),
    State('island-team-win', 'data'),
    State('team', 'data'),
    State('dummy-output', 'data'),
    prevent_initial_call=True
)
def team_wins(n_clicks_island, island_wins, teams, player_gun):
    if island_wins == None:
        island_wins = 0
    island_wins += 1
    add_team_score(1, teams)
    add_side_score(1)
    give_player_gun(player_gun)

    return island_wins


@app.callback(
    Output('long-team-win', 'data'),
    Input('long-wins-button', 'n_clicks'),
    State('long-team-win', 'data'),
    State('team', 'data'),
    State('dummy-output', 'data'),
    prevent_initial_call=True
)
def team_wins(n_clicks_long, long_wins, teams, player_gun):
    if long_wins == None:
        long_wins = 0
    add_side_score(0)
    add_team_score(0, teams)
    give_player_gun(player_gun)

    long_wins += 1
    return long_wins


@app.callback(
    Output('scoreboard', 'children'),
    Input('team', 'data'),
    Input('island-wins-button', 'n_clicks'),
    Input('long-wins-button', 'n_clicks'),
    State('long-team-win', 'data'),
    State('island-team-win', 'data'),
    prevent_initial_call=True
)
def display_teams(teams, islandclick, longclick, init_long, init_island):
    if teams is None:
        return dash.no_update
    else:
        # Load the data from the JSON file
        time.sleep(0.2)
        data = load_data('nerffight.json')

        # Create a list to hold the scoreboard children
        children = []

        # Add a header to the scoreboard
        children.append(html.H2('Scoreboard'))

        # Add player scores to the scoreboard
        for player, player_data in data['players'].items():
            children.append(html.P(f"{player}: {player_data['games_won']} wins", style={'margin': '1px'}))

        # Add side scores to the scoreboard
        for side, side_data in data['side'].items():
            children.append(html.P(f"{side.capitalize()}: {side_data['side_win']} wins", style={'margin': '1px'}))

        return children


@app.callback(
    Output('win-histogram', 'figure'),
    Input('team', 'data'),  # Trigger the callback whenever the team data is updated
    Input('island-wins-button', 'n_clicks'),
    Input('long-wins-button', 'n_clicks'),
    prevent_initial_call=True
)
def update_histogram(teams, islandclikc, longclick):
    if teams is None:
        return dash.no_update
    else:
        # Load the data from the JSON file
        time.sleep(0.2)
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
    Input('island-wins-button', 'n_clicks'),
    Input('long-wins-button', 'n_clicks'),
    prevent_initial_call=True
)
def update_game_history_graph(teams, islandclick, longclick):
    if teams is None:
        return dash.no_update
    else:
        # Load the data from the JSON file
        time.sleep(0.2)
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


# Callback for updating the donut chart
@app.callback(
    Output('donut-chart', 'figure'),
    Input('team', 'data'),  # Trigger the callback whenever the team data is updated
    Input('island-wins-button', 'n_clicks'),
    Input('long-wins-button', 'n_clicks'),
    prevent_initial_call=True
)
def update_donut_chart(teams, islandclikc, longclick):
    if teams is None:
        return dash.no_update
    else:
        # Load the data from the JSON file
        time.sleep(0.2)
        data = load_data('nerffight.json')

        # Create a list of side names and their number of wins
        side_names = list(data['side'].keys())
        side_wins = [side_data['side_win'] for side_data in data['side'].values()]

        # Create a donut chart using Plotly
        figure = {
            'data': [{
                'type': 'pie',
                'labels': side_names,
                'values': side_wins,
                'hole': .4,  # This creates the hole in the middle of the pie chart
            }],
            'layout': {
                'title': 'Side Wins',
            },
        }

        return figure


@callback(
    Output('gun_choice', 'children'),
    Input('team', 'data'),
)
def guns_for_players(team):
    # Load the data from the JSON file
    data = load_data('nerffight.json')
    players = []
    for sides in team:
        for player in sides:
            players.append(player)

    # Define the list of guns
    guns = load_guns()
    # Generate a dropdown for each player
    player_dropdowns = []
    for player in players:
        dropdown = dmc.Select(
            label=player,
            placeholder="Select a gun",
            id={'type': 'player-gun-dropdown', 'index': player},
            data=[{'value': gun, 'label': gun} for gun in guns],
            style={"width": 200, "marginBottom": 10},
        )
        player_dropdowns.append(dropdown)

    # Create the layout with these dropdowns
    layout = html.Div(player_dropdowns)

    return layout


@app.callback(
    Output('dummy-output', 'data'),
    [
        Input({'type': 'player-gun-dropdown', 'index': ALL}, 'value'),
        State('team', 'data'),
    ],
    prevent_initial_call=True
)
def update_player_guns(gun_values, team):
    # Load the data from the JSON file
    data = load_data('nerffight.json')
    players = []
    for sides in team:
        for player in sides:
            players.append(player)

    player_guns = []
    for player, gun in zip(players, gun_values):
        if gun:
            player_guns.append(player)
            player_guns.append(gun)
    return player_guns


@app.callback(
    Output('player_donut-chart', 'figure'),
    Input('team', 'data'),  # Trigger the callback whenever the team data is updated
    Input('island-wins-button', 'n_clicks'),
    Input('long-wins-button', 'n_clicks'),
    prevent_initial_call=True
)
def update_player_donut_chart(teams, islandclikc, longclick):
    if teams is None:
        return dash.no_update
    else:
        # Load the data from the JSON file
        time.sleep(0.2)
        data = load_data('nerffight.json')
        players = data['players'].keys()
        players = list(players)
        player_amount = len(players)
        print('player amount',player_amount)
        print((players))
        fig = make_subplots(rows=1, cols=player_amount, subplot_titles=players, specs=[[{'type': 'domain'}]*player_amount])
        for i, player in enumerate(players, start=1):
            wins = data['players'][player]['games_won']
            losses = data['players'][player]['games_played'] - wins
            values = [wins, losses]
            
            # Define colors for wins and losses
            colors = ['green', 'red']

            fig.add_trace(go.Pie(labels=['Wins','Loss'], values=values, marker=dict(colors=colors)), row=1, col=i)
        
        fig.update_layout(height=300)
        return fig


@app.callback(
    Output('player_side_donut-chart', 'figure'),
    Input('team', 'data'),  # Trigger the callback whenever the team data is updated
    Input('island-wins-button', 'n_clicks'),
    Input('long-wins-button', 'n_clicks'),
    prevent_initial_call=True
)
def update_player_side_donut_chart(teams, islandclikc, longclick):
    if teams is None:
        return dash.no_update
    else:
        # Load the data from the JSON file
        time.sleep(0.2)
        data = load_data('nerffight.json')
        players = data['players'].keys()
        players = list(players)
        player_amount = len(players)
        print('player amount',player_amount)
        print((players))
        subplot_titles = []

        for player in players:
            subplot_titles.append('')
            subplot_titles.append(player)
            

        fig = make_subplots(rows=1, cols=player_amount*2, subplot_titles=subplot_titles, specs=[[{'type': 'domain'}]*player_amount*2])
        for i, player in enumerate(players, start=1):
            long = 0
            long_loss = 0
            islands = 0
            island_loss = 0
            for score, game in data['players'][player]['game_history']:
                if score == 0:
                    long += 1
                if score == 1:
                    long_loss += 1
                if score == 2:
                    islands += 1
                if score == 3:
                    island_loss += 1
                i
            values = [long, long_loss]
            # Define colors for wins and losses
            colors = ['green', 'red']
            fig.add_trace(go.Pie(labels=['LongWin','LongLoss'], values=values, marker=dict(colors=colors)), row=1, col=i+i-1)
            values = [islands, island_loss]
            # Define colors for wins and losses
            colors = ['yellow', 'purple']
            fig.add_trace(go.Pie(labels=['IslandsWin','IslandsLoss'], values=values, marker=dict(colors=colors)), row=1, col=i+i)
            
        fig.update_layout(height=400)
        return fig

# Run the application
if __name__ == '__main__':
    app.run_server(debug=True, port=8070)