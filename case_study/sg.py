# Author: Gergely Zahoranszky-Kohalmi, PhD
#
# Email: gergely.zahoranszky-kohalmi@nih.gov
#
# Organization: National Center for Advancing Translational Sciences (NCATS/NIH)
#
# Script: sg.py
#
# Aim: Convert the Cytoscape JSON file exported by SmartGraph (https://smartgraph.ncats.io) to dataframe.
#
# References: 
#
# [1] Zahoránszky-Kőhalmi, G., Sheils, T. & Oprea, T.I. SmartGraph: a network pharmacology investigation platform.
#     J Cheminform 12, 5 (2020). DOI: https://doi.org/10.1186/s13321-020-0409-9
#
# [2] SmartGraph [https://smartgraph.ncats.io/]
# 
# [3] Cytoscape.js [https://js.cytoscape.org/]
#
# [4] P. Shannondoi et al. Cytoscape: A Software Environment for Integrated Models of Biomolecular Interaction Networks. Genome Res. 2003. 13: 2498-2504
#     DOI: 10.1101/gr.1239303
#
# Ref: https://www.programiz.com/python-programming/json
# Ref: https://networkx.github.io/documentation/networkx-1.10/tutorial/tutorial.html#adding-attributes-to-graphs-nodes-and-edges
# Ref: http://json.parser.online.fr/
# Ref: https://www.geeksforgeeks.org/reading-and-writing-json-to-a-file-in-python/
# Ref: https://reqbin.com/code/python/poyzx88o/python-requests-get-example#:~:text=To%20send%20an%20HTTP%20GET,method%20with%20the%20headers%3D%20parameter.
# Ref: https://www.w3schools.com/python/ref_requests_get.asp
# Ref: https://js.cytoscape.org/#layouts/cose
#


import json
import sys
import pandas as pd
import requests
import networkx as nx



# Cytoscape API URL
cytoscape_api_url = "http://localhost:1234/v1"





#layout_type = 'hierarchical'
#layout_type = 'cose'
layout_type = 'grid'


new_style_name = 'SmartGraph API'

new_style_json = {
    "title": new_style_name,
    "defaults": [
        {"visualProperty": "NODE_SIZE", "value": 40},
        {"visualProperty": "EDGE_LINE_TYPE", "value": "SOLID"},
        {"visualProperty": "EDGE_WIDTH", "value": 2},
        {"visualProperty": "EDGE_CURVED", "value": False},
        {"visualProperty": "EDGE_TARGET_ARROW_SHAPE", "value": "DELTA"}
        
    ],
    "mappings": [
        {
            "mappingType": "discrete",
            "mappingColumn": "node_type",
            "mappingColumnType": "String",
            "visualProperty": "NODE_FILL_COLOR",
            "map": [
                {"key": "compound", "value": "#4C8DA6"},
                {"key": "target", "value": "#AA4A44"},
                {"key": "pattern", "value": "#D8C571"}
                
            ]
            
        },
        {
            "mappingType": "discrete",
            "mappingColumn": "node_type",
            "mappingColumnType": "String",
            "visualProperty": "NODE_SHAPE",
            "map": [
                {"key": "compound", "value": "ROUND_RECTANGLE"},
                {"key": "target", "value": "ELLIPSE"},
                {"key": "pattern", "value": "TRIANGLE"},


                
            ]
            
        },   
        
        {
            "mappingType": "passthrough",
            "mappingColumn": "node_id",
            "mappingColumnType": "String",
            "visualProperty": "NODE_LABEL"
            
        }

    ]
}



def sg_graph_to_json (G_sg):
    # G_sg: a NetworkX graph object

    sg_graph_json = {}
    sg_nodes = []
    sg_edges = []
    G_sg_json = {}

    for node_label in nx.nodes(G_sg):
        node_attributes = {}
        keys = G_sg.nodes[node_label].keys()
        for k in keys:
            node_attributes[k] = G_sg.nodes[node_label][k]

        node_attributes['node_label'] = node_label
        sg_nodes.append(node_attributes)


    for edge_label in nx.edges(G_sg):
        edge_attributes = {}
        keys = G_sg.edges[edge_label].keys()
        for k in keys:
            edge_attributes[k] = G_sg.edges[edge_label][k]
                                                        
        edge_attributes['edge_label'] = edge_label[0] + '_' + edge_label[1]
        edge_attributes['start_node'] = edge_label[0]
        edge_attributes['end_node'] = edge_label[1]
        sg_edges.append(edge_attributes)


    sg_graph_json['nodes'] = sg_nodes
    sg_graph_json['edges'] = sg_edges
    
    G_sg_json['sgp_graph'] = sg_graph_json
    
    return (G_sg_json)


