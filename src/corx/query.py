import abc
import dataclasses
import datetime
import typing
import uuid

__all__ = [
    'Query',
    'QueryHandler',
    'QueryExecutor',
]

from corx.base import UseCases, HasUseCase, Singleton, Executor
from corx.dispatcher import Dispatchable, Dispatcher

_T = typing.TypeVar('_T')
_C = typing.TypeVar('_C')


@dataclasses.dataclass
class Query(Dispatchable, abc.ABC):
    created_at: float = dataclasses.field(init=False, default_factory=datetime.datetime.now().timestamp)
    uuid: str = dataclasses.field(init=False, default_factory=lambda: str(uuid.uuid4()))

    @staticmethod
    def use_case() -> UseCases:
        return UseCases.Query


class QueryHandler(typing.Generic[_T], HasUseCase, metaclass=Singleton):
    def __init__(self):
        Dispatcher().register(self.handles(), type(self))

    @staticmethod
    def use_case() -> UseCases:
        return UseCases.Query

    @staticmethod
    @abc.abstractmethod
    def handles() -> typing.Type[_T]:
        raise NotImplementedError

    @abc.abstractmethod
    def handle(self, query: _T) -> typing.Union[typing.Any, typing.Awaitable[typing.Any]]:
        raise NotImplementedError


class QueryExecutor(Executor):
    @staticmethod
    def use_case() -> UseCases:
        return UseCases.Query

    _registry: typing.Dict[typing.Type[Query], typing.Type[QueryHandler]] = dict()

    def register(self, dispatchable: typing.Type[Query],
                 executable: typing.Type[QueryHandler]):
        if dispatchable in self._registry:
            raise Exception(f'{dispatchable} is already registered with {self._registry[dispatchable]}.')

        self._registry[dispatchable] = executable

    def execute(self, dispatchable: Query):
        query_class = type(dispatchable)

        handler_class = self._registry.get(query_class)
        if handler_class is None:
            raise Exception(f'No handler for {query_class.__name__}')

        handler = handler_class()
        process = handler.handle(dispatchable)

        if isinstance(process, typing.Coroutine):
            self._loop.push(process)
