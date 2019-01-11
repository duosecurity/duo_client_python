from __future__ import absolute_import, print_function
import unittest
import json
from copy import deepcopy
from mock import patch
from duo_client.admin import Admin
from duo_client.paginator import Paginator
from duo_client.exceptions import MaxRequestAttemptsReached


DEFAULT_IKEY = "SAMPLEIKEY12345"
DEFAULT_SKEY = "SAMPLESKEY1234567890**"
DEFAULT_HOST = "test123-api.duosecurity.com"
DEFAULT_CERTS = None


def get_paginated_authlog_generator(num_records, stat=True):
    data = {
        "response": {
            "authlogs": [
                {
                    "access_device": "device",
                    "application": "app",
                    "auth_device": "auth_device",
                    "factor": "factor"
                },
            ],
        }
    }
    for i in range(num_records):
        page = deepcopy(data)
        page["stat"] = "OK" if stat else "FAIL"

        if i < (num_records - 1):
            page["response"]["metadata"] = {
                "next_offset": ["12345", "340a23e3-23f3-23c1-87dc-1491a23dfdbb"],
                "total_objects": num_records
            }
        yield json.dumps(page).encode("utf-8")

def get_paginated_endpoint_generator(num_records, stat=True):
    data = {
        "response": [
            {
                "browsers": [],
                "device_identifier": "3FA47335-1976-3BED-8286-D3F1ABCDEA13",
                "device_identifier_type": "hardware_uuid",
                "trusted_endpoint": True,
                "username": "ejennings"
            }
        ],
    }
    for i in range(num_records):
        page = deepcopy(data)
        page["stat"] = "OK" if stat else "FAIL"

        if i < (num_records - 1):
            page["metadata"] = {
                "next_offset": i,
                "total_objects": num_records
            }
        yield json.dumps(page).encode("utf-8")


class MockHTTPResponse(object):

    def __init__(self, status, reason):
        self.status = status
        self.reason = reason


def get_duo_client(
    ikey=DEFAULT_IKEY,
    skey=DEFAULT_SKEY,
    host=DEFAULT_HOST,
    certs=DEFAULT_CERTS
):
    return Admin(ikey=ikey, skey=skey, host=host, ca_certs=certs)


