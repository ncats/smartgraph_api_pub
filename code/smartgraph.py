# Author: Gergely Zahoranszky-Kohalmi, PhD
#
# Organization: National Center for Advancing Translational Sciences (NCATS/NIH)
#
# Email: gergely.zahoranszky-kohalmi@nih.gov
#
#
# Ref: https://pandas.pydata.org/docs/reference/api/pandas.read_json.html
# Ref: https://jsonformatter.curiousconcept.com/#
# Ref: https://stackoverflow.com/questions/42518864/convert-json-data-from-request-into-pandas-dataframe
# Ref: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html
# Ref: https://stackoverflow.com/questions/17141558/how-to-sort-a-dataframe-in-python-pandas-by-two-or-more-columns
# Ref: https://stackoverflow.com/questions/18162970/read-only-cells-in-ipython-jupyter-notebook
# Ref: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_excel.html
# Ref: https://pbpython.com/dataframe-gui-overview.html
# Ref: https://marc-wouts.medium.com/pandas-dataframes-as-interactive-html-datatables-9737c7266abf
# Ref: https://pandas.pydata.org/docs/reference/api/pandas.concat.html
# Ref: https://stackoverflow.com/questions/31168819/how-to-send-an-array-using-requests-post-python-value-error-too-many-values
# Ref: https://www.programcreek.com/python/example/6251/requests.post
# Ref: https://python.plainenglish.io/python-why-you-cant-use-arrays-in-query-strings-with-requests-and-urllib-and-how-to-fix-it-da0ad2ad2e06
# Ref: https://stackoverflow.com/questions/24714543/how-to-make-post-requests-using-with-list-as-parameters-in-python
# Ref: https://stackoverflow.com/questions/15900338/python-request-post-with-param-data
# Ref: https://stackoverflow.com/questions/20658572/python-requests-print-entire-http-request-raw
# Ref: https://community.neo4j.com/t5/drivers-stacks/neo4j-return-graph-results-from-api/td-p/45990
# Ref: https://stackoverflow.com/questions/52885356/iterating-over-subpaths-vs-path-elements
# Ref: https://community.neo4j.com/t5/neo4j-graph-platform/how-to-get-edge-properties-in-query-result/m-p/48403/highlight/true
# Ref: https://networkx.org/documentation/stable/reference/classes/digraph.html
# Ref: https://rollbar.com/blog/throwing-exceptions-in-python/
# Ref: https://neo4j.com/docs/api/python-driver/current/api.html
# Ref: https://github.com/neo4j/docker-neo4j/issues/223
# Ref: https://stackoverflow.com/questions/60523942/neo4j-how-to-access-nodes-properties-in-python
# Ref: https://stackoverflow.com/questions/17801665/how-to-get-an-arbitrary-element-from-a-frozenset
# Ref: https://fastapi.tiangolo.com/tutorial/path-operation-configuration/#tags
# Ref: https://stackoverflow.com/questions/54900893/querying-path-in-neo4j-how-to-show-node-edge-info-only-once
#
#
# Start server: uvicorn server:app --reload
#
#

import neo4j_utils
import sys


import networkx as nx
import json

def add_node (G, node_id, node_metadata):
    G.add_node(node_id)

    for key in node_metadata.keys():
        G.nodes[node_id][key] = node_metadata[key]

    return (G)


def add_edge (G, start_node, end_node, edge_metadata):
    G.add_edge (start_node, end_node)
    
    for key in edge_metadata.keys():
        G[start_node][end_node][key] = edge_metadata[key]


    return (G)



def process_nodes (G, nodes):
    valid_node_types = ['target', 'compound', 'pattern']

    node_id = None
    for n in nodes:

        node_metadata = {}

        node_type = n['node_type']

        if node_type not in valid_node_types:
            raise Exception ("Invalid node type found: %s. Terminating ..." % (node_type))

        
        #print (n)
        
        for k in n.keys():
            
            data_at_hand = n[k] 
            if isinstance (data_at_hand, list):
                node_metadata[k] = ",".join(n[k])
            else:
            
                if k == 'node_id':
                    node_id = n[k]
                
                node_metadata[k] = n[k]

        G = add_node (G, node_id, node_metadata)



    return (G)



def process_edges (G, edges):
    valid_edge_types = ['tested_on', 'regulates', 'pattern_of', 'potent_pattern_of']


    for e in edges:
        
        edge_metadata ={}

        edge_uuid = e['uuid']
        edge_type = e['edge_type']
        
        #print (e, flush = True)

        if edge_type not in valid_edge_types:
            print ("Invalid edge type found: %s. Terminating ..." % (edge_type))
            sys.exit(-1)


        start_node = e['start_node']
        end_node = e['end_node']
        #edge_metadata['edge_type'] = edge_type
        #edge_metadata['uuid'] = edge_uuid
        edge_metadata['start_node'] = start_node
        edge_metadata['end_node'] = end_node

        
        for k in e.keys():
            data_at_hand = e[k]
            
            if isinstance (data_at_hand, list):
                edge_metadata[k] = ",".join(e[k])
            else:

                if k == 'start_node':
                    node_id = e[k]
                if k == 'end_node':
                    node_id = e[k]

                edge_metadata[k] = e[k]


        G = add_edge (G, start_node, end_node, edge_metadata)

    return (G)



def parse_graph (graph_json):
    #with open(input_json) as f:
    #    data = json.load(f)
    G = nx.DiGraph()

   
    nodes = graph_json['nodes']
    edges = graph_json['edges']
    
    G = process_nodes (G, nodes)

    G = process_edges (G, edges)




    return (G)

def to_graphml (G_json):
    G_graphml = ''
    G = parse_graph (G_json)
    linefeed = chr(10)
    #s = linefeed.join(nx.generate_graphml(G))

    for line in nx.generate_graphml(G):
        G_graphml += line

    return (G_graphml)





def extract_node_properties (node, nodes):
    
    node_properties = {}
    
    node_type = list(node.labels)[0]
    #print (node_type)

    raw_properties = node.items()
    
    
    for k, v in raw_properties:
        node_properties[k] = v

    node_properties['node_type'] = node_type.lower()

    if node_properties['node_type'] == 'compound':
        node_properties['node_id'] = node_properties['hash']
        node_properties['inchikey'] = node_properties['hash']
        node_properties['nsinchikey'] = node_properties['nostereo_hash']

    elif node_properties['node_type'] == 'pattern':
        node_properties['node_id'] = node_properties['pattern_id']
        node_properties['inchikey'] = node_properties['hash']

    elif node_properties['node_type'] == 'target':
        node_properties['node_id'] = node_properties['uniprot_id']
    else:
        raise Exception ("[ERROR] Invalid node type encountered in SmartGraph JSON.")

    nodes.append (node_properties)
 
    return (nodes)

def extract_specific_node_property (node, spec_prop):
    props = node.items()

    for k, v in props:
        if k == spec_prop:
            return (v)

    return (None)


def extract_edge_properties (edge, edges):
       
    edge_properties = {}
    tmp = []
    
    raw_properties = edge.items()
    
    
    mode_type = None

    for k, v in raw_properties:
        if k == 'edgeType':
            edge_properties['action_type'] = v
        elif k == 'unique_label':
            edge_properties['edge_label'] = v
        elif k == 'ppi_uid':
            edge_properties['edge_label'] = v
        elif k == 'edgeInfo':
            edge_properties['mechanism_details'] = v

        else:
            edge_properties[k] = v

    
    edge_properties['uuid'] = edge_properties['uuid'] + '_' + edge_properties['edge_label']






    edge_properties['edge_type'] = edge.type.lower()
    #print(edge.start_node.items())


    if edge_properties['edge_type'] == 'regulates':
        start_node_id = extract_specific_node_property (edge.start_node, 'uniprot_id')
        end_node_id = extract_specific_node_property (edge.end_node, 'uniprot_id')
    elif edge_properties['edge_type'] == 'tested_on':
        start_node_id = extract_specific_node_property (edge.start_node, 'hash')
        end_node_id = extract_specific_node_property (edge.end_node, 'uniprot_id')
    elif edge_properties['edge_type'] == 'pattern_of':
        start_node_id = extract_specific_node_property (edge.start_node, 'pattern_id')
        end_node_id = extract_specific_node_property (edge.end_node, 'hash')
    elif edge_properties['edge_type'] == 'potent_pattern_of':
        start_node_id = extract_specific_node_property (edge.start_node, 'pattern_id')
        end_node_id = extract_specific_node_property (edge.end_node, 'uniprot_id')
    else:
        raise Exception ('[ERROR] Invalid edge type encountered in SmartGraph JSON.')


    edge_properties['start_node'] = start_node_id
    edge_properties['end_node'] = end_node_id
    
    #edge_label = edge_properties['edge_label']

    
    
    #tmp = edge_label.split('_')
    
    

    
    edges.append(edge_properties)
    
    return (edges)





