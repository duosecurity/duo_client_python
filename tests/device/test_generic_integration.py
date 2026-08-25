import import duo_client.device
from .. import util
import uuid
import pytest


class TestDeviceGeneric(unittest.TestCase):
    def setUp(self):
        self.device_api = duo_client.device.Device(
            'test_ikey', 'test_akey', 'example.com', mkey='test_mkey')
        )
        # monkeypatch client's _connect()
        self.client._connect = lambda: util.MockHTTPConnection()

    def test_create_pending():
        existing_caches = self.device_api.get_device_caches()
        for cache in existing_caches:
            if cache['status'] == 'pending':
                cache_key = cache['cache_key']
                self.device_api.delete_device_cache(cache_key)
        # Test creating and activating two caches
        device_cache = self.device_api.create_device_cache()
        assert isinstance(device_cache, dict)
        assert 'cache_key' in device_cache
        cache_key = device_cache['cache_key']
        cache_key2 = None
        with pytest.raises(ValueError) as err:
            device_cache2 = self.device_api.create_device_cache()
            cache_key2 = device_cache2['cache_key']
            self.device_api.delete_device_cache(cache_key)
            self.device_api.delete_device_cache(cache_key2)
        self.device_api.delete_device_cache(cache_key)
        assert err

    def test_create_and_delete_pending():
        existing_caches = self.device_api.get_device_caches()
        for cache in existing_caches:
            if cache['status'] == 'pending':
                cache_key = cache['cache_key']
                self.device_api.delete_device_cache(cache_key)
        # Test creating and activating two caches
        device_cache = self.device_api.create_device_cache()
        cache_key = device_cache['cache_key']
        resp = self.device_api.delete_device_cache(cache_key)
        assert isinstance(resp, dict)
        assert resp == {}

    def test_create_and_fetch():
        existing_caches = self.device_api.get_device_caches()
        for cache in existing_caches:
            if cache['status'] == 'pending':
                cache_key = cache['cache_key']
                self.device_api.delete_device_cache(cache_key)
        # Test creating and activating two caches
        device_cache = self.device_api.create_device_cache()
        cache_key = device_cache['cache_key']
        caches = self.device_api.get_device_caches()
        assert [cache['cache_key'] for cache in caches]
        self.device_api.delete_device_cache(cache_key)

    def test_add_devices_to_cache():
        existing_caches = self.device_api.get_device_caches()
        for cache in existing_caches:
            if cache['status'] == 'pending':
                cache_key = cache['cache_key']
                self.device_api.delete_device_cache(cache_key)
        # Test creating and activating two caches
        device_cache = self.device_api.create_device_cache()
        device_ids = [{"device_id": str(uuid.uuid4())}]
        cache_key = device_cache['cache_key']
        # Add a single device
        self.device_api.add_device_to_cache(cache_key, device_ids)
        cache = self.device_api.get_device_cache_by_key(cache_key)
        assert cache['device_count'] == 1
        # Readd the same device once
        self.device_api.add_device_to_cache(cache_key, device_ids)
        cache = self.device_api.get_device_cache_by_key(cache_key)
        assert cache['device_count'] == 1
        # Readd the same device 5 times
        for _ in range(5):
            self.device_api.add_device_to_cache(cache_key, device_ids)
            cache = self.device_api.get_device_cache_by_key(cache_key)
            assert cache['device_count'] == 1
        # Add two additional devices to the one existing device
        device_ids = [{"device_id": str(uuid.uuid4())}, {"device_id": str(uuid.uuid4())}]
        self.device_api.add_device_to_cache(cache_key, device_ids)
        cache = self.device_api.get_device_cache_by_key(cache_key)
        assert cache['device_count'] == 3
        # Add 999 devices (below max per request)
        device_ids = []
        for _ in range(999):
            device_ids.append({"device_id": str(uuid.uuid4())})
        self.device_api.add_device_to_cache(cache_key, device_ids)
        cache = self.device_api.get_device_cache_by_key(cache_key)
        assert cache['device_count'] == 1002
        # Add 1010 more devices (over max per request)
        device_ids = []
        for _ in range(1010):
            device_ids.append({"device_id": str(uuid.uuid4())})
        self.device_api.add_device_to_cache(cache_key, device_ids)
        cache = self.device_api.get_device_cache_by_key(cache_key)
        assert cache['device_count'] == 2012
        self.device_api.delete_device_cache(cache_key)


    def test_add_invalid_device_to_cache():
        existing_caches = self.device_api.get_device_caches()
        for cache in existing_caches:
            if cache['status'] == 'pending':
                cache_key = cache['cache_key']
                self.device_api.delete_device_cache(cache_key)
        # Test creating and activating two caches
        device_cache = self.device_api.create_device_cache()
        device_ids = [{"device_id": "potato"}]
        cache_key = device_cache['cache_key']
        # Add a single device
        with pytest.raises(RuntimeError) as err:
            self.device_api.add_device_to_cache(cache_key, device_ids)
        assert err
        cache = self.device_api.get_device_cache_by_key(cache_key)
        assert cache['device_count'] == 0
        self.device_api.delete_device_cache(cache_key)

    def test_activate_cache():
        existing_caches = self.device_api.get_device_caches()
        for cache in existing_caches:
            if cache['status'] == 'pending':
                cache_key = cache['cache_key']
                self.device_api.delete_device_cache(cache_key)
        # Check if we already have an activated cache
        # for unknown reasons there is no way to deactivate a cache
        # it must be replaced
        found_active_cache = False
        for cache in existing_caches:
            if cache['status'] == 'active':
                found_active_cache = False#cache['cache_key']
        if found_active_cache:
            device_cache = self.device_api.create_device_cache()
            cache_key = device_cache['cache_key']
            res = self.device_api.activate_device_cache(cache_key)
            assert res == {}
            existing_caches = self.device_api.get_device_caches()
            assert found_active_cache not in [cache['cache_key'] for cache in existing_caches]
            assert cache_key in [cache['cache_key'] for cache in existing_caches]
            current_cache = self.device_api.get_device_cache_by_key(cache_key)
            assert current_cache['status'] == 'active'
        if not found_active_cache:
            device_cache1 = self.device_api.create_device_cache()
            cache_key = device_cache1['cache_key']
            res = self.device_api.activate_device_cache(cache_key)
            assert res == {}
            current_cache = self.device_api.get_device_cache_by_key(cache_key)
            assert current_cache['status'] == 'active'
            assert current_cache['cache_key'] == cache_key
            device_cache2 = self.device_api.create_device_cache()
            cache_key = device_cache2['cache_key']
            res = self.device_api.activate_device_cache(cache_key)
            assert res == {}
            # Duo silently deletes the active cache on promotion of new cache
            existing_caches = self.device_api.get_device_caches()
            assert len(existing_caches) == 1
            assert existing_caches[0]['status'] == 'active'
            assert existing_caches[0]['cache_key'] == cache_key

    def test_create_and_fetch_specific():
        existing_caches = self.device_api.get_device_caches()
        for cache in existing_caches:
            if cache['status'] == 'pending':
                cache_key = cache['cache_key']
                self.device_api.delete_device_cache(cache_key)
        # Test creating and activating two caches
        device_cache = self.device_api.create_device_cache()
        cache_key = device_cache['cache_key']
        current_cache = self.device_api.get_device_cache_by_key(cache_key)
        assert current_cache['cache_key'] == cache_key
        assert current_cache['status'] == 'pending'
        self.device_api.delete_device_cache(cache_key)

    def test_activate_cache_with_devices_no_predefined():
        # Create 300 random devices for our cache
        device_ids = []
        num_devices = 3000
        for _ in range(num_devices):
            device_ids.append({"device_id": str(uuid.uuid4())})
        result_cache = self.device_api.activate_cache_with_devices(device_ids)
        assert result_cache['device_count'] == num_devices
        assert result_cache['status'] == 'active'

    def test_activate_cache_with_devices_predefined():
        existing_caches = self.device_api.get_device_caches()
        for cache in existing_caches:
            if cache['status'] == 'pending':
                cache_key = cache['cache_key']
                self.device_api.delete_device_cache(cache_key)
        device_cache = self.device_api.create_device_cache()
        cache_key = device_cache['cache_key']
        # Create 300 random devices for our cache
        device_ids = []
        num_devices = 3000
        for _ in range(num_devices):
            device_ids.append({"device_id": str(uuid.uuid4())})
        result_cache = self.device_api.activate_cache_with_devices(device_ids, cache_key=cache_key)
        assert result_cache['device_count'] == num_devices
        assert result_cache['status'] == 'active'

        # Test adding devices to an already activated cache
        with pytest.raises(ValueError) as err:
            self.device_api.activate_cache_with_devices(device_ids, cache_key=cache_key)
        assert err
