import asyncio
import dataclasses

from corx.command import Command, handles
from corx.dispatcher import get_dispatcher, dispatch
from corx.event import Event, reacts

class Aggregate:
    duration = 0
    def set_duration(self, duration: int):
        self.duration = duration

@dataclasses.dataclass
class Ping(Command):
    duration: int


@dataclasses.dataclass
class Pong(Event[Aggregate]):
    duration: int

    def apply(self, aggregate):
        aggregate.set_duration(self.duration)


@handles(Ping)
async def handle_ping(command: Ping):
    print(f'Ping {command.duration}')
    await asyncio.sleep(command.duration)

    dispatch(Pong(duration=command.duration))


@reacts(Pong)
async def react_pong(event: Pong):
    print(f'Pong {event.duration}')
    await asyncio.sleep(event.duration)

    dispatch(Ping(duration=event.duration))



if __name__ == '__main__':
    get_dispatcher().propagate_exceptions(True)
    dispatch(Ping(duration=1), Ping(duration=2), Ping(duration=3))