def aggregate_nodes(nodes):
    aggregated_nodes = {}
    
    for node in nodes:
        node_id = node['node_id']
        aggregated_nodes[node_id] = node
    
    result = []
    
    #print (aggregated_nodes.keys())
    
    for v in aggregated_nodes.values():
        result.append (v)
        
    return (result)



def aggregate_edges(edges):
    aggregated_edges = {}
    
    for edge in edges:
        edge_id = edge['uuid']
        aggregated_edges[edge_id] = edge
    
    result = []
    
    for v in aggregated_edges.values():
        result.append (v)
        
    return (result)



#G_graphml = to_graphml (G_json)

#print (G_graphml)


### End of network parsing logic


###
### Neo4j Cypher queries section
###

# cite

def cite():
    res_json = {'citation': 'Zahoránszky-Kőhalmi, G., Sheils, T. & Oprea, T.I. SmartGraph: a network pharmacology investigation platform. J Cheminform 12, 5 (2020). https://doi.org/10.1186/s13321-020-0409-9'}

    return (res_json)

def bibtex ():
    sg_bibtex = "@article{, abstract = {© 2020 The Author(s). Motivation: Drug discovery investigations need to incorporate network pharmacology concepts while navigating the complex landscape of drug-target and target-target interactions. This task requires solutions that integrate high-quality biomedical data, combined with analytic and predictive workflows as well as efficient visualization. SmartGraph is an innovative platform that utilizes state-of-the-art technologies such as a Neo4j graph-database, Angular web framework, RxJS asynchronous event library and D3 visualization to accomplish these goals. Results: The SmartGraph framework integrates high quality bioactivity data and biological pathway information resulting in a knowledgebase comprised of 420,526 unique compound-target interactions defined between 271,098 unique compounds and 2018 targets. SmartGraph then performs bioactivity predictions based on the 63,783 Bemis-Murcko scaffolds extracted from these compounds. Through several use-cases, we illustrate the use of SmartGraph to generate hypotheses for elucidating mechanism-of-action, drug-repurposing and off-target prediction. Availability: https://smartgraph.ncats.io/.}, author = {G. Zahoránszky-Kohalmi and T. Sheils and T.I. Oprea}, doi = {10.1186/s13321-020-0409-9}, issn = {17582946}, issue = {1}, journal = {Journal of Cheminformatics}, keywords = {Bioactivity prediction,Network perturbation,Network pharmacology,Network visualization,Pathway analysis,Potent chemical pattern,Protein-protein interactions (PPIs),Scaffold,Target deconvolution,neo4j}, title = {SmartGraph: A network pharmacology investigation platform}, volume = {12}, year = {2020}, }"

    return (sg_bibtex)





# find all bioactivities of a target

def bioactivity_target (target_proteins, activity_cutoff = 0.0, activity_type = None, format = 'json'):
    # target_protein: UniProtIDs
    # activity_cutoff: in uM units, if 0, then all activities will be reported
    # activity_type:string

    conn = neo4j_utils.open_neo4j_connection()
    
    #query = "MATCH p = (ra:Substance)-[:PRODUCT_OF|REAGENT_OF|REACTANT_OF*.." + str(search_depth) + "]->(pr:Substance) where pr.inchikey='" + target_molecule + "' and pr.inchikey<>ra.inchikey return p"
    

    l_targets = []
    l_targets = target_proteins.split(',')

    

    query = "MATCH (c:Compound)-[rel:TESTED_ON]->(t:Target) WHERE t.uniprot_id IN ['" + "', '".join(l_targets) + "']"



    if activity_cutoff > 0.0:
        query += " AND rel.activity<=" + str(activity_cutoff)

    if activity_type != None:
        query += " AND rel.activity_type='" + activity_type + "'"
    

    query += " RETURN c, t, rel"

    #print (query)

    all_nodes = []
    all_edges = []

    # Use this in conjuction with Neo4j v4.x
    #with conn.session(database="neo4j") as session:


    # Use this in conjuction with Neo4j v3.x
    with conn.session() as session:
        #print (query) 
        g = session.read_transaction(
            lambda tx: tx.run(query).graph())

      
        for n in g.nodes:
            #print("id %s labels %s props %s" % (n.id, n.labels, n.items()))
            all_nodes = extract_node_properties (n, all_nodes)


        for r in g.relationships:
            #print("id %s type %s start %s end %s props %s" % (r.id, r.type, r.start_node.id, r.end_node.id, r.items()))
            all_edges = extract_edge_properties (r, all_edges)


    #print (result)

    #print (all_nodes)
    #print (all_edges)
  
    
    G_json = {}

    G_json['nodes'] = aggregate_nodes(all_nodes)
    G_json['edges'] = aggregate_edges(all_edges)
    
    conn.close()
    

    if format == 'graphml':
        return (to_graphml(G_json))
        

    return (G_json)




# find all bioactivities of a compound

def bioactivity_compound (inchikeys, stereo = True, activity_cutoff = 0.0, activity_type = None, format = 'json'):
    # activity_cutoff: in uM units, if 0, then all activities will be reported
    # activity_type:string


    l_inchikeys = []
    l_nsinchikeys = []


    l_inchikeys = inchikeys.split(',')
 

    for ik in l_inchikeys:
        l_nsinchikeys.append(ik.split('-')[0].strip())



    conn = neo4j_utils.open_neo4j_connection()
    
    #query = "MATCH p = (ra:Substance)-[:PRODUCT_OF|REAGENT_OF|REACTANT_OF*.." + str(search_depth) + "]->(pr:Substance) where pr.inchikey='" + target_molecule + "' and pr.inchikey<>ra.inchikey return p"
    
    
    
  

    if stereo:
        query = "MATCH (c:Compound)-[rel:TESTED_ON]->(t:Target) WHERE c.hash IN ['" + "', '".join(l_inchikeys) + "']"
    else:
        query = "MATCH (c:Compound)-[rel:TESTED_ON]->(t:Target) WHERE c.nostereo_hash IN ['" + "', '".join(l_nsinchikeys) + "']"
        

    if activity_cutoff > 0.0:
        query += " AND rel.activity<=" + str(activity_cutoff)

    if activity_type != None:
        query += " AND rel.activity_type='" + activity_type + "'"
    

    query += " RETURN c, t, rel"

    #print (query)

    all_nodes = []
    all_edges = []

    # Use this in conjuction with Neo4j v4.x
    #with conn.session(database="neo4j") as session:


    # Use this in conjuction with Neo4j v3.x
    with conn.session() as session:
        #print (query) 
        g = session.read_transaction(
            lambda tx: tx.run(query).graph())

      
        for n in g.nodes:
            #print("id %s labels %s props %s" % (n.id, n.labels, n.items()))
            all_nodes = extract_node_properties (n, all_nodes)


        for r in g.relationships:
            #print("id %s type %s start %s end %s props %s" % (r.id, r.type, r.start_node.id, r.end_node.id, r.items()))
            all_edges = extract_edge_properties (r, all_edges)


    #print (result)

    #print (all_nodes)
    #print (all_edges)
  
    
    G_json = {}

    G_json['nodes'] = aggregate_nodes(all_nodes)
    G_json['edges'] = aggregate_edges(all_edges)
    
    conn.close()

    if format == 'graphml':
        return (to_graphml(G_json))
    
    return (G_json)


# bioactivity between a specific compound and a specific target 

