import json
import os
import traceback

import urllib
import base64

import yaml
from cloudfoundry_client.operations.push import push
from cloudfoundry_client.client import CloudFoundryClient
from cloudfoundry_client.errors import InvalidStatusCode
from workflow import ICON_ERROR, ICON_INFO


class ImageCache:
    def __init__(self, base_directory, url_loader=urllib.urlretrieve):
        if not os.path.exists(base_directory):
            os.makedirs(base_directory)
        self.base_directory = base_directory
        self.url_loader = url_loader

    def __load_image_from_url(self, guid, url):
        file_path = self.base_directory + '/' + guid + '.png'
        if not (os.path.exists(file_path)):
            self.url_loader(url, file_path)
        return file_path

    def __load_image_from_base64(self, guid, data):
        file_path = self.base_directory + '/' + guid + '.png'
        if not (os.path.exists(file_path)):
            image_data = base64.b64decode(data.split(',')[1].strip())
            with(open(file_path, 'wb')) as f:
                f.write(image_data)
        return file_path

    def load_image(self, guid, base64_data_or_url):
        if base64_data_or_url.startswith('http'):
            return self.__load_image_from_url(guid, base64_data_or_url)
        elif base64_data_or_url.startswith('data:image'):
            return self.__load_image_from_base64(guid, base64_data_or_url)
        else:
            return None


class Command:
    def __init__(self):
        pass

    def execute(self, credentials, args):
        try:
            client = self.__build_client(credentials)
            return self.do_execute(client, credentials, args)
        except BaseException as e:
            return self.do_handle_error(e)

    def do_handle_error(self, e):
        traceback.print_exc()
        items = list()
        items.append(
            dict(title="The command cannot be executed", subtitle=str(e), icon=ICON_ERROR))
        return items

    def do_execute(self, client, credentials, args):
        pass

    @staticmethod
    def __build_client(credentials):
        proxy = dict(http=os.environ.get('HTTP_PROXY', ''), https=os.environ.get('HTTPS_PROXY', ''))
        client = CloudFoundryClient(credentials["endpoint"], proxy=proxy, verify=False)
        client.init_with_user_credentials(credentials["login"], credentials["password"])
        return client


class ListResourcesCommand(Command):
    def __init__(self, name, resource_type, manager_getter, item_builder, cache):
        Command.__init__(self)
        self.name = name
        self.manager_getter = manager_getter
        self.item_builder = item_builder
        self.resource_type = resource_type
        self.type = '__list'
        self.cache = cache

    def load_image(self, guid, extra_data):
        image_url = extra_data['imageUrl']
        image_path = self.cache.load_image(guid, image_url)
        return image_path

    def resource_to_item(self, resource):
        item = self.item_builder(resource)
        item['__json'] = json.dumps(resource)
        item['__type'] = self.resource_type

        # if an image is available, use it as the icon
        if 'entity' in resource and 'extra' in resource['entity']:
            extra = resource['entity']['extra']
            if extra:
                extra_data = json.loads(extra)
                if 'imageUrl' in extra_data:
                    item['icon'] = self.load_image(resource['metadata']['guid'], extra_data)

        if item['subtitle'] is None:
            item['subtitle'] = ''

        return item

    def do_execute(self, client, credentials, args):
        items = list()
        manager = self.manager_getter(client)

        for resource in manager:
            items.append(self.resource_to_item(resource))

        if len(items) == 0:
            items.append(dict(title="No " + self.resource_type + " found", subtitle="", icon=None))
        return items


class ListAppsToBind(Command):
    def __init__(self, apps_command):
        Command.__init__(self)
        self.apps_command = apps_command
        self.type = '__list-bindable-apps'

    def do_execute(self, client, credentials, args):
        items = self.apps_command.execute(credentials, args)
        for item in items:
            if '__json' in item:
                item['__type'] = 'bindable app'
                item['__service_guid'] = args[0]

        return items


class ListServicePlans(Command):
    def __init__(self, plans_command):
        Command.__init__(self)
        self.type = '__list-service-plans'
        self.plans_command = plans_command

    def do_execute(self, client, credentials, args):
        items = self.plans_command.execute(credentials, args)
        result = list()
        for item in items:
            if '__json' in item:
                obj = json.loads(item['__json'])
                if obj['entity']['service_guid'] == args[0]:
                    result.append(item)
        return result


class BindAppToService(Command):
    def __init__(self):
        Command.__init__(self)
        self.type = '__bind-app'

    def do_execute(self, client, credentials, args):
        items = list()
        app = client.v2.apps.get(args[0])
        app_name = app['entity']['name']
        service = client.v2.service_instances.get(args[1])
        service_name = service['entity']['name']

        client.v2.service_bindings.create(args[0], args[1], name=app_name + '-' + service_name)
        items.append(dict(title="The application has been bounded to the service", subtitle="", icon=ICON_INFO))

    def do_handle_error(self, e):
        if isinstance(e, InvalidStatusCode):
            if str(e.status_code) == '400':
                body = e.body
                if body['error_code'] == 'CF-ServiceBindingAppServiceTaken':
                    items = list()
                    items.append(dict(title="The app is bound to the service", subtitle="", icon=None))
                    return items

        return Command.do_handle_error(self, e)


