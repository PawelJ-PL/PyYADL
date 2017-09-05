from redis import StrictRedis, ConnectionPool
from PyYADL.distributed_lock import AbstractDistributedLock


class RedisLock(AbstractDistributedLock):

    def __init__(self, name, prefix=None, ttl=-1, existing_connection_pool=None, redis_host='localhost', redis_port=6379,
                 redis_password=None, redis_db=0, **kwargs):
        super().__init__(name, prefix, ttl)
        client_connection = existing_connection_pool or ConnectionPool(host=redis_host, port=redis_port,
                                                                       password=redis_password, db=redis_db, **kwargs)
        self._client = StrictRedis(connection_pool=client_connection)

    def _write_lock_if_not_exists(self):
        pass