def bioactivity_c2t (inchikeys, target_proteins, stereo = True, activity_type = None, format = 'json'):
    # target_proteins: UniProtIDs
    # activity_cutoff: in uM units, if 0, then all activities will be reported
    # activity_type:string



    l_inchikeys = []
    l_nsinchikeys = []
    l_targets = []

    l_inchikeys = inchikeys.split(',')
    l_targets = target_proteins.split(',')
 

    for ik in l_inchikeys:
        l_nsinchikeys.append(ik.split('-')[0].strip())




    conn = neo4j_utils.open_neo4j_connection()
    
    #query = "MATCH p = (ra:Substance)-[:PRODUCT_OF|REAGENT_OF|REACTANT_OF*.." + str(search_depth) + "]->(pr:Substance) where pr.inchikey='" + target_molecule + "' and pr.inchikey<>ra.inchikey return p"
    
 
    if stereo:
        query = "MATCH (c:Compound)-[rel:TESTED_ON]->(t:Target) WHERE c.hash IN ['" + "', '".join(l_inchikeys) + "']"

    else:
        query = "MATCH (c:Compound)-[rel:TESTED_ON]->(t:Target) WHERE c.nostereo_hash IN ['" + "', '".join(l_nsinchikeys) + "']"
        

    query += " AND t.uniprot_id IN ['" + "', '".join(l_targets) + "']"
 
 
    if activity_type != None:
        query += " AND rel.activity_type='" + activity_type + "'"
    

    query += " RETURN c, t, rel"

    #print (query)

    all_nodes = []
    all_edges = []

    # Use this in conjuction with Neo4j v4.x
    #with conn.session(database="neo4j") as session:


    # Use this in conjuction with Neo4j v3.x
    with conn.session() as session:
        #print (query) 
        g = session.read_transaction(
            lambda tx: tx.run(query).graph())

      
        for n in g.nodes:
            #print("id %s labels %s props %s" % (n.id, n.labels, n.items()))
            all_nodes = extract_node_properties (n, all_nodes)


        for r in g.relationships:
            #print("id %s type %s start %s end %s props %s" % (r.id, r.type, r.start_node.id, r.end_node.id, r.items()))
            all_edges = extract_edge_properties (r, all_edges)


    #print (result)

    #print (all_nodes)
    #print (all_edges)
  
    
    G_json = {}

    G_json['nodes'] = aggregate_nodes(all_nodes)
    G_json['edges'] = aggregate_edges(all_edges)
    
    conn.close()

    if format == 'graphml':
        return (to_graphml(G_json))

    return (G_json)



# find potent compounds of a target

def potent_compounds (target_proteins, activity_type = None, format = 'json'):
    # target_proteins: UniProtIDs of target proteins, comma-separated
    # activity_cutoff: in uM units, if 0, then all activities will be reported
    # activity_type:string
    
    l_targets = []
    l_targets = target_proteins.split(',')

    conn = neo4j_utils.open_neo4j_connection()
    
    #query = "MATCH p = (ra:Substance)-[:PRODUCT_OF|REAGENT_OF|REACTANT_OF*.." + str(search_depth) + "]->(pr:Substance) where pr.inchikey='" + target_molecule + "' and pr.inchikey<>ra.inchikey return p"
    
    
    query = "MATCH (c:Compound)-[rel:TESTED_ON]->(t:Target) WHERE t.uniprot_id IN ['" + "', '".join(l_targets) + "'] AND rel.activity<=t.activity_cutoff"



    if activity_type != None:
        query += " and rel.activity_type='" + activity_type + "'"
    

    query += " RETURN c, t, rel"

    #print (query)

    all_nodes = []
    all_edges = []

    # Use this in conjuction with Neo4j v4.x
    #with conn.session(database="neo4j") as session:


    # Use this in conjuction with Neo4j v3.x
    with conn.session() as session:
        #print (query) 
        g = session.read_transaction(
            lambda tx: tx.run(query).graph())

      
        for n in g.nodes:
            #print("id %s labels %s props %s" % (n.id, n.labels, n.items()))
            all_nodes = extract_node_properties (n, all_nodes)


        for r in g.relationships:
            #print("id %s type %s start %s end %s props %s" % (r.id, r.type, r.start_node.id, r.end_node.id, r.items()))
            all_edges = extract_edge_properties (r, all_edges)


    #print (result)

    #print (all_nodes)
    #print (all_edges)
  
    
    G_json = {}

    G_json['nodes'] = aggregate_nodes(all_nodes)
    G_json['edges'] = aggregate_edges(all_edges)
    
    conn.close()

    if format == 'graphml':
        return (to_graphml(G_json))
    
    return (G_json)





# find N-length path between a set of source and a set of target proteins

def path_regulatory (source_proteins, target_proteins, shortest_paths=True, max_length=4, confidence_cutoff=0.0, directed=True, format = 'json'):

    l_sources = []
    l_targets = []

    l_sources = source_proteins.split(',')
    l_targets = target_proteins.split(',')

    conn = neo4j_utils.open_neo4j_connection()

    if directed:
        if shortest_paths:
            query = "MATCH p=shortestPath((t1:Target)-[r:REGULATES*.." + str(max_length) + "]->(t2:Target)) WHERE t1.uniprot_id IN ['" + "', '".join(l_sources) + "'] AND t2.uniprot_id IN ['" + "', '".join(l_targets) + "'] AND t1.uuid<>t2.uuid"
        else:
            query = "MATCH p=(t1:Target)-[r:REGULATES*.." + str(max_length) + "]->(t2:Target)  WHERE t1.uniprot_id IN ['" + "', '".join(l_sources) + "'] AND t2.uniprot_id IN ['" + "', '".join(l_targets) + "']"

    else:

        if shortest_paths:
            query = "MATCH p=shortestPath((t1:Target)-[r:REGULATES*.." + str(max_length) + "]-(t2:Target)) WHERE t1.uniprot_id IN ['" + "', '".join(l_sources) + "'] AND t2.uniprot_id IN ['" + "', '".join(l_targets) + "'] AND t1.uuid<>t2.uuid"

        else:
            query = "MATCH p=(t1:Target)-[r:REGULATES*.." + str(max_length) + "]-(t2:Target) WHERE t1.uniprot_id IN ['" + "', '".join(l_sources) + "'] AND t2.uniprot_id IN ['" + "', '".join(l_targets) + "']"

    if confidence_cutoff>0.0:
        query += " AND ALL(rel in r WHERE rel.max_confidence_value>=" + str(confidence_cutoff) + ")"


    query += " RETURN p"


    #print (query)

    all_nodes = []
    all_edges = []

    # Use this in conjuction with Neo4j v4.x
    #with conn.session(database="neo4j") as session:


    # Use this in conjuction with Neo4j v3.x
    with conn.session() as session:
        #print (query) 
        g = session.read_transaction(
            lambda tx: tx.run(query).graph())

      
        for n in g.nodes:
            #print("id %s labels %s props %s" % (n.id, n.labels, n.items()))
            all_nodes = extract_node_properties (n, all_nodes)


        for r in g.relationships:
            #print("id %s type %s start %s end %s props %s" % (r.id, r.type, r.start_node.id, r.end_node.id, r.items()))
            all_edges = extract_edge_properties (r, all_edges)


    #print (result)

    #print (all_nodes)
    #print (all_edges)
  
    
    G_json = {}

    G_json['nodes'] = aggregate_nodes(all_nodes)
    G_json['edges'] = aggregate_edges(all_edges)
    
    conn.close()

    if format == 'graphml':
        return (to_graphml(G_json))
    
    return (G_json)



