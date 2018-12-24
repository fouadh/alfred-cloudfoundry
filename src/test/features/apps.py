from lettuce import step, world, before, after
import json
import os

# a bit complicated, cannot we do simpler in python ???
import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))) + "/../main")
from cf_commands import get_apps
import requests


class AlfredWorkflowStub:
    def __init__(self):
        self.items = list()

    def add_item(self, title, subtitle=None):
        self.items.append({"title": title, "subtitle": subtitle})

    def contains_item(self, title, subtitle=None):
        for item in self.items:
            if item["title"] == title and item["subtitle"] == subtitle:
                return True

        return False


@after.each_scenario
def cleanup(_):
    requests.delete('http://localhost:2525/imposters')


@before.each_scenario
def init_workfow(_):
    world.workflow = AlfredWorkflowStub()
    requests.post('http://localhost:2525/imposters', json=load_json_fixture('uaa-stubs'))

def load_json_fixture(name):
    with open(os.path.join(os.path.dirname(__file__), '../fixtures/' + name + '.json'), 'r') as f:
        return json.load(f)

@step("no application is hosted on Cloud Foundry")
def clean_apps(step_instance):
    requests.post('http://localhost:2525/imposters', json=load_json_fixture('cf-noapp-stubs'))


@step("I want to list all of them")
def list_all_apps(step_instance):
    target = {
        "endpoint": "https://localhost:3001",
        "login": "alice@acme.com",
        "password": "alice123"
    }
    get_apps(world.workflow, target)


@step("one application named (.*) is started on Cloud Foundry")
def start_app(step_instance, app_name):
    requests.post('http://localhost:2525/imposters', json=load_json_fixture('cf-apps-stubs'))


@step('the workflow should contain an item with title \'(.*)\' and subtitle \'(.*)\'')
def check_item_title_and_subtitle(step_instance, title, subtitle):
    assert world.workflow.contains_item(title, subtitle)


@step("the workflow should contain an item with title '(.*)' and no subtitle")
def check_item_title(step_instance, title):
    assert world.workflow.contains_item(title)
