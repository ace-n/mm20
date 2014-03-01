"""@actionHandler Handles the client's actions sent to the engine from the server.
"""
from config.handle_constants import retrieveConstants
from objects.client_action import Action
from unittest import TestCase, main

actionBuffer = {}
actionDispatch = {}

_game = None


def set_game(game):
    """Takes in a game object to be used by the action handler.

    There should be a better way to do this.
    """
    _game = game


def response(status_code, **kwargs):
    """Creates a response formatted to be understood by the server.
    """
    kwargs["status"] = status_code
    return kwargs

_TODO = response(500, message="not yet implemented")
_INVALID = response(404, message="invalid call")


def bufferAction(action, *args, **kwargs):
    """Adds the action to a buffered list of actions so that it can be executed later.
    """
    action = Action(action, args, kwargs)
    actionBuffer[action.key] = action


def executeAction(action):
    """Executes the given action.
    """
    if action in actionDispatch:
        return actionDispatch[action.key](action.args, action.kwargs)
    else:
        return response(404, message="invalid call")


def _movePlayer(*args, **kwargs):
    """Attempts to move a player from one room to another
    """
    if 'room' in kwargs and 'player' in kwargs:
        return _game.people[kwargs['player']].move(kwargs['room'])
    else:
        return _INVALID
    # return _TODO
actionDispatch['movePlayer'] = _movePlayer


def _eatFood(*args, **kwargs):
    """Attempts to have a player eat the food from FoodTable
    """
    if 'foodTable' in kwargs and 'player' in kwargs:
        return _game.people[kwargs['player']].eat(kwargs['foodTable'])
    else:
        return _INVALID
    # return _TODO
actionDispatch['eatFood'] = _eatFood


def _sleep(*args, **kwargs):
    """Attempts to tell a player to sleep
    """
    if 'player' in kwargs and 'hours' in kwargs:
        return _game.people[kwargs['player']].sleep(kwargs['hours'])
    else:
        return _INVALID

    # return _TODO
actionDispatch['sleep'] = _sleep


def _code(*args, **kwargs):
    """Attempts to tell a player to code
    """
    if 'player' in kwargs and 'team' in kwargs and 'attribute' in kwargs:
        return _game.people[kwargs['player']].code(kwargs['team'], kwargs['attribute'])
    else:
        return _INVALID
    # return _TODO
actionDispatch['code'] = _code


def _getMap(*args, **kwargs):
    """Returns a json version of the current game maps
    """
    # This should be the same json interpretation that the logger uses.
    return _TODO
actionDispatch['getMap'] = _getMap


def _info(*args, **kwargs):
    """What does this do?
    """
    return _TODO
actionDispatch['info'] = _info


def _serverInfo(*args, **kwargs):
    """Returns information about the server
    """
    constants = retrieveConstants('generalInfo')
    return response(200, version=constants.VERSION, name=constants.NAME)
actionDispatch['serverInfo'] = _serverInfo


class TestaActionHandler(TestCase):
    """Holds the test cases to test the Action Handler
    """
    def placeholder(self):
        pass

if __name__ == "__main__":
    # Run all of the test cases
    main()