# find N-length path between a set of compounds and a set of targets
def path_c2t (inchikeys, target_proteins,  stereo=True, shortest_paths=True, max_length=4, activity_cutoff=0.0, activity_type=None, confidence_cutoff=0.0, format = 'json'):

    l_inchikeys = []
    l_nsinchikeys = []

    l_targets = []

    l_inchikeys = inchikeys.split(',')
    l_targets = target_proteins.split(',')

    for ik in l_inchikeys:
        l_nsinchikeys.append(ik.split('-')[0].strip())


    conn = neo4j_utils.open_neo4j_connection()

    query = "MATCH (c:Compound)-[a:TESTED_ON]->(t1:Target)"
     
    first = True



    if activity_cutoff > 0.0:
        query+= " WHERE a.activity<=" + str(activity_cutoff)
        first = False

    if activity_type!=None:
        if first:
            query+= " WHERE a.activity_type='" + activity_type + "'"
            first = False
        else:
            query+= " AND a.activity_type='" + activity_type + "'"

    if first:
        query += " WHERE "
        first = False

    else:
        query += " AND "

    if stereo:
        query += " c.hash IN ['" + "', '".join(l_inchikeys) + "']"
    else:
        query += " c.nostereo_hash IN ['" + "', '".join(l_nsinchikeys) + "']"
    query += " WITH t1, COLLECT(c) as compounds, COLLECT(t1) as targets"

    if shortest_paths:
        query += " MATCH p1=shortestPath((t1)-[r*.." + str(max_length) + "]->(q:Target))"
    
    else:
        query += " MATCH p1=(t1)-[r*.." + str(max_length) + "]->(q:Target)"
    
    query += " WHERE q.uniprot_id IN ['" + "', '".join(l_targets) + "']"

    query += " AND t1.uuid<>q.uuid"

    if confidence_cutoff>0.0:
         query += " AND ALL(rel in r WHERE rel.max_confidence_value>=" + str(confidence_cutoff) + ")"
     

    query += " UNWIND compounds as x"
    query += " UNWIND targets as y"
    query += " MATCH p2=shortestPath((x)-[z:TESTED_ON]-(y))"
    query += " RETURN p1, p2"

     #print (query)

    all_nodes = []
    all_edges = []

     # Use this in conjuction with Neo4j v4.x
     #with conn.session(database="neo4j") as session:


     # Use this in conjuction with Neo4j v3.x
    with conn.session() as session:
        #print (query) 
        g = session.read_transaction(
            lambda tx: tx.run(query).graph())
       
        for n in g.nodes:
            #print("id %s labels %s props %s" % (n.id, n.labels, n.items()))
            all_nodes = extract_node_properties (n, all_nodes)

        for r in g.relationships:
            #print("id %s type %s start %s end %s props %s" % (r.id, r.type, r.start_node.id, r.end_node.id, r.items()))
            all_edges = extract_edge_properties (r, all_edges)


    G_json = {}
    G_json['nodes'] = aggregate_nodes(all_nodes)
    G_json['edges'] = aggregate_edges(all_edges)
     
    conn.close()

    if format == 'graphml':
        return (to_graphml(G_json))
     
    return (G_json)



# get all targets available from a target in N steps


def path_regulatory_open (protein_targets, shortest_paths=True, max_length=4, explore_mode='undirected', confidence_cutoff=0.0, format = 'json'):
    """
        explore_mode:
            - 'undirected': finds all paths that are reacheable from the target proteins in `max_length` of steps, regardless of the direction of the edges
            - 'source': finds all paths starting from the provided protein targets that are reacheable within `max_length` of steps
            - 'target': finds all paths  ending in the provided protein targets and are at most `max_length` length
    """

    acceptable_modes = ['undirected', 'source', 'target']

    conn = neo4j_utils.open_neo4j_connection()
    

    l_targets = []
    
    l_targets = protein_targets.split(',')

    if explore_mode not in acceptable_modes:
        raise Exception ("[ERROR]: /path_regulatory_open encountered an invalide `explore_mode` parameter. Valid options: ['undirected', 'source', 'target']")

    if explore_mode == 'undirected':
        if shortest_paths:
            query = "MATCH p=shortestPath((t1:Target)-[r:REGULATES*.." + str(max_length) + "]-(t2:Target)) WHERE t1.uniprot_id IN ['" + "', '".join (l_targets) + "']"
            query += " AND t1.uuid<>t2.uuid"

        else:
            query = "MATCH p=(t1:Target)-[r:REGULATES*.." + str(max_length) + "]-(t2:Target) WHERE t1.uniprot_id IN ['" + "', '".join (l_targets) + "']"

    elif explore_mode == 'source':
        if shortest_paths:
            query = "MATCH p=shortestPath((t1:Target)-[r:REGULATES*.." + str(max_length) + "]->(t2:Target)) WHERE t1.uniprot_id IN ['" + "', '".join (l_targets) + "']"
            query += " AND t1.uuid<>t2.uuid"

        else:
            query = "MATCH p=(t1:Target)-[r:REGULATES*.." + str(max_length) + "]->(t2:Target) WHERE t1.uniprot_id IN ['" + "', '".join (l_targets) + "']"

    elif explore_mode == 'target':

        if shortest_paths:
            query = "MATCH p=shortestPath((t1:Target)<-[r:REGULATES*.." + str(max_length) + "]-(t2:Target)) WHERE t1.uniprot_id IN ['" + "', '".join (l_targets) + "']"
            query += " AND t1.uuid<>t2.uuid"

        else:
            query = "MATCH p=(t1:Target)<-[r:REGULATES*.." + str(max_length) + "]-(t2:Target) WHERE t1.uniprot_id IN ['" + "', '".join (l_targets) + "']"

     




 
    

    if confidence_cutoff > 0.0:
        query += " AND ALL(rel in r WHERE rel.max_confidence_value>=" + str(confidence_cutoff) + ")"

     

    query += " RETURN p"

    #print (query)

    all_nodes = []
    all_edges = []

     # Use this in conjuction with Neo4j v4.x
     #with conn.session(database="neo4j") as session:


     # Use this in conjuction with Neo4j v3.x
    with conn.session() as session:
        #print (query) 
        g = session.read_transaction(
            lambda tx: tx.run(query).graph())
       
        for n in g.nodes:
            #print("id %s labels %s props %s" % (n.id, n.labels, n.items()))
            all_nodes = extract_node_properties (n, all_nodes)

        for r in g.relationships:
            #print("id %s type %s start %s end %s props %s" % (r.id, r.type, r.start_node.id, r.end_node.id, r.items()))
            all_edges = extract_edge_properties (r, all_edges)


    G_json = {}
    G_json['nodes'] = aggregate_nodes(all_nodes)
    G_json['edges'] = aggregate_edges(all_edges)
     
    conn.close()


    if format == 'graphml':
        return (to_graphml(G_json))
     
    return (G_json)




# get all compounds available from target proteins in N steps

