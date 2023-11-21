from dash import html, Patch
import dash_table
import dash_bootstrap_components as dbc
from dash import html



btn_remove_file_id_counter = 0



def generate_patched_output(uploaded_data):
    return generate_output(uploaded_data,output_container=Patch())


def generate_output(uploaded_data,output_container):
    for obj in uploaded_data:
        output_container.append(create_file_card(obj["filename"],obj["dataframe"],obj["platform"]))
    return output_container


def create_file_card(filename,dataframe,platform):

    global btn_remove_file_id_counter
    btn_remove_file_id_counter += 1

    return  html.Div(id={"type": "card-btn-remove-file", "index":btn_remove_file_id_counter},
        children = dbc.Card([
                dbc.CardHeader(html.H5(filename,id={"type": "card-filename-title", "index":btn_remove_file_id_counter})),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.P(f'Numero di righe: {len(dataframe)}'),
                            html.P(f'Piattaforma rilevata: {platform}'),
                        ], width=4),
                        dbc.Col([
                            dash_table.DataTable(
                                id='table',
                                columns=[{'name': i, 'id': i} for i in dataframe.columns],
                                data=dataframe.to_dict('records'),
                                style_table={'className':'uploaded_data_table'}
                            )
                        ], width=8)
                    ]),
                    html.Div(
                        className="remove-file-btn-container",
                        children=[
                        dbc.Button(
                            html.Img(src="assets/img/bin_black.png", title= "Rimuovi file", alt="Rimuovi file", className="icon"), id={"type": "btn-remove-file", "index":btn_remove_file_id_counter}, outline=True, color="danger", className="me-1 btn-remove-file", n_clicks=0
                        )
                    ])
                ])

            ], body=True))