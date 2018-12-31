from cloudfoundry_client.client import CloudFoundryClient
from workflow import ICON_ERROR
import traceback
import yaml
import json


class Command:
    def __init__(self, resource_type, manager_getter, item_builder):
        self.manager_getter = manager_getter
        self.item_builder = item_builder
        self.resource_type = resource_type

    @staticmethod
    def __build_client(credentials):
        client = CloudFoundryClient(credentials["endpoint"], verify=False)
        client.init_with_user_credentials(credentials["login"], credentials["password"])
        return client

    def execute(self, credentials):
        try:
            items = list()
            client = self.__build_client(credentials)
            manager = self.manager_getter(client)

            for resource in manager:
                item = self.item_builder(resource)
                item['json'] = json.dumps(resource)

                if item['subtitle'] is None:
                    item['subtitle'] = ''

                items.append(item)

            if len(items) == 0:
                items.append(dict(title="No " + self.resource_type + " found", subtitle="", icon=None))

        except BaseException as e:
            traceback.print_exc()
            items.append(
                dict(title="The command cannot be executed", subtitle=str(e), icon=ICON_ERROR))

        return items


class CommandManager:

    def __init__(self):
        self.commands = self.__load_commands()

    def can_execute(self, command):
        return self.commands[command]

    def execute(self, command, credentials):
        return self.commands[command].execute(credentials)

    @staticmethod
    def __get_entity_property(resource, name):
        if name:
            return resource["entity"][name]
        else:
            return None

    def __build_command(self, resource_type, manager, title_property, subtitle_property):
        return Command(resource_type, lambda client: vars(client.v2)[manager],
                       lambda item: dict(title=self.__get_entity_property(item, title_property),
                                         subtitle=self.__get_entity_property(item, subtitle_property),
                                         icon=None))

    def __build_command_from_item(self, item):
        if ('subtitle' in item) is False:
            item['subtitle'] = None

        return self.__build_command(item['resource'], item['manager'], item['title'], item['subtitle'])

    def __load_commands(self):
        result = dict()
        stream = file('./commands.yml', 'r')
        config = yaml.safe_load(stream)
        commands_list = config['commands']
        for item in commands_list:
            result[item['name']] = self.__build_command_from_item(item)
        return result


cmd_manager = CommandManager()


def can_execute(command):
    return cmd_manager.can_execute(command)


def execute(command, credentials):
    return cmd_manager.execute(command, credentials)