def subgraph_target_induced (protein_targets, endpoint_type='both', shortest_paths=True, max_length=4, explore_mode='undirected', format = 'json'):
    """
        Extracts a subgraph induced by a set of provided protein targets so that these targets are one endpoints of paths that end in compounds/targets/both, and the lengths of paths is <= `max_length`.

        explore_mode:
            - 'undirected': finds all paths that are reacheable from the target proteins in `max_length` of steps, regardless of the direction of the edges
            - 'source': finds all paths starting from the provided protein targets that are reacheable within `max_length` of steps
            - 'target': finds all paths  ending in the provided protein targets and are at most `max_length` length

        endpoint_type:
            - 'compound': endpoints are compounds
            - 'target': endpoints are targets
            - 'both': endpoints are either compounds or targets
    """

    acceptable_modes = ['undirected', 'source', 'target']
    acceptable_endpoint_types = ['compound', 'target', 'both']

    conn = neo4j_utils.open_neo4j_connection()
    

    l_targets = []
    
    l_targets = protein_targets.split(',')

    if explore_mode not in acceptable_modes:
        raise Exception ("[ERROR]: /subgraph_target_induced encountered an invalid `explore_mode` parameter. Valid options: ['undirected', 'source', 'target']")


    if endpoint_type not in acceptable_endpoint_types:
        raise Exception ("[ERROR]: /subgraph_target_induced encountered an invalid `endpoint_type` parameter. Valid options: ['compound', 'target', 'both']")


     
    endpoint_constraint = ''
    self_node_constraint = ''

    if endpoint_type == 'compound':
        endpoint_constraint = 'c:Compound'
        self_node_constraint = ''

    elif endpoint_type == 'target':
        endpoint_constraint = 't2:Target'
        self_node_constraint = ' AND t1.uuid<>t2.uuid'


    elif endpoint_type == 'both':
        endpoint_constraint = 'x'
        self_node_constraint = ' AND t1.uuid<>x.uuid'


    if explore_mode == 'undirected':
        if shortest_paths:
            query = "MATCH p=shortestPath((t1:Target)-[r:TESTED_ON|REGULATES*.." + str(max_length) + "]-(" + endpoint_constraint + ")) WHERE t1.uniprot_id IN ['" + "', '".join (l_targets) + "']"
            query += self_node_constraint

        else:
            query = "MATCH p=(t1:Target)-[r:TESTED_ON|REGULATES*.." + str(max_length) + "]-(" + endpoint_constraint + ") WHERE t1.uniprot_id IN ['" + "', '".join (l_targets) + "']"

    elif explore_mode == 'source':
        if shortest_paths:
            query = "MATCH p=shortestPath((t1:Target)-[r:TESTED_ON|REGULATES*.." + str(max_length) + "]->(" + endpoint_constraint + ")) WHERE t1.uniprot_id IN ['" + "', '".join (l_targets) + "']"
            query += self_node_constraint

        else:
            query = "MATCH p=(t1:Target)-[r:TESTED_ON|REGULATES*.." + str(max_length) + "]->(" + endpoint_constraint + ") WHERE t1.uniprot_id IN ['" + "', '".join (l_targets) + "']"
    
    elif explore_mode == 'target':

        if shortest_paths:
            query = "MATCH p=shortestPath((t1:Target)<-[r:TESTED_ON|REGULATES*.." + str(max_length) + "]-(" + endpoint_constraint + ")) WHERE t1.uniprot_id IN ['" + "', '".join (l_targets) + "']"
            query += self_node_constraint
        
        else:
            query = "MATCH p=(t1:Target)<-[r:TESTED_ON|REGULATES*.." + str(max_length) + "]-(" + endpoint_constraint + ") WHERE t1.uniprot_id IN ['" + "', '".join (l_targets) + "']"
 

    query += " RETURN p"

    #print (query)

    all_nodes = []
    all_edges = []

    # Use this in conjuction with Neo4j v4.x
    #with conn.session(database="neo4j") as session:


    # Use this in conjuction with Neo4j v3.x
    with conn.session() as session:
        #print (query) 
        g = session.read_transaction(
            lambda tx: tx.run(query).graph())
       
        for n in g.nodes:
            #print("id %s labels %s props %s" % (n.id, n.labels, n.items()))
            all_nodes = extract_node_properties (n, all_nodes)

        for r in g.relationships:
            #print("id %s type %s start %s end %s props %s" % (r.id, r.type, r.start_node.id, r.end_node.id, r.items()))
            all_edges = extract_edge_properties (r, all_edges)


    G_json = {}
    G_json['nodes'] = aggregate_nodes(all_nodes)
    G_json['edges'] = aggregate_edges(all_edges)
     
    conn.close()

    if format == 'graphml':
        return (to_graphml(G_json))
    
    return (G_json)



# get all targets available from a compound in N steps


def subgraph_compound_induced (inchikeys, stereo=True, shortest_paths=True, max_length=4, format = 'json'):
    """
        Extracts a subgraph induced by a set of provided compounds so that paths starting from them are of length <= `max_length`.
    """


    conn = neo4j_utils.open_neo4j_connection()
    

    l_inchikeys = []
    l_nsinchikeys = []
    
    l_inchikeys = inchikeys.split(',')


     
    for ik in l_inchikeys:
        l_nsinchikeys.append(ik.split('-')[0].strip())


    hash_field = ''

    compound_hashes = []

    if stereo:
        hash_field = 'hash'
        compound_hashes = l_inchikeys
    else:
        hash_field = 'nostereo_hash'
        compound_hashes = l_nsinchikeys

    if shortest_paths:
        query = "MATCH (c:Compound)-[r*.." + str(max_length) + "]->(t:Target) WHERE c." + hash_field + " IN ['" + "', '".join (compound_hashes) + "']"
        query += " WITH COLLECT (DISTINCT t) AS targets, COLLECT (DISTINCT c) AS compounds"
        query += " UNWIND compounds as compound"
        query += " UNWIND targets as target"
        query += " MATCH p=shortestPath((compound)-[r*.." + str(max_length) + "]->(target))"


    else:
        query = "MATCH (c:Compound)-[r*.." + str(max_length) + "]->(t:Target) WHERE c." + hash_field + " IN ['" + "', '".join (compound_hashes) + "']"
        query += " WITH COLLECT (DISTINCT t) AS targets, COLLECT (DISTINCT c) AS compounds"
        query += " UNWIND compounds as compound"
        query += " UNWIND targets as target"
        query += " MATCH p=(compound)-[r*.." + str(max_length) + "]->(target)"
 

    query += " RETURN p"

    #print (query)

    all_nodes = []
    all_edges = []

    # Use this in conjuction with Neo4j v4.x
    #with conn.session(database="neo4j") as session:
    
    # Use this in conjuction with Neo4j v3.x
    with conn.session() as session:
        #print (query) 
        g = session.read_transaction(
            lambda tx: tx.run(query).graph())
       
        for n in g.nodes:
            #print("id %s labels %s props %s" % (n.id, n.labels, n.items()))
            all_nodes = extract_node_properties (n, all_nodes)

        for r in g.relationships:
            #print("id %s type %s start %s end %s props %s" % (r.id, r.type, r.start_node.id, r.end_node.id, r.items()))
            all_edges = extract_edge_properties (r, all_edges)


    G_json = {}
    G_json['nodes'] = aggregate_nodes(all_nodes)
    G_json['edges'] = aggregate_edges(all_edges)
     
    conn.close()

    if format == 'graphml':
        return (to_graphml(G_json))

     
    return (G_json)




# get SMILES of a compound

def smiles_compound (compound_inchikey, stereo=True):
    compound_smiles = []
    compound_inchikeys = []
    compound_nsinchikeys = []
    res = {}


    if stereo:
        query = "MATCH (c:Compound) WHERE c.hash='" + compound_inchikey + "' RETURN c.smiles as smiles, c.hash as inchikey, c.nostereo_hash as nsinchikey"
    else:
        compound_nsinchikey = compound_inchikey.split('-')[0].strip()
        query = "MATCH (c:Compound) WHERE c.nostereo_hash='" + compound_nsinchikey + "' RETURN c.smiles as smiles, c.hash as inchikey, c.nostereo_hash as nsinchikey"

    #print (query)
    
    conn = neo4j_utils.open_neo4j_connection()
    

    session = conn.session()
    results = session.run (query)

    
    for record in results:
        compound_smiles.append(record["smiles"])
        compound_inchikeys.append(record["inchikey"])
        compound_nsinchikeys.append(record["nsinchikey"])

    session.close()
    conn.close()
    
    res['smiles'] = compound_smiles[0]
    res['inchikey'] = compound_inchikeys[0]
    res['nsinchikey'] = compound_nsinchikeys[0]
    res['stereo'] = stereo


    final_json = {}
    final_json ['compound'] = res
    
    return (final_json)


# get SMILES of a pattern




def smiles_pattern (pattern_id):
    smiles = []
    inchikeys = []
    p_ids = []
    p_types = []

    res = {}


    query = "MATCH (p:Pattern) WHERE p.pattern_id='" + pattern_id + "' RETURN p.smiles as smiles, p.hash as inchikey, p.pattern_type as pattern_type, p.pattern_id as pattern_id, p.uuid as uuid"

    #print (query)
    
    conn = neo4j_utils.open_neo4j_connection()
    

    session = conn.session()
    results = session.run (query)

    
    for record in results:
        smiles.append(record["smiles"])
        inchikeys.append(record["inchikey"])
        p_ids.append(record["pattern_id"])
        p_types.append(record["pattern_type"])

    session.close()
    conn.close()
    
    res['smiles'] = smiles[0]
    res['inchikey'] = inchikeys[0]
    res['pattern_id'] = p_ids[0]
    res['pattern_type'] = p_types[0]


    final_json = {}
    final_json ['pattern'] = res
    
    return (final_json)
    
    return (final_json)



# get patterns of a compound

