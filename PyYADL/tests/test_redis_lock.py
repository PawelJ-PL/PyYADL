from json import loads
from unittest import TestCase
from unittest.mock import patch, ANY
from PyYADL.redis_lock import RedisLock


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
        self.assertDictEqual(loads(value), {'timestamp': 1504732028, 'secret': 'SecretData'})
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
        self.assertDictEqual(loads(value), {'timestamp': 1504732028, 'secret': 'SecretData'})
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
        self.assertDictEqual(loads(value), {'timestamp': 1504732028, 'secret': 'SecretData'})
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
        self.assertDictEqual(loads(value), {'timestamp': 1504732028, 'secret': 'SecretData'})
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