class TestPaginator(unittest.TestCase):

    def setUp(self):
        self.client = get_duo_client()
        self.paginator = Paginator(self.client)

    def test_offset_from_md_exists(self):
        self.paginator = Paginator(self.client)

        metadata = {
            "next_offset": 7
        }

        metadata_with_complex_offset = {
            "next_offset": [
                "15329518950000123456789",
                "af0ba235-0b33-23c8-bc23-a31aa0231de8"
            ]
        }

        self.assertEqual(
            self.paginator._next_offset_from_metadata(metadata),
            7
        )

        self.assertEqual(self.paginator._next_offset_from_metadata(
                metadata_with_complex_offset
            ),
            ["15329518950000123456789", "af0ba235-0b33-23c8-bc23-a31aa0231de8"]
        )

    def test_offset_from_md_doesnt_exist(self):
        self.paginator = Paginator(self.client)

        metadata = {"test": [1,2,3,4]}
        metadata_wrong_type = ["testing", 1, 2, 3]

        self.assertIsNone(self.paginator._next_offset_from_metadata(
            metadata
        ))

        self.assertIsNone(self.paginator._next_offset_from_metadata(
            metadata_wrong_type
        ))

    def test_offset_from_request_exists(self):
        self.paginator = Paginator(self.client)

        response = {
            "authlogs": [1, 2, 3, 4],
            "metadata": {
                "next_offset": [
                    "15329518950000123456789",
                    "af0ba235-0b33-23c8-bc23-a31aa0231de8"
                ],
                "total_objects": 4
            }
        }
        response_wrong_type = [1, 2, 3, 4]
        response_missing_offset = {"foo": True, "bar": False}

        self.assertEqual(
            self.paginator._next_offset_from_response(response),
            ["15329518950000123456789", "af0ba235-0b33-23c8-bc23-a31aa0231de8"]
        )

        self.assertIsNone(self.paginator._next_offset_from_response(
            response_wrong_type
        ))

        self.assertIsNone(self.paginator._next_offset_from_response(
            response_missing_offset
        ))

    def test_next_offset_metadata_precedence(self):
        self.paginator = Paginator(self.client)

        response = {
            "authlogs": [1, 2, 3, 4],
            "metadata": {
                "next_offset": [
                    "15329518950000123456789",
                    "af0ba235-0b33-23c8-bc23-a31aa0231de8"
                ],
                "total_objects": 4
            }
        }

        metadata = {
            "next_offset": [
                "95329518950000123499999",
                "aaaba235-0b33-23c8-bc23-a31aa02zzzzz"
            ]
        }

        self.assertEqual(
            self.paginator._get_next_offset(response, metadata),
            ["95329518950000123499999", "aaaba235-0b33-23c8-bc23-a31aa02zzzzz"]
        )

    def test_next_offset_cast_to_text_type(self):
        self.paginator = Paginator(self.client)

        metadata = {
            "next_offset": 100
        }

        response = {}

        self.assertEqual(
            self.paginator._get_next_offset(response, metadata),
            "100"
        )

    @patch("duo_client.paginator.sleep")
    @patch.object(Admin, 'api_call')
    def test_throws_max_retries_exception(self, mocked_api_call, mocked_sleep):
        self.paginator = Paginator(self.client, max_attempts=3)

        mock_http_response = MockHTTPResponse(429, "429 Rate Limit!")
        mock_response_content = b"{}"

        mocked_api_call.return_value = (mock_http_response, mock_response_content,)
        mocked_sleep.return_value(None)

        with self.assertRaises(MaxRequestAttemptsReached):
            self.paginator.request_all_pages(
                "GET",
                "/adminapi/pretendapi/endpoint",
                {}
            )

    @patch("duo_client.paginator.sleep")
    @patch.object(Admin, 'api_call')
    def test_num_of_pages_returned_offset_in_metadata(
        self,
        mocked_api_call,
        mocked_sleep
    ):
        self.paginator = Paginator(self.client)

        endpoint_generator = get_paginated_endpoint_generator(8, stat=True)
        mock_http_response = MockHTTPResponse(200, "200 Ok")

        def get_next_page(method, path, params):
            return (mock_http_response, next(endpoint_generator))

        mocked_sleep.return_value = None
        mocked_api_call.side_effect = get_next_page

        pages = self.paginator.request_all_pages(
            "GET",
            "/adminapi/pretendapi/endpoint",
            {}
        )

        self.assertEqual(len(pages), 8)

    @patch("duo_client.paginator.sleep")
    @patch.object(Admin, 'api_call')
    def test_num_of_pages_returned_offset_in_response(
        self,
        mocked_api_call,
        mocked_sleep
    ):
        self.paginator = Paginator(self.client)

        authlog_generator = get_paginated_authlog_generator(10, stat=True)
        mock_http_response = MockHTTPResponse(200, "200 Ok")

        def get_next_page(method, path, params):
            return (mock_http_response, next(authlog_generator),)

        mocked_sleep.return_value = None
        mocked_api_call.side_effect = get_next_page

        pages = self.paginator.request_all_pages(
            "GET",
            "/adminapi/pretendapi/endpoint",
            {}
        )

        self.assertEqual(len(pages), 10)


    @patch("duo_client.paginator.sleep")
    @patch.object(Admin, 'api_call')
    def test_num_of_pages_returned_with_max_pages_set(self, mocked_api_call, mocked_sleep):
        self.paginator = Paginator(self.client)

        authlog_generator = get_paginated_authlog_generator(100, stat=True)
        mock_http_response = MockHTTPResponse(200, "200 Ok")

        def get_next_page(method, path, params):
            return (mock_http_response, next(authlog_generator))

        mocked_sleep.return_value = None
        mocked_api_call.side_effect = get_next_page

        pages = self.paginator.request_all_pages(
            "GET",
            "/adminapi/pretendapi/endpoint",
            {},
            max_pages=2
        )

        self.assertEqual(len(pages), 2)


if __name__ == "__main__":
    unittest.main()
