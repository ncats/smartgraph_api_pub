# Author: Gergely Zahoranszky-Kohalmi, PhD
#
# Email: gergely.zahoranszky-kohalmi@nih.gov
#
# Organization: National Center for Advancing Translational Sciences (NCATS/NIH)
#
# 
#
# References
#
#
# Ref: https://www.rdkit.org/docs/source/rdkit.Chem.Scaffolds.MurckoScaffold.html
# Ref: https://realpython.com/python-sleep/
# Ref: https://fastapi.tiangolo.com/
# Ref: https://dev.to/ruarfff/understanding-python-async-with-fastapi-42hn
# Ref: https://github.com/tiangolo/fastapi/issues/1728
# Ref: https://github.com/tiangolo/fastapi/issues/1009
# Ref: https://fastapi.tiangolo.com/sq/tutorial/path-params/#create-an-enum-class
# Ref: https://www.freecodecamp.org/news/python-json-how-to-convert-a-string-to-json/
# Ref: https://networkx.org/documentation/stable/reference/readwrite/generated/networkx.readwrite.graphml.generate_graphml.html#networkx.readwrite.graphml.generate_graphml
# Ref: https://www.adamsmith.haus/python/answers/how-to-check-if-a-variable-is-a-list-in-python
# Ref: https://fastapi.tiangolo.com/advanced/response-directly/
#



from typing import Union
from typing import Any

from fastapi import FastAPI, Response, APIRouter

from enum import Enum

import orjson
import uvicorn

#import endpoint
#from endpoint import *

import smartgraph as sg


import os
import pandas as pd


class ExportFormat(str, Enum):
    json = "json"
    graphml = "graphml"

class ExplorationMode(str, Enum):
    source = "source"
    target = "target"
    undirected = "undirected"


class EndNodeType(str, Enum):
    compound = "compound"
    target = "target"
    both = "both"



class CustomORJSONResponse(Response):
    media_type = "application/json"
    
    def render(self, content: Any) -> bytes:
        assert orjson is not None, "orjson must be installed"
        return orjson.dumps(content, option=orjson.OPT_INDENT_2)


smartgraphUiUrl = os.environ['SMARTGRAPH_UI_URL'] or 'https://smartgraph-ui.ncats.nih.gov'
smartgraphApiSwaggerUrl = os.environ['SMARTGRAPH_API_SWAGGER_URL'] or 'https://smartgraph-api.ncats.nih.gov/docs'

# Base URL for the API
base_path = os.environ['SMARTGRAPH_API_BASE_PATH'] or '/'

app = FastAPI(title='SmartGraph API',
    description=f'API functionality for the SmartGraph network-pharmacology investigation platform.<BR><BR>Publication: [https://jcheminf.biomedcentral.com/articles/10.1186/s13321-020-0409-9](https://jcheminf.biomedcentral.com/articles/10.1186/s13321-020-0409-9)<BR><BR>SmartGraph Webapp: [{smartgraphUiUrl}]({smartgraphUiUrl})<BR><BR>SmartGraph API Swagger: [{smartgraphApiSwaggerUrl}]({smartgraphApiSwaggerUrl})',
    docs_url=f'{base_path}/docs',
    redoc_url=f'{base_path}/redoc',
    openapi_url=f'{base_path}/openapi.json',
    debug=True
)

router = APIRouter(prefix=base_path)





@router.get("/cite", response_class=CustomORJSONResponse, tags=["About"])
def cite ():
	return (sg.cite())


@router.get("/bibtex", response_class=CustomORJSONResponse, tags=["About"])
def cite ():
	return (sg.bibtex())
    

@router.get("/version", response_class=CustomORJSONResponse, tags=["About"])
def version ():
	return ({'SmartGraph API v1'})

