import dash
from dash import html, dcc, Input, Output, callback
import dash_mantine_components as dmc


dash.register_page(__name__,
                   path="/")

layout = dmc.Container([
    dmc.Grid(
        children=[
            dmc.Col(
                html.Div([
                    html.Header([
                        dcc.Link(html.Img(src='assets/media/forstaLogo.png'), href='/')
                    ]),
                    html.Div([
                        
                        html.Div([
                                    dcc.Link([html.Img(src='assets/media/logo.png')], href='/page1', className='minerLink'),
                                    html.P('Consept Miner', className='logoText')
                                ], className='logoBox'),
  
                    ], className='logoSpace'),
                ])
            )
        ]
    )
], p=0, m=0, fluid=True, className='Home')