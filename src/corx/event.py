import abc
import dataclasses
import datetime
import typing
import uuid

from corx.aggregate import Aggregate
from corx.base import UseCases, HasUseCase, Singleton, Executor
from corx.dispatcher import Dispatchable, Dispatcher

__all__ = [
    'Event',
    'EventListener',
    'EventExecutor',
    'RuntimeEventStore',
    'ProcessManager',
    'AnyEvent',
]


@dataclasses.dataclass
class Event(Dispatchable, abc.ABC):
    _versions = {}

    timestamp: float = dataclasses.field(init=False, default_factory=datetime.datetime.now().timestamp)
    uuid: str = dataclasses.field(init=False, default_factory=lambda: str(uuid.uuid4()))
    version: int = dataclasses.field(init=False)

    def __post_init__(self):
        self.version = self._versions.setdefault(type(self), 0) + 1
        self._versions[type(self)] = self.version

    @staticmethod
    def use_case() -> UseCases:
        return UseCases.Event

    @abc.abstractmethod
    def apply(self, aggregate: Aggregate):
        raise NotImplementedError


EventType = typing.TypeVar('EventType', bound=typing.Type[Event])


class AnyEvent(Event, abc.ABC):
    ...


class EventListener(HasUseCase):
    def __init__(self):
        for react in self.reacts():
            Dispatcher().register(react, type(self))

    @staticmethod
    def use_case() -> UseCases:
        return UseCases.Event

    @staticmethod
    def reacts() -> typing.Tuple[typing.Type[Event]]:
        return AnyEvent,

    @abc.abstractmethod
    async def react(self, event: Event):
        raise NotImplementedError


EventListenerType = typing.TypeVar('EventListenerType', bound=typing.Type[EventListener])


class ProcessManager(EventListener, abc.ABC):
    ...


class RuntimeEventStore(EventListener, metaclass=Singleton):
    def __init__(self):
        super().__init__()
        self._store: typing.Dict[str, Event] = {}

    async def react(self, event: Event):
        self._store[event.uuid] = event

    def clear(self):
        self._store.clear()

    def seed_events(self, *events: Event):
        for event in events:
            self._store[event.uuid] = event

    def get(self) -> typing.List[Event]:
        return sorted(self._store.values(), key=lambda event: event.timestamp)

    def get_latest_by_type(self, event_type: EventType) -> Event:
        events = list(self._store.values()).copy()
        events = filter(lambda event: type(event) is event_type, events)
        return sorted(events, key=lambda event: event.version)[-1]


class EventExecutor(Executor):
    @staticmethod
    def use_case() -> UseCases:
        return UseCases.Event

    _registry: typing.Dict[EventType, typing.List[EventListenerType]] = dict()

    def register(self, dispatchable: EventType, executable: EventListenerType):
        self._registry.setdefault(dispatchable, []).append(executable)

    def execute(self, dispatchable: Event):
        event_class = type(dispatchable)

        all_listeners: typing.List[EventListenerType] = (
                self._registry.get(event_class, [])
                + self._registry.get(AnyEvent, []))

        for listener_class in all_listeners:
            if listener_class not in self._deactivated:
                listener = listener_class()
                process = listener.react(dispatchable)
                self._loop.push(process)
