import json
import time
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, ALL, Patch, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from upload import *
import upload_ui
from analyzer import Analyzer
from provenience_resolution import ProvenienceResolutor
from normalizer_factory import NormalizerFactory
from visualizer import Visualizer
from upload_errors import *


external_stylesheets = [dbc.icons.FONT_AWESOME]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, use_pages=True,
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}]
                )

server = app.server


# PAGINA PRINCIPALE

app.layout = html.Div([
                dcc.Store(id='alert-to-show'),
                dcc.Store(id='client-data', data={'uploader':Uploader().serialize(), 'analyzer':Analyzer().serialize()}),
                dcc.Store(id='client-data-tmp-1', data={'uploader':Uploader().serialize(), 'analyzer':Analyzer().serialize()}),
                dcc.Store(id='client-data-tmp-2', data={'uploader':Uploader().serialize(), 'analyzer':Analyzer().serialize()}),
                dcc.Store(id="client-options", data={'first-visit':True}, storage_type='local'),
                dcc.Download(id="download-data"),
                html.Div(
                    id='header',
                    children = [
                        html.H1(id='main-title-1', className='main-title', children='Demo'),
                        html.H1(id='main-title-2', className='main-title', children='graphs'),
                    ]
                ),
                dcc.Location(id='url', refresh=False),
                html.Div(id = 'page-content',
                    children =[
                        dash.page_container
                    ])
])



#uploader = Uploader()
#analyzer = Analyzer()





# Analisi dati: cambio url

@app.callback(
    Output('client-data-tmp-1', 'data'),
    [Input('url', 'pathname')], State('client-data','data')
)
def update_client_data(pathname, client_data):
    analyzer = Analyzer.deserialize(client_data['analyzer'])
    if analyzer is not None:
        if pathname != '/analytics':
            analyzer.clear()
        client_data['analyzer'] = analyzer.serialize()
        return client_data
    return dash.no_update

@app.callback(
    Output('graphs_container', 'children'),
    [Input('url', 'pathname')], State('client-data','data')
)
def update_graphs(pathname, client_data):
    if pathname != '/analytics':
        raise PreventUpdate
    analyzer = Analyzer.deserialize(client_data['analyzer'])
    uploader = Uploader.deserialize(client_data['uploader'])
    if analyzer is not None:
        analyzer.load_data(uploader.get_merged_data(), uploader.get_generic_metadata())
        analyzer.create_all_graphs()
        graphs = analyzer.get_visualizations()
        metadata = analyzer.get_formatted_metadata()
        summary = analyzer.generate_data_summary()
        return Visualizer.create_complex_vis(graphs, metadata, summary)

    raise PreventUpdate




# Upload e rimozione dei file

@app.callback(Output('output-data-upload', 'children'),
              Output('alert-to-show', 'data'),
              Output('upload-data', 'contents'),
              Output('client-data-tmp-2','data'),
              Input('upload-data', 'contents'), State('upload-data', 'filename'), Input('btn_rimuovi_file_caricati', 'n_clicks'),
              Input({"type": "btn-remove-file", "index": ALL}, 'n_clicks'), State({"type": "card-filename-title", "index": ALL},'children'), State('client-data','data'),
              prevent_initial_call=False)
