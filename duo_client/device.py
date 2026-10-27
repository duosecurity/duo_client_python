"""
Duo Security Device API reference client implementation.

"""
from __future__ import absolute_import

import six.moves.urllib

from . import client
import six
import warnings
import json

MAX_DEVICE_IDS = 1000
DEVICE_CACHE_STATUS = [
    "active",
    "pending"
]


class Device(client.Client):
    account_id = None

    def api_call(self, method, path, params):
        if self.account_id is not None:
            params['account_id'] = self.account_id
        return super(Device, self).api_call(method, path, params)

    def _validate_device_ids(self, device_ids):
        # For some reason this is a list of dicts
        if not isinstance(device_ids, list):
            raise ValueError
        for device_id_dict in device_ids:
            if not isinstance(device_id_dict, dict):
                raise ValueError
            if 'device_id' not in device_id_dict:
                raise ValueError
        return True

    def create_device_cache(self):
        existing_caches = self.get_device_caches()
        for cache in existing_caches:
            cache_key = cache['cache_key']
            if cache['status'] == "pending":
                raise ValueError(
                    f"Cannot create a cache when a cache is pending ({cache_key})")
        return self.json_api_call(
            'POST',
            f'/device/v1/management_systems/{self.mkey}/device_cache',
            {}
        )

    def delete_device_cache(self, cache_key):
        device_cache = self.get_device_cache_by_key(cache_key)
        if device_cache['status'] != "pending":
            raise ValueError(
                f"Only Pending device caches can be deleted ({cache_key})")
        return self.json_api_call(
            'DELETE',
            f'/device/v1/management_systems/{self.mkey}/device_cache/{cache_key}',
            {}
        )

    def activate_device_cache(self, cache_key):
        return self.json_api_call(
            'POST',
            f'/device/v1/management_systems/{self.mkey}/device_cache/{cache_key}/activate',
            {}
        )

    def add_device_to_cache(self, cache_key, device_ids):
        # We only return the last result
        result = None
        for device_start in range(0, len(device_ids), MAX_DEVICE_IDS):
            device_end = device_start + MAX_DEVICE_IDS
            if device_end > len(device_ids):
                device_end = len(device_ids)
            device_ids_chunk = device_ids[device_start:device_end]
            self._validate_device_ids(device_ids_chunk)
            params = {
                'devices': json.dumps(device_ids_chunk),
            }

            result = self.json_api_call(
                'POST',
                f'/device/v1/management_systems/{self.mkey}/device_cache/{cache_key}/devices',
                params
            )
        return result

    def get_device_caches(self, status=None):
        params = {}
        if status:
            if status not in DEVICE_CACHE_STATUS:
                raise ValueError
            params = {"status": status}
        params = six.moves.urllib.parse.urlencode(params, doseq=True)
        if params:
            url = f'/device/v1/management_systems/{self.mkey}/device_cache?{params}'
        else:
            url = f'/device/v1/management_systems/{self.mkey}/device_cache'
        return self.json_api_call(
            'GET',
            url,
            {}
        )

    def get_device_cache_by_key(self, cache_key):
        return self.json_api_call(
            'GET',
            f'/device/v1/management_systems/{self.mkey}/device_cache/{cache_key}',
            {}
        )

    def get_device_cache_by_key(self, cache_key):
        return self.json_api_call(
            'GET',
            f'/device/v1/management_systems/{self.mkey}/device_cache/{cache_key}',
            {}
        )

    def activate_cache_with_devices(self, device_ids, cache_key=None):
        # Remove any existing pending caches, since there can only be one
        if not cache_key:
            existing_caches = self.get_device_caches()
            for cache in existing_caches:
                if cache['status'] == 'pending':
                    cache_key = cache['cache_key']
                    self.delete_device_cache(cache_key)
            device_cache = self.create_device_cache()
        else:
            device_cache = self.get_device_cache_by_key(cache_key)
            if device_cache['status'] != 'pending':
                raise ValueError("Specified Cache is not in pending state")
        cache_key = device_cache['cache_key']
        self.add_device_to_cache(cache_key, device_ids)
        self.activate_device_cache(cache_key)
        return self.get_device_cache_by_key(cache_key)
