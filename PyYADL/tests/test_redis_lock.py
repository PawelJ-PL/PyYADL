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
