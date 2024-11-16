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
branch_name = os.environ['bamboo_repository_git_branch']

jira = JIRA(jira_base_url, basic_auth=(user, password), options={'verify': False})

summary = '[Bamboo] Panbet build failed'
description = 'Build logs: ' + os.environ['bamboo_resultsUrl']

if 'bamboo_shortJobKey' in os.environ and os.environ['bamboo_shortJobKey'] == 'REBASE':
    if 'bamboo_inject_git_rebase' in os.environ and os.environ['bamboo_inject_git_rebase'] == 'fail':
        summary = '[Bamboo] git-rebase failed'
        description = description + '\n(x) git rebase origin/master'
    else:
        description = description + '\n(/) git rebase origin/master'
    description = description + '\n(x) ant build'

elif 'bamboo_shortJobKey' in os.environ and os.environ['bamboo_shortJobKey'] == 'MERGE':
    description = description + '\n(/) git rebase origin/master\n(/) ant build'
    if 'bamboo_inject_git_merge' in os.environ and os.environ['bamboo_inject_git_merge'] == 'fail':
        summary = '[Bamboo] git-merge failed'
        description = description + '\n(x) git merge to origin/master_test'
    else:
        description = description + '\n(/) git merge to origin/master_test'
    description = description + '\n(x) ant build'


issue_dict = {
    'project': 'DEVENG',
    # 'project': 'PAN',
    'summary': summary,
    'description': description,
    # principal
    'customfield_10110': 'Berezovskiy Evgeniy',
    'priority': {'name': 'Critical'},
    # Reviewer
    'customfield_11238': 'tarnov.s',
    'components': {'name': 'Development Engineering'},
    'parent': {'key': 'DEVENG-1147'},
    # 'parent': {'key': branch_name},
    'issuetype': {'name': 'Sub-task'},
}

if not config.getboolean('DEFAULT', 'dry_run', fallback=True):
    new_issue = jira.create_issue(fields=issue_dict)
    print('Sub-task created: %s/browse/%s' % (jira_base_url, new_issue.key))
    # parent_issue = jira.issue(branch_name)
    # jira.transition_issue(parent_issue, 'Reopen Issue', 'Переоткрыто до решения sub-task %s' % new_issue.key)
    # print('Parent task reopened: %s/browse/%s' % (jira_base_url, parent_issue.key))
else:
    print('[DRY_RUN]Sub-task created: %s' % issue_dict)