@router.get("/bioactivity_target/{target_uniprot_ids}", response_class=CustomORJSONResponse, tags=["Bioactivities"])
def bioactivity_target (target_uniprot_ids: str, activity_cutoff: Union[float, None] = 0.0, activity_type: Union [str, None] = None, format: Union[ExportFormat, None] = ExportFormat.json):
    """
		Returns a graph containing the requested target protein, and all compounds that have an activity value reported for the given target.


        - Arguments:
	   
        - `target_uniprot_ids`: UniProt IDs of the target protein. Example UniProt ID: P11509. Comma-separated list. It's possible to provide a single value without any commas.
        
        - `activity_cutoff`: report activites that are equal to or lower than the provided value (unit: uM). If set to 0 (default), then no cutoff is applied.
        
        - `activity_type`: only consider the provided type of bioactivity

    """
    res_json = sg.bioactivity_target (target_uniprot_ids, activity_cutoff, activity_type, format)
    
    if format == ExportFormat.graphml:
        return (Response(content = res_json, media_type = 'application/xml'))
    
    return (res_json)


@router.get("/bioactivity_compound/{inchikeys}", response_class=CustomORJSONResponse, tags=["Bioactivities"])
def bioactivity_compound (inchikeys: str, stereo: Union[bool, None] = True, activity_cutoff: Union[float, None] = 0.0, activity_type: Union[str, None] = None, format: Union[ExportFormat, None] = ExportFormat.json):
    """
		Returns a graph containing the requested compound, and all target proteins that have an activity value reported for the given compound.


        - Arguments:
        
        - `inchikeys`: Comma-separated list of InChI-Keys of compounds. Example: GKXFMVMVFTYRCV-UHFFFAOYSA-N . It's possible to provide a single value without any commas.
                    Note, that you can also provide the "non-stereo InChIKey", e.g. in the above example: GKXFMVMVFTYRCV. In this case, 
                    make sure to set the `stereo` argument to `False`.

        - `stereo`:  Boolean. If True, then the provided `inchikey` argument will subject to exact match. If set to `False`, then
                   only the first section of the `inchikey` will be matched. Default: `True`.

        - `activity_cutoff`: report activites that are equal to or lower than the provided value (unit: uM). If set to 0 (default), then no cutoff is applied.

        - `activity_type`: only consider the provided type of bioactivity


    """

    res_json = sg.bioactivity_compound (inchikeys, stereo, activity_cutoff, activity_type, format)

    if format == ExportFormat.graphml:
        return (Response(content = res_json, media_type = 'application/xml'))


    return (res_json)


@router.get("/bioactivity_c2t/{inchikeys}/{uniprot_ids}", response_class=CustomORJSONResponse, tags=["Bioactivities"])
def bioactivity_c2t (inchikeys:str, uniprot_ids: str, stereo: Union[bool, None] = True, activity_type: Union[str, None] = None, format: Union[ExportFormat, None] = ExportFormat.json):
    """
		Returns a graph containing the requested compound, and all target proteins that have an activity value reported for the given compound.


        - Arguments:
        
        - `inchikey`: Comma-separated list of InChI-Key of compounds. Example: GKXFMVMVFTYRCV-UHFFFAOYSA-N . It's possible to provide a single value without any commas.
                    Note, that you can also provide the "non-stereo InChIKey", e.g. in the above example: GKXFMVMVFTYRCV. In this case, 
                    make sure to set the `stereo` argument to `False`.

        - `uniprot_ids`: Comma-separated list of UniProt IDs of the target proteins. Example UniProt ID: P11509 . It's possible to provide a single value without any commas.

        - `stereo`:  Boolean. If True, then the provided `inchikey` argument will subject to exact match. If set to `False`, then
                   only the first section of the `inchikey` will be matched. Default: `True`.

        - `activity_type`: only consider the provided type of bioactivity
    """

    res_json = sg.bioactivity_c2t (inchikeys, uniprot_ids, stereo, activity_type, format)

    if format == ExportFormat.graphml:
        return (Response(content = res_json, media_type = 'application/xml'))


    return (res_json)


