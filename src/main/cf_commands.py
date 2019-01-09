import json
import os
import traceback

import yaml
from cloudfoundry_client.client import CloudFoundryClient
from workflow import ICON_ERROR, ICON_INFO


class Command:
    def __init__(self):
        pass

    def execute(self, credentials, args):
        try:
            client = self.__build_client(credentials)
            return self.do_execute(client, credentials, args)
        except BaseException as e:
            traceback.print_exc()
            items = list()
            items.append(
                dict(title="The command cannot be executed", subtitle=str(e), icon=ICON_ERROR))
            return items

    def do_execute(self, client, credentials, args):
        pass

    def get_type(self):
        return self.type

    def get_resource_type(self):
        return self.resource_type

    @staticmethod
    def __build_client(credentials):
        proxy = dict(http=os.environ.get('HTTP_PROXY', ''), https=os.environ.get('HTTPS_PROXY', ''))
        client = CloudFoundryClient(credentials["endpoint"], proxy=proxy, verify=False)
        client.init_with_user_credentials(credentials["login"], credentials["password"])
        return client


class ListResourcesCommand(Command):
    def __init__(self, resource_type, manager_getter, item_builder):
        Command.__init__(self)
        self.manager_getter = manager_getter
        self.item_builder = item_builder
        self.resource_type = resource_type
        self.type = '__list'

    def do_execute(self, client, credentials, args):
        items = list()
        manager = self.manager_getter(client)

        for resource in manager:
            item = self.item_builder(resource)
            item['__json'] = json.dumps(resource)
            item['__type'] = self.resource_type

            if item['subtitle'] is None:
                item['subtitle'] = ''

            items.append(item)

        if len(items) == 0:
            items.append(dict(title="No " + self.resource_type + " found", subtitle="", icon=None))
        return items


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

    def do_execute(self, client, credentials, args):
        items = list()
        getattr(vars(client.v2)[self.manager_name], self.function)(args[0])
        items.append(
            dict(title=self.description + " order has been sent", subtitle="it should be effective in a few moment",
                 icon=ICON_INFO))
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


class CommandManager:

    def __init__(self):
        self.commands = self.__load_commands()

    def can_execute(self, command):
        return command in self.commands

    def execute(self, command, credentials, args):
        return self.commands[command].execute(credentials, args)

    def find_actions_by_resource(self, resource):
        return [cmd for cmd in self.commands.values() if cmd.get_type() == '__action' and cmd.get_resource_type() == resource]

    @staticmethod
    def __get_entity_property(resource, name):
        if name:
            return resource["entity"][name]
        else:
            return None

    def __build_list_command(self, resource_type, manager, title_property, subtitle_property):
        return ListResourcesCommand(resource_type, lambda client: vars(client.v2)[manager],
                                    lambda item: dict(title=self.__get_entity_property(item, title_property),
                                                      subtitle=self.__get_entity_property(item, subtitle_property),
                                                      icon=None))

    @staticmethod
    def __build_action_command(item):
        return ActionCommand(action_name=item['name'], manager_name=item['manager'], function=item['function'],
                             description=item['description'], resource=item['resource'], modifier=item['modifier'],
                             subtitle=item['subtitle'])

    def __build_command_from_item(self, item):
        if not ('subtitle' in item):
            item['subtitle'] = None

        type = item['type']
        if type == 'list':
            return self.__build_list_command(item['resource'], item['manager'], item['title'], item['subtitle'])
        elif type == 'action':
            return self.__build_action_command(item)
        else:
            raise Exception("Unknown command type: " + type)

    def __load_commands(self):
        result = dict()
        stream = file('./commands.yml', 'r')
        config = yaml.safe_load(stream)
        commands_list = config['commands']
        for item in commands_list:
            result[item['name']] = self.__build_command_from_item(item)
        result['stats-app'] = AppStatsCommand()
        return result


cmd_manager = CommandManager()


def can_execute(command):
    return cmd_manager.can_execute(command)


def execute(command, credentials, args):
    return cmd_manager.execute(command=command, credentials=credentials, args=args)