def parse_graph (graph_json):
    G = nx.DiGraph()

        
    nodes = graph_json['nodes']
    edges = graph_json['edges']
    
    G = process_nodes (G, nodes)

    G = process_edges (G, edges)



    return (G)



def add_node (G, node_id, node_metadata):
    G.add_node(node_id)
    
    
    for key in node_metadata.keys():
        G.nodes[node_id][key] = node_metadata[key]
    
    G.nodes[node_id]['node_id'] = node_id
    
    return (G)


def process_nodes (G, nodes):
    valid_node_types = ['compound', 'target', 'pattern']


    for n in nodes:

        node_metadata = {}

        node_type = n['node_type']

        if node_type not in valid_node_types:
            print ("Invalid node type found: %s. Terminating ..." % (node_type))
            sys.exit(-1)

        node_uuid = n['uuid']

        # Ignoring source info. Filtering should be done before this stage,
        # because at this stage we're only interested in synthesis routes.


        node_metadata['uuid'] = node_uuid
        node_metadata['node_type'] = node_type


        if node_type == 'target':


            uniprot_id = n['uniprot_id']
            fullname = n['fullname']
            activity_cutoff = n['activity_cutoff']

            synonyms = n['synonyms']
            gene_symbols = n['gene_symbols']
            node_id = n['node_id']
            
            node_metadata['uniprot_id'] = uniprot_id
            node_metadata['fullname'] = fullname
            node_metadata['activity_cutoff'] = activity_cutoff
            node_metadata['synonyms'] = synonyms
            node_metadata['gene_symbols'] = gene_symbols
            
            node_metadata['node_id'] = node_id
            
            # node_metadata['rxid'] = rxid
            # node_metadata['name'] = rxid
            # node_metadata['yield_score'] = yield_score
            # node_metadata['yield_predicted'] = yield_predicted




            G = add_node (G, node_id, node_metadata)
            
 
        

        elif node_type == 'compound':
            # Then it's a substance node.

            inchikey = n['inchikey']
            nsinchikey = n['nsinchikey']
            smiles = n['smiles']
            node_id = n['node_id']
            
            node_metadata['inchikey'] = inchikey
            node_metadata['nsinchikey'] = nsinchikey
            node_metadata['name'] = inchikey
            node_metadata['smiles'] = smiles
            node_metadata['node_id'] = node_id


            # placeholder for parsing synthesis planning roles of substances
            # i.e.: starting material, intermedier, target molecule

            G = add_node (G, node_id, node_metadata)

        elif node_type == 'pattern':
            # Then it's a substance node.

            inchikey = n['inchikey']

            smiles = n['smiles']

            node_id = n['node_id']


            pattern_id = n['pattern_id']
            pattern_type = n['pattern_type']
            
            node_metadata['inchikey'] = inchikey

            node_metadata['name'] = node_id
            node_metadata['smiles'] = smiles
            node_metadata['node_id'] = node_id
            node_metadata['pattern_id'] = pattern_id
            node_metadata['pattern_type'] = pattern_type


            # placeholder for parsing synthesis planning roles of substances
            # i.e.: starting material, intermedier, target molecule

            G = add_node (G, node_id, node_metadata)

    return (G)


def add_edge (G, start_node, end_node, edge_metadata):
    G.add_edge (start_node, end_node)
    
    for key in edge_metadata.keys():
        G[start_node][end_node][key] = edge_metadata[key]


    return (G)

def process_edges (G, edges):
    valid_edge_types = ['potent_pattern_of', 'pattern_of', 'tested_on', 'regulates']


    for e in edges:
        
        edge_metadata ={}

        edge_uuid = e['uuid']
        edge_type = e['edge_type']

        if edge_type not in valid_edge_types:
            print ("Invalid edge type found: %s. Terminating ..." % (edge_type))
            sys.exit(-1)


        start_node = e['start_node']
        end_node = e['end_node']
        edge_metadata['edge_type'] = edge_type
        edge_metadata['uuid'] = edge_uuid
        
        edge_metadata['start_node'] = start_node
        edge_metadata['end_node'] = end_node
        edge_metadata['edge_label'] = e['edge_label']


        if edge_type == 'regulates':
            edge_metadata['max_confidence_value'] = e['max_confidence_value']
            edge_metadata['mechanism_details'] = e['mechanism_details']
            edge_metadata['action_type'] = e['action_type']
            edge_metadata['sourceDB'] = e['sourceDB']

        elif edge_type == 'pattern_of':
            edge_metadata['ratio'] = e['ratio']
            edge_metadata['islargest'] = e['islargest']
            edge_metadata['action_type'] = e['action_type']


        G = add_edge (G, start_node, end_node, edge_metadata)

    return (G)



