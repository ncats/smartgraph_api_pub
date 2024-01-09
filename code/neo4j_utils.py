# Author: Gergely Zahoranszky-Kohalmi, PhD
#
# Organization: National Center for Advancing Translational Sciences (NCATS/NIH)
#
# Email: gergely.zahoranszky-kohalmi@nih.gov
#
#
#
# References
#
#

import neo4j
from neo4j import GraphDatabase


###
### Init Neo4j connection section
###

import os

def read_neo4j_config():
        db_par = {}
        db_par['host'] = os.environ['neo4j_host']
        db_par['port'] = os.environ['neo4j_port_bolt']
        db_par['user'] = os.environ['neo4j_user']
        db_par['pwd'] = os.environ['neo4j_password']

        return (db_par)


def open_neo4j_connection ():
    conn_pars = read_neo4j_config ()

    neo4j_uri = "bolt://" + conn_pars['host'] + ":" + conn_pars['port']
    
    conn = GraphDatabase.driver(neo4j_uri, auth=(conn_pars['user'], conn_pars['pwd']), max_connection_lifetime=1000)

    return (conn)