@router.get("/potent_compounds/{uniprot_ids}", response_class=CustomORJSONResponse, tags=["Bioactivities"])
def potent_compounds (uniprot_ids: str, activity_type: Union[str, None] = None, format: Union[ExportFormat, None] = ExportFormat.json):
    """
 		Returns the 'potent compounds' of the target. Potent compounds are defined within the scope of SmartGraph.


         - Arguments:

         - `uniprot_ids`: UniProt IDs of the target protein. Comma-separated list. Example UniProt ID: P11509. It's possible to submit a value without any commas.

         - `activity_type`: only consider the provided type of bioactivity
    """
    
    res_json = sg.potent_compounds (uniprot_ids, activity_type, format)

    if format == ExportFormat.graphml:
        return (Response(content = res_json, media_type = 'application/xml'))


    return (res_json)


@router.get("/predict/{uniprot_id}", response_class=CustomORJSONResponse, tags=["Prediction"])
def predict (uniprot_id: str, limit: Union [int, None]=300, format: Union[ExportFormat, None] = ExportFormat.json):
    """
        Computes "potent pattern"-based bioactivity predictions. This can be used in a drug repositioning setting.

        - Arguments:

        - `uniprot_id`: UniProt ID of the protein target to compute predictions for. Example UniProt ID: P49841 .

    """

    res_json = sg.predict (uniprot_id, limit = limit, format = format)

    if format == ExportFormat.graphml:
        return (Response(content = res_json, media_type = 'application/xml'))



    return (res_json)



@router.get("/path_c2t/{inchikeys}/{uniprot_ids}", response_class=CustomORJSONResponse, tags=["Path Search"])
def path_c2t (inchikeys: str, uniprot_ids: str, stereo: Union [bool, None]=True, shortest_paths: Union[bool, None]=True, max_length: Union[int, None]=2, activity_cutoff: Union[float, None]=0.0, activity_type: Union[str, None]=None, confidence_cutoff: Union[float, None]=0.0, format: Union[ExportFormat, None] = ExportFormat.json):
    """
		Finds paths (via compound-target bioactivity and target-target regulatory relationships) between a set of compounds and a set of target proteins.


        - Arguments:
        
        - `inchikeys`: Comma-separated list of InChI-Keys of compounds. Example: OXAZEQNCEUDROZ-UHFFFAOYSA-N .  It also takes a single value without any comma.
                    Note, that you can also provide the "non-stereo InChIKey", e.g. in the above example: OXAZEQNCEUDROZ. In this case, 
                    make sure to set the `stereo` argument to `False`.

        - `uniprot_ids`: Comma-separated list of UniProt IDs of the target proteins. Example UniProt ID: P08581 . It also takes a single value without any comma.

        - `stereo`:  Boolean. If True, then the provided `inchikey` argument will subject to exact match. If set to `False`, then
                   only the first section of the `inchikey` will be matched. Default: `True`.

        - `shortest_paths`:  Boolean. If `True`, then the shortest paths will be returned. Otherwise, all paths between the compound and the target. Default: `True`.

        - `max_length`:  Integer. The maiximal number of edges between the provided compound and the target.

        - `activity_cutoff`: report activites that are equal to or lower than the provided value (unit: uM). If set to 0 (default), then no cutoff is applied.

        - `activity_type`: only consider the provided type of bioactivity

        - `confidence_cutoff`: only consider regulatory edges of confidence greater than equal to the provided value

    """

    res_json = sg.path_c2t (inchikeys, uniprot_ids, stereo, shortest_paths, max_length, activity_cutoff, activity_type, confidence_cutoff, format)



    if format == ExportFormat.graphml:
        return (Response(content = res_json, media_type = 'application/xml'))


    return (res_json)



