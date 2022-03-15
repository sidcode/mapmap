from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

import dash_cytoscape as cyto
import plotly.graph_objects as go
import plotly.express as px

import json
import networkx as nx

# SETTINGS
MIN_CONNECTIONS = 5
SEED = 1300
XSCALE = 400
YSCALE = 300


# LOAD DATA

col_swatch = px.colors.qualitative.Dark24
json_datapath = "data/impact_dao_survey_data.json"
with open(json_datapath, 'r') as json_file:
    global_data = json.load(json_file)
    project_data = {
        p['Project Name']: {
            'Twitter': p['Twitter'],
            'Website': p['Project Website'],
            'Metrics': p['Impact Metrics'],
            'Description': p['Project Description'],
            'Capital Tags': p['Impact Capital'],
            'Role Tags': p['Impact Roles'],
            'Followers': p['DAO Followers']
        }
        for p in global_data
    }
    all_projects = list(project_data.keys())


def build_elements(list_of_projects):

    graph = {
        k: v['Followers'] 
        for k,v in project_data.items()
        if k in list_of_projects
    }

    G = nx.from_dict_of_lists(graph)
    G.remove_edges_from(nx.selfloop_edges(G))
    G = nx.k_core(G, MIN_CONNECTIONS)
    pos = nx.spring_layout(G, seed=SEED)

    nodes = []
    for project in list_of_projects:
        if project not in pos.keys():
            continue
        p = project_data.get(project)
        x, y = pos[project]
        s = len(p['Followers'])
        c = col_swatch[int(abs(x)*20)]
        nodes.append({
            'data': {
                'id': project,
                'label': project,
                'node_size': s,
                'color': c
            },
            'position': {'x': x*XSCALE, 'y': y*YSCALE}
        })
    edges = [
        {'data': {'source': source, 'target': target}}
        for source, target in G.edges()
    ]
    elements = nodes + edges    

    return elements



# APP SET-UP

stylesheet = [
    {
        "selector": "node",
        "style": {
            'content': 'data(label)',
            "width": "data(node_size)", 
            "height": "data(node_size)", 
            "background-color": "data(color)",
            "background-opacity": .5,
            'font-size': '10px',
            'text-wrap': 'wrap'
        },
    },
    {
        "selector": "edge", 
        "style": {
            "width": .1, 
            "curve-style": "bezier"
        }
    },
]


def make_graph():

    elements = build_elements(all_projects)
    graph = cyto.Cytoscape(
        id='cytoscape',    
        layout={'name': 'preset'},
        style={'width': '100%', 'height': '70vh'},
        elements=elements,
        stylesheet=stylesheet
    )
    return graph

content = html.Div([
    dbc.Row([
        dbc.Col([
            html.Strong("Impact DAO Network Map - V0.1"),
            html.P("Click on a DAO to learn more about its mission and impact.")
        ])
    ], align='center'),
    dbc.Row(make_graph()),
    dbc.Row(id='cytoscape-tapNode')
])


app = Dash(__name__, suppress_callback_exceptions=False)
server = app.server
app.title = "Impact DAO Network Map"
app.layout = html.Div([content])

# CALLBACKS
@app.callback(Output('cytoscape-tapNode', 'children'),
              Input('cytoscape', 'tapNodeData'))
def displayTapNodeData(node):
    if node:
        project = node['label']        
        twitter = project_data[project]['Twitter']
        desc = project_data[project]['Description']
        website = project_data[project]['Website']
        metrics = project_data[project]['Metrics']
        return [
            html.Strong(project),            
            html.P(desc),
            "Twitter:", html.A(f"@{twitter}", href=f"https://twitter.com/{twitter}"),
            " | Website: ", html.A(website, href=website),
            " | Metrics: ", html.A("Available here", href=metrics),
        ]


# RUN

if __name__ == "__main__":
    app.run_server(debug=True)
