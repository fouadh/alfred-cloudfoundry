#!/usr/bin/python
# encoding: utf-8

import sys
import json
import os
from cf_commands import can_execute

from workflow import Workflow3, ICON_ERROR, ICON_INFO, notify
from workflow.background import run_in_background, is_running

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

    items = sorted(items, key=lambda k: k['title'])

    if output_file:
        with open(output_file, "w") as f:
            f.write(json.dumps(items))

    for item in items:
        workflow.add_item(title=item["title"], subtitle=item["subtitle"], icon=item["icon"])

    workflow.send_feedback()


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
        clear_caches(workflow)
        notify.notify(title='Your credentials have been saved')

    return None


def setup_endpoint(workflow):
    workflow.settings['cf_endpoint'] = workflow.args[0]
    clear_caches(workflow)
    notify.notify('The endpoint has been saved')
    return None


def do_execute(workflow):
    cmd = ['/usr/bin/python', workflow.workflowfile('execute_command.py')]
    run_in_background('execute-command', cmd)


def get_items(workflow, command):
    # Load data, update if necessary
    if not workflow.cached_data_fresh(command, max_age=15):
        do_execute(workflow)
        return []

    items = workflow.cached_data(command, max_age=0)

    if not items:
        do_execute(workflow)
        return []

    return items


def display_progress_message(workflow):
    workflow.rerun = 0.1
    workflow.add_item(title='Command in progress...', subtitle='It may take a few seconds...', valid=False,
                      icon=ICON_INFO)
    workflow.send_feedback()


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
            items = get_items(workflow, command)

            if is_running('execute-command'):
                display_progress_message(workflow)
                return 0
    else:
        log.debug("NO COMMAND")

    if items:
        log.debug("ITEMS: " + str(items))
        render_items(workflow, items)


if __name__ == '__main__':
    wf = Workflow3()
    log = wf.logger
    sys.exit(wf.run(main))
