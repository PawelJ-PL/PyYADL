from time import time
from json import dumps, loads
from redis import StrictRedis, ConnectionPool, WatchError
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
        value = dumps({'timestamp': int(time()), 'secret': self._secret, 'exclusive': True})
        ttl = self.ttl if self.ttl > 0 else None
        result = self._client.set(name=self.LOCK_KEY, value=value, ex=ttl, nx=True)
        return bool(result)

    def _verify_secret(self) -> bool:
        result = self._client.get(self.LOCK_KEY)
        secret = loads(result.decode('utf-8')).get('secret') if result is not None else None
        if secret is None:
            raise RuntimeError('release unlocked lock')
        return secret == self._secret

    def _delete_lock(self):
        return bool(self._client.delete(self.LOCK_KEY))


class RedisWriteLock(RedisLock):
    pass


class RedisReadLock(RedisLock):
    def _write_lock_if_not_exists(self):
        with self._client.pipeline() as pipe:
            try:
                pipe.watch(self.LOCK_KEY)
                raw_lock_data = pipe.get(self.LOCK_KEY)
                lock_data = loads(raw_lock_data.decode('utf-8')) if raw_lock_data else self._generate_new_lock_data()
                if not self._is_valid_read_lock_data(lock_data):
                    return False

                lock_data['secret'] = list(set(lock_data['secret'] + [self._secret]))
                lock_data['timestamp'] = int(time())
                ttl = self.ttl if self.ttl > 0 else None
                pipe.multi()
                pipe.set(self.LOCK_KEY, value=dumps(lock_data), ex=ttl)
                pipe.execute()
                return True
            except WatchError:
                self.logger.info('Key %s has changed during transaction. Trying to retry', self.LOCK_KEY)
                return self._write_lock_if_not_exists()

    @staticmethod
    def _is_valid_read_lock_data(lock_data):
        return (lock_data.get('exclusive', True) is False) and (isinstance(lock_data.get('secret'), (list, set, tuple)))

    def _generate_new_lock_data(self):
        return {'timestamp': int(time()), 'secret': [self._secret], 'exclusive': False}

    def _verify_secret(self) -> bool:
        with self._client.pipeline() as pipe:
            try:
                pipe.watch(self.LOCK_KEY)
                raw_lock_data = pipe.get(self.LOCK_KEY)
                if raw_lock_data is None:
                    return False
                lock_data = loads(raw_lock_data.decode('utf-8'))
                if not self._is_valid_read_lock_data(lock_data):
                    return False
                return self._secret in lock_data['secret']
            except WatchError:
                self.logger.info('Key %s has changed during transaction. Trying to retry', self.LOCK_KEY)
                return self._verify_secret()

    def _delete_lock(self):
        with self._client.pipeline() as pipe:
            try:
                pipe.watch(self.LOCK_KEY)
                raw_lock_data = pipe.get(self.LOCK_KEY)
                if raw_lock_data is None:
                    return False
                lock_data = loads(raw_lock_data.decode('utf-8'))
                if not self._is_valid_read_lock_data(lock_data):
                    return False
                if self._secret not in lock_data['secret']:
                    return False
                secrets = lock_data['secret']
                secrets.remove(self._secret)
                ttl = pipe.ttl(self.LOCK_KEY)
                if not secrets:
                    pipe.multi()
                    pipe.delete(self.LOCK_KEY)
                    pipe.execute()
                    return True
                else:
                    lock_data['secret'] = secrets
                    pipe.multi()
                    pipe.set(self.LOCK_KEY, value=dumps(lock_data), ex=ttl)
                    pipe.execute()
                    return True
            except WatchError:
                self.logger.info('Key %s has changed during transaction. Trying to retry', self.LOCK_KEY)
                return self._delete_lock()
