from time import time
from json import dumps, loads
from redis import StrictRedis, ConnectionPool
from PyYADL.distributed_lock import AbstractDistributedLock


class RedisLock(AbstractDistributedLock):

    def __init__(self, name, prefix=None, ttl=-1, existing_connection_pool=None, redis_host='localhost', redis_port=6379,
                 redis_password=None, redis_db=0, **kwargs):
        super().__init__(name, prefix, ttl)
        client_connection = existing_connection_pool or ConnectionPool(host=redis_host, port=redis_port,
                                                                       password=redis_password, db=redis_db, **kwargs)
        self._client = StrictRedis(connection_pool=client_connection)
        self.LOCK_KEY = self._build_lock_key()

    def _build_lock_key(self):
        key = ''
        if self.prefix:
            key = key + self.prefix + ':'
        key = key + 'lock:' + self.name
        return key

    def _write_lock_if_not_exists(self):
        value = dumps({'timestamp': int(time()), 'secret': self._secret})
        ttl = self.ttl if self.ttl > 0 else None
        result = self._client.set(name=self.LOCK_KEY, value=value, ex=ttl, nx=True)
        return bool(result)

    def _read_secret(self):
        result = self._client.get(self.LOCK_KEY)
        return loads(result.decode('utf-8')).get('secret') if result is not None else None

    def _delete_lock(self):
        return bool(self._client.delete(self.LOCK_KEY))
