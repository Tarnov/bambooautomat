import os
import re
import sys
import requests
import configparser
import urllib3
from jira import JIRA

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
jira_base_url = config['DEFAULT']['jira_base_url']
bamboo_rest_url = config['DEFAULT']['bamboo_base_url'] + '/rest/api/latest'
build_full_key = config['DEFAULT']['build_full_key']
jql = config['DEFAULT']['jql']
dry_run = config.getboolean('DEFAULT', 'dry_run', fallback=False)

jira = JIRA(jira_base_url, basic_auth=(user, password), options={'verify': False})
print("============================JQL RESULT=============================")
print("JQL: %s" % jql)
search_result = jira.search_issues(jql, maxResults=False)
print("RESULT: %s (total: %s)" % (len(search_result), search_result.total))
if search_result:
    print("======================CREATING BUILD-BRANCHES======================")
    for issue in search_result:
        print(issue.key)
        url = "%s/plan/%s/branch/%s?vcsBranch=%s&enabled=true&cleanupEnabled=true" % (
            bamboo_rest_url, build_full_key, issue.key, issue.key)
        if dry_run:
            print("   [DryRun] %s" % url)
        else:
            response = requests.put(url, auth=(user, password), verify=False)
            if response.status_code == 200:
                print("   Success")
            elif "This name is already used in a branch or plan" in response.json()["message"]:
                print("   Branch already exist.")
                branch_url = bamboo_rest_url + "/plan/" + build_full_key + "/branch/" + issue.key + ".json"
                branch_response = requests.get(branch_url, auth=(user, password), verify=False)
                if branch_response.status_code == 200:
                    if not branch_response.json()['enabled']:
                        print("   Branch disabled. Enabling...")
                        enable_branch_url = "%s/plan/%s/enable" % (bamboo_rest_url, branch_response.json()['key'])
                        enable_branch_response = requests.post(enable_branch_url, auth=(user, password), verify=False)
                        if enable_branch_response.status_code <= 204:
                            print("   Branch enabled.")
                        else:
                            print("      Fail: " + str(enable_branch_response.status_code))
                            print(enable_branch_response.content)
                else:
                    print("      Fail: " + str(branch_response.status_code))
                    print(branch_response.content)
            else:
                print("   Fail: " + str(response.status_code))
                print(response.content)
                exit(1)

    print("==========================STARTING BUILDS==========================")
    for issue in search_result:
        print("%s status: %s" % (issue.key, issue.fields.status))
        branch_url = bamboo_rest_url + "/plan/"+build_full_key+"/branch/"+issue.key+".json"
        branch_response = requests.get(branch_url, auth=(user, password), verify=False)
        if branch_response.status_code == 200:
            print("   Starting build:")
            start_url = "%s/queue/%s?stage&executeAllStages&bamboo.variable.build.source=%s" % (
                bamboo_rest_url, branch_response.json()['key'], "PANBUILD-PANBETBRANCHSTARTER")
            if str(issue.fields.status) == "Resolved":
                print("      reopenOnFail=true")
                start_url += "&bamboo.variable.reopenOnFail=true"
            if dry_run:
                print("   [DryRun] %s" % start_url)
            else:
                start_response = requests.post(start_url, auth=(user, password), verify=False)
                if start_response.status_code == 200:
                    print("      Success")
                else:
                    print("      Fail: " + str(start_response.status_code))
                    print(start_response.content)
        else:
            print("      Fail: " + str(branch_response.status_code))
            print(branch_response.content)
else:
    print("========================NOTHING TO DO HERE=========================")
