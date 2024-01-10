echo "Get citation"
echo " "
echo " "
curl -X GET "http://127.0.0.1:5070/cite"
echo " "
echo " "
echo "Get bibtext"
echo " "
echo " "
curl -X GET "http://127.0.0.1:5070/bibtex"
echo " "
echo " "
echo "Get version"
echo " "
echo " "
curl -X GET "http://127.0.0.1:5070/version"
echo " "
echo " "
echo "Get a graph containing the requested target protein, and all compounds that have an activity value reported for the given target."
echo " "
echo " "
curl -X GET "http://127.0.0.1:5070/bioactivity_target/P11509?activity_cutoff=0&activity_type=activity" 
echo " "
echo " "
echo "Get a graph containing the requested compound, and all target proteins that have an activity value reported for the given compound."
echo " "
echo " "
curl -X GET "http://127.0.0.1:5070/bioactivity_compound/GKXFMVMVFTYRCV-UHFFFAOYSA-N?activity_cutoff=0&activity_type=activity" 
echo " "
echo " "
echo "Get a graph containing the requested compound, and all target proteins that have an activity value reported for the given compound."
echo " "
echo " "
curl -X GET "http://127.0.0.1:5070/bioactivity_c2t/GKXFMVMVFTYRCV-UHFFFAOYSA-N/P11509?activity_cutoff=0&activity_type=activity" 
echo " "
echo " "
echo "Returns the 'potent compounds' of the target. Potent compounds are defined within the scope of SmartGraph."
echo " "
echo " "
curl -X GET "http://127.0.0.1:5070/potent_compounds/P11509?activity_type=activity" 
echo " "
echo " "
echo "Get "potent pattern"-based bioactivity predictions. This can be used in a drug repositioning setting."
echo " "
echo " "
curl -X GET "http://127.0.0.1:5070/predict/P11509" 
echo " "
echo " "
echo "Get paths (via compound-target bioactivity and target-target regulatory relationships) between a set of compounds and a set of target proteins."
echo " "
echo " "
curl -X GET "http://127.0.0.1:5070/path_c2t/OXAZEQNCEUDROZ-UHFFFAOYSA-N/P08581?max_length=100&activity_cutoff=0&activity_type=activity" 
echo " "
echo " "
echo "Get regulatory pathway between two sets of protein (sources and targets)."
echo " "
echo " "
curl -X GET "http://127.0.0.1:5070/path_regulatory/Q13315/P10636?max_length=100&directed=True&confidence_cutoff=.1" 
echo " "
echo " "
echo "Get "open ended" regulatory pathway that start/end in any of the provided protein targets, reachable in distance=`max_length`."
echo " "
echo " "
curl -X GET "http://127.0.0.1:5070/path_regulatory_open/Q13315?max_length=100&confidence_cutoff=.1" 
echo " "
echo " "
echo "Get a subgraph induced by a set of provided protein targets so that these targets are one endpoints of paths that end in compounds/targets/both, and the lengths of paths is <= `max_length`."
echo " "
echo " "
curl -X GET "http://127.0.0.1:5070/subgraph_target_induced/Q13315?max_length=1&endnode_type=compound" 
echo " "
echo " "
echo "Get a subgraph induced by a set of provided compounds so that paths starting from them are of length <= `max_length`."
echo " "
echo " "
curl -X GET "http://127.0.0.1:5070/subgraph_compound_induced/OXAZEQNCEUDROZ-UHFFFAOYSA-N?max_length=4" 
echo " "
echo " "
echo "Get the patterns associated with provided compounds."
echo " "
echo " "
curl -X GET "http://127.0.0.1:5070/patterns_of_compounds/OXAZEQNCEUDROZ-UHFFFAOYSA-N?pattern_type=scaffold" 
echo " "
echo " "
echo "Get the potent patterns of provided target proteins. Potent patterns are defined in context of SmartGraph."
echo " "
echo " "
curl -X GET "http://127.0.0.1:5070/potent_patterns/Q13315?pattern_type=scaffold" 
echo " "
echo " "
echo "Get the SMILES of a compound based on its scaffold pattern."
echo " "
echo " "
curl -X GET "http://127.0.0.1:5070/smiles_pattern/scaffold.100077" 
echo " "
echo " "
echo "Get the SmartGraph style for Cytoscape."
echo " "
echo " "
curl -X GET "http://127.0.0.1:5070/sg_stlye" 
echo " "
echo " "