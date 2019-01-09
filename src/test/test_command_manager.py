import sys, os

current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_dir + '/../main/')

from cf_commands import cmd_manager


def test_commands_are_built():
    commands = cmd_manager.commands
    assert len(commands) > 0


def test_list_command_is_correctly_built():
    command = cmd_manager.commands['apps']
    assert command.name == 'apps'
    assert command.type == '__list'
    assert command.resource_type == 'application'
    assert command.manager_getter is not None


def test_action_command_is_correctly_built():
    command = cmd_manager.commands['start-app']
    assert command.name == 'start-app'
    assert command.type == '__action'
    assert command.resource_type == 'application'
    assert command.description == 'Start'
    assert command.manager_name == 'apps'
    assert command.function == 'start'
    assert command.subtitle == 'Start this application'
    assert command.modifier == 'cmd'
    assert command.condition == dict(state='STOPPED')


def test_application_actions_are_present():
    commands = cmd_manager.find_actions_by_resource('application')
    assert len(commands) > 0


def test_toto_actions_do_not_exist():
    commands = cmd_manager.find_actions_by_resource('toto')
    assert len(commands) == 0


def test_can_execute_start_app_command():
    assert cmd_manager.can_execute('start-app')


def test_cannot_execute_toto_command():
    assert not cmd_manager.can_execute('toto')
