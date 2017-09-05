from PyYADL.backends.redis import RedisBackendAdapter


class DistributedLock:
    def __init__(self, backend=None):
        '''
        :type backend: PyYADL.backends.adapter_interface.Backend
        '''
        if backend is not None:
            self.backend = backend
        else:
            self.backend = RedisBackendAdapter()
