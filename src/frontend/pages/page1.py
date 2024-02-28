import dash
from dash import html, dcc, Input, Output, callback
import dash_mantine_components as dmc

dash.register_page(__name__,
                   path="/page1")



layout = dmc.Container(
    children=[
        dmc.Grid(
            dmc.Col(
                children=[
                    html.H1("Add Player", id='Page1-title',className='titles'),
                    dmc.Col(
                        children=[
                            dcc.Input(
                                id='Add_player_bar',
                                placeholder='Add player name'
                            ),
                            dmc.Button("Submit", id="submit-player-btn", variant="filled")
                        ]
                    
                    ),
                    dmc.Col(
                        id="page1-names",
                    ),        
                ],
                id='Title-button-col-page1',
                className= "side-margin page1-width", 
            )
        )
    ], p=0, m=0, className='page-container'
)