def patterns_of_compounds (inchikeys, stereo=True, pattern_type='scaffold', min_ratio=0.0, is_largest=None, format = 'json'):
    """
        Returns the patterns associated with provided compounds.
    """


    conn = neo4j_utils.open_neo4j_connection()
    

    l_inchikeys = []
    l_nsinchikeys = []
    
    l_inchikeys = inchikeys.split(',')


     
    for ik in l_inchikeys:
        l_nsinchikeys.append(ik.split('-')[0].strip())


    hash_field = ''

    compound_hashes = []

    if stereo:
        hash_field = 'hash'
        compound_hashes = l_inchikeys
    else:
        hash_field = 'nostereo_hash'
        compound_hashes = l_nsinchikeys

    query = "MATCH paths=shortestPath((c:Compound)<-[r:PATTERN_OF*..1]-(p:Pattern)) WHERE c." + hash_field + " IN ['" + "', '".join (compound_hashes) + "']"
 
    query += " AND p.pattern_type='" + pattern_type + "'"

    if min_ratio > 0.0:
        query += " AND ALL(rel in r WHERE rel.ratio>=" + str(min_ratio) + ")"


    if is_largest != None:
         query += " AND ALL(rel in r WHERE rel.islargest='" + str(is_largest).lower() + "')"

    query += " RETURN paths"

    #print (query)

    all_nodes = []
    all_edges = []

    # Use this in conjuction with Neo4j v4.x
    #with conn.session(database="neo4j") as session:
    
    # Use this in conjuction with Neo4j v3.x
    with conn.session() as session:
        #print (query) 
        g = session.read_transaction(
            lambda tx: tx.run(query).graph())
       
        for n in g.nodes:
            #print("id %s labels %s props %s" % (n.id, n.labels, n.items()))
            all_nodes = extract_node_properties (n, all_nodes)

        for r in g.relationships:
            #print("id %s type %s start %s end %s props %s" % (r.id, r.type, r.start_node.id, r.end_node.id, r.items()))
            all_edges = extract_edge_properties (r, all_edges)


    G_json = {}
    G_json['nodes'] = aggregate_nodes(all_nodes)
    G_json['edges'] = aggregate_edges(all_edges)
     
    conn.close()

    if format == 'graphml':
        return (to_graphml(G_json))

     
    return (G_json)



# get potent patterns of a target

def potent_patterns (targets, pattern_type='scaffold', format = 'json'):
    """
        Returns the potent patterns of provided target proteins. Potent patterns are defined in context of SmartGraph.
    """


    conn = neo4j_utils.open_neo4j_connection()
    

    l_targets = []
    l_targets = targets.split(',')


    query = "MATCH paths=shortestPath((p:Pattern)-[r:POTENT_PATTERN_OF*..1]->(t:Target)) WHERE t.uniprot_id IN ['" + "', '".join (l_targets) + "']"
 
    query += " AND p.pattern_type='" + pattern_type + "'"

    query += " RETURN paths"

    #print (query)

    all_nodes = []
    all_edges = []

    # Use this in conjuction with Neo4j v4.x
    #with conn.session(database="neo4j") as session:
    
    # Use this in conjuction with Neo4j v3.x
    with conn.session() as session:
        #print (query) 
        g = session.read_transaction(
            lambda tx: tx.run(query).graph())
       
        for n in g.nodes:
            #print("id %s labels %s props %s" % (n.id, n.labels, n.items()))
            all_nodes = extract_node_properties (n, all_nodes)

        for r in g.relationships:
            #print("id %s type %s start %s end %s props %s" % (r.id, r.type, r.start_node.id, r.end_node.id, r.items()))
            all_edges = extract_edge_properties (r, all_edges)


    G_json = {}
    G_json['nodes'] = aggregate_nodes(all_nodes)
    G_json['edges'] = aggregate_edges(all_edges)
     
    conn.close()

    if format == 'graphml':
        return (to_graphml(G_json))

     
    return (G_json)



# make prediction for repurposing

def predict (target, limit=300, format = 'json'):
    """
       Computes "potent pattern"-based bioactivity predictions. This can be used in a drug repositioning setting.
    """


    query = "MATCH (t:Target) WHERE t.uniprot_id='" + target +"' MATCH (t)<-[r1:POTENT_PATTERN_OF]-(p:Pattern) MATCH (p)-[r2:PATTERN_OF]->(c:Compound) WHERE NOT ((c)-[:TESTED_ON]->(t)) WITH {segments:[{start: startNode(r1), relationship:r1, end: endNode(r1)},{start: startNode(r2), relationship:r2, end: endNode(r2)}]} AS ret RETURN ret"

    if limit > 0:
        query += " LIMIT " + str(limit)

    #print (query)


    conn = neo4j_utils.open_neo4j_connection()


    all_nodes = []
    all_edges = []

    # Use this in conjuction with Neo4j v4.x
    #with conn.session(database="neo4j") as session:
    
    # Use this in conjuction with Neo4j v3.x
    with conn.session() as session:
        #print (query) 
        g = session.read_transaction(
            lambda tx: tx.run(query).graph())
       
        for n in g.nodes:
            #print("id %s labels %s props %s" % (n.id, n.labels, n.items()))
            all_nodes = extract_node_properties (n, all_nodes)

        for r in g.relationships:
            #print("id %s type %s start %s end %s props %s" % (r.id, r.type, r.start_node.id, r.end_node.id, r.items()))
            all_edges = extract_edge_properties (r, all_edges)


    G_json = {}
    G_json['nodes'] = aggregate_nodes(all_nodes)
    G_json['edges'] = aggregate_edges(all_edges)
     
    conn.close()

    if format == 'graphml':
        return (to_graphml(G_json))

     
    return (G_json)


# Return SmartGraph Cytoscape Style File

