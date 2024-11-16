import base64
import os
import re
import sys
import subprocess
import configparser
import requests
import urllib3
import concurrent.futures
from jira import JIRA
from jinja2 import Environment, FileSystemLoader
import faulthandler
faulthandler.enable(all_threads=True)


class ExecutionResult:
    def __init__(self, output, errors, return_code):
        self.output = output.decode('utf-8').strip()
        self.errors = errors.decode('utf-8').strip()
        self.returnCode = return_code


def cmd(command_line, on_error_exit_with=''):
    process = subprocess.Popen(command_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, errors = process.communicate()
    if on_error_exit_with != '' and process.returncode != 0:
        print(on_error_exit_with)
        print(errors)
        exit(process.returncode)
    return ExecutionResult(output, errors, process.returncode)


# Custom test
def regexp(string, expr):
    return re.fullmatch(expr, string)


# Custom filter
def base64_encode(string):
    return base64.b64encode(string.encode("UTF-8")).decode("UTF-8")


def set_exit_code(i):
    global exit_code
    exit_code = i


def exception_handler(function, *args, **kwargs):
    try:
        result = function(*args, **kwargs)
        return True, result
    except BaseException as e:
        return False, e


def multi_threading(function, items, *args, **kwargs):
    success_list = []
    fail_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        if callable(function):
            future_to_items = {executor.submit(exception_handler, function, item, *args, **kwargs): item for item in items}
        else:
            future_to_items = {executor.submit(exception_handler, getattr(item, function), *args, **kwargs): item for item in items}
        for future in concurrent.futures.as_completed(future_to_items):
            item = future_to_items[future]
            check_result, extra = future.result()
            if check_result:
                success_list.append([item, extra])
            else:
                fail_list.append([item, extra])
    return success_list, fail_list


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

requests = requests.Session()
requests.verify = False

jira = JIRA(jira_base_url, basic_auth=(user, password), options={'verify': False})
templates_path = os.path.join(config_args['DEFAULT']['config_dir'], 'template.d')
env = Environment(loader=FileSystemLoader(templates_path), extensions=['jinja2.ext.do'])
env.tests['regexp'] = regexp
env.filters['b64encode'] = base64_encode
template_file = os.path.join(templates_path, config_args['DEFAULT']['template'] + '.j2')
exit_code = 0
with open(template_file) as template_str:
    template = env.from_string(template_str.read())
    result = template.render(jira=jira, env=os.environ, config=config,
                             cmd=cmd, requests=requests, multi_threading=multi_threading,
                             print=print, exit=exit, set_exit_code=set_exit_code)
if 'output' in config['DEFAULT']:
    with open(config['DEFAULT']['output'], 'w') as output_file:
        output_file.write(result)
else:
    print(result)
exit(exit_code)
