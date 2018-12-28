from cloudfoundry_client.client import CloudFoundryClient
from workflow import ICON_ERROR
import traceback


def build_client(credentials):
    client = CloudFoundryClient(credentials["endpoint"], verify=False)
    client.init_with_user_credentials(credentials["login"], credentials["password"])
    return client


def execute_list_command(credentials, resource_type, get_manager, item_builder):
    try:
        items = list()
        client = build_client(credentials)
        manager = get_manager(client)

        for item in manager:
            items.append(item_builder(item))

        if len(items) == 0:
            items.append(dict(title="No " + resource_type + " found", subtitle="", icon=None))

    except BaseException:
        traceback.print_exc()
        items.append(
            dict(title="You are not identified: please provide your credentials", subtitle="", icon=ICON_ERROR))

    return items


def get_apps(credentials):
    return execute_list_command(credentials, 'application', lambda client: client.v2.apps,
                                lambda item: dict(title=item["entity"]["name"], subtitle=item["entity"]["state"],
                                                  icon=None))


def get_routes(credentials):
    return execute_list_command(credentials, 'route', lambda client: client.v2.routes,
                                lambda item: dict(title=item["entity"]["host"], subtitle="", icon=None))


def get_services(credentials):
    return execute_list_command(credentials, 'service', lambda client: client.v2.services,
                                lambda item: dict(title=item["entity"]["label"], subtitle=item["entity"]["description"],
                                                  icon=None))


def get_services_plans(credentials):
    return execute_list_command(credentials, 'service plan', lambda client: client.v2.services,
                                lambda item: dict(title=item["entity"]["label"], subtitle=item["entity"]["description"],
                                                  icon=None))


def get_buildpacks(credentials):
    return execute_list_command(credentials, 'buildpack', lambda client: client.v2.buildpacks,
                                lambda item: dict(title=item["entity"]["name"], subtitle=item["entity"]["filename"],
                                                  icon=None))


def get_service_bindings(credentials):
    return execute_list_command(credentials, 'service binding', lambda client: client.v2.service_bindings,
                                lambda item: dict(title=item["entity"]["name"], subtitle="",
                                                  icon=None))


def get_service_brokers(credentials):
    return execute_list_command(credentials, 'service broker', lambda client: client.v2.service_brokers,
                                lambda item: dict(title=item["entity"]["name"], subtitle="",
                                                  icon=None))

def get_shared_domains(credentials):
    return execute_list_command(credentials, 'service broker', lambda client: client.v2.shared_domains,
                                lambda item: dict(title=item["entity"]["name"], subtitle="",
                                                  icon=None))

def get_service_instances(credentials):
    return execute_list_command(credentials, 'service instance', lambda client: client.v2.service_instances,
                                lambda item: dict(title=item["entity"]["name"], subtitle="",
                                                  icon=None))


def get_spaces(credentials):
    return execute_list_command(credentials, 'space', lambda client: client.v2.spaces,
                                lambda item: dict(title=item["entity"]["name"], subtitle="",
                                                  icon=None))


def get_service_keys(credentials):
    return execute_list_command(credentials, 'service key', lambda client: client.v2.service_keys,
                                lambda item: dict(title=item["entity"]["name"], subtitle="",
                                                  icon=None))


def get_cups(credentials):
    return execute_list_command(credentials, 'user provided instance',
                                lambda client: client.v2.user_provided_service_instances,
                                lambda item: dict(title=item["entity"]["name"], subtitle="",
                                                  icon=None))


def get_stacks(credentials):
    return execute_list_command(credentials, 'stack', lambda client: client.v2.stacks,
                                lambda item: dict(title=item["entity"]["name"], subtitle=item["entity"]["description"],
                                                  icon=None))


def get_organizations(credentials):
    return execute_list_command(credentials, 'stack', lambda client: client.v2.organizations,
                                lambda item: dict(title=item["entity"]["name"], subtitle="",
                                                  icon=None))


commands = {"apps": get_apps, "routes": get_routes, "services": get_services, "buildpacks": get_buildpacks,
            "service-bindings": get_service_bindings, "service-brokers": get_service_brokers,
            "service-instances": get_service_instances, "spaces": get_spaces, "service-keys": get_service_keys,
            "service-plans": get_services_plans, "cups": get_cups, "stacks": get_stacks,
            "organizations": get_organizations}


def can_execute(command):
    return commands[command]


def execute(command, credentials):
    return commands[command](credentials)
