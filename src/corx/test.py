import abc
import typing
import unittest

import corx.command
import corx.dispatcher
import corx.event

__all__ = [
    'UnitTestCase'
]

EVENT_BUILTINS = [
    'timestamp',
    'uuid',
    'version',
]


class UnitTestCase(unittest.TestCase, abc.ABC):
    dispatcher: corx.dispatcher.Dispatcher

    @classmethod
    def setUpClass(cls):
        cls.dispatcher = corx.dispatcher.Dispatcher()
        cls._event_store = corx.event.reacts(corx.event.AnyEvent)(corx.event.RuntimeEventStore)()

        cls.dispatcher.propagate_exceptions(True)

    def tearDown(self):
        self._event_store.clear()

    def given(self, *events: corx.event.Event):
        self._event_store.seed_events(*events)

    def when(self, *commands: corx.command.Command):
        self.dispatcher.dispatch(*commands)

    def then(self, *expected_events: typing.Union[corx.event.EventType, corx.event.Event], strict: bool = False):
        log_events = self._event_store.get()

        if len(expected_events) != len(log_events):
            self.fail(f'Expected {len(expected_events)} events, but got {len(log_events)} events.')

        for expected, actual in zip(expected_events, log_events):
            if isinstance(expected, type):
                self.assertIsInstance(actual, expected, 'Event type mismatch.')
            elif isinstance(expected, corx.event.Event):
                excepted_data = expected.__dict__.copy()
                actual_data = actual.__dict__.copy()

                if not strict:
                    for builtin in EVENT_BUILTINS:
                        excepted_data.pop(builtin)
                        actual_data.pop(builtin)

                self.assertDictEqual(excepted_data, actual_data, 'Excepted Event data mismatch')