def sg_json2graph (sg_json):
    G = parse_graph (sg_json)

    print (G)

    return (G)


def graph2cyjs (G):

    
    cy_json_data = nx.cytoscape_data(G, name='uuid', ident='node_label')
    
    new_json = {}
    new_json['data'] = {}
    new_json['data']['name'] = 'test'
    new_json['directed']: True
    new_json['multigraph']: False
    new_json['elements'] = cy_json_data['elements']


    return (cy_json_data)


    

def parse_input_json (fname, idx = None):
    # if gtype == 'synth_graph':
    
    with open(fname) as json_file:
        sg_json = json.load(json_file)

        G = sg_json2graph (sg_json)

        cy_json = graph2cyjs (G)
        



    return (cy_json)



def show_in_cytotscape(cy_json):
    
        
    # Send the network to Cytoscape
    response = requests.post(f"{cytoscape_api_url}/networks?format=cyjs", json = cy_json)
    SUID = None
    
    
    if response.ok:
        network_suid = response.json()['networkSUID']
        print(f"Network created with SUID: {network_suid}")
        
        # Create a view for the network
        view_response = requests.get(f"{cytoscape_api_url}/networks/{network_suid}/views/first")
        if view_response.ok:
            print("Network view created.")
            
            SUID = int(view_response.json()['data']['SUID'])

            return (SUID)
        else:
            print("Failed to create network view.")

        return (None)
    else:
        print("Failed to create network.")

    return (None)



def create_style (style_name, style_json):

    
    # Create style if does not exist
    
    
    # Cytoscape API URL
    cytoscape_api_url = "http://localhost:1234/v1"
    

    
    # Check if the style already exists
    existing_styles_response = requests.get(f"{cytoscape_api_url}/styles")
    if existing_styles_response.ok:
        existing_styles = existing_styles_response.json()
        print("Existing styles:", existing_styles)  # Debug print
    
        style_names = [style['title'] for style in existing_styles if isinstance(style, dict)]
        
        if style_name in style_names:
            print(f"Style '{style_name}' already exists. Applying existing style.")
        else:
            print(f"Creating new style '{style_name}'.")
    
    
    
            # Create the new style in Cytoscape
            create_style_response = requests.post(f"{cytoscape_api_url}/styles", json = style_json)
    
            if create_style_response.ok:
                print(f"New style '{style_name}' created.")

                return (True)
            
            else:
                print("Failed to create new style.")
    else:
        print("Failed to retrieve existing styles.")

    return (False)


def apply_style (network_suid, style_name, style_json):

    create_style (style_name, style_json)

    
    
    apply_style_response = requests.get(f"{cytoscape_api_url}/apply/styles/{style_name}/{network_suid}")
    #print (apply_style_response)
    
    if apply_style_response.ok:
        print(f"Style '{style_name}' applied to the network.")
        
        return (True)
    else:
        print(f"Failed to apply style '{style_name}'.")

    return (False)


def apply_layout (network_suid, layout_type):

    apply_style_response = requests.get(f"{cytoscape_api_url}/apply/layouts/{layout_type}/{network_suid}")
    
    if apply_style_response.ok:
        print(f"Layout '{layout_type}' applied to the network.")
        
        return (True)
    else:
        print(f"Failed to apply layout '{layout_type}'.")

    return (False)   


# def visualize_in_cytoscape_from_file (fname, idx):# Workflow:

#     # change the targetmol as fname as needed to send new networks to Cytoscape App



    
#     #print (targetmol)
    


    
#     cy_json = parse_input_json (fname, idx = idx)
    
#     suid = show_in_cytotscape(cy_json)
#     print (suid)
    
#     apply_style (suid, new_style_name, new_style_json)
    
#     apply_layout (suid, layout_type)



def visualize_in_cytoscape (cy_json):# Workflow:

    
    suid = show_in_cytotscape(cy_json)
    #print (suid)
    
    apply_style (suid, new_style_name, new_style_json)
    
    apply_layout (suid, layout_type)