def get_sg_style ():
    SG_style = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <vizmap id="VizMap-2023_02_13-20_07" documentVersion="3.1">
        <visualStyle name="SmartGraph">
            <network>
                <visualProperty default="550.0" name="NETWORK_WIDTH"/>
                <visualProperty default="#FFFFFF" name="NETWORK_BACKGROUND_PAINT"/>
                <visualProperty default="0.0" name="NETWORK_CENTER_X_LOCATION"/>
                <visualProperty default="false" name="NETWORK_ANNOTATION_SELECTION"/>
                <visualProperty default="0.0" name="NETWORK_CENTER_Y_LOCATION"/>
                <visualProperty default="" name="NETWORK_TITLE"/>
                <visualProperty default="false" name="NETWORK_FORCE_HIGH_DETAIL"/>
                <visualProperty default="400.0" name="NETWORK_HEIGHT"/>
                <visualProperty default="1.0" name="NETWORK_SCALE_FACTOR"/>
                <visualProperty default="false" name="NETWORK_NODE_LABEL_SELECTION"/>
                <visualProperty default="0.0" name="NETWORK_CENTER_Z_LOCATION"/>
                <visualProperty default="true" name="NETWORK_EDGE_SELECTION"/>
                <visualProperty default="true" name="NETWORK_NODE_SELECTION"/>
                <visualProperty default="550.0" name="NETWORK_SIZE"/>
                <visualProperty default="0.0" name="NETWORK_DEPTH"/>
            </network>
            <node>
                <dependency value="true" name="nodeCustomGraphicsSizeSync"/>
                <dependency value="false" name="nodeSizeLocked"/>
                <visualProperty default="C,C,c,0.00,0.00" name="NODE_CUSTOMGRAPHICS_POSITION_6"/>
                <visualProperty default="0.0" name="NODE_X_LOCATION"/>
                <visualProperty default="255" name="NODE_TRANSPARENCY"/>
                <visualProperty default="DefaultVisualizableVisualProperty(id=NODE_CUSTOMPAINT_2, name=Node Custom Paint 2)" name="NODE_CUSTOMPAINT_2"/>
                <visualProperty default="10.0" name="COMPOUND_NODE_PADDING"/>
                <visualProperty default="DefaultVisualizableVisualProperty(id=NODE_CUSTOMPAINT_6, name=Node Custom Paint 6)" name="NODE_CUSTOMPAINT_6"/>
                <visualProperty default="75.0" name="NODE_WIDTH"/>
                <visualProperty default="35.0" name="NODE_HEIGHT"/>
                <visualProperty default="SOLID" name="NODE_BORDER_STROKE"/>
                <visualProperty default="DefaultVisualizableVisualProperty(id=NODE_CUSTOMPAINT_3, name=Node Custom Paint 3)" name="NODE_CUSTOMPAINT_3"/>
                <visualProperty default="C,C,c,0.00,0.00" name="NODE_CUSTOMGRAPHICS_POSITION_4"/>
                <visualProperty default="C,C,c,0.00,0.00" name="NODE_CUSTOMGRAPHICS_POSITION_8"/>
                <visualProperty default="DefaultVisualizableVisualProperty(id=NODE_CUSTOMPAINT_5, name=Node Custom Paint 5)" name="NODE_CUSTOMPAINT_5"/>
                <visualProperty default="C,C,c,0.00,0.00" name="NODE_LABEL_POSITION"/>
                <visualProperty default="SansSerif,plain,12" name="NODE_LABEL_FONT_FACE"/>
                <visualProperty default="C,C,c,0.00,0.00" name="NODE_CUSTOMGRAPHICS_POSITION_7"/>
                <visualProperty default="50.0" name="NODE_CUSTOMGRAPHICS_SIZE_2"/>
                <visualProperty default="false" name="NODE_SELECTED"/>
                <visualProperty default="255" name="NODE_BORDER_TRANSPARENCY"/>
                <visualProperty default="ROUND_RECTANGLE" name="NODE_SHAPE">
                    <discreteMapping attributeName="node_type" attributeType="string">
                        <discreteMappingEntry attributeValue="pattern" value="HEXAGON"/>
                        <discreteMappingEntry attributeValue="compound" value="ROUND_RECTANGLE"/>
                        <discreteMappingEntry attributeValue="target" value="TRIANGLE"/>
                    </discreteMapping>
                </visualProperty>
                <visualProperty default="255" name="NODE_LABEL_TRANSPARENCY"/>
                <visualProperty default="C,C,c,0.00,0.00" name="NODE_CUSTOMGRAPHICS_POSITION_5"/>
                <visualProperty default="org.cytoscape.cg.model.NullCustomGraphics,0,[ Remove Graphics ]," name="NODE_CUSTOMGRAPHICS_7"/>
                <visualProperty default="DefaultVisualizableVisualProperty(id=NODE_CUSTOMPAINT_9, name=Node Custom Paint 9)" name="NODE_CUSTOMPAINT_9"/>
                <visualProperty default="50.0" name="NODE_CUSTOMGRAPHICS_SIZE_6"/>
                <visualProperty default="50.0" name="NODE_CUSTOMGRAPHICS_SIZE_7"/>
                <visualProperty default="50.0" name="NODE_CUSTOMGRAPHICS_SIZE_8"/>
                <visualProperty default="C,C,c,0.00,0.00" name="NODE_CUSTOMGRAPHICS_POSITION_2"/>
                <visualProperty default="50.0" name="NODE_CUSTOMGRAPHICS_SIZE_9"/>
                <visualProperty default="org.cytoscape.cg.model.NullCustomGraphics,0,[ Remove Graphics ]," name="NODE_CUSTOMGRAPHICS_9"/>
                <visualProperty default="#FFFF00" name="NODE_SELECTED_PAINT"/>
                <visualProperty default="org.cytoscape.cg.model.NullCustomGraphics,0,[ Remove Graphics ]," name="NODE_CUSTOMGRAPHICS_4"/>
                <visualProperty default="50.0" name="NODE_CUSTOMGRAPHICS_SIZE_5"/>
                <visualProperty default="#89D0F5" name="NODE_FILL_COLOR">
                    <discreteMapping attributeName="node_type" attributeType="string">
                        <discreteMappingEntry attributeValue="pattern" value="#0C2C84"/>
                        <discreteMappingEntry attributeValue="compound" value="#67A9CF"/>
                        <discreteMappingEntry attributeValue="target" value="#FB6A4A"/>
                    </discreteMapping>
                </visualProperty>
                <visualProperty default="0.0" name="NODE_BORDER_WIDTH"/>
                <visualProperty default="200.0" name="NODE_LABEL_WIDTH"/>
                <visualProperty default="DefaultVisualizableVisualProperty(id=NODE_CUSTOMPAINT_4, name=Node Custom Paint 4)" name="NODE_CUSTOMPAINT_4"/>
                <visualProperty default="#000000" name="NODE_LABEL_COLOR"/>
                <visualProperty default="0.0" name="NODE_Y_LOCATION"/>
                <visualProperty default="org.cytoscape.cg.model.NullCustomGraphics,0,[ Remove Graphics ]," name="NODE_CUSTOMGRAPHICS_6"/>
                <visualProperty default="0.0" name="NODE_DEPTH"/>
                <visualProperty default="DefaultVisualizableVisualProperty(id=NODE_CUSTOMPAINT_8, name=Node Custom Paint 8)" name="NODE_CUSTOMPAINT_8"/>
                <visualProperty default="org.cytoscape.cg.model.NullCustomGraphics,0,[ Remove Graphics ]," name="NODE_CUSTOMGRAPHICS_5"/>
                <visualProperty default="ROUND_RECTANGLE" name="COMPOUND_NODE_SHAPE"/>
                <visualProperty default="0.0" name="NODE_Z_LOCATION"/>
                <visualProperty default="50.0" name="NODE_CUSTOMGRAPHICS_SIZE_3"/>
                <visualProperty default="35.0" name="NODE_SIZE"/>
                <visualProperty default="#CCCCCC" name="NODE_BORDER_PAINT"/>
                <visualProperty default="C,C,c,0.00,0.00" name="NODE_CUSTOMGRAPHICS_POSITION_3"/>
                <visualProperty default="" name="NODE_TOOLTIP"/>
                <visualProperty default="DefaultVisualizableVisualProperty(id=NODE_CUSTOMPAINT_1, name=Node Custom Paint 1)" name="NODE_CUSTOMPAINT_1"/>
                <visualProperty default="org.cytoscape.cg.model.NullCustomGraphics,0,[ Remove Graphics ]," name="NODE_CUSTOMGRAPHICS_3"/>
                <visualProperty default="true" name="NODE_VISIBLE"/>
                <visualProperty default="DefaultVisualizableVisualProperty(id=NODE_CUSTOMPAINT_7, name=Node Custom Paint 7)" name="NODE_CUSTOMPAINT_7"/>
                <visualProperty default="org.cytoscape.cg.model.NullCustomGraphics,0,[ Remove Graphics ]," name="NODE_CUSTOMGRAPHICS_1"/>
                <visualProperty default="org.cytoscape.cg.model.NullCustomGraphics,0,[ Remove Graphics ]," name="NODE_CUSTOMGRAPHICS_2"/>
                <visualProperty default="12" name="NODE_LABEL_FONT_SIZE"/>
                <visualProperty default="org.cytoscape.cg.model.NullCustomGraphics,0,[ Remove Graphics ]," name="NODE_CUSTOMGRAPHICS_8"/>
                <visualProperty default="50.0" name="NODE_CUSTOMGRAPHICS_SIZE_1"/>
                <visualProperty default="50.0" name="NODE_CUSTOMGRAPHICS_SIZE_4"/>
                <visualProperty default="true" name="NODE_NESTED_NETWORK_IMAGE_VISIBLE"/>
                <visualProperty default="C,C,c,0.00,0.00" name="NODE_CUSTOMGRAPHICS_POSITION_9"/>
                <visualProperty default="#1E90FF" name="NODE_PAINT"/>
                <visualProperty default="" name="NODE_LABEL">
                    <passthroughMapping attributeName="name" attributeType="string"/>
                </visualProperty>
                <visualProperty default="0.0" name="NODE_LABEL_ROTATION"/>
                <visualProperty default="C,C,c,0.00,0.00" name="NODE_CUSTOMGRAPHICS_POSITION_1"/>
            </node>
            <edge>
                <dependency value="false" name="arrowColorMatchesEdge"/>
                <visualProperty default="#000000" name="EDGE_TARGET_ARROW_UNSELECTED_PAINT"/>
                <visualProperty default="NONE" name="EDGE_SOURCE_ARROW_SHAPE"/>
                <visualProperty default="#000000" name="EDGE_SOURCE_ARROW_UNSELECTED_PAINT"/>
                <visualProperty default="0.5" name="EDGE_STACKING_DENSITY"/>
                <visualProperty default="0.0" name="EDGE_Z_ORDER"/>
                <visualProperty default="SOLID" name="EDGE_LINE_TYPE"/>
                <visualProperty default="" name="EDGE_TOOLTIP"/>
                <visualProperty default="AUTO_BEND" name="EDGE_STACKING"/>
                <visualProperty default="#323232" name="EDGE_PAINT"/>
                <visualProperty default="6.0" name="EDGE_TARGET_ARROW_SIZE"/>
                <visualProperty default="#FFFF00" name="EDGE_TARGET_ARROW_SELECTED_PAINT"/>
                <visualProperty default="255" name="EDGE_TRANSPARENCY"/>
                <visualProperty default="#FFFF00" name="EDGE_SOURCE_ARROW_SELECTED_PAINT"/>
                <visualProperty default="Dialog,plain,10" name="EDGE_LABEL_FONT_FACE"/>
                <visualProperty default="6.0" name="EDGE_SOURCE_ARROW_SIZE"/>
                <visualProperty default="#000000" name="EDGE_LABEL_COLOR"/>
                <visualProperty default="0.0" name="EDGE_LABEL_ROTATION"/>
                <visualProperty default="200.0" name="EDGE_LABEL_WIDTH"/>
                <visualProperty default="#404040" name="EDGE_UNSELECTED_PAINT"/>
                <visualProperty default="" name="EDGE_BEND"/>
                <visualProperty default="DELTA" name="EDGE_TARGET_ARROW_SHAPE">
                    <discreteMapping attributeName="action_type" attributeType="string">
                        <discreteMappingEntry attributeValue="up" value="DELTA"/>
                        <discreteMappingEntry attributeValue="down" value="T"/>
                        <discreteMappingEntry attributeValue="undefined" value="CIRCLE"/>
                    </discreteMapping>
                </visualProperty>
                <visualProperty default="2.0" name="EDGE_WIDTH"/>
                <visualProperty default="#FF0000" name="EDGE_SELECTED_PAINT"/>
                <visualProperty default="10" name="EDGE_LABEL_FONT_SIZE"/>
                <visualProperty default="true" name="EDGE_CURVED"/>
                <visualProperty default="#848484" name="EDGE_STROKE_UNSELECTED_PAINT"/>
                <visualProperty default="255" name="EDGE_LABEL_TRANSPARENCY"/>
                <visualProperty default="false" name="EDGE_SELECTED"/>
                <visualProperty default="true" name="EDGE_VISIBLE"/>
                <visualProperty default="#FF0000" name="EDGE_STROKE_SELECTED_PAINT"/>
                <visualProperty default="" name="EDGE_LABEL"/>
            </edge>
        </visualStyle>
    </vizmap>
    """


    return (SG_style)

"""

