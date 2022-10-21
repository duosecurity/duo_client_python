import unittest
from .. import util
import duo_client.admin
import os


class TestAdmin(unittest.TestCase):

    TEST_RESOURCES_DIR = dir_path = os.path.join(
        os.path.abspath(os.curdir), 'tests', 'resources')

    def setUp(self):
        self.client = duo_client.admin.Admin(
            'test_ikey', 'test_akey', 'example.com')
        self.client.account_id = 'DA012345678901234567'
        # monkeypatch client's _connect()
        self.client._connect = lambda: util.MockHTTPConnection()

        # if you are wanting to simulate getting lists of objects
        # rather than a single object
        self.client_list = duo_client.admin.Admin(
            'test_ikey', 'test_akey', 'example.com')
        self.client_list.account_id = 'DA012345678901234567'
        self.client_list._connect = \
            lambda: util.MockHTTPConnection(data_response_should_be_list=True)

        # if you are wanting to get a response from a call to get
        # authentication logs
        self.client_authlog = duo_client.admin.Admin(
            'test_ikey', 'test_akey', 'example.com')
        self.client_authlog.account_id = 'DA012345678901234567'
        self.client_authlog._connect = \
            lambda: util.MockHTTPConnection(data_response_from_get_authlog=True)

        # client to simulate basic structure of a call to fetch Duo Trust
        # Monitor events.
        self.client_dtm = duo_client.admin.Admin(
            'test_ikey',
            'test_akey',
            'example.com',
        )
        self.client_dtm.account_id = 'DA012345678901234567'
        self.client_dtm._connect = \
            lambda: util.MockHTTPConnection(data_response_from_get_dtm_events=True)

        self.client_activity = duo_client.admin.Admin(
            'test_ikey', 'test_akey', 'example.com')
        self.client_activity.account_id = 'DA012345678901234567'
        self.client_activity._connect = \
            lambda: util.MockHTTPConnection(data_response_from_get_items=True)


if __name__ == '__main__':
    unittest.main()
