from cloudfoundry_client.client import CloudFoundryClient
from workflow import ICON_ERROR
import traceback


def build_client(credentials):
    client = CloudFoundryClient(credentials["endpoint"], verify=False)
    client.init_with_user_credentials(credentials["login"], credentials["password"])
    return client


def get_apps(credentials):
    try:
        items = list()
        manager = build_client(credentials).v2.apps
        size = 0

        for item in manager:
            items.append(dict(title=item["entity"]["name"], subtitle=item["entity"]["state"], icon=None))
            size = size + 1

        if size == 0:
            items.append(dict(title="No application found", subtitle="", icon=None))

    except BaseException:
        traceback.print_exc()
        items.append(
            dict(title="You are not identified: please provide your credentials", subtitle="", icon=ICON_ERROR))

    return items


def get_routes(credentials):
    try:
        items = list()
        manager = build_client(credentials).v2.routes

        for item in manager:
            items.append(dict(title=item["entity"]["host"], subtitle="", icon=None))

        if len(items) == 0:
            items.append(dict(title="No route found", subtitle="", icon=None))

    except BaseException:
        traceback.print_exc()
        items.append(
            dict(title="You are not identified: please provide your credentials", subtitle="", icon=ICON_ERROR))

    return items
