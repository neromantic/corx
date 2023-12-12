import abc
import typing

__all__ = [
    'Aggregate',
    'HasAggregate'
]


class Aggregate(object):
    ...


class HasAggregate:
    @staticmethod
    @abc.abstractmethod
    def aggregate() -> typing.Type[Aggregate]:
        raise NotImplementedError
