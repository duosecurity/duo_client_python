import json

from .base import TestAdmin


class TestIDV(TestAdmin):
    def test_start_idv(self):
        """ Test start identity verification process
        """
        response = self.client.start_idv('DU012345678901234567')
        self.assertEqual(response['uri'], '/admin/v2/identity_verification/DU012345678901234567/start')

    def test_get_idv_status(self):
        """ Test get identity verification process status
        """
        response = self.client.get_idv_status('DU012345678901234567')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v2/identity_verification/DU012345678901234567/status')

    def test_cancel_idv(self):
        """ Test cancel identity verification process
        """
        response = self.client.cancel_idv('DU012345678901234567', 'inq_PY3skN8RKxPKBPdpbpdtZfHy6rwJ')
        body = json.loads(response["body"])
        self.assertEqual(response['uri'], '/admin/v2/identity_verification/DU012345678901234567/cancel')
        self.assertEqual(body['inquiry_id'], 'inq_PY3skN8RKxPKBPdpbpdtZfHy6rwJ')
