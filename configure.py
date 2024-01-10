# Author:   Gergely Zahoranszky-Kohalmi, PhD
#
# Email: gergely.zahoranszky-kohalmi@nih.gov
#
# Organization: National Center for Advancing Translational Sciences (NCATS/NIH)
#
# Unit Tests for the AICP API
#
#
# References
#
# Ref: https://www.geeksforgeeks.org/taking-input-in-python/
#

import sys

fname_urls = '.all_urls_env'
fname_conf = '.all_config_env'


fname_out = '.env'

neo4j_context = None
urls_context = None
testing_context = None


parameters = {}


deployment_type = None
db_instance = None

docker_file_to_deploy = None

# All scenarios use the same docker-compose file, this datastructure is kept here, should there be need to use multiple docker-compose files in the future.
docker_types = {'local': 'docker-compose.yml',
                'ci': 'docker-compose.yml',
                'qa': 'docker-compose.yml',
                'prod': 'docker-compose.yml'
}




def parse_context_dependent_parameters (context, fname, parameters):
    prefix = context + '_'

    tmp = []
    k = None
    v = None


    fp = open (path_to_envs + '/' + fname, 'r')

    line = fp.readline ()

    while line:

        if line.startswith (prefix) and not line.startswith('#'):
            tmp = line.split('=')

            k = tmp[0].strip()[len(prefix):]
            v = '='.join(tmp[1:]).strip()

            parameters[k] = v


        line = fp.readline ()

    fp.close()

    return (parameters)



def write_parameters (parameters, fname):
    fp = open (fname, 'w+')

    for k in parameters.keys():
        fp.write(k + '=' + parameters[k] + '\n')

    fp.close()



if len(sys.argv) < 2:
    raise Exception ('\n\n[SYNTAX] python configure.py <path_to_environment_template_files (w/o trailing slash)>\n\n')

path_to_envs = sys.argv[1]


deployment_type = input("\n\n[Q] What type of deployment is performed [ local | ci | qa | prod ]: ")

parameters = parse_context_dependent_parameters ('invariant', fname_urls, parameters)
parameters = parse_context_dependent_parameters ('invariant', fname_conf, parameters)
    

if deployment_type == 'local':
    print ('\n[*] Local deployment selected.\n')

    docker_file_to_deploy = docker_types['local']

    parameters = parse_context_dependent_parameters ('local', fname_urls, parameters)
    parameters = parse_context_dependent_parameters ('local', fname_conf, parameters)


elif deployment_type == 'ci':
    print ('\n[*] CI deployment selected.\n')

    docker_file_to_deploy = docker_types['ci']

    parameters = parse_context_dependent_parameters ('ci', fname_urls, parameters)
    parameters = parse_context_dependent_parameters ('ci', fname_conf, parameters)



elif deployment_type == 'prod':
    print ('\n[*] !!! PROD !!! deployment selected.\n')

    docker_file_to_deploy = docker_types['prod']


    parameters = parse_context_dependent_parameters ('prod', fname_urls, parameters)
    parameters = parse_context_dependent_parameters ('prod', fname_conf, parameters)



else:
    raise Exception('\n\n[ERROR] Invalid deployment type provided. Valid options: [ local | ci | qa | prod ] .\n\n')




write_parameters (parameters, fname_out)


print ('\n\nEnvironment file was created. To compile the Docker containers respective to the requested environment, please run:\n\ndocker compose -f ' + docker_file_to_deploy + ' build --parallel\n\nThen,\n\ndocker compose -f ' + docker_file_to_deploy + ' up -d\n\n')

