from cloudfoundry_client.client import CloudFoundryClient
from workflow import ICON_ERROR, ICON_INFO
import traceback
import yaml
import json


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

    @staticmethod
    def __build_client(credentials):
        client = CloudFoundryClient(credentials["endpoint"], verify=False)
        client.init_with_user_credentials(credentials["login"], credentials["password"])
        return client


class ListResourcesCommand(Command):
    def __init__(self, resource_type, manager_getter, item_builder):
        Command.__init__(self)
        self.manager_getter = manager_getter
        self.item_builder = item_builder
        self.resource_type = resource_type

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


class StartAppCommand(Command):
    def do_execute(self, client, credentials, args):
        items = list()
        client.v2.apps.start(args[0])
        items.append(dict(title="Start order has been sent", subtitle="it should be effective in a few moment...",
                          icon=ICON_INFO))
        return items


class StopAppCommand(Command):
    def do_execute(self, client, credentials, args):
        items = list()
        client.v2.apps.stop(args[0])
        items.append(dict(title="Stop order has been sent", subtitle="it should be effective in a few moment...",
                          icon=ICON_INFO))
        return items


class CommandManager:

    def __init__(self):
        self.commands = self.__load_commands()

    def can_execute(self, command):
        return command in self.commands

    def execute(self, command, credentials, args):
        return self.commands[command].execute(credentials, args)

    @staticmethod
    def __get_entity_property(resource, name):
        if name:
            return resource["entity"][name]
        else:
            return None

    def __build_command(self, resource_type, manager, title_property, subtitle_property):
        return ListResourcesCommand(resource_type, lambda client: vars(client.v2)[manager],
                                    lambda item: dict(title=self.__get_entity_property(item, title_property),
                                                      subtitle=self.__get_entity_property(item, subtitle_property),
                                                      icon=None))

    def __build_command_from_item(self, item):
        if not ('subtitle' in item):
            item['subtitle'] = None

        return self.__build_command(item['resource'], item['manager'], item['title'], item['subtitle'])

    def __load_commands(self):
        result = dict()
        stream = file('./commands.yml', 'r')
        config = yaml.safe_load(stream)
        commands_list = config['commands']
        for item in commands_list:
            result[item['name']] = self.__build_command_from_item(item)

        result['stop-app'] = StopAppCommand()
        result['start-app'] = StartAppCommand()
        return result


cmd_manager = CommandManager()


def can_execute(command):
    return cmd_manager.can_execute(command)


def execute(command, credentials, args):
    return cmd_manager.execute(command=command, credentials=credentials, args=args)
