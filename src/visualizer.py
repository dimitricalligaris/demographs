from dash import html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from analyzer import DashboardCharts

class Visualizer():
    "crea una struttura visiva complessa a partire da visualizzazioni singole"

    def create_complex_vis(visualizations,metadata,data_summary):
        return Visualizer.main_layout(visualizations,data_summary,metadata)

    
    def main_layout(visualizations,data_summary,metadata=None):
        return dbc.Container([
            dbc.Row([
                dbc.Col(dbc.Card(data_summary, id='data-summary'), width=12)
                ]),
            dbc.Row([     
                    dbc.Col(Visualizer.create_package_for_chart(visualizations,metadata,DashboardCharts.CHOROPLETH_MAP.value), lg=7, xs=12),
                    dbc.Col(Visualizer.create_package_for_chart(visualizations,metadata,DashboardCharts.NATIONALITIES_BARCHART.value), lg=5, xs=12),
                ], id='info_geografiche', class_name='dashboard-section', justify='center'),
            dbc.Row([
                dbc.Col(Visualizer.create_package_for_chart(visualizations,metadata,DashboardCharts.AGE_DISTRIBUTION_GRAPH.value), lg=6,md=6,xs=12),
                dbc.Col(Visualizer.create_package_for_chart(visualizations,metadata,DashboardCharts.GENDER_PIECHART.value), lg=6,md=6,xs=12)
            ], justify="center",id='info_demografiche')
        ], fluid=True)
    

    @staticmethod
    def create_package(graph, metadata):
        return dbc.Card([
            dbc.CardBody([
                graph,
                metadata
            ])],
            className = 'graph-package'
        )
    
    @staticmethod
    def create_empty_graph():
        graph = dcc.Graph()
        return Visualizer.create_package(graph,"")

    
    @staticmethod
    def create_package_for_chart(visualizations,metadata,chart_key):
        try:
            return Visualizer.create_package(visualizations[chart_key],metadata[chart_key])
        except:
            return Visualizer.create_empty_graph()
