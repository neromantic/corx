from corx.command import CommandExecutor
from corx.dispatcher import Dispatcher
from corx.event import EventExecutor
from corx.query import QueryExecutor


def bootstrap():
    Dispatcher().register_executors(
        CommandExecutor(),
        QueryExecutor(),
        EventExecutor()
    )
