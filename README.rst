**PyYADL** (Yet Another Distributed Lock)
=========================================

description
-----------

This is yet another distributed lock for Python with interface
compatible with standard Lock/RLock class (only constructor parameters
are different and release method has one optional parameter *force*)

Currently there is only one implementation, based on Redis, but it's
very easy to extend base class and adapt it to any other distributed
storage (like Etcd, databases - both relational and NoSQL, distributed
file systems etc.)

Redis lock
----------

usage
~~~~~

examples:
^^^^^^^^^

**Create lock object**

.. code:: python

    from PyYADL import RedisLock
    lock = RedisLock(name='test_lock', prefix='my_app', ttl=60, existing_connection_pool=None, redis_host='127.0.0.1', redis_port=6379, redis_password='secret', redis_db=0)

Parameters meaning: \* **name** - each resource should have unique lock
name, which would be shared across all systems. ``Required`` \*
**prefix** - prefix useful to avoid conflicts in names. ``Optional`` \*
**ttl** - how many seconds lock will be active. If ttl <= 0, lock will
be valid until release. ``Optional`` ``Default: -1`` \*
**existing\_connection\_pool** already established connection pool
``Optional`` \* **redis\_host** ``Optional`` ``Default: localhost`` \*
**redis\_port** ``Optional`` ``Default: 6379`` \* **redis\_password**
``Optional`` \* **redis\_db** ``Optional`` ``Default: 0``

**Basic usage**

.. code:: python

    from PyYADL import RedisLock

    lock = RedisLock('test_lock')
    lock.acquire()
    lock.release()

Basic lock and release operations. If lock already acquired, will wait
for release or ttl expire

.. code:: python

    from PyYADL import RedisLock

    lock = RedisLock('test_lock')
    with lock:
        # do some tasks
        pass

Lock and release using context manager

.. code:: python

    from PyYADL import RedisLock

    lock1 = RedisLock('test_lock')
    lock2 = RedisLock('test_lock')
    lock1.acquire()
    lock2.release()

Will raise RuntimeError (because lock is owned by other instance)

.. code:: python

    from PyYADL import RedisLock

    lock1 = RedisLock('test_lock')
    lock2 = RedisLock('test_lock')
    lock1.acquire()
    lock2.release(force=True)

Will release lock, because force parameter is set to True

.. code:: python

    from PyYADL import RedisLock

    lock = RedisLock('test_lock')
    status = lock.acquire(blocking=False)

Will acquire lock and return True, if lock released, otherwise return
False without waiting

.. code:: python

    from PyYADL import RedisLock

    lock = RedisLock('test_lock')
    status = lock.acquire(timeout=12)

Will try to acquire lock for 12 seconds. In case of success will return
True, otherwise return False

Read and Write locks
--------------------

There are two lock subtypes: \* Write Lock (typical lock, exclusive) \*
Read Lock (non exclusive)

At the same time, there can be only one write lock (mainly for changes)
or many read lock (mainly for read operations). If write lock has been
acquired, read lock cannot be obtained and when at least one read lock
exists, write lock cannot be acuired.

Usage
~~~~~

Examples
^^^^^^^^

.. code:: python

    from PyYADL import RedisWriteLock

    lock = RedisWriteLock('test_lock')
    status = lock.acquire(blocking=True, timeout=20)

Equivalent of RedisLock class

.. code:: python

    from PyYADL import RedisReadLock

    lock1 = RedisReadLock('test_lock')
    lock2 = RedisReadLock('test_lock')
    lock1.acquire()
    lock2.acquire()

Will create two read locks (at the same time there can be many read
locks)

.. code:: python

    from PyYADL import RedisReadLock, RedisWriteLock

    lock1 = RedisReadLock('test_lock')
    lock2 = RedisReadLock('test_lock')
    lock3 = RedisWriteLock('test_lock')
    lock1.acquire()
    lock2.acquire()
    lock3.acquire()

Will acquire only lock1 and lock2 (write lock can't be obtained when
other locks exists)

.. code:: python

    from PyYADL import RedisReadLock, RedisWriteLock

    lock1 = RedisWriteLock('test_lock')
    lock2 = RedisReadLock('test_lock')

    lock1.acquire()
    lock2.acquire()

Will acquire only lock1 (when write lock exists, read lock cannot be
obtained)
