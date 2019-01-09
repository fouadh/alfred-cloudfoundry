import sys, os

current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_dir + '/../main/')

from cf_commands import cmd_manager


def test_can_evaluate_condition():
    action = cmd_manager.commands['start-app']

    assert action.evaluate_condition(dict(entity=dict(state='STOPPED')))
    assert action.evaluate_condition(dict(entity=dict(state='STARTED'))) is False
