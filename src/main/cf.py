#!/usr/bin/python
# encoding: utf-8

import sys
import json
import os
from cf_commands import get_apps, get_routes, get_services, get_buildpacks

from workflow import Workflow3, ICON_ERROR, notify

log = None


def render_items(workflow, items):
    output_file = os.getenv('output')
    if output_file:
        with open(output_file, "w") as f:
            f.write(json.dumps(items))

    for item in items:
        workflow.add_item(title=item["title"], subtitle=item["subtitle"], icon=item["icon"])
    workflow.send_feedback()


def findCredentials(workflow):
    try:
        endpoint = workflow.settings['cf_endpoint']
        login = workflow.settings['cf_login']
        password = workflow.get_password('cf_password')
        if endpoint and login and password:
            return dict(endpoint=endpoint, login=login, password=password)
    except:
        log.debug("Credentials not defined")

    return None


def cleanup(workflow):
    workflow.settings['cf_endpoint'] = None
    workflow.settings['cf_login'] = None
    try:
        workflow.delete_password('cf_password')
    except BaseException:
        log.debug('Password not found')
    notify.notify(title="Data cleaned")


def setup_credentials(workflow):
    data = workflow.args[0].split(" ")
    if len(data) != 2:
        items = list()
        items.append(
            dict(title="You need to provide login and password to this command", subtitle="", icon=ICON_ERROR))
        return items
    else:
        workflow.settings['cf_login'] = data[0].strip()
        workflow.save_password('cf_password', password=data[1].strip())
        notify.notify(title='Your credentials have been saved')

    return None


def setup_endpoint(workflow):
    workflow.settings['cf_endpoint'] = workflow.args[0]
    notify.notify('The endpoint has been saved')
    return None


def buildNoCredentialsMessage():
    items = list()
    items.append(
        dict(title="You are not identified: please provide your credentials", subtitle="", icon=ICON_ERROR))
    return items


def execute_list_command(workflow, function):
    credentials = findCredentials(workflow)
    if credentials:
        return function(credentials)
    else:
        return buildNoCredentialsMessage()


def main(workflow):
    items = None
    command = os.getenv('command')

    if command:
        log.debug("command: " + command.upper())
        if command == 'apps':
            items = execute_list_command(workflow, get_apps)
        elif command == 'routes':
            items = execute_list_command(workflow, get_routes)
        elif command == 'services':
            items = execute_list_command(workflow, get_services)
        elif command == 'buildpacks':
            items = execute_list_command(workflow, get_buildpacks)
        elif command == 'set-endpoint':
            setup_endpoint(workflow)
        elif command == 'set-credentials':
            items = setup_credentials(workflow)
        elif command == 'cleanup':
            cleanup(workflow)

    if items:
        render_items(workflow, items)


if __name__ == '__main__':
    wf = Workflow3()
    log = wf.logger
    sys.exit(wf.run(main))
