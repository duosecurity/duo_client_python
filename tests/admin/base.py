import unittest
from .. import util
import duo_client.admin


class TestAdmin(unittest.TestCase):

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


if __name__ == '__main__':
    unittest.main()
