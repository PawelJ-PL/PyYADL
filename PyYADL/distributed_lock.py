from logging import getLogger
from time import time, sleep
from uuid import uuid4
from abc import ABCMeta, abstractmethod


class AbstractDistributedLock(metaclass=ABCMeta):
    def __init__(self, name, prefix=None, ttl=-1):
        self.ttl = ttl
        self.name = name
        self.prefix = prefix
        self._secret = str(uuid4())
        self.logger = getLogger(self.__class__.__name__)

    def acquire(self, blocking=True, timeout=-1):
        entered_at = time()
        while True:
            result = self._write_lock_if_not_exists()
            if result:
                return True
            elif not blocking or (timeout > 0 and time() > entered_at + timeout):
                return False
            sleep(1)

    def release(self, force=False):
        if force or self._verify_secret():
            result = self._delete_lock()
            if not result:
                raise RuntimeError('release unlocked lock')
        else:
            raise RuntimeError('cannot release un-acquired lock')

    @abstractmethod
    def _write_lock_if_not_exists(self) -> bool:
        pass

    @abstractmethod
    def _verify_secret(self) -> bool:
        pass

    @abstractmethod
    def _delete_lock(self) -> bool:
        pass

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def __str__(self):
        return '<{0}.{1} object at {2}> prefix: {3}, name: {4} , ttl: {5}, _secret: {6}'.format(__name__,
                                                                                                self.__class__.__name__,
                                                                                                hex(id(self)), self.prefix,
                                                                                                self.name, self.ttl,
                                                                                                self._secret)
