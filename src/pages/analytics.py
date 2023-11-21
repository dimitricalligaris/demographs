import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, title='Analytics - Demographs')

# PAGINA DASHBOARD DI ANALISI

layout = html.Div(
                        children=[
                            dcc.Loading(
                                html.Div(id='graphs_container',children=[html.P('Nessun dato visualizzabile', id='no-data-text')]),
                                type='dot'
                            ),
                            html.Br(),
                            dcc.Link(dbc.Button(
                                children=[
                                    html.I(id='back-to-upload-icon', className='fa-solid fa-angles-left'),
                                    html.Span('Torna all\'upload')],
                                id='btn_torna_alla_home', outline=True, color="primary", className='btn_cb me-1'), href='/'),
                        ]
                    )
