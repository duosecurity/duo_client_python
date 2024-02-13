import unittest
from unittest.mock import patch
from .. import util
import duo_client.admin


class TestAccountAdmin(unittest.TestCase):

    def setUp(self):
        child_host = 'example2.com'
        kwargs = {'ikey': 'test_ikey', 'skey': 'test_skey', 'host': 'example.com'}

        patcher = patch("duo_client.admin.AccountAdmin.get_child_api_host")
        self.mock_child_host = patcher.start()
        self.mock_child_host.return_value = child_host
        self.addCleanup(patcher.stop)

        self.client = duo_client.admin.AccountAdmin(
            'DA012345678901234567', **kwargs)
        
        # monkeypatch client's _connect()
        self.client._connect = lambda: util.MockHTTPConnection()


if __name__ == '__main__':
    unittest.main()
