import os
import re
import sys
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
jql = config['DEFAULT']['jql']

jira = JIRA(jira_base_url, basic_auth=(user, password), options={'verify': False})
print("============================JQL RESULT=============================")
print("JQL: %s" % jql)
search_result = jira.search_issues(jql, maxResults=False)
print("RESULT: %s (total: %s)" % (len(search_result), search_result.total))
if search_result:
    for issue in search_result:
        print("%s/browse/%s - %s" % (jira_base_url, issue.key, issue.fields.summary))
    exit(1)
else:
    exit(0)
