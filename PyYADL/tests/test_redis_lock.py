from json import loads
from unittest import TestCase
from unittest.mock import patch, ANY, MagicMock

from redis import WatchError

from PyYADL import RedisLock, RedisWriteLock, RedisReadLock


class TestRedisLock(TestCase):

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    @patch('PyYADL.redis_lock.time')
    @patch('PyYADL.distributed_lock.sleep')
    def test_should_acquire_new_lock(self, mock_sleep, mock_time, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'SecretData'
        lock = RedisLock(name='TestLock', prefix='RedisLockUnitTest')
        mock_redis.return_value.set.return_value = True
        mock_time.return_value = 1504732028

        # when
        result = lock.acquire()

        # then
        self.assertTrue(result)
        mock_redis.return_value.set.assert_called_once_with(ex=None, name='RedisLockUnitTest:lock:TestLock', nx=True,
                                                            value=ANY)
        value = mock_redis.return_value.set.mock_calls[0][2].get('value')
        self.assertDictEqual(loads(value), {'timestamp': 1504732028, 'secret': 'SecretData', 'exclusive': True})
        mock_sleep.assert_not_called()

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    @patch('PyYADL.redis_lock.time')
    @patch('PyYADL.distributed_lock.sleep')
    def test_should_acquire_new_write_lock(self, mock_sleep, mock_time, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'SecretData'
        lock = RedisWriteLock(name='TestLock', prefix='RedisLockUnitTest')
        mock_redis.return_value.set.return_value = True
        mock_time.return_value = 1504732028

        # when
        result = lock.acquire()

        # then
        self.assertTrue(result)
        mock_redis.return_value.set.assert_called_once_with(ex=None, name='RedisLockUnitTest:lock:TestLock', nx=True,
                                                            value=ANY)
        value = mock_redis.return_value.set.mock_calls[0][2].get('value')
        self.assertDictEqual(loads(value), {'timestamp': 1504732028, 'secret': 'SecretData', 'exclusive': True})
        mock_sleep.assert_not_called()

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    @patch('PyYADL.redis_lock.time')
    @patch('PyYADL.distributed_lock.sleep')
    def test_should_acquire_new_lock_with_ttl(self, mock_sleep, mock_time, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'SecretData'
        lock = RedisLock(name='TestLock', prefix='RedisLockUnitTest', ttl=15)
        mock_redis.return_value.set.return_value = True
        mock_time.return_value = 1504732028

        # when
        result = lock.acquire()

        # then
        self.assertTrue(result)
        mock_redis.return_value.set.assert_called_once_with(ex=15, name='RedisLockUnitTest:lock:TestLock', nx=True,
                                                            value=ANY)
        value = mock_redis.return_value.set.mock_calls[0][2].get('value')
        self.assertDictEqual(loads(value), {'timestamp': 1504732028, 'secret': 'SecretData', 'exclusive': True})
        mock_sleep.assert_not_called()

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    @patch('PyYADL.redis_lock.time')
    @patch('PyYADL.distributed_lock.sleep')
    def test_should_wait_when_lock_exists(self, mock_sleep, mock_time, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'SecretData'
        lock = RedisLock(name='TestLock', prefix='RedisLockUnitTest', ttl=15)
        mock_redis.return_value.set.side_effect = (False, False, False, True)
        mock_time.return_value = 1504732028

        # when
        result = lock.acquire()

        # then
        self.assertTrue(result)
        mock_redis.return_value.set.assert_called_with(ex=15, name='RedisLockUnitTest:lock:TestLock', nx=True, value=ANY)
        self.assertEqual(mock_redis.return_value.set.call_count, 4)
        value = mock_redis.return_value.set.mock_calls[0][2].get('value')
        self.assertDictEqual(loads(value), {'timestamp': 1504732028, 'secret': 'SecretData', 'exclusive': True})
        self.assertEqual(mock_sleep.call_count, 3)

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    @patch('PyYADL.redis_lock.time')
    @patch('PyYADL.distributed_lock.sleep')
    def test_should_return_false_when_non_blocking_and_lock_exists(self, mock_sleep, mock_time, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'SecretData'
        lock = RedisLock(name='TestLock', prefix='RedisLockUnitTest')
        mock_redis.return_value.set.return_value = False
        mock_time.return_value = 1504732028

        # when
        result = lock.acquire(blocking=False)

        # then
        self.assertFalse(result)
        mock_redis.return_value.set.assert_called_once_with(ex=None, name='RedisLockUnitTest:lock:TestLock', nx=True,
                                                            value=ANY)
        value = mock_redis.return_value.set.mock_calls[0][2].get('value')
        self.assertDictEqual(loads(value), {'timestamp': 1504732028, 'secret': 'SecretData', 'exclusive': True})
        mock_sleep.assert_not_called()

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    @patch('PyYADL.distributed_lock.sleep')
    @patch('PyYADL.distributed_lock.time')
    def test_should_wait_timeout_period_and_return_true_if_success_locked(self, mock_time, mock_sleep, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'SecretData'
        lock = RedisLock(name='TestLock', prefix='RedisLockUnitTest')
        mock_redis.return_value.set.side_effect = (False, False, True)
        mock_time.side_effect = (1504732028, 1504732029, 1504732030)

        # when
        result = lock.acquire(timeout=3)

        # then
        self.assertTrue(result)
        mock_redis.return_value.set.assert_called_with(ex=None, name='RedisLockUnitTest:lock:TestLock', nx=True,
                                                       value=ANY)
        self.assertEqual(mock_redis.return_value.set.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    @patch('PyYADL.distributed_lock.sleep')
    @patch('PyYADL.distributed_lock.time')
    def test_should_wait_timeout_period_and_return_false_if_success_failed(self, mock_time, mock_sleep, mock_uuid,
                                                                           mock_redis):
        # given
        mock_uuid.return_value = 'SecretData'
        lock = RedisLock(name='TestLock', prefix='RedisLockUnitTest')
        mock_redis.return_value.set.return_value = False
        mock_time.side_effect = (1504732028, 1504732029, 1504732030, 1504732031, 1504732032)

        # when
        result = lock.acquire(timeout=3)

        # then
        self.assertFalse(result)
        mock_redis.return_value.set.assert_called_with(ex=None, name='RedisLockUnitTest:lock:TestLock', nx=True,
                                                       value=ANY)
        self.assertEqual(mock_redis.return_value.set.call_count, 4)
        self.assertEqual(mock_sleep.call_count, 3)

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    def test_should_release_lock(self, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'QWERTY'
        lock = RedisLock(name='TestLock', prefix='RedisLockUnitTest')
        mock_redis.return_value.get.return_value = b'{"secret": "QWERTY", "timestamp": 1504732028}'
        mock_redis.return_value.delete.return_value = 1

        # when
        lock.release()

        # then
        mock_redis.return_value.delete.assert_called_once_with('RedisLockUnitTest:lock:TestLock')

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    def test_should_raise_exception_when_no_lock_found(self, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'QWERTY'
        lock = RedisLock(name='TestLock', prefix='RedisLockUnitTest')
        mock_redis.return_value.get.return_value = None
        mock_redis.return_value.delete.return_value = 1

        # when
        with self.assertRaisesRegex(RuntimeError, 'release unlocked lock'):
            lock.release()

        # then
        mock_redis.return_value.delete.assert_not_called()

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    def test_should_raise_exception_when_try_to_release_lock_owned_by_other_instance(self, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'QWERTY'
        lock = RedisLock(name='TestLock', prefix='RedisLockUnitTest')
        mock_redis.return_value.get.return_value = b'{"secret": "ABCDE", "timestamp": 1504732028}'
        mock_redis.return_value.delete.return_value = 1

        # when
        with self.assertRaisesRegex(RuntimeError, 'cannot release un-acquired lock'):
            lock.release()

        # then
        mock_redis.return_value.delete.assert_not_called()

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    def test_should_raise_exception_when_lock_released_in_meantime(self, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'QWERTY'
        lock = RedisLock(name='TestLock', prefix='RedisLockUnitTest')
        mock_redis.return_value.get.return_value = b'{"secret": "QWERTY", "timestamp": 1504732028}'
        mock_redis.return_value.delete.return_value = 0

        # when
        with self.assertRaisesRegex(RuntimeError, 'release unlocked lock'):
            lock.release()

        # then
        mock_redis.return_value.delete.assert_called_once_with('RedisLockUnitTest:lock:TestLock')

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    def test_should_release_lock_owned_by_other_instance_when_force(self, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'QWERTY'
        lock = RedisLock(name='TestLock', prefix='RedisLockUnitTest')
        mock_redis.return_value.get.return_value = b'{"secret": "ABCDE", "timestamp": 1504732028}'
        mock_redis.return_value.delete.return_value = 1

        # when
        lock.release(force=True)

        # then
        mock_redis.return_value.delete.assert_called_once_with('RedisLockUnitTest:lock:TestLock')

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    @patch('PyYADL.redis_lock.time')
    def test_should_acquire_read_lock_when_not_exists(self, mock_time, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'QWERTY'
        pipeline = MagicMock()
        pipeline.return_value.get.return_value = None
        mock_redis.return_value.pipeline.return_value.__enter__ = pipeline
        lock = RedisReadLock('TestLock', prefix='RedisLockUnitTest')
        mock_time.return_value = 123456

        # when
        result = lock.acquire()

        # then
        self.assertTrue(result)
        pipeline.return_value.watch.assert_called_once_with('RedisLockUnitTest:lock:TestLock')
        pipeline.return_value.set.assert_called_once_with('RedisLockUnitTest:lock:TestLock', ex=None, value=ANY)
        value = pipeline.return_value.set.mock_calls[0][2].get('value')
        self.assertDictEqual(loads(value), {'timestamp': 123456, 'secret': ['QWERTY'], 'exclusive': False})
        pipeline.return_value.execute.assert_called_once_with()

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    @patch('PyYADL.redis_lock.time')
    def test_should_acquire_read_lock_when_other_non_exclusive_exists(self, mock_time, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'QWERTY'
        pipeline = MagicMock()
        pipeline.return_value.get.return_value =\
            b'{"timestamp": 123456, "secret": ["secret", "other"], "exclusive": false}'
        mock_redis.return_value.pipeline.return_value.__enter__ = pipeline
        lock = RedisReadLock('TestLock', prefix='RedisLockUnitTest')
        mock_time.return_value = 123456

        # when
        result = lock.acquire()

        # then
        self.assertTrue(result)
        pipeline.return_value.watch.assert_called_once_with('RedisLockUnitTest:lock:TestLock')
        pipeline.return_value.set.assert_called_once_with('RedisLockUnitTest:lock:TestLock', ex=None, value=ANY)
        value = pipeline.return_value.set.mock_calls[0][2].get('value')
        self.assertDictEqual(loads(value), {'timestamp': 123456, 'secret': ANY, 'exclusive': False})
        secrets = loads(value).get('secret')
        self.assertSetEqual(set(secrets), {'QWERTY', 'secret', 'other'})
        pipeline.return_value.execute.assert_called_once_with()

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    @patch('PyYADL.redis_lock.time')
    def test_should_repeat_query_when_value_changed_in_meantime(self, mock_time, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'QWERTY'
        pipeline = MagicMock()
        pipeline.return_value.get.return_value = None
        mock_redis.return_value.pipeline.return_value.__enter__ = pipeline
        lock = RedisReadLock('TestLock', prefix='RedisLockUnitTest')
        mock_time.return_value = 123456
        pipeline.return_value.set.side_effect = (WatchError(), WatchError(), 'OK')

        # when
        result = lock.acquire()

        # then
        self.assertTrue(result)
        self.assertEqual(pipeline.return_value.watch.call_count, 3)
        self.assertEqual(pipeline.return_value.set.call_count, 3)
        value = pipeline.return_value.set.mock_calls[0][2].get('value')
        self.assertDictEqual(loads(value), {'timestamp': 123456, 'secret': ['QWERTY'], 'exclusive': False})
        pipeline.return_value.execute.assert_called_once_with()

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    @patch('PyYADL.redis_lock.time')
    def test_should_not_acquire_read_lock_when_write_lock_exists(self, mock_time, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'QWERTY'
        pipeline = MagicMock()
        pipeline.return_value.get.return_value = \
            b'{"timestamp": 123456, "secret": "secretData", "exclusive": true}'
        mock_redis.return_value.pipeline.return_value.__enter__ = pipeline
        lock = RedisReadLock('TestLock', prefix='RedisLockUnitTest')
        mock_time.return_value = 123456

        # when
        result = lock.acquire(blocking=False)

        # then
        self.assertFalse(result)
        pipeline.return_value.watch.assert_called_once_with('RedisLockUnitTest:lock:TestLock')
        pipeline.return_value.set.assert_not_called()

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    @patch('PyYADL.redis_lock.time')
    def test_should_not_acquire_read_lock_when_non_exclusive_lock_exists_with_non_list_secret(self, mock_time, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'QWERTY'
        pipeline = MagicMock()
        pipeline.return_value.get.return_value = \
            b'{"timestamp": 123456, "secret": "secretData", "exclusive": false}'
        mock_redis.return_value.pipeline.return_value.__enter__ = pipeline
        lock = RedisReadLock('TestLock', prefix='RedisLockUnitTest')
        mock_time.return_value = 123456

        # when
        result = lock.acquire(blocking=False)

        # then
        self.assertFalse(result)
        pipeline.return_value.watch.assert_called_once_with('RedisLockUnitTest:lock:TestLock')
        pipeline.return_value.set.assert_not_called()

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    def test_should_release_single_read_lock_when_others_not_exists(self, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'QWERTY'
        pipeline_verify_secret = MagicMock()
        pipeline_delete_lock = MagicMock()
        pipeline_verify_secret.return_value.get.return_value = \
            b'{"timestamp": 123456, "secret": ["QWERTY"], "exclusive": false}'
        pipeline_delete_lock.return_value.get.return_value = \
            b'{"timestamp": 123456, "secret": ["QWERTY"], "exclusive": false}'
        verify_secret_pipeline_cm = MagicMock()
        delete_lock_pipeline_cm = MagicMock()
        verify_secret_pipeline_cm.__enter__ = pipeline_verify_secret
        delete_lock_pipeline_cm.__enter__ = pipeline_delete_lock
        mock_redis.return_value.pipeline.side_effect = (verify_secret_pipeline_cm, delete_lock_pipeline_cm)
        lock = RedisReadLock('TestLock', prefix='RedisLockUnitTest')

        # when
        lock.release()

        # then
        pipeline_delete_lock.return_value.watch.assert_called_once_with('RedisLockUnitTest:lock:TestLock')
        pipeline_delete_lock.return_value.delete.assert_called_once_with('RedisLockUnitTest:lock:TestLock')
        pipeline_delete_lock.return_value.execute.assert_called_once_with()

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    def test_should_only_remove_secret_on_release_when_multiple_read_locks(self, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'QWERTY'
        pipeline_verify_secret = MagicMock()
        pipeline_delete_lock = MagicMock()
        pipeline_verify_secret.return_value.get.return_value = \
            b'{"timestamp": 123456, "secret": ["QWERTY", "secretData"], "exclusive": false}'
        pipeline_delete_lock.return_value.get.return_value = \
            b'{"timestamp": 123456, "secret": ["QWERTY", "secretData"], "exclusive": false}'
        pipeline_delete_lock.return_value.ttl.return_value = 102
        verify_secret_pipeline_cm = MagicMock()
        delete_lock_pipeline_cm = MagicMock()
        verify_secret_pipeline_cm.__enter__ = pipeline_verify_secret
        delete_lock_pipeline_cm.__enter__ = pipeline_delete_lock
        mock_redis.return_value.pipeline.side_effect = (verify_secret_pipeline_cm, delete_lock_pipeline_cm)
        lock = RedisReadLock('TestLock', prefix='RedisLockUnitTest')

        # when
        lock.release()

        # then
        pipeline_delete_lock.return_value.watch.assert_called_once_with('RedisLockUnitTest:lock:TestLock')
        pipeline_delete_lock.return_value.delete.assert_not_called()
        pipeline_delete_lock.return_value.set.assert_called_once_with('RedisLockUnitTest:lock:TestLock', ex=102, value=ANY)
        value = pipeline_delete_lock.return_value.set.mock_calls[0][2].get('value')
        self.assertDictEqual(loads(value), {'timestamp': 123456, 'secret': ['secretData'], 'exclusive': False})

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    def test_should_not_release_read_lock_when_exclusive_exists(self, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'QWERTY'
        pipeline_verify_secret = MagicMock()
        pipeline_verify_secret.return_value.get.return_value = \
            b'{"timestamp": 123456, "secret": ["QWERTY"], "exclusive": true}'
        verify_secret_pipeline_cm = MagicMock()
        verify_secret_pipeline_cm.__enter__ = pipeline_verify_secret
        mock_redis.return_value.pipeline.return_value = verify_secret_pipeline_cm
        lock = RedisReadLock('TestLock', prefix='RedisLockUnitTest')

        # when
        with self.assertRaisesRegex(RuntimeError, 'cannot release un-acquired lock'):
            lock.release()

        # then
        pipeline_verify_secret.return_value.watch.assert_called_once_with('RedisLockUnitTest:lock:TestLock')

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    def test_should_not_release_read_lock_when_not_list_secrets(self, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'QWERTY'
        pipeline_verify_secret = MagicMock()
        pipeline_verify_secret.return_value.get.return_value = \
            b'{"timestamp": 123456, "secret": "QWERTY", "exclusive": false}'
        verify_secret_pipeline_cm = MagicMock()
        verify_secret_pipeline_cm.__enter__ = pipeline_verify_secret
        mock_redis.return_value.pipeline.return_value = verify_secret_pipeline_cm
        lock = RedisReadLock('TestLock', prefix='RedisLockUnitTest')

        # when
        with self.assertRaisesRegex(RuntimeError, 'cannot release un-acquired lock'):
            lock.release()

        # then
        pipeline_verify_secret.return_value.watch.assert_called_once_with('RedisLockUnitTest:lock:TestLock')

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    def test_should_not_release_read_lock_when_no_lock_exists(self, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'QWERTY'
        pipeline_verify_secret = MagicMock()
        pipeline_verify_secret.return_value.get.return_value = None
        verify_secret_pipeline_cm = MagicMock()
        verify_secret_pipeline_cm.__enter__ = pipeline_verify_secret
        mock_redis.return_value.pipeline.return_value = verify_secret_pipeline_cm
        lock = RedisReadLock('TestLock', prefix='RedisLockUnitTest')

        # when
        with self.assertRaisesRegex(RuntimeError, 'cannot release un-acquired lock'):
            lock.release()

        # then
        pipeline_verify_secret.return_value.watch.assert_called_once_with('RedisLockUnitTest:lock:TestLock')

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    def test_should_not_release_read_lock_when_not_owner(self, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'QWERTY'
        pipeline_verify_secret = MagicMock()
        pipeline_verify_secret.return_value.get.return_value = \
            b'{"timestamp": 123456, "secret": ["otherLock"], "exclusive": false}'
        verify_secret_pipeline_cm = MagicMock()
        verify_secret_pipeline_cm.__enter__ = pipeline_verify_secret
        mock_redis.return_value.pipeline.return_value = verify_secret_pipeline_cm
        lock = RedisReadLock('TestLock', prefix='RedisLockUnitTest')

        # when
        with self.assertRaisesRegex(RuntimeError, 'cannot release un-acquired lock'):
            lock.release()

        # then
        pipeline_verify_secret.return_value.watch.assert_called_once_with('RedisLockUnitTest:lock:TestLock')

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    def test_should_not_release_read_lock_when_not_exists_on_delete(self, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'QWERTY'
        pipeline_verify_secret = MagicMock()
        pipeline_delete_lock = MagicMock()
        pipeline_verify_secret.return_value.get.return_value = \
            b'{"timestamp": 123456, "secret": ["QWERTY"], "exclusive": false}'
        pipeline_delete_lock.return_value.get.return_value = None
        verify_secret_pipeline_cm = MagicMock()
        delete_lock_pipeline_cm = MagicMock()
        verify_secret_pipeline_cm.__enter__ = pipeline_verify_secret
        delete_lock_pipeline_cm.__enter__ = pipeline_delete_lock
        mock_redis.return_value.pipeline.side_effect = (verify_secret_pipeline_cm, delete_lock_pipeline_cm)
        lock = RedisReadLock('TestLock', prefix='RedisLockUnitTest')

        # when
        with self.assertRaisesRegex(RuntimeError, 'release unlocked lock'):
            lock.release()

        # then
        pipeline_delete_lock.return_value.watch.assert_called_once_with('RedisLockUnitTest:lock:TestLock')
        pipeline_delete_lock.return_value.delete.assert_not_called()
        pipeline_delete_lock.return_value.set.assert_not_called()

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    def test_should_not_release_read_lock_when_non_exclusive_found_on_delete(self, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'QWERTY'
        pipeline_verify_secret = MagicMock()
        pipeline_delete_lock = MagicMock()
        pipeline_verify_secret.return_value.get.return_value = \
            b'{"timestamp": 123456, "secret": ["QWERTY"], "exclusive": false}'
        pipeline_delete_lock.return_value.get.return_value = \
            b'{"timestamp": 123456, "secret": ["QWERTY"], "exclusive": true}'
        verify_secret_pipeline_cm = MagicMock()
        delete_lock_pipeline_cm = MagicMock()
        verify_secret_pipeline_cm.__enter__ = pipeline_verify_secret
        delete_lock_pipeline_cm.__enter__ = pipeline_delete_lock
        mock_redis.return_value.pipeline.side_effect = (verify_secret_pipeline_cm, delete_lock_pipeline_cm)
        lock = RedisReadLock('TestLock', prefix='RedisLockUnitTest')

        # when
        with self.assertRaisesRegex(RuntimeError, 'release unlocked lock'):
            lock.release()

        # then
        pipeline_delete_lock.return_value.watch.assert_called_once_with('RedisLockUnitTest:lock:TestLock')
        pipeline_delete_lock.return_value.delete.assert_not_called()
        pipeline_delete_lock.return_value.set.assert_not_called()

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    def test_should_not_release_read_lock_when_non_secrets_list_on_delete(self, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'QWERTY'
        pipeline_verify_secret = MagicMock()
        pipeline_delete_lock = MagicMock()
        pipeline_verify_secret.return_value.get.return_value = \
            b'{"timestamp": 123456, "secret": ["QWERTY"], "exclusive": false}'
        pipeline_delete_lock.return_value.get.return_value = \
            b'{"timestamp": 123456, "secret": "QWERTY", "exclusive": false}'
        verify_secret_pipeline_cm = MagicMock()
        delete_lock_pipeline_cm = MagicMock()
        verify_secret_pipeline_cm.__enter__ = pipeline_verify_secret
        delete_lock_pipeline_cm.__enter__ = pipeline_delete_lock
        mock_redis.return_value.pipeline.side_effect = (verify_secret_pipeline_cm, delete_lock_pipeline_cm)
        lock = RedisReadLock('TestLock', prefix='RedisLockUnitTest')

        # when
        with self.assertRaisesRegex(RuntimeError, 'release unlocked lock'):
            lock.release()

        # then
        pipeline_delete_lock.return_value.watch.assert_called_once_with('RedisLockUnitTest:lock:TestLock')
        pipeline_delete_lock.return_value.delete.assert_not_called()
        pipeline_delete_lock.return_value.set.assert_not_called()

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    def test_should_not_release_read_lock_when_not_owner_on_delete(self, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'QWERTY'
        pipeline_verify_secret = MagicMock()
        pipeline_delete_lock = MagicMock()
        pipeline_verify_secret.return_value.get.return_value = \
            b'{"timestamp": 123456, "secret": ["QWERTY"], "exclusive": false}'
        pipeline_delete_lock.return_value.get.return_value = \
            b'{"timestamp": 123456, "secret": ["otherSecret"], "exclusive": false}'
        verify_secret_pipeline_cm = MagicMock()
        delete_lock_pipeline_cm = MagicMock()
        verify_secret_pipeline_cm.__enter__ = pipeline_verify_secret
        delete_lock_pipeline_cm.__enter__ = pipeline_delete_lock
        mock_redis.return_value.pipeline.side_effect = (verify_secret_pipeline_cm, delete_lock_pipeline_cm)
        lock = RedisReadLock('TestLock', prefix='RedisLockUnitTest')

        # when
        with self.assertRaisesRegex(RuntimeError, 'release unlocked lock'):
            lock.release()

        # then
        pipeline_delete_lock.return_value.watch.assert_called_once_with('RedisLockUnitTest:lock:TestLock')
        pipeline_delete_lock.return_value.delete.assert_not_called()
        pipeline_delete_lock.return_value.set.assert_not_called()

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    def test_should_retry_when_key_changed_on_verify(self, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'QWERTY'
        pipeline_verify_secret = MagicMock()
        pipeline_delete_lock = MagicMock()
        pipeline_verify_secret.return_value.get.side_effect = \
            (WatchError(), WatchError(), b'{"timestamp": 123456, "secret": ["QWERTY"], "exclusive": false}')
        pipeline_delete_lock.return_value.get.return_value = \
            b'{"timestamp": 123456, "secret": ["QWERTY"], "exclusive": false}'
        verify_secret_pipeline_cm = MagicMock()
        delete_lock_pipeline_cm = MagicMock()
        verify_secret_pipeline_cm.__enter__ = pipeline_verify_secret
        delete_lock_pipeline_cm.__enter__ = pipeline_delete_lock
        mock_redis.return_value.pipeline.side_effect = (verify_secret_pipeline_cm, verify_secret_pipeline_cm,
                                                        verify_secret_pipeline_cm, delete_lock_pipeline_cm)
        lock = RedisReadLock('TestLock', prefix='RedisLockUnitTest')

        # when
        lock.release()

        # then
        self.assertEqual(pipeline_verify_secret.return_value.watch.call_count, 3)
        self.assertEqual(pipeline_delete_lock.return_value.watch.call_count, 1)
        pipeline_delete_lock.return_value.watch.assert_called_once_with('RedisLockUnitTest:lock:TestLock')
        pipeline_delete_lock.return_value.delete.assert_called_once_with('RedisLockUnitTest:lock:TestLock')
        pipeline_delete_lock.return_value.execute.assert_called_once_with()

    @patch('PyYADL.redis_lock.StrictRedis')
    @patch('PyYADL.distributed_lock.uuid4')
    def test_should_retry_when_key_changed_on_delete(self, mock_uuid, mock_redis):
        # given
        mock_uuid.return_value = 'QWERTY'
        pipeline_verify_secret = MagicMock()
        pipeline_delete_lock = MagicMock()
        pipeline_verify_secret.return_value.get.return_value = \
            b'{"timestamp": 123456, "secret": ["QWERTY"], "exclusive": false}'
        pipeline_delete_lock.return_value.get.return_value = \
            b'{"timestamp": 123456, "secret": ["QWERTY"], "exclusive": false}'
        pipeline_delete_lock.return_value.delete.side_effect = (WatchError(), WatchError(), 1)
        verify_secret_pipeline_cm = MagicMock()
        delete_lock_pipeline_cm = MagicMock()
        verify_secret_pipeline_cm.__enter__ = pipeline_verify_secret
        delete_lock_pipeline_cm.__enter__ = pipeline_delete_lock
        mock_redis.return_value.pipeline.side_effect = (verify_secret_pipeline_cm, delete_lock_pipeline_cm,
                                                        delete_lock_pipeline_cm, delete_lock_pipeline_cm)
        lock = RedisReadLock('TestLock', prefix='RedisLockUnitTest')

        # when
        lock.release()

        # then
        self.assertEqual(pipeline_verify_secret.return_value.watch.call_count, 1)
        self.assertEqual(pipeline_delete_lock.return_value.watch.call_count, 3)