@router.get("/path_regulatory/{source_uniprot_ids}/{target_uniprot_ids}", response_class=CustomORJSONResponse, tags=["Path Search"])
def path_regulatory (source_uniprot_ids: str, target_uniprot_ids: str, shortest_paths: Union[bool, None]=True, max_length: Union[int, None]=4, confidence_cutoff: Union[float, None]=0.0, directed: Union[bool, None]=True, format: Union[ExportFormat, None] = ExportFormat.json):
    """
        Find regulatory pathway between two sets of protein (sources and targets).

        - Arguments:
        

        - `source_uniprot_ids`: Comma separated list of UniProt IDs of the source proteins. Example UniProt ID: Q13315 . It also takes a single value without any comma.

        - `target_uniprot_ids`: Comma separated list of UniProt IDs of the target proteins. Example UniProt ID: P10636 . It also takes a single value without any comma.

        - `shortest_paths`:  Boolean. If `True`, then the shortest paths will be returned. Otherwise, all paths between the compound and the target. Default: `True`.

        - `max_length`:  Integer. The maiximal number of edges between the provided compound and the target. Default: 4 .

        - `confidence_cutoff`: only consider regulatory edges of confidence greater than equal to the provided value

        - `directed`: Boolean. If set to `False`, the network will be treated as undirected . Default: directed network, i.e. `True`.


    """


    res_json = sg.path_regulatory (source_uniprot_ids, target_uniprot_ids, shortest_paths, max_length, confidence_cutoff, directed, format)

    if format == ExportFormat.graphml:
        return (Response(content = res_json, media_type = 'application/xml'))
    
    return (res_json)



@router.get("/path_regulatory_open/{uniprot_ids}", response_class=CustomORJSONResponse, tags=["Path Search"])
def path_regulatory_open (uniprot_ids, shortest_paths: Union[bool, None]=True, max_length: Union[int, None]=2, explore_mode: Union[ExplorationMode, None]=ExplorationMode.undirected, confidence_cutoff: Union[float, None]=0.0, format: Union[ExportFormat, None] = ExportFormat.json):
    """
        Find "open ended" regulatory pathway that start/end in any of the provided protein targets, reachable in distance=`max_length`.


        - Arguments:
        

        - `uniprot_ids`: Comma separated list of UniProt IDs of the protein targets. Example UniProt ID: Q13315 . It also takes a single value without any comma.

        - `shortest_paths`:  Boolean. If `True`, then the shortest paths will be returned. Otherwise, all paths between the compound and the target. Default: `True`.

        - `max_length`:  Integer. The maiximal number of edges between the provided compound and the target. Default: 4 .

        - `explore_mode`: Enum ['undirected', 'source', 'target']

            - 'undirected': finds all paths that are reacheable from the target proteins in `max_length` of steps, regardless of the direction of the edges
            - 'source': finds all paths starting from the provided protein targets that are reacheable within `max_length` of steps
            - 'target': finds all paths ending in the provided protein targets and are at most `max_length` length

        - `confidence_cutoff`: only consider regulatory edges of confidence greater than equal to the provided value



    """
    
    res_json = sg.path_regulatory_open (uniprot_ids, shortest_paths, max_length, explore_mode, confidence_cutoff, format)

    if format == ExportFormat.graphml:
        return (Response(content = res_json, media_type = 'application/xml'))

    return (res_json)


