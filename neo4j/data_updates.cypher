CALL apoc.periodic.iterate(
  "MATCH ()-[r:TESTED_ON]->() WHERE r.activity IS NOT NULL RETURN r",
  "SET r.activity = toFloat(r.activity)",
  {batchSize:1000, parallel:false, iterateList:true}
)

CALL apoc.periodic.iterate(
  "MATCH ()-[r:PATTERN_OF]->() WHERE r.islargest IS NOT NULL RETURN r ",
  "SET r.islargest = CASE WHEN toLower(r.islargest) = 'true' THEN true ELSE false END",
  {batchSize:1000, parallel:false, iterateList:true}
)

CALL apoc.periodic.iterate(
  "MATCH ()-[r:PATTERN_OF]->() WHERE r.ratio IS NOT NULL RETURN r ",
  "SET r.ratio = toFloat(r.ratio)",
  {batchSize:1000, parallel:false, iterateList:true}
)

CALL apoc.periodic.iterate(
  "MATCH ()-[r:REGULATES]->() WHERE r.max_confidence_value IS NOT NULL RETURN r ",
  "SET r.max_confidence_value = toFloat(r.max_confidence_value)",
  {batchSize:1000, parallel:false, iterateList:true}
)

CALL apoc.periodic.iterate(
    "MATCH (n:Target) WHERE n.gene_symbols IS NOT NULL RETURN n",
    "SET n.gene_symbols = apoc.text.split(replace(replace(n.gene_symbols, ']', ''), '[', ''), ',')
     SET n.gene_symbols = [item in n.gene_symbols | trim(replace(item, '\"', ''))]",
    {batchSize:1000, parallel:false, iterateList:true}
)

CALL apoc.periodic.iterate(
    "MATCH (n:Target) WHERE n.synonyms IS NOT NULL RETURN n",
    "SET n.synonyms = apoc.text.split(replace(replace(n.synonyms, ']', ''), '[', ''), ',')
     SET n.synonyms = [item in n.synonyms | trim(replace(item, '\"', ''))]",
    {batchSize:1000, parallel:false, iterateList:true}
)