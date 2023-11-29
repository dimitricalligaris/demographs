import base64
import io

from dash import dash_table

import pandas as pd
import json
from upload_errors import *

class Uploader:
    def __init__(self):
        self.uploaded_files_data = {}
        self.generic_metadata = {}

    def get_df_from_file(self, contents, filename):
        content_type, content_string = contents.split(',')

        decoded = base64.b64decode(content_string)
        try:
            if '.csv' in filename:
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            else:
                raise FiletypeNotSupportedError('Formato file non supportato.', filename)
        except Exception as e:
            raise FiletypeNotSupportedError('Errore durante la lettura del file.', filename)
        return df
        

    def save(self, df, filename, detected_platform):
        self.uploaded_files_data[filename] = {
            'filename': filename,
            'dataframe': df,
            'platform': detected_platform
        }


    def delete_file_data(self, filename):
        del self.uploaded_files_data[filename]
    



    def clear(self):
        self.uploaded_files_data = {}
        self.generic_metadata = {}

    def has_data(self):
        if self.uploaded_files_data == {}:
            return False
        return True
    
    def get_data_from_filename(self,filename):
        return self.uploaded_files_data[filename]
    
    def get_data_from_filenames(self,filenames):
        output = []
        for name in filenames:
            output.append(self.get_data_from_filename(name))
        return output

    def get_df_from_filename(self,filename):
        return self.uploaded_files_data[filename]['dataframe']


    def get_all_data(self):
        return self.uploaded_files_data.values()


    def get_uploaded_files_number(self):
        return len(self.uploaded_files_data.values())




    def get_merged_data(self):
        dataframes = [file['dataframe'] for file in self.get_all_data()]
        return pd.concat(dataframes, axis=0, ignore_index=False)
    



    def get_generic_metadata(self):
        self.update_generic_metadata()
        return self.generic_metadata

    def update_generic_metadata(self):
        self.generic_metadata["n_of_files"] = len(self.uploaded_files_data)
        self.generic_metadata["n_of_rows"] = len(self.get_merged_data())
        




    def get_table_from_saved_data(self):
        if len(self.uploaded_files_data) > 0:
            df_concat = self.get_merged_data()
            table = dash_table.DataTable(
                data=df_concat.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df_concat.columns],
                id='uploaded_data_table',
                style_table={'backgroundColor': 'rgba(0,0,0,0)', 'paper_bgcolor': 'rgba(0,0,0,0)'},
                style_cell={'backgroundColor': 'rgba(0,0,0,0)'}
            )
            return table
        else:
            return None

    def get_filenames(self):
        return list(self.uploaded_files_data.keys())



    def serialize(self):
        # Convertire i DataFrame in stringhe JSON
        serialized_data = {
            filename: {
                'filename': file_data['filename'],
                'dataframe': file_data['dataframe'].to_json(orient='split') if 'dataframe' in file_data else None,
                'platform': file_data['platform']
            } for filename, file_data in self.uploaded_files_data.items()
        }
        return {
            'uploaded_files_data': serialized_data,
            'generic_metadata': self.generic_metadata
        }

    @staticmethod
    def deserialize(serialized_uploader):
        uploader = Uploader()
        for filename, file_data in serialized_uploader['uploaded_files_data'].items():
            df = pd.read_json(file_data['dataframe'], orient='split') if file_data['dataframe'] is not None else None
            uploader.uploaded_files_data[filename] = {
                'filename': filename,
                'dataframe': df,
                'platform': file_data['platform']
            }
        uploader.generic_metadata = serialized_uploader['generic_metadata']
        return uploader