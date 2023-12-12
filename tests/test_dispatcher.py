import asyncio
import time
import unittest

import corx
from .factory import CommandFactory, EventFactory


class TestDispatcher(corx.test.UnitTestCase):
    def test_sync_dispatch(self):
        command = CommandFactory.create_command('DispatchCommand', ['duration'])
        event = EventFactory.create_event('EmittedEvent')

        def handle(self_, command_):
            time.sleep(command_.duration)
            event.dispatch()

        CommandFactory.register_command_handler(command, handle)

        start = time.time()
        self.when(command(duration=0.1), command(duration=0.1))

        self.assertAlmostEqual(0.2, time.time() - start, 1)

    def test_async_dispatch(self):
        command = CommandFactory.create_command('DispatchCommand', ['duration'])

        event = EventFactory.create_event('EmittedEvent')

        async def handle(self_, command_):
            await asyncio.sleep(command_.duration)
            event.dispatch()

        CommandFactory.register_command_handler(command, handle)

        start = time.time()
        self.when(command(duration=0.1), command(duration=0.1))

        self.assertAlmostEqual(0.1, time.time() - start, 1)

    def test_dispatched_events(self):
        id_counter = 0

        command = CommandFactory.create_command('DispatchCommand')
        given_event = EventFactory.create_event('GivenEvent')
        emitted_event = EventFactory.create_event('EmittedEvent', ['counter'])

        async def handle(self_, command_):
            nonlocal id_counter
            emitted_event.dispatch(counter=id_counter)
            id_counter += 1

        CommandFactory.register_command_handler(command, handle)

        self.given(given_event())

        self.when(command(), command())

        self.then(
            given_event,
            emitted_event(counter=0),
            emitted_event(counter=1),
        )

        last_given_event = self._event_store.get_latest_by_type(given_event)
        last_emitted_event = self._event_store.get_latest_by_type(emitted_event)

        self.assertEqual(1, last_given_event.version)
        self.assertEqual(2, last_emitted_event.version)


if __name__ == '__main__':
    unittest.main()
