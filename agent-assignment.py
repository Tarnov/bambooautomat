import os
import re
import sys
import requests
import configparser
import urllib3


def check_response(response, status_code=200):
    if response.status_code == status_code:
        return True
    else:
        print('Fail "%s": %s' % (response.url, str(response.status_code)))
        print(response.content)
        exit(1)


urllib3.disable_warnings()
arg_ptrn = re.compile(r'(.*?)=(.*)')
config_args = configparser.ConfigParser()
for arg in sys.argv:
    if '=' in arg:
        arg_result = arg_ptrn.search(arg)
        config_args['DEFAULT'][arg_result.group(1)] = arg_result.group(2)

config_global_file = os.path.join(config_args['DEFAULT']['config_dir'], '.global.ini')
config = configparser.ConfigParser()
config.read([config_global_file], encoding='utf-8')
for section_arg in config_args.sections():
    for (key, val) in config_args.items(section_arg):
        config_args[section_arg][key] = val
for (key, val) in config_args.items('DEFAULT'):
    config['DEFAULT'][key] = val

user = config['DEFAULT']['service_user_name']
password = config['DEFAULT']['service_user_pass']
bamboo_rest_url = config['DEFAULT']['bamboo_base_url'] + '/rest/api/latest'
dry_run = config.getboolean('DEFAULT', 'dry_run', fallback=False)
agents_ptrn = re.compile(config['DEFAULT']['agents_ptrn'])
assignment_type = config['DEFAULT']['assignment_type']

requests_session = requests.Session()
requests_session.verify = False
requests_session.auth = (user, password)

entities = {}

if assignment_type == 'PLAN':
    build_full_key = config['DEFAULT']['build_full_key']
    build_name_url = "%s/plan/%s.json" % (bamboo_rest_url, build_full_key)
    build_name_response = requests_session.get(build_name_url)
    check_response(build_name_response)
    build_json = build_name_response.json()
    build_name = "%s %s" % (build_json['projectName'], build_json['buildName'])

    entity_id_url = "%s/agent/assignment/search?searchTerm=%s&entityType=%s&executorType=AGENT" % (
                        bamboo_rest_url, build_name, assignment_type)
    entity_id_response = requests_session.get(entity_id_url)
    check_response(entity_id_response)

    for entity in entity_id_response.json()["searchResults"]:
        if entity["id"] == build_full_key:
            entities[entity["searchEntity"]["id"]] = build_name

if assignment_type == 'DEPLOYMENT_PROJECT':
    deployment_project_ptrn = config.get('DEFAULT', 'deployment_project_ptrn', fallback=None)
    deployment_project_id = config.get('DEFAULT', 'deployment_project_id', fallback=None)

    if deployment_project_ptrn:
        deployment_project_ptrn = re.compile(deployment_project_ptrn)
        deployment_project_url = '%s/deploy/project/all' % bamboo_rest_url
        deployment_project_response = requests_session.get(deployment_project_url)
        check_response(deployment_project_response)
        for deployment_project in deployment_project_response.json():
            if deployment_project_ptrn.fullmatch(deployment_project['name']):
                entities[deployment_project['id']] = deployment_project['name']

    elif deployment_project_id:
        deployment_project_url = '%s/deploy/project/%s' % (bamboo_rest_url, deployment_project_id)
        deployment_project_response = requests_session.get(deployment_project_url)
        check_response(deployment_project_response)
        deployment_project = deployment_project_response.json()
        entities[deployment_project['id']] = deployment_project['name']

if not entities:
    print("entity_id is not found")
    exit(1)

agents_url = "%s/agent" % bamboo_rest_url
agents_response = requests_session.get(agents_url)
check_response(agents_response)

print("Assignment type: %s" % assignment_type)
print("Entities amount: %s" % len(entities))
print("Agents to be assigned pattern: %s" % config['DEFAULT']['agents_ptrn'])
print("%s agents are available." % len(agents_response.json()))
for agent in agents_response.json():
    agent_name = agent['name']
    agent_id = agent['id']
    print("%s:" % agent_name)
    agent_assignment_url = "%s/agent/assignment?executorType=AGENT&executorId=%s" % (bamboo_rest_url, agent_id)
    agent_assignment_response = requests_session.get(agent_assignment_url)
    check_response(agent_assignment_response)
    assignments = []
    for assignment in agent_assignment_response.json():
        assignments.append(assignment['id'])
    if agents_ptrn.fullmatch(agent_name):
        for entity_id, entity_name in entities.items():
            if entity_id not in assignments:
                if not dry_run:
                    agent_url = "%s/assignment?executorType=AGENT&executorId=%s&assignmentType=%s&entityId=%s" % (
                        agents_url, agent_id, assignment_type, entity_id)
                    agent_response = requests_session.post(agent_url)
                    check_response(agent_response)
                    print("    ADD %s" % entity_name)
                else:
                    print("    [DryRun] ADD %s" % entity_name)
    else:
        for entity_id, entity_name in entities.items():
            if entity_id in assignments:
                if not dry_run:
                    agent_url = "%s/assignment?executorType=AGENT&executorId=%s&assignmentType=%s&entityId=%s" % (
                        agents_url, agent_id, assignment_type, entity_id)
                    agent_response = requests_session.delete(agent_url)
                    check_response(agent_response, status_code=204)
                    print("    DEL %s" % entity_name)
                else:
                    print("    [DryRun] DEL %s" % entity_name)
