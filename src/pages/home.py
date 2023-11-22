import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/', title='Home - Demographs')


reset_button = dbc.Button("Rimuovi tutti i file caricati", id='btn_rimuovi_file_caricati', outline=True, color="danger", className="btn_cb me-1")


welcome_text = html.Div(id="welcome-text", style={'display': 'block'}, children=[
                    html.P(["Hai dei report demografici di crowdsourcing da analizzare? Sei nel posto giusto!"]),
                    html.P(["Carica su Demographs i report demografici esportati da Prolific ed Amazon Mechanical Turk, e lui li analizzerà per te creando statistiche e visualizzazioni!"]),
                    html.P(["Se non hai un report demografico a portata di mano, uso quello di prova: ", html.A("test-data.csv", id="text-download-test-data", className="download_text", n_clicks=0)]),
                    html.P(["Nota: la piattaforma non tiene traccia dei file salvati, né dei dati in essi contenuti."], id="note-data-not-saved"),
                ])

welcome_msg = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Benvenuto in Demographs"), close_button=True),
                dbc.ModalBody(
                    welcome_text
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Ok, iniziamo!",
                        id="btn-close-welcome-msg",
                        className="ms-auto",
                        n_clicks=0,
                    )
                ),
            ],
            id="welcome-msg",
            is_open=False,
            backdrop="static",
            size='lg'
        ),
    ]
)



instructions = html.Div(id="instructions", style={'display': 'block'}, children=[
                    html.P(["Per iniziare, carica uno o più file esportati dalla piattaforma di crowdsourcing con il quale hai svolto dei task, ad esempio Prolific o Amazon Mechanical Turk."]),
                    html.P(["Una volta caricati i file, è possibile visualizzarne il contenuto o eventualmente rimuoverli. Infine, puoi passare alla fase di analisi."]),
                ])




# PAGINA PRINCIPALE DI UPLOAD

layout = html.Div([
                welcome_msg,
                instructions,
                dcc.Upload(
                    id='upload-data',
                    children=html.Div(id='upload-area',
                                      children = [
                                        html.A([
                                            html.I(id='add-file-icon', className='icon fa-solid fa-circle-plus fa-2xl'),
                                            html.Span('Aggiungi file',id='drop-title')
                                        ])
                    ]),
                    multiple=True
                ),
                html.Div(id="uploaded-files-general-btn-section", style={'display':'none'}, children=[
                    html.Span(id="total-uploaded-files-text", children=["Totale file caricati: "]),
                    dcc.Link(dbc.Button('Analizza dati', id='btn_analizza_dati', outline=True, color="primary", className="btn_cb me-1"), href='/analytics'),
                    reset_button
                ]),
                html.Div(id="alerts-container"),
                html.Div(id='output-data-upload'),

            ])