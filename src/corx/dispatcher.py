import abc
import dataclasses
import typing

__all__ = [
    'Dispatchable',
    'Executor',
    'get_dispatcher'
]

from corx.loop import get_async_loop

_T = typing.TypeVar('_T')
_C = typing.TypeVar('_C')


class Executor():
    def __init__(self):
        self._loop = get_async_loop()
        self._deactivated = set()

    @abc.abstractmethod
    def register(self, dispatchable, executable):
        raise NotImplementedError

    @abc.abstractmethod
    def execute(self, dispatchable):
        raise NotImplementedError

    def deactivate(self, executable):
        self._deactivated.add(executable)

    def activate(self, executable):
        self._deactivated.remove(executable)

@dataclasses.dataclass
class Dispatchable(abc.ABC):

    @classmethod
    def dispatch(cls, *args, **kwargs):
        instance = cls.__call__(*args, **kwargs)
        get_dispatcher().dispatch(instance)


class __Dispatcher():
    def __init__(self) -> None:
        self._executors = {}
        self._loop = get_async_loop()

    def dispatch(self, *dispatchables: _T) -> None:
        for dispatchable in dispatchables:
            executor = self._resolve(type(dispatchable))
            executor.execute(dispatchable)
        self._loop.process()

    def propagate_exceptions(self, status: bool):
        self._loop.propagate_exceptions(status)

    def register_executor(self, dispatchable: typing.Type[Dispatchable], executor: Executor):
        self._executors[dispatchable] = executor

    def _resolve(self, instance: typing.Type[Dispatchable]) -> Executor:
        return self._executors[instance.__bases__[0]]

    def register(self, dispatchable: typing.Type[Dispatchable], executable: typing.Type[_C]) -> None:
        executor = self._resolve(dispatchable)
        executor.register(dispatchable, executable)

    def deactivate(self, executable: typing.Any) -> None:
        self._resolve(executable).deactivate(executable)

    def activate(self, executable: typing.Any) -> None:
        self._resolve(executable).activate(executable)

__dispatcher = None

def get_dispatcher() -> __Dispatcher:
    global __dispatcher

    if __dispatcher is None:
        __dispatcher = __Dispatcher()

    return __dispatcher


def dispatch( *dispatchables: _T):
    return get_dispatcher().dispatch(*dispatchables)