class ActionCommand(Command):
    def __init__(self, action_name, resource, manager_name, function, description, modifier, subtitle):
        self.manager_name = manager_name
        self.name = action_name
        self.resource_type = resource
        self.function = function
        self.description = description
        self.modifier = modifier
        self.subtitle = subtitle
        self.type = '__action'
        self.condition = None

    def add_condition(self, condition):
        self.condition = condition

    def evaluate_condition(self, item):
        if self.condition is None:
            return True

        for key in self.condition:
            if not (self.condition[key] == item["entity"][key]):
                return False

        return True

    def do_execute(self, client, credentials, args):
        items = list()
        getattr(vars(client.v2)[self.manager_name], self.function)(args[0])
        items.append(
            dict(title=self.description + " order has been sent", subtitle="it should be effective in a few moment",
                 icon=ICON_INFO))
        return items


class GetRecentLogs(Command):
    def __init__(self):
        self.type = '__recent-logs'

    def do_execute(self, client, credentials, args):
        items = list()
        app = client.v2.apps[args[0]]
        text = ""
        for log in app.recent_logs():
            if log:
                text = text + str(log) + "\n"

        items.append(
            dict(title="The recent logs have been retrieved", subtitle="Press Cmd+C to save them in the clipboard",
                 icon=ICON_INFO, __json=text))
        return items


class AppStatsCommand(Command):
    def __init__(self):
        self.type = '__custom'

    def do_execute(self, client, credentials, args):
        items = list()
        json_str = client.v2.apps.get_stats(args[0])
        items.append(
            dict(title="The stats have been obtained", subtitle="Press Cmd+C to save them in the clipboard",
                 icon=ICON_INFO, __json=json.dumps(json_str)))
        return items


class PushCommand(Command):
    def __init__(self):
        self.type = '__custom'

    def do_execute(self, client, credentials, args):
        items = list()
        if 'space' in credentials:
            operation = push.PushOperation(client)
            operation.push(credentials['space'], args[0])
            items.append(dict(title="The application has been pushed", subtitle="", icon=ICON_INFO))
        else:
            items.append(dict(title="Please target a space before pushing an app",
                              subtitle="Display the list of spaces, then press Cmd and select the space",
                              icon=ICON_ERROR))
        return items


class CreateServiceInstance(Command):
    def __init__(self):
        self.type = '__create-service-instance'

    def do_execute(self, client, credentials, args):
        items = list()
        if 'space' in credentials and credentials['space']:
            client.v2.service_instances.create(credentials['space'], args[1], args[0])
            items.append(dict(title="The service instance has been created", subtitle="", icon=ICON_INFO))
        else:
            items.append(dict(title="Please target a space before creating a service instance",
                              subtitle="Display the list of spaces, then press Cmd and select the space",
                              icon=ICON_ERROR))
        return items


class CommandManager:

    def __init__(self, cache_dir=None):
        self.cache = ImageCache(base_directory=cache_dir)
        self.commands = self.__load_commands()

    def can_execute(self, command):
        return command in self.commands

    def execute(self, command, credentials, args):
        return self.commands[command].execute(credentials, args)

    def find_actions_by_resource(self, resource):
        return [cmd for cmd in self.commands.values() if
                cmd.type == '__action' and cmd.resource_type == resource]

    @staticmethod
    def __get_entity_property(resource, name):
        if name:
            return resource["entity"][name]
        else:
            return None

    def __build_list_command(self, name, resource_type, manager, title_property, subtitle_property):
        return ListResourcesCommand(name=name, resource_type=resource_type, cache=self.cache,
                                    manager_getter=lambda client: vars(client.v2)[manager],
                                    item_builder=lambda item: dict(
                                        title=self.__get_entity_property(item, title_property),
                                        subtitle=self.__get_entity_property(item, subtitle_property),
                                        icon=None))

    @staticmethod
    def __build_action_command(item):
        cmd = ActionCommand(action_name=item['name'], manager_name=item['manager'], function=item['function'],
                            description=item['description'], resource=item['resource'], modifier=item['modifier'],
                            subtitle=item['subtitle'])
        if 'condition' in item:
            cmd.add_condition(item['condition'])
        return cmd

    def __build_command_from_item(self, item):
        if not ('subtitle' in item):
            item['subtitle'] = None

        type = item['type']
        if type == 'list':
            return self.__build_list_command(item['name'], item['resource'], item['manager'], item['title'],
                                             item['subtitle'])
        elif type == 'action':
            return self.__build_action_command(item)
        else:
            raise Exception("Unknown command type: " + type)

    def __load_commands(self):
        result = dict()
        stream = file(current_dir + '/commands.yml', 'r')
        config = yaml.safe_load(stream)
        commands_list = config['commands']
        for item in commands_list:
            result[item['name']] = self.__build_command_from_item(item)
        result['stats-app'] = AppStatsCommand()
        result['list-bindable-apps'] = ListAppsToBind(result['apps'])
        result['push'] = PushCommand()
        result['bind-app'] = BindAppToService()
        result['list-service-plans'] = ListServicePlans(result['service-plans'])
        result['create-service-instance'] = CreateServiceInstance()
        result['get-recent-logs'] = GetRecentLogs()
        return result


current_dir = os.path.dirname(os.path.realpath(__file__))
cmd_manager = CommandManager(cache_dir=current_dir + '/thumbs')


def can_execute(command):
    return cmd_manager.can_execute(command)


def execute(command, credentials, args):
    return cmd_manager.execute(command=command, credentials=credentials, args=args)