def update_output(list_of_contents, list_of_names, n_clicks_btn_rimuovi_file_caricati, n_clicks_remove_btn, filenames, client_data):
    
    analyzer = Analyzer.deserialize(client_data['analyzer'])
    uploader = Uploader.deserialize(client_data['uploader'])

    alert_msg = []
    UPLOAD_DATA_CONTENTS = None                # x reset del contenuto di dcc.Upload
    
    if is_triggered('btn_rimuovi_file_caricati'):
        uploader.clear()
        analyzer.clear()
        patched_list = Patch()
        patched_list.clear()
        alert_msg = create_info_msg("Tutti i file sono stati rimossi.")
        alert_msg = json.dumps(alert_msg)
        updata_client_data(client_data,uploader,analyzer)
        return patched_list, alert_msg, UPLOAD_DATA_CONTENTS, client_data
    elif is_triggered('upload-data') and list_of_contents is not None:
        output_data_upload = None
        saved_files_filenames,not_saved_files_info = save_uploaded_data(list_of_contents, list_of_names, uploader)
        if saved_files_filenames:         # verifica se almeno un file è stato caricato con successo
            alert_msg += (create_successful_upload_msg(saved_files_filenames))         
        if uploader.has_data():
            uploaded_data = uploader.get_data_from_filenames(saved_files_filenames)
            output_data_upload = upload_ui.generate_patched_output(uploaded_data)
        if not_saved_files_info:
            alert_msg = alert_msg+(create_upload_error_msg(not_saved_files_info))
        alert_msg = json.dumps(alert_msg)
        updata_client_data(client_data,uploader,analyzer)
        return output_data_upload, alert_msg, UPLOAD_DATA_CONTENTS, client_data       # aggiunge solo i dati nuovi
    elif is_triggered('btn-remove-file'):
        patched_list = Patch()
        values_to_remove = []
        for i, val in enumerate(n_clicks_remove_btn):
            if val>0:
                values_to_remove.insert(0, i)
                uploader.delete_file_data(filenames[i])
                msg = create_info_msg(f"Il file {filenames[i]} è stato rimosso.")
                alert_msg = json.dumps(msg)
        for v in values_to_remove:
            del patched_list[v]
        updata_client_data(client_data,uploader,analyzer)
        return patched_list, alert_msg, UPLOAD_DATA_CONTENTS, client_data
    else:           # per aggiornamento/raggiungimento pagina
        if uploader.has_data():
            updata_client_data(client_data,uploader,analyzer)
            return upload_ui.generate_output(uploader.get_all_data(),[]), alert_msg, UPLOAD_DATA_CONTENTS, client_data # rigenera tutti i dati
    updata_client_data(client_data,uploader,analyzer)
    return None, alert_msg, UPLOAD_DATA_CONTENTS, client_data

@staticmethod
def is_triggered(id):
    return id in dash.callback_context.triggered[0]['prop_id'].split('.')[0]

@staticmethod
def updata_client_data(client_data,uploader,analyzer):
    client_data['uploader'] = uploader.serialize()
    client_data['analyzer'] = analyzer.serialize()




@app.callback(
    Output('client-data', 'data'),
    [Input('client-data-tmp-1', 'data'),
     Input('client-data-tmp-2', 'data')],
    [State('client-data', 'data')], prevent_initial_call=True
)
def update_store(client_data_tmp_1, client_data_tmp_2, client_data):
    triggered_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'client-data-tmp-1' and client_data_tmp_1:
        client_data['uploader'],client_data['analyzer'] = client_data_tmp_1['uploader'],client_data_tmp_1['analyzer']
    elif triggered_id == 'client-data-tmp-2' and client_data_tmp_2:
        client_data['uploader'],client_data['analyzer'] = client_data_tmp_2['uploader'],client_data_tmp_2['analyzer']
    else:
        raise PreventUpdate

    return client_data






def create_upload_error_msg(not_saved_files_info):
    msgs = []
    unsupported_files = [e.filename for e in not_saved_files_info if isinstance(e, FiletypeNotSupportedError)]
    duplicate_files = [e.filename for e in not_saved_files_info if isinstance(e, DuplicatedFileError)]
    unknown_platform_files = [e.filename for e in not_saved_files_info if isinstance(e, PlatformNotSupportedError)]
    undetected_error_files = [e.filename for e in not_saved_files_info if isinstance(e, GenericFileUploadError)]

    if unsupported_files:
        unsupported_file_count = len(unsupported_files)
        msgs.append(f"{unsupported_file_count} file non supportat{'o' if unsupported_file_count == 1 else 'i'}: {', '.join(unsupported_files)}.")

    if duplicate_files:
        duplicate_file_count = len(duplicate_files)
        msgs.append(f"{duplicate_file_count} file già present{'e' if duplicate_file_count == 1 else 'i'}: {', '.join(duplicate_files)}.")

    if unknown_platform_files:
        unknown_platform_file_count = len(unknown_platform_files)
        msgs.append(f"{unknown_platform_file_count} file con piattaforma di origine non rilevata: {', '.join(unknown_platform_files)}.")

    if undetected_error_files:
        undetected_error_files_count = len(undetected_error_files)
        msgs.append(f"{undetected_error_files_count} file non caricat{'o' if undetected_error_files_count == 1 else 'i'} a causa di errori nella lettura del file: {', '.join(undetected_error_files)}.")

    return [{"type": "error", "message": msg} for msg in msgs]


def create_info_msg(msg):
    return [{"type": "info", "message": msg}]

def create_success_msg(msg):
    return [{"type": "success", "message": msg}]


