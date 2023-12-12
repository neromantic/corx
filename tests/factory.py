import dataclasses
import typing

import corx

HandlerClosure = typing.NewType('HandleClosure', typing.Union[
    typing.Callable[[corx.command.CommandHandler, corx.command.Command], None],
    typing.Coroutine
])


class CommandFactory(object):
    @staticmethod
    def create_command(name: str, fields: typing.List[str] = None):
        if not fields:
            fields = []

        return dataclasses.make_dataclass(
            cls_name=name,
            fields=[(field, typing.Any) for field in fields],
            bases=(corx.command.Command,),
        )

    @staticmethod
    def register_command_handler(command: typing.Type[corx.command.Command],
                                 cb: HandlerClosure) -> corx.command.CommandHandler:
        handler_cls = type(
            command.__name__ + 'Handler',
            (corx.command.CommandHandler,),
            {
                'handle': cb,
                'handles': lambda self_: command
            }
        )

        return handler_cls()


class EventFactory(object):
    @staticmethod
    def create_event(name: str, fields: typing.List[str] = None):
        if not fields:
            fields = []

        return dataclasses.make_dataclass(
            cls_name=name,
            fields=[(field, typing.Any) for field in fields],
            bases=(corx.event.Event,),
            namespace={
                'apply': lambda self_, aggregate: None
            }
        )
