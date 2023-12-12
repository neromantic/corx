import abc
import asyncio
import enum
import typing


__all__ = [
    'Singleton',
    'AsyncLoop',
    'UseCases',
    'HasUseCase',
    'Executor',
]


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AsyncLoop(metaclass=Singleton):
    def __init__(self):
        self._loop = asyncio.get_event_loop()
        self._queue = asyncio.Queue()
        self._worker_tasks = []
        self._processing = False
        self._exception_propagating = False
        self._exceptions = []

    def push(self, process: typing.Coroutine) -> None:
        self._queue.put_nowait(process)
        self._manage_workers()

    def propagate_exceptions(self, status: bool):
        self._exception_propagating = status

    def _manage_workers(self) -> None:
        queue_size = self._queue.qsize()
        if queue_size > len(self._worker_tasks) * 2:
            self._add_worker()

    def _add_worker(self) -> None:
        worker_task = self._loop.create_task(self._worker())
        self._worker_tasks.append(worker_task)

    async def _worker(self) -> None:
        while True:
            process = await self._queue.get()
            try:
                await process
            except Exception as e:
                self._exceptions.append(e)
            finally:
                self._queue.task_done()

    def is_processing(self) -> bool:
        return self._processing

    def process(self) -> None:
        if not self._processing:
            self._processing = True

            for _ in range(self._queue.qsize() - len(self._worker_tasks)):
                self._add_worker()

            self._loop.run_until_complete(self._queue.join())
            self._processing = False

            if self._exception_propagating:
                for exception in self._exceptions:
                    raise exception


class UseCases(enum.Enum):
    Command = 1
    Query = 2
    Event = 3


class HasUseCase:
    @staticmethod
    @abc.abstractmethod
    def use_case() -> UseCases:
        raise NotImplementedError


class Executor(HasUseCase, metaclass=Singleton):
    _loop: AsyncLoop = AsyncLoop()

    _deactivated = set()

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
