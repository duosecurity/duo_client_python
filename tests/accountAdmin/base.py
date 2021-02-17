import unittest
from .. import util
import duo_client.admin


class TestAccountAdmin(unittest.TestCase):

    def setUp(self):
        kwargs = {'ikey': 'test_ikey', 'skey': 'test_skey', 'host': 'example.com'}
        self.client = duo_client.admin.AccountAdmin(
            'DA012345678901234567', **kwargs)
        # monkeypatch client's _connect()
        self.client._connect = lambda: util.MockHTTPConnection()


if __name__ == '__main__':
    unittest.main()
