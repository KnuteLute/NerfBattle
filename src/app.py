from dash import Dash, html, dcc, Input, Output, callback
import dash
import dash_mantine_components as dmc
#import dash_bootstrap_components as dbc
import os

import backend.AppCallback, backend.PageOneCallback
assets_path = os.getcwd() + 'assets'

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True, pages_folder="frontend/pages", assets_folder=assets_path)


app.layout = html.Div([dash.page_container,
                       dcc.Location(id="url", refresh=True),
                      ]
                      )


if __name__ == "__main__":
    app.run_server(debug=True, port=8050)

    
