# **PyYADL** (Yet Another Distributed Lock)

## description
This is yet another distributed lock for Python with interface compatible with standard Lock/RLock class (only constructor parameters are different and release method has one optional parameter _force_)

Currently there is only one implementation, based on Redis, but it's very easy to extend base class and adapt it to any other distributed storage (like Etcd, databases - both relational and NoSQL, distributed file systems etc.)

## Redis lock
### usage

#### examples:

**Create lock object**
```python
from PyYADL.redis_lock import RedisLock
lock = RedisLock(name='test_lock', prefix='my_app', ttl=60, existing_connection_pool=None, redis_host='127.0.0.1', redis_port=6379, redis_password='secret', redis_db=0)
```
Parameters meaning:
* **name** - each resource should have unique lock name, which would be shared across all systems. `Required`
* **prefix** - prefix useful to avoid conflicts in names. `Optional`
* **ttl** - how many seconds lock will be active. If ttl <= 0, lock will be valid until release. `Optional` `Default: -1`
* **existing_connection_pool** already established connection pool `Optional`
* **redis_host** `Optional` `Default: localhost`
* **redis_port** `Optional` `Default: 6379`
* **redis_password** `Optional`
* **redis_db** `Optional` `Default: 0`

**Basic usage**
```python
from PyYADL.redis_lock import RedisLock

lock = RedisLock('test_lock')
lock.acquire()
lock.release()
```
Basic lock and release operations. If lock already acquired, will wait for release or ttl expire

```python
from PyYADL.redis_lock import RedisLock

lock = RedisLock('test_lock')
with lock:
    # do some tasks
    pass
```
Lock and release using context manager

```python
from PyYADL.redis_lock import RedisLock

lock1 = RedisLock('test_lock')
lock2 = RedisLock('test_lock')
lock1.acquire()
lock2.release()
```
Will raise RuntimeError (because lock is owned by other instance)

```python
from PyYADL.redis_lock import RedisLock

lock1 = RedisLock('test_lock')
lock2 = RedisLock('test_lock')
lock1.acquire()
lock2.release(force=True)
```
Will release lock, because force parameter is set to True

```python
from PyYADL.redis_lock import RedisLock

lock = RedisLock('test_lock')
status = lock.acquire(blocking=False)
```
Will acquire lock and return True, if lock released, otherwise return False without waiting

```python
from PyYADL.redis_lock import RedisLock

lock = RedisLock('test_lock')
status = lock.acquire(timeout=12)
```
Will try to acquire lock for 12 seconds. In case of success will return True, otherwise return False