def path_c2t_single_ended (inchikey, target_protein, stereo=True, shortest_paths=True, max_length=4, activity_cutoff=0.0, activity_type=None, confidence_cutoff=0.0):

    conn = neo4j_utils.open_neo4j_connection()

    query = "MATCH (c:Compound)-[a:TESTED_ON]->(t1:Target)"
    
    first = True

    nsinchikey = inchikey.split('-')[0].strip()

    if activity_cutoff > 0.0:
        query+= " WHERE a.activity<=" + str(activity_cutoff)
        first = False

    if activity_type!=None:
        if first:
            query+= " WHERE a.activity_type='" + activity_type + "'"
            first = False
        else:
            query+= " AND a.activity_type='" + activity_type + "'"


    
    if first:
        query += " WHERE "
        first = False

    else:
        query += " AND "
    
    if stereo:
        query += " c.hash='" + inchikey+ "'"
    else:
        query += " c.nostereo_hash='" + nsinchikey+ "'"

    query += " WITH t1, COLLECT(c) as compounds, COLLECT(t1) as targets"

    if shortest_paths:
        query += " MATCH p1=shortestPath((t1)-[r*.." + str(max_length) + "]->(q:Target))"
    else:
        query += " MATCH p1=(t1)-[r*.." + str(max_length) + "]->(q:Target)"

    query += " WHERE q.uniprot_id='" + target_protein + "'"

    query += " AND t1.uuid<>q.uuid"

    if confidence_cutoff>0.0:
         query += " AND ALL(rel in r WHERE rel.max_confidence_value>=" + str(confidence_cutoff) + ")"
    

    query += " UNWIND compounds as x"
    query += " UNWIND targets as y"
    query += " MATCH p2=shortestPath((x)-[z:TESTED_ON]-(y))"
    query += " RETURN p1, p2"

    #print (query)

    all_nodes = []
    all_edges = []

    # Use this in conjuction with Neo4j v4.x
    #with conn.session(database="neo4j") as session:


    # Use this in conjuction with Neo4j v3.x
    with conn.session() as session:
        #print (query) 
        g = session.read_transaction(
            lambda tx: tx.run(query).graph())

      
        for n in g.nodes:
            #print("id %s labels %s props %s" % (n.id, n.labels, n.items()))
            all_nodes = extract_node_properties (n, all_nodes)


        for r in g.relationships:
            #print("id %s type %s start %s end %s props %s" % (r.id, r.type, r.start_node.id, r.end_node.id, r.items()))
            all_edges = extract_edge_properties (r, all_edges)


    #print (result)

    #print (all_nodes)
    #print (all_edges)
  
    
    G_json = {}

    G_json['nodes'] = aggregate_nodes(all_nodes)
    G_json['edges'] = aggregate_edges(all_edges)
    
    conn.close()
    
    return (G_json)
"""



# find N-length path between two targets (option: all paths or only all shortest paths)
"""
def path_regulatory_single_ended (source_protein, target_protein, shortest_paths=True, max_length=4, confidence_cutoff=0.0, directed=True):


    conn = neo4j_utils.open_neo4j_connection()

    if directed:
        if shortest_paths:
            query = "MATCH p=shortestPath((t1:Target)-[r*.." + str(max_length) + "]->(t2:Target)) WHERE t1.uniprot_id='" + source_protein + "' AND t2.uniprot_id='" + target_protein + "' AND t1.uuid<>t2.uuid"
        else:
            query = "MATCH p=(t1:Target)-[r*.." + str(max_length) + "]->(t2:Target)  WHERE t1.uniprot_id='" + source_protein + "' AND t2.uniprot_id='" + target_protein + "'"

    else:

        if shortest_paths:
            query = "MATCH p=shortestPath((t1:Target)-[r*.." + str(max_length) + "]-(t2:Target)) WHERE t1.uniprot_id='" + source_protein + "' AND t2.uniprot_id='" + target_protein + "' AND t1.uuid<>t2.uuid"

        else:
            query = "MATCH p=(t1:Target)-[r*.." + str(max_length) + "]-(t2:Target) WHERE t1.uniprot_id='" + source_protein + "' AND t2.uniprot_id='" + target_protein + "'"

    if confidence_cutoff>0.0:
        query += " AND ALL(rel in r WHERE rel.max_confidence_value>=" + str(confidence_cutoff) + ")"


    query += " RETURN p"


    print (query)

    all_nodes = []
    all_edges = []

    # Use this in conjuction with Neo4j v4.x
    #with conn.session(database="neo4j") as session:


    # Use this in conjuction with Neo4j v3.x
    with conn.session() as session:
        #print (query) 
        g = session.read_transaction(
            lambda tx: tx.run(query).graph())

      
        for n in g.nodes:
            #print("id %s labels %s props %s" % (n.id, n.labels, n.items()))
            all_nodes = extract_node_properties (n, all_nodes)


        for r in g.relationships:
            #print("id %s type %s start %s end %s props %s" % (r.id, r.type, r.start_node.id, r.end_node.id, r.items()))
            all_edges = extract_edge_properties (r, all_edges)


    #print (result)

    #print (all_nodes)
    #print (all_edges)
  
    
    G_json = {}

    G_json['nodes'] = aggregate_nodes(all_nodes)
    G_json['edges'] = aggregate_edges(all_edges)
    
    conn.close()
    
    return (G_json)
"""

