from uuid import uuid4
from abc import ABCMeta, abstractmethod


class AbstractDistributedLock(metaclass=ABCMeta):
    def __init__(self, name, prefix=None, ttl=-1):
        self.ttl = ttl
        self.name = name
        self.prefix = prefix
        self._secret = uuid4()

    def acquire(self, blocking=True, timeout=-1):
        self._write_lock_if_not_exists()

    def release(self, force=False):
        pass

    @abstractmethod
    def _write_lock_if_not_exists(self) -> bool:
        pass

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __str__(self):
        return '<{0}.{1} object at {2}> prefix: {3}, name: {4} , ttl: {5}, _secret: {6}'.format(__name__,
                                                                                               self.__class__.__name__,
                                                                                               hex(id(self)), self.prefix,
                                                                                               self.name, self.ttl,
                                                                                               self._secret)
