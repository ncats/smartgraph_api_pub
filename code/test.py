# Author: Gergely Zahoranszky-Kohalmi, PhD
#
# Organization: National Center for Advancing Translational Sciences (NCATS/NIH)
#
# Email: gergely.zahoranszky-kohalmi@nih.gov
#
#
#
# References


import smartgraph as sg


target_protein = 'P11509'
activity_cutoff = 0.001
#activity_type = None
activity_type = 'activity'


res_json = sg.bioactivity_target (target_protein, activity_cutoff, activity_type)

print (res_json)



print ('\n\n\n')

res_json = sg.potent_compounds (target_protein, activity_type)


print (res_json)


res_json = sg.smiles_compound ('JUZUBCBEFKWHQP-UHFFFAOYSA-N', stereo = True)

print (res_json)

res_json = sg.smiles_compound ('JUZUBCBEFKWHQP-UHFFFAOYSA-N', stereo = False)

print (res_json)



res_json = sg.smiles_pattern ('scaffold.100077')

print (res_json)


res_json = sg.bioactivity_compound ('GKXFMVMVFTYRCV-UHFFFAOYSA-N', stereo = True, activity_cutoff = 0, activity_type = None)

print (res_json)


res_json = sg.bioactivity_c2t ('GKXFMVMVFTYRCV-UHFFFAOYSA-N', 'P11509', stereo = True, activity_type = None)

print (res_json)



res_json = sg.path_c2t ('OXAZEQNCEUDROZ-UHFFFAOYSA-N', 'P08581', stereo=True, shortest_paths=True, max_length=2, activity_cutoff=0.0, activity_type=None, confidence_cutoff=0.1)

print (res_json)


res_json = sg.path_c2t ('OXAZEQNCEUDROZ-UHFFFAOYSA-N', 'P08581', stereo=True, shortest_paths=False, max_length=2, activity_cutoff=0.0, activity_type=None, confidence_cutoff=0.1)

print (res_json)


#res_json = sg.path_regulatory_single_ended ('Q13315', 'P10636', shortest_paths=True, max_length=5, confidence_cutoff=0.0, directed=False)
#print (res_json)

res_json = sg.path_regulatory ('Q13315', 'P10636', shortest_paths=True, max_length=5, confidence_cutoff=0.0, directed=False)

print (res_json)

res_json = sg.path_regulatory_open ('Q13315', shortest_paths=True, max_length=2, explore_mode='undirected', confidence_cutoff=0.0)

print (res_json)



res_json = sg.patterns_of_compounds ('DOCNVAAXJTVMNS-VMPITWQZSA-N', stereo=True, pattern_type='scaffold', min_ratio=0.5, is_largest=True)

print (res_json)



res_json = sg.potent_patterns ('Q13315', pattern_type='scaffold')

print (res_json)




res_json = sg.subgraph_compound_induced ('OXAZEQNCEUDROZ-UHFFFAOYSA-N', stereo=True, shortest_paths=True, max_length=3)

print (res_json)

res_json = sg.subgraph_target_induced ('Q13315', endpoint_type='both', shortest_paths=True, max_length=2, explore_mode='source')

print (res_json)


res_json = sg.predict ('P49841', limit=300)

print (res_json)


