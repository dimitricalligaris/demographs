import math
import time
import numpy as np
from normalizer import StandardColumns
import plotly.express as px
from dash import dcc, html
import pandas as pd
from enum import Enum
from collections.abc import Iterable


MAIN_CHART_COLOR = '#054a2c'


class DashboardCharts(Enum):
    AGE_DISTRIBUTION_GRAPH = '1'
    CHOROPLETH_MAP = '2'
    NATIONALITIES_BARCHART = '3'
    GENDER_PIECHART = '4'


class Analyzer():
    "crea visualizzazioni grafiche a partire da dati"
 
    def __init__(self):
        self.data = None
        self.visualizations = {}
        self.generic_metadata = None


    def load_data(self,df,generic_metadata):
        self.data = pd.concat([self.data,df], axis=0, ignore_index=False)
        self.generic_metadata = generic_metadata
        

    def clear(self):
        self.data = None
        self.visualizations = {}
        self.generic_metadata = None

    def get_visualizations(self):
        return {key: dcc.Graph(id=key, figure=val['figure'], config={'displayModeBar': False}, responsive=True) 
                for key, val in self.visualizations.items()}
    
    def get_formatted_metadata(self):
        raw_metadata = self.get_raw_metadata()
        output = {}
        for key,metadata in raw_metadata.items():
            if metadata is None:
                output[key] = ""
            else:
                output[key] = (f"Dati relativi a {metadata['used_rows']} su {metadata['total_rows']} record totali ({metadata['used_rows']/metadata['total_rows']*100:.1f}%)")
        return {key: html.P(metadata, className='metadata-container') for key,metadata in output.items()}




    def complete_generic_metadata(self):
        "integra i metadati generici in base ai dati disponibili"
        self.generic_metadata['formatted_mean_time_spent'] = time.strftime("%Hh %Mm %Ss",time.gmtime(math.ceil(np.mean(self.data[StandardColumns.TIME_SPENT.value].dropna()))))
        self.generic_metadata['formatted_median_time_spent'] = time.strftime("%Hh %Mm %Ss",time.gmtime(math.ceil(np.median(self.data[StandardColumns.TIME_SPENT.value].dropna()))))


    def generate_data_summary(self):

        try:
            self.complete_generic_metadata()
        except:
            return ""

        started_at = self.data[StandardColumns.STARTED_AT.value].dropna()
        completed_at = self.data[StandardColumns.COMPLETED_AT.value].dropna()

        return html.P([
            html.H5("Riepilogo", id='summary-title'),
            html.Ul([
                html.Li(f"Quantità di file presi in considerazione: {self.generic_metadata['n_of_files']} file, per un totale di {self.generic_metadata['n_of_rows']} righe"),
                html.Li(f"Tempo mediano delle risposte: {self.generic_metadata['formatted_median_time_spent']}. Tempo medio delle risposte: {self.generic_metadata['formatted_mean_time_spent']} (calcolato effettuato su {Analyzer.calculate_raw_metadata(self.data, StandardColumns.TIME_SPENT)['used_rows']} righe)."),
                html.Li(f"I task sono stati svolti tra il {min(started_at).strftime('%d/%m/%Y')} e il {max(completed_at).strftime('%d/%m/%Y')}"),
            ])
        ])


    def get_figures(self):
        return [group['figure'] for group in self.visualizations.values()]


    def get_raw_metadata(self):
        return {key: val['metadata'] for key,val in self.visualizations.items()}


    def has_data(self):
        if self.data is None:
            return False
        return True
    

    def add_visualization_data(self,id,figure,metadata=None):
        visualization = {'figure': figure, 'metadata': metadata}
        self.visualizations[id]=visualization
    

    
    def create_all_graphs(self):
        self.visualizations = {}    # reset visualizzazioni precedenti
        self.create_users_choropleth_graph()
        self.create_users_nationality_graph()
        self.create_age_distribution_graph()
        self.create_gender_pie_chart()
        self.apply_common_layout()
 


    def apply_common_layout(self):
        for fig in self.get_figures():
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_gridcolor='#828181',
                yaxis_gridcolor='#828181',
                title_x=0.5,
                title_font=dict(size=22),
                xaxis=dict(
                    title_standoff=40
                ),
                yaxis=dict(
                    title_standoff=40,
                    automargin=True
                ),

            )


    # Metodi specifici di creazione grafici
    
    def create_age_distribution_graph(self):
        if field_exists (self.data, StandardColumns.AGE):
            fig = px.histogram(
                self.data,
                x=StandardColumns.AGE.value,
                nbins=20,
                color_discrete_sequence=[MAIN_CHART_COLOR]
                )
            fig.update_traces(
                hovertemplate='età: %{x}<br>frequenza: %{y}'
            )
            fig.update_layout(title='Distribuzione dell\'età',
                  xaxis_title='età',
                  yaxis_title='frequenza')
            metadata = Analyzer.calculate_raw_metadata(self.data, StandardColumns.AGE)
            self.add_visualization_data(DashboardCharts.AGE_DISTRIBUTION_GRAPH.value,fig,metadata)


    def create_users_choropleth_graph(self):
        if field_exists (self.data, StandardColumns.NATIONALITY):
            country_distribution = self.data[StandardColumns.NATIONALITY.value].value_counts().reset_index()
            country_distribution.columns = [StandardColumns.NATIONALITY.value, 'risposte']
            color_scale = [(0, 'rgb(230, 230, 230)'), (1, MAIN_CHART_COLOR)]
            fig = px.choropleth(
                country_distribution,
                locations=StandardColumns.NATIONALITY.value,
                locationmode='country names',
                color='risposte',
                color_continuous_scale=color_scale,
                range_color=[0,country_distribution['risposte'].max()],
                projection = 'equirectangular'
            )
            fig.update_traces(
                hovertemplate='nazionalità: %{location}<br>risposte: %{z}'
            )  
            fig.update_layout(
                xaxis_title='nazionalità',
            )

            fig.update_coloraxes(colorbar_len=0.6)
            
            fig.update_layout(title='Provenienza dei workers')
            
            fig.update_layout(
                autosize=True,
                margin = dict(
                        l=0,
                        r=0,
                        b=5,
                        #t=0,
                        pad=4,
                        autoexpand=True
                    ),

            )
            metadata = Analyzer.calculate_raw_metadata(self.data, StandardColumns.NATIONALITY)
            self.add_visualization_data(DashboardCharts.CHOROPLETH_MAP.value,fig,metadata)

    def create_users_nationality_graph(self):
        if field_exists(self.data, StandardColumns.NATIONALITY):
            country_distribution = self.data[StandardColumns.NATIONALITY.value].value_counts().reset_index()
            country_distribution.columns = [StandardColumns.NATIONALITY.value, 'risposte']
            
            country_distribution = country_distribution.sort_values(by='risposte')

            fig = px.bar(country_distribution, 
                        x='risposte', 
                        y=StandardColumns.NATIONALITY.value, 
                        orientation='h', 
                        title='Frequenza per ciascun paese',
                        text_auto=True,
                        color_discrete_sequence=[MAIN_CHART_COLOR])
            fig.update_traces(
                hovertemplate='nazionalità: %{y}<br>risposte: %{x}'
            )  
            fig.update_layout(
                showlegend=False,
                yaxis_title='nazionalità'
                )
            
            metadata = Analyzer.calculate_raw_metadata(self.data, StandardColumns.NATIONALITY)
            self.add_visualization_data(DashboardCharts.NATIONALITIES_BARCHART.value, fig, metadata)

    

    def create_gender_pie_chart(self):
            if field_exists(self.data, StandardColumns.SEX):
                gender_distribution = self.data[StandardColumns.SEX.value].value_counts().reset_index()
                gender_distribution.columns = [StandardColumns.SEX.value, 'count']

                fig = px.pie(gender_distribution,
                            names=StandardColumns.SEX.value,
                            values='count',
                            title='Distribuzione di genere',
                            color=StandardColumns.SEX.value,
                            color_discrete_map={
                                'M': '#03a1a1',
                                'F': 'pink'
                            })
                fig.update_traces(
                    hovertemplate='sesso: %{label}<br>frequenza: %{value}'
                )  
                metadata = Analyzer.calculate_raw_metadata(self.data, StandardColumns.SEX)
                self.add_visualization_data(DashboardCharts.GENDER_PIECHART.value, fig, metadata)



    @staticmethod
    def calculate_raw_metadata(data, used_columns):
        if not isinstance(used_columns, Iterable):
            used_columns = [used_columns]
        total_rows = len(data)
        not_null_rows = Analyzer.count_valid_rows(data,used_columns)
        metadata = {
            'total_rows': total_rows,
            'used_rows': not_null_rows,
        }        
        return metadata

    @staticmethod
    def count_valid_rows(data,columns):
        return len(data.dropna(subset=[col.value for col in columns]))


    def serialize(self):
        data = self.data.to_json(orient='split') if self.data is not None else None
        return {
            'data': data,
            'visualizations': self.visualizations,
            'generic_metadata': self.generic_metadata
        }

    @staticmethod
    def deserialize(serialized_analyzer):
        analyzer = Analyzer()
        analyzer.data = pd.read_json(serialized_analyzer['data'], orient='split') if serialized_analyzer['data'] is not None else None
        analyzer.visualizations = serialized_analyzer['visualizations']
        analyzer.generic_metadata = serialized_analyzer['generic_metadata']
        return analyzer



@staticmethod
def field_exists(df,field):
    "restituisce True se il campo è presente tra gli attributi del dataframe"
    return field.value in df.columns and df[field.value].notna().any()



from marshmallow import Schema, fields

class MyCustomClass:
    def __init__(self, attribute1, attribute2):
        self.attribute1 = attribute1
        self.attribute2 = attribute2

class MyCustomClassSchema(Schema):
    attribute1 = fields.Str()
    attribute2 = fields.Dict