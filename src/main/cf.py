#!/usr/bin/python
# encoding: utf-8

import sys
import json
import os
from cf_commands import can_execute

from workflow import Workflow3, ICON_ERROR, ICON_INFO, notify, PasswordNotFound
from workflow.background import run_in_background, is_running

log = None

# Age of the cache of items in seconds
CACHE_MAX_AGE = 15

# Icon for workflow update availability
ICON_UPDATE = 'update_available.png'

# GitHub repo for self-updating
UPDATE_SETTINGS = {'github_slug': 'fouadh/alfred-cloudfoundry', 'frequency': 1}

# GitHub Issues
HELP_URL = 'https://github.com/fouadh/alfred-cloudfoundry/issues'


def search_key_for_item(item):
    elements = [item['title'], item['subtitle']]
    return u' '.join(elements)


def render_items(workflow, items):
    output_file, query = get_args(workflow)
    items = prepare_items_to_render(items, query)
    dump_items(items, output_file)
    for item in items:
        workflow.add_item(title=item["title"], subtitle=item["subtitle"], icon=item["icon"])
    workflow.send_feedback()


def prepare_items_to_render(items, query):
    if query:
        items = wf.filter(query, items, search_key_for_item, min_score=20)
    items = sorted(items, key=lambda k: k['title'])
    return items


def dump_items(items, output_file):
    if output_file:
        with open(output_file, "w") as f:
            f.write(json.dumps(items))


def get_args(workflow):
    external_args = os.getenv('external-args')
    if external_args:
        return parse_external_args(external_args)
    elif len(workflow.args):
        return None, workflow.args[0]
    else:
        return None, None


def parse_external_args(external_args):
    args = external_args.split("|")
    if len(args) > 1:
        return args[0], args[1]
    else:
        return args[0], None


def clear_caches(workflow, notify_user=False):
    try:
        workflow.clear_cache()
    except:
        log.debug("Cache error when trying to clean it")
    if notify_user:
        notify.notify(title="Caches have been cleared")


def clear_credentials(workflow):
    workflow.settings['cf_endpoint'] = None
    workflow.settings['cf_login'] = None
    try:
        workflow.delete_password('cf_password')
    except PasswordNotFound:
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
    if not workflow.cached_data_fresh(command, max_age=CACHE_MAX_AGE):
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


def clear_caches_and_notify(workflow):
    clear_caches(workflow, True)


commands = {
    'set-endpoint': setup_endpoint,
    'set-credentials': setup_credentials,
    'clear-caches': clear_caches_and_notify,
    'clear-credentials': clear_credentials
}


def main(workflow):
    if workflow.update_available:
        log.info("Downloading new version of the workflow...")
        workflow.start_update()

    items = None
    command = os.getenv('command')
    log.debug("ARGS: " + str(workflow.args))

    if command:
        log.debug("COMMAND: " + command.upper())
        if command in commands:
            commands[command](workflow)
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
    wf = Workflow3(update_settings=UPDATE_SETTINGS,
                   help_url=HELP_URL)
    log = wf.logger
    sys.exit(wf.run(main))
