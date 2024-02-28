from dash import html, dcc
import dash_mantine_components as dmc

def create_page3_layout():
    return html.Div([
        dcc.Link(dmc.Button("Back to Home", variant="outline"), href="/"),
        html.Br(),  # Adds a line break for spacing
        dmc.Paper([
            dmc.Title("Page 3"),
            dmc.Text("This is the content of Page 3."),
            # Add more components specific to Page 1 here
        ], style={'padding': '20px'})
    ])