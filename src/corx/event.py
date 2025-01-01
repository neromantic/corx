import abc
import dataclasses
import datetime
import typing
import uuid

from corx.dispatcher import Dispatchable, get_dispatcher, Executor

__all__ = [
    'Event',
    'EventType',
    'EventListener',
    'EventExecutor',
    'RuntimeEventStore',
    'ProcessManager',
    'AnyEvent',
]

_T = typing.TypeVar('_T')

@dataclasses.dataclass
class Event(typing.Generic[_T], Dispatchable, abc.ABC):
    _versions = {}

    timestamp: float = dataclasses.field(init=False, default_factory=datetime.datetime.now().timestamp)
    uuid: str = dataclasses.field(init=False, default_factory=lambda: str(uuid.uuid4()))
    version: int = dataclasses.field(init=False)

    def __post_init__(self):
        self.version = self._versions.setdefault(type(self), 0) + 1
        self._versions[type(self)] = self.version

    @abc.abstractmethod
    def apply(self, aggregate: _T):
        raise NotImplementedError


EventType = typing.TypeVar('EventType', bound=typing.Type[Event])


class AnyEvent(Event, abc.ABC):
    ...


class EventListener():
    @abc.abstractmethod
    async def react(self, event: Event):
        raise NotImplementedError


EventListenerType = typing.TypeVar('EventListenerType', bound=typing.Callable[[Event], typing.Union[typing.Coroutine, typing.Any]])


def reacts(*events: EventType):
    def wrap(cls):
        for react in events:
            get_dispatcher().register(react, cls)
        return cls

    return wrap


class ProcessManager(EventListener, abc.ABC):
    ...


class RuntimeEventStore(EventListener):
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
    _registry: typing.Dict[EventType, typing.List[EventListenerType]] = dict()

    def register(self, dispatchable: EventType, executable: EventListenerType):
        self._registry.setdefault(dispatchable, []).append(executable)

    def execute(self, dispatchable: Event):
        event_class = type(dispatchable)

        all_listeners: typing.List[EventListenerType] = (
                self._registry.get(event_class, [])
                + self._registry.get(AnyEvent, []))

        for listener in all_listeners:
            if listener not in self._deactivated:
                process = listener(dispatchable)
                self._loop.push(process)
