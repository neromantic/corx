import abc
import dataclasses
import datetime
import typing
import uuid

from corx.base import UseCases, HasUseCase, Singleton, Executor
from corx.dispatcher import Dispatchable, Dispatcher

__all__ = [
    'Command',
    'CommandHandler',
    'CommandExecutor'
]


@dataclasses.dataclass
class Command(Dispatchable, abc.ABC):
    created_at: float = dataclasses.field(init=False, default_factory=datetime.datetime.now().timestamp)
    uuid: str = dataclasses.field(init=False, default_factory=lambda: str(uuid.uuid4()))

    @staticmethod
    def use_case() -> UseCases:
        return UseCases.Command


CommandType = typing.TypeVar('CommandType', bound=typing.Type[Command])


class CommandHandler(typing.Generic[CommandType], HasUseCase, metaclass=Singleton):
    def __init__(self):
        Dispatcher().register(self.handles(), type(self))

    @staticmethod
    def use_case() -> UseCases:
        return UseCases.Command

    @staticmethod
    @abc.abstractmethod
    def handles() -> CommandType:
        raise NotImplementedError

    @abc.abstractmethod
    def handle(self, command: Command) -> typing.Optional[typing.Coroutine]:
        raise NotImplementedError


CommandHandlerType = typing.TypeVar('CommandHandlerType', bound=typing.Type[CommandHandler])


class CommandExecutor(Executor):
    @staticmethod
    def use_case() -> UseCases:
        return UseCases.Command

    _registry: typing.Dict[CommandType, CommandHandlerType] = dict()

    def register(self, dispatchable: CommandType, executable: CommandHandlerType):
        if dispatchable in self._registry:
            raise Exception(f'{dispatchable} is already registered with {self._registry[dispatchable]}.')

        self._registry[dispatchable] = executable

    def execute(self, dispatchable: Command):
        command_class: CommandType = type(dispatchable)

        handler_class = self._registry.get(command_class)
        if handler_class is None:
            raise Exception(f'No handler for {command_class.__name__}')

        handler = handler_class()
        process = handler.handle(dispatchable)

        if isinstance(process, typing.Coroutine):
            self._loop.push(process)
