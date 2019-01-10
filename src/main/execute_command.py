from cf_commands import execute
from workflow import Workflow3, ICON_ERROR
import os
import sys

log = None


def execute_list_command(workflow, command_name, args):
    def execution_wrapper():
        return execute(command_name, credentials, args)

    credentials = find_credentials(workflow)
    if credentials:
        return workflow.cached_data(command_name, execution_wrapper, max_age=15)
    else:
        return workflow.cached_data(command_name, build_no_credentials_message, max_age=15)


def find_credentials(workflow):
    try:
        endpoint = workflow.settings['cf_endpoint']
        login = workflow.settings['cf_login']
        password = workflow.get_password('cf_password')
        space = None
        if 'cf_space' in workflow.settings:
            space = workflow.settings['cf_space']

        if endpoint and login and password:
            return dict(endpoint=endpoint, login=login, password=password, space=space)
    except:
        log.debug("Credentials not defined")

    return None


def build_no_credentials_message():
    items = list()
    items.append(
        dict(title="You are not identified: please provide your credentials", subtitle="", icon=ICON_ERROR))
    return items


def main(workflow):
    command = os.getenv('command')
    elements = command.split(' ')
    command_name = elements.pop(0)
    execute_list_command(workflow, command_name, elements)


if __name__ == '__main__':
    wf = Workflow3()
    log = wf.logger
    sys.exit(wf.run(main))
