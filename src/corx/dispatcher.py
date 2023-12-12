import abc
import dataclasses
import typing

from corx.base import HasUseCase, AsyncLoop, Executor, Singleton

__all__ = [
    'Dispatchable',
    'Dispatcher',
]

_T = typing.TypeVar('_T')
_C = typing.TypeVar('_C')


@dataclasses.dataclass
class Dispatchable(HasUseCase, abc.ABC):

    @classmethod
    def dispatch(cls, *args, **kwargs):
        instance = cls.__call__(*args, **kwargs)
        Dispatcher().dispatch(instance)


class Dispatcher(metaclass=Singleton):
    _executors: typing.List[Executor]
    _loop: AsyncLoop

    def __init__(self) -> None:
        self._executors = []
        self._loop = AsyncLoop()

    def dispatch(self, *dispatchables: _T) -> None:
        for dispatchable in dispatchables:
            executor = self._resolve(dispatchable)
            executor.execute(dispatchable)
        self._loop.process()

    def propagate_exceptions(self, status: bool):
        self._loop.propagate_exceptions(status)

    def register_executors(self, *executors: Executor):
        for executor in executors:
            self._executors.append(executor)

    def _resolve(self, instance: typing.Type[HasUseCase]) -> Executor:
        for executor in self._executors:
            if executor.use_case() == instance.use_case():
                return executor

        raise Exception(f'No executor for {instance.use_case()}.')

    def register(self, dispatchable: typing.Type[Dispatchable], executable: typing.Type[_C]) -> None:
        executor = self._resolve(dispatchable)
        executor.register(dispatchable, executable)

    def deactivate(self, executable: typing.Type[HasUseCase]) -> None:
        self._resolve(executable).deactivate(executable)

    def activate(self, executable: typing.Type[HasUseCase]) -> None:
        self._resolve(executable).activate(executable)
