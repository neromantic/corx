import abc
import dataclasses
import datetime
import typing
import uuid

from corx.dispatcher import Dispatchable, Executor, get_dispatcher

__all__ = [
    'Command',
    'CommandType',
    'CommandExecutor'
]


@dataclasses.dataclass
class Command(Dispatchable, abc.ABC):
    created_at: float = dataclasses.field(init=False, default_factory=datetime.datetime.now().timestamp)
    uuid: str = dataclasses.field(init=False, default_factory=lambda: str(uuid.uuid4()))


CommandType = typing.TypeVar('CommandType', bound=typing.Type[Command])
CommandHandlerType = typing.TypeVar('CommandHandlerType', bound=typing.Callable[[Command], typing.Union[typing.Coroutine, typing.Any]])


def handles(command: CommandType):
    def wrap(method):
        get_dispatcher().register(command, method)
        return method

    return wrap


class CommandExecutor(Executor):
    _registry: typing.Dict[CommandType, CommandHandlerType] = dict()

    def register(self, dispatchable: CommandType, executable: CommandHandlerType):
        if dispatchable in self._registry:
            raise Exception(f'{dispatchable} is already registered with {self._registry[dispatchable]}.')

        self._registry[dispatchable] = executable

    def execute(self, dispatchable: Command):
        command_class: CommandType = type(dispatchable)

        handler_method = self._registry.get(command_class)
        if handler_method is None:
            raise Exception(f'No handler for {command_class.__name__}')

        result = handler_method(dispatchable)

        if isinstance(result, typing.Coroutine):
            self._loop.push(result)
