import unittest
from .. import util
import duo_client.authorization


class TestAuthorization(unittest.TestCase):

    def setUp(self):
        self.client = duo_client.authorization.Authorization(
            'test_ikey', 'test_skey', 'example.com')
        self.client._connect = lambda: util.MockHTTPConnection()


if __name__ == '__main__':
    unittest.main()
