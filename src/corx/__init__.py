__version__ = "1.0.0"

from . import aggregate
from . import bootstrap
from . import command
from . import dispatcher
from . import event
from . import query
from . import test

__all__ = [
    'test',
    'command',
    'query',
    'event',
    'dispatcher',
    'aggregate',
]

bootstrap.bootstrap()