@router.get("/subgraph_target_induced/{uniprot_ids}", response_class=CustomORJSONResponse, tags=["Subgraphs"])
def subgraph_target_induced (uniprot_ids: str, endnode_type: Union[EndNodeType, None]=EndNodeType.both, shortest_paths: Union[bool, None]=True, max_length: Union[int, None]=4, explore_mode: Union[ExplorationMode, None]=ExplorationMode.undirected, format: Union[ExportFormat, None] = ExportFormat.json):
    """
        Extracts a subgraph induced by a set of provided protein targets so that these targets are one endpoints of paths that end in compounds/targets/both, and the lengths of paths is <= `max_length`.

        - Arguments:
        

        - `uniprot_ids`: Comma separated list of UniProt IDs of the protein targets. Example UniProt ID: Q13315 . It also takes a single value without any comma.

        - `endnode_type`:
            - 'compound': endpoints are compounds
            - 'target': endpoints are targets
            - 'both': endpoints are either compounds or targets

        - `shortest_paths`:  Boolean. If `True`, then the shortest paths will be returned. Otherwise, all paths between the compound and the target. Default: `True`.

        - `max_length`:  Integer. The maximal number of edges between the provided compound and the target. Default: 4 .

        - `explore_mode`: Enum ['undirected', 'source', 'target']

            - 'undirected': finds all paths that are reacheable from the target proteins in `max_length` of steps, regardless of the direction of the edges
            - 'source': finds all paths starting from the provided protein targets that are reacheable within `max_length` of steps
            - 'target': finds all paths ending in the provided protein targets and are at most `max_length` length

    """

    res_json = sg.subgraph_target_induced (uniprot_ids, endnode_type, shortest_paths, max_length, explore_mode, format)
 
    if format == ExportFormat.graphml:
        return (Response(content = res_json, media_type = 'application/xml'))
   
    return (res_json)


@router.get("/subgraph_compound_induced/{inchikeys}", response_class=CustomORJSONResponse, tags=["Subgraphs"])
def subgraph_compound_induced (inchikeys: str, stereo: Union[bool, None]=True, shortest_paths: Union[bool, None]=True, max_length: Union[int, None]=4, format: Union[ExportFormat, None] = ExportFormat.json):
    """
        Extracts a subgraph induced by a set of provided compounds so that paths starting from them are of length <= `max_length`.

        - Arguments:
        

        - `inchikey`: Comma-separated list of InChI-Keys of compounds. Example: OXAZEQNCEUDROZ-UHFFFAOYSA-N .  It also takes a single value without any comma.
                    Note, that you can also provide the "non-stereo InChIKey", e.g. in the above example: OXAZEQNCEUDROZ. In this case, 
                    make sure to set the `stereo` argument to `False`.

        - `stereo`:  Boolean. If True, then the provided `inchikey` argument will subject to exact match. If set to `False`, then
                   only the first section of the `inchikey` will be matched. Default: `True`.

        - `shortest_paths`:  Boolean. If `True`, then the shortest paths will be returned. Otherwise, all paths between the compound and the target. Default: `True`.

        - `max_length`:  Integer. The maiximal number of edges between the provided compound and the target. Default: 4 .


    """

    res_json = sg.subgraph_compound_induced (inchikeys, stereo, shortest_paths, max_length, format)

    if format == ExportFormat.graphml:
        return (Response(content = res_json, media_type = 'application/xml'))

    return (res_json)


@router.get("/patterns_of_compounds/{inchikeys}", response_class=CustomORJSONResponse, tags=["Subgraphs"])
def patterns_of_compounds (inchikeys: str, stereo: Union[bool, None]=True, pattern_type='scaffold', min_ratio: Union[float, None]=0.0, is_largest: Union[bool, None]=None, format: Union[ExportFormat, None] = ExportFormat.json):
    """
        Returns the patterns associated with provided compounds.

        - Arguments:
        

        - `inchikey`: Comma-separated list of InChI-Keys of compounds. Example: OXAZEQNCEUDROZ-UHFFFAOYSA-N .  It also takes a single value without any comma.
                    Note, that you can also provide the "non-stereo InChIKey", e.g. in the above example: OXAZEQNCEUDROZ. In this case, 
                    make sure to set the `stereo` argument to `False`.

        - `stereo`:  Boolean. If True, then the provided `inchikey` argument will subject to exact match. If set to `False`, then
                   only the first section of the `inchikey` will be matched. Default: `True`.

        - `pattern_type`:  String. Default: scaffold, which means Bemis-Murcko Scaffold [Bemis GW, Murcko MA (1996) The properties of known drugs 1 Molecular frameworks. J Med Chem 39(15):2887–2893] 

        - `min_ratio`:  Float [0.0, 1.0]. Return patterns of minimal overlap ratio between the pattern and the compound, based on heavy atom count. Default: 0.0.

        - `is_largest`:  Boolean. If `True`, then only return the largest scaffold. This is relevant if hierarchical scaffolds (HierS) are generated. [Wilkens SJ, Janes J, Su AI (2005) HierS: hierarchical scaffold clustering using topological chemical graphs. J Med Chem 48(9):3182–3193, Jeremy JY. Google Code open source project, unm-biocomp-hscaf, Java library for HierS chemical scaffolds] Default: None, i.e. this is not taken into account by defult.


    """

    res_json = sg.patterns_of_compounds (inchikeys, stereo, pattern_type, min_ratio, is_largest, format)

    if format == ExportFormat.graphml:
        return (Response(content = res_json, media_type = 'application/xml'))

    return (res_json)


