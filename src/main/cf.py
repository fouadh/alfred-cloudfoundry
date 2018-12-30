#!/usr/bin/python
# encoding: utf-8

import sys
import json
import os
from cf_commands import can_execute, execute

from workflow import Workflow3, ICON_ERROR, notify

log = None


def search_key_for_item(item):
    elements = [item['title'], item['subtitle']]
    return u' '.join(elements)


def render_items(workflow, items):
    external_args = os.getenv('external-args')
    query = None
    output_file = None

    if external_args:
        log.debug("EXTERNAL ARGS: " + external_args)

        args = external_args.split("|")
        output_file = args[0]
        if len(args) > 1:
            query = args[1]

    elif len(workflow.args):
        query = workflow.args[0]

    if query:
        items = wf.filter(query, items, search_key_for_item, min_score=20)

    items = sorted(items, key=lambda k: k['title'], reverse=True)

    if output_file:
        with open(output_file, "w") as f:
            f.write(json.dumps(items))

    for item in items:
        workflow.add_item(title=item["title"], subtitle=item["subtitle"], icon=item["icon"])

    workflow.send_feedback()


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


def clear_caches(workflow):
    workflow.clear_cache()
    notify.notify(title="Caches have been cleared")


def clear_credentials(workflow):
    workflow.settings['cf_endpoint'] = None
    workflow.settings['cf_login'] = None
    try:
        workflow.delete_password('cf_password')
    except BaseException:
        log.debug('Password not found')
    notify.notify(title="Credentials have been cleared")


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


def execute_list_command(workflow, command):
    def execution_wrapper():
        return execute(command, credentials, log)

    credentials = find_credentials(workflow)
    if credentials:
        return workflow.cached_data(command, execution_wrapper, max_age=15)
    else:
        return buildNoCredentialsMessage()


def main(workflow):
    items = None
    command = os.getenv('command')
    log.debug("ARGS: " + str(workflow.args))

    if command:
        log.debug("COMMAND: " + command.upper())
        if command == 'set-endpoint':
            setup_endpoint(workflow)
        elif command == 'set-credentials':
            items = setup_credentials(workflow)
        elif command == 'clear-caches':
            clear_caches(workflow)
        elif command == 'clear-credentials':
            clear_credentials(workflow)
        elif can_execute(command):
            items = execute_list_command(workflow, command)
    else:
        log.debug("NO COMMAND")

    if items:
        render_items(workflow, items)


if __name__ == '__main__':
    wf = Workflow3()
    log = wf.logger
    sys.exit(wf.run(main))
