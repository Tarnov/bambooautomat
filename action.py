import configparser
import os
import re
import sys
import urllib3
from jira import JIRA

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
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

if 'issue' in config['DEFAULT']:
    issue_key = config['DEFAULT']['issue']
    print("Isuue: %s" % issue_key)
    jira = JIRA(jira_base_url, basic_auth=(user, password), options={'verify': False})
    issue = jira.issue(issue_key)
    if 'transition' in config['DEFAULT']:
        print("Transition: %s" % config['DEFAULT']['transition'])
        transitions = jira.transitions(issue)
        print("Allowed transitions: %s" % transitions)
        for transition in transitions:
            if transition['name'] == config['DEFAULT']['transition']:
                jira.transition_issue(issue, transition['id'], fields={})
                print('Transition "%s" Id "%s"' % (transition['name'], transition['id']))
                break
    if 'comment' in config['DEFAULT']:
        comment = config['DEFAULT']['comment']
        if comment.startswith('file://'):
            try:
                commnet_path = comment[7:]
                print("Reading comment from file: %s" % commnet_path)
                with open(commnet_path, 'r') as f:
                    comment = f.read()
                new_comment = jira.add_comment(issue_key, comment)
                print("Comment added to %s" % issue_key)
            except OSError as err:
                print(err)
                exit(1)
        else:
            new_comment = jira.add_comment(issue_key, comment)
            print("Comment added to %s" % issue_key)













