from . import command
from . import dispatcher
from . import event
from . import test

__all__ = [
    'test',
    'command',
    'event',
    'dispatcher',
]


__dispatcher = dispatcher.get_dispatcher()

__dispatcher.register_executor(command.Command, command.CommandExecutor())
__dispatcher.register_executor(event.Event, event.EventExecutor())