@router.get("/potent_patterns/{uniprot_ids}", response_class=CustomORJSONResponse, tags=["Bioactivities"])
def potent_patterns (uniprot_ids: str, pattern_type: Union[str, None]='scaffold', format: Union[ExportFormat, None] = ExportFormat.json):
    """
        Returns the potent patterns of provided target proteins. Potent patterns are defined in context of SmartGraph.

        - Arguments:
        

        - `uniprot_ids`: Comma separated list of UniProt IDs of the protein targets. Example UniProt ID: Q13315 . It also takes a single value without any comma.

        - `pattern_type`:  String. Default: scaffold, which means Bemis-Murcko Scaffold [Bemis GW, Murcko MA (1996) The properties of known drugs 1 Molecular frameworks. J Med Chem 39(15):2887–2893] 

    """


    res_json = sg.potent_patterns (uniprot_ids, pattern_type, format)

    if format == ExportFormat.graphml:
        return (Response(content = res_json, media_type = 'application/xml'))

    return (res_json)


@router.get("/smiles_compound/{inchikey}", response_class=CustomORJSONResponse, tags=["Utilities"])
def smiles_compound (inchikey: str, stereo: Union[bool, None]=True):
    """
		Returns the SMILES of a compound based on its InChI-Key.


        - Arguments:
        
        - `inchikey`: InChI-Key of the compound. Example: OXAZEQNCEUDROZ-UHFFFAOYSA-N .
                    Note, that you can also provide the "non-stereo InChIKey", e.g. in the above example: OXAZEQNCEUDROZ. In this case, 
                    make sure to set the `stereo` argument to `False`.


        - `stereo`:  Boolean. If True, then the provided `inchikey` argument will subject to exact match. If set to `False`, then
                   only the first section of the `inchikey` will be matched. Default: `True`.
    """

    res_json = sg.smiles_compound (inchikey, stereo)
    
    return (res_json)


@router.get("/smiles_pattern/{pattern_id}", response_class=CustomORJSONResponse, tags=["Utilities"])
def smiles_pattern (pattern_id: str):
    """
		Returns the SMILES of a compound based on its InChI-Key.


        - Arguments:
        
        - `pattern_id`: Pattern ID of the pattern. The patttern is an abstract structure, e.g. Bemis-Murcko Scaffold [Bemis GW, Murcko MA (1996) The properties of known drugs 1 Molecular frameworks. J Med Chem 39(15):2887–2893] . Example: scaffold.100077 


    """
    
    res_json = sg.smiles_pattern (pattern_id)
    
    return (res_json)



@router.get("/sg_stlye", response_class=CustomORJSONResponse, tags=["Utilities"])
def sg_style_compound ():
    """
        Returns the SmartGraph style for Cytoscape.

    """

    res_json = sg.get_sg_style ()

    return (Response(content = res_json, media_type = 'application/xml'))


app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(app,host='0.0.0.0', port=int(os.environ['sg_api_int_port']))
