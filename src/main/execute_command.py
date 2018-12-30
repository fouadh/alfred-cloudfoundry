from cf_commands import execute
from workflow import Workflow3, ICON_ERROR
import os
import sys

log = None


def execute_list_command(workflow, command):
    log.debug("-----> ICI")

    def execution_wrapper():
        return execute(command, credentials)

    credentials = find_credentials(workflow)
    if credentials:
        return workflow.cached_data(command, execution_wrapper, max_age=15)
    else:
        return workflow.cached_data(command, build_no_credentials_message, max_age=15)


def find_credentials(workflow):
    try:
        endpoint = workflow.settings['cf_endpoint']
        login = workflow.settings['cf_login']
        password = workflow.get_password('cf_password')
        if endpoint and login and password:
            return dict(endpoint=endpoint, login=login, password=password)
    except:
        log.debug("Credentials not defined")

    return None


def build_no_credentials_message():
    items = list()
    items.append(
        dict(title="You are not identified: please provide your credentials", subtitle="", icon=ICON_ERROR))
    return items


def main(wf):
    command = os.getenv('command')
    print("EXECUTE COMMAND: " + str(command))
    execute_list_command(wf, command)
    wf.logger.debug("TEST")


if __name__ == '__main__':
    wf = Workflow3()
    log = wf.logger
    sys.exit(wf.run(main))