def create_successful_upload_msg(saved_filenames):
    if len(saved_filenames) > 1:
        msg = f"{len(saved_filenames)} file caricati con successo."
    else:
        msg = f"File {saved_filenames[0]} caricato con successo."

    return create_success_msg(msg)



# Visibilità btn analisi e rimozione di tutti i file

@app.callback(
    Output('uploaded-files-general-btn-section','style'),
    [Input('output-data-upload', 'children'), Input('btn_rimuovi_file_caricati', 'n_clicks')],
    [State('uploaded-files-general-btn-section', 'style')], Input({"type":"btn-remove-file","index":ALL},"n_clicks"), Input('client-data','data')
)
def change_btn_section_visibility(trigger_1, trigger_2, btn_section_style, remove_file_clicks, client_data):
    uploader = Uploader.deserialize(client_data['uploader'])
    if uploader.has_data():
        btn_section_style['display'] = 'block'
    else:
        btn_section_style['display'] = 'none'
    return btn_section_style



# Aggiornamento numero di file caricati

@app.callback(
        Output('total-uploaded-files-text','children'),
        Input('output-data-upload','children'), Input('client-data','data')
)
def update_uploaded_files_number(input,client_data):
    uploader = Uploader.deserialize(client_data['uploader'])
    text = 'Totale file caricati: '
    n_of_files = uploader.get_uploaded_files_number()
    return text+str(n_of_files)



@staticmethod
def save_uploaded_data(list_of_contents, list_of_names, uploader):
    "dati dei file, salva quelli idonei e ne restituisce la lista dei nomi"
    saved_files_filenames = []
    not_saved_files_info = []
    for file, filename in zip(list_of_contents, list_of_names):
        try:
            try:
                currently_stored_filenames = uploader.get_filenames()
                if filename in currently_stored_filenames:
                    raise DuplicatedFileError(f"File già presente",filename)
                df = uploader.get_df_from_file(file, filename)
                supported, origin_platform = ProvenienceResolutor.isSupported(df)
                if not supported:
                    raise PlatformNotSupportedError(f"Piattaforma non supportata",filename)
                normalizer = NormalizerFactory.create_normalizer(df,origin_platform)
                normalized_df = normalizer.normalize()
                uploader.save(normalized_df, filename, origin_platform)
                saved_files_filenames.append(filename)
            except (FiletypeNotSupportedError, DuplicatedFileError, PlatformNotSupportedError) as e:
                not_saved_files_info.append(e)
            except:
                raise GenericFileUploadError("Errore generico di caricamento file", filename)
        except GenericFileUploadError as e:
            not_saved_files_info.append(e)
    return saved_files_filenames, not_saved_files_info



# Visualizzazione notifiche

@app.callback(
    Output("alerts-container", "children"),
    Input({"type":"btn-remove-file","index":ALL}, "n_clicks"),
    Input("alert-to-show", "data"),
    State("alerts-container", "children"),
)
def show_alert(n, msgs_json, alerts):
    if n is None or msgs_json == '' or msgs_json == []:
        return alerts
    new_alerts = []
    msg_data = json.loads(msgs_json)
    if not isinstance(msg_data, list):
        msg_data = [msg_data]
    for msg in msg_data:
        msg_type = msg.get("type", "info")
        msg_content = msg.get("message", "")
        new_alerts.append(create_alert(msg_content, msg_type))
    return new_alerts + (alerts if alerts else [])

def create_alert(msg,alert_type="info"):
    timestamp = int(time.time() * 1000)
    color_map = {
        "error": "danger",
        "success": "success",
        "info": "info"
    }
    color = color_map.get(alert_type)
    return dbc.Alert(msg, className= 'alert', id=f"alert-{timestamp}", is_open=True, duration=6000, color=color, dismissable=True)



# Messaggio di benvenuto

@app.callback(
    Output("welcome-msg", "is_open"), Output("client-options", "data"),
    [Input("btn-close-welcome-msg", "n_clicks"), State("client-options", "data")],
)
def toggle_welcome_msg(n1, client_options):
    patched_options = Patch()
    patched_options["first-visit"] = False
    if client_options["first-visit"] and not n1:
        return True, patched_options
    return False, patched_options



# Scaricamento file di prova

@app.callback(
    Output("download-data", "data"),
    Input("text-download-test-data", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    if n_clicks > 0:
        return dcc.send_file(
            "data/test_data.csv"
        )



if __name__ == '__main__':
    app.run_server(debug=False)
    