from __future__ import absolute_import, print_function
from time import sleep
import six
from .exceptions import MaxRequestAttemptsReached


def get_backoff_seconds_exp(wait_const, min_wait_seconds, max_attempts):
    """Calculate a counter and wait time in seconds for each retried request.

    :param wait_const: The constant to apply to the exponential calculation
    :param min_wait_seconds: Minimum wait time to yield
    :max_attemps: Maximum number of wait times to yield
    :returns: A generator that yields a counter and a wait time in seconds
    :rtype: generator
    """

    for attempt in range(max_attempts):
        yield (attempt, max(wait_const**attempt, min_wait_seconds))


class Paginator(object):
    """Class will retry rate limited requests + chain paginated requests."""

    DEFAULT_MAX_ATTEMPTS = 4
    DEFAULT_MIN_WAIT_SECONDS = 1
    DEFAULT_WAIT_CONST = 5
    DEFAULT_BACKOFF_FUNC = get_backoff_seconds_exp
    DEFAULT_ALL_PAGES = -1
    DEFAULT_META_OFFSET_NAME = "next_offset"
    DEFAULT_STATUSES_TO_RETRY_ON = (429,)

    def __init__(
        self,
        duo_client,
        max_attempts=DEFAULT_MAX_ATTEMPTS,
        wait_const=DEFAULT_WAIT_CONST,
        min_wait_seconds=DEFAULT_MIN_WAIT_SECONDS,
        backoff_func=DEFAULT_BACKOFF_FUNC,
        statues_to_retry_on=DEFAULT_STATUSES_TO_RETRY_ON
    ):
        """Initializes the Paginator class with some boiler-plate configs.

        :param duo_client: Duo Admin/Auth client
        :param max_attempts: (optional) max attempts for each HTTP request
        :param wait_const: (optional) const applied to the exp backoff calculation
        :param min_wait_seconds: (optional) minimum wait for the exp backoff calculation
        :param backoff_func: (optional) function that yields exp backoff times
        :param statuses_to_retry_on: (optional) tuple of HTTP status codes to retry on
        :rtype: None
        """

        self._duo_client = duo_client
        self._max_attempts = max_attempts
        self._wait_const = wait_const
        self._min_wait_seconds = min_wait_seconds
        self._backoff_func = backoff_func
        self._statuses_to_retry_on = statues_to_retry_on

    def _next_offset_from_metadata(self, metadata):
        """Returns the next offset from the metadata that comes from some API
        endpoints. Method will return None if the offset doesn't exist in the
        API response.

        :param metadata: The metadata response from parsed JSON api response
        :returns: The next_offset object from the JSON api response
        """

        if isinstance(metadata, dict):
            return metadata.get("next_offset", None)

    def _next_offset_from_response(self, response):
        """Returns the next offset from the response that comes from some API
        endpoints. Method will return None if the offset doesn't exist in the
        API response.

        :param response: The response form the parsed JSON api response
        :returns: the next_offset object from the JSON api response
        """

        if isinstance(response, dict):
            return response.get("metadata", {}).get("next_offset", None)

    def _get_next_offset(self, response, metadata):
        """Extract the next offset from the response metadata. Returns None if
        there is the offset is missing. Some api endpoints have the paging meta
        data in the response and sometimes it's one level deeper. This method
        looks in both places.

        :param response: dict parsed from the json/HTTP response
        :param metadata: dict parsed from the json/HTTP response
        :returns: The next offset from the json metadata or response.
        """

        md = None

        if "next_offset" in metadata:
            md = self._next_offset_from_metadata(metadata)
        else:
            md = self._next_offset_from_response(response)

        return six.text_type(md) if isinstance(md, int) else md

    def _request_with_retry(self, method, path, params):
        """Make an HTTP request via the specified Duo client, and retry if the
        API responds with a 429 status. Method will raise MaxRequestAttemptsReached
        if the client gets too many 429 status codes.

        :param method: The method for the HTTP call ("GET", "POST", etc...)
        :param path: The path to make the request on ("/sample/route", "/data"...)
        :param params: Parameters (dict) to use in the request
        :return: The json data from the API
        :rtype: dict
        """

        # Generator which yields sleep durations.
        backoff_gen = self._backoff_func(
            self._wait_const,
            self._min_wait_seconds,
            self._max_attempts
        )

        for _, wait_seconds in backoff_gen:
            try:
                http_response, http_resp_data = self._duo_client.api_call(
                    method,
                    path,
                    params
                )
                return self._duo_client.parse_json_response_and_metadata(
                    http_response, http_resp_data
                )
            except RuntimeError as e:
                if getattr(e, 'status', -1) in self._statuses_to_retry_on:
                    sleep(wait_seconds)
                else:
                    raise e

        raise MaxRequestAttemptsReached(
            "Reached the max number of request attempts"
        )

    def request(
        self,
        method,
        path,
        params,
        meta_offset_name=DEFAULT_META_OFFSET_NAME,
        max_pages=DEFAULT_ALL_PAGES
    ):
        """Make a request on the specified API endpoint and return a generator.
        The generator will make requests on the API and yield the pages.

        :param method: The method for the HTTP call ("GET", "POST", etc...)
        :param path: The path to make the request on ("/saf0ba235-0b33-23c8-bc23-a31aa0231de8ample/route", "/data"...)
        :param params: Parameters (dict) to use in the request
        :param meta_offset_name: The name of the subsequent param used to request the next page
        :param max_pages: The number of pages to fetch (-1 means all pages)
        :returns: A generator to yield pages from the api responses
        :rtype: generator
        """

        while max_pages:
            max_pages -= 1
            response, metadata = self._request_with_retry(method, path, params)
            next_offset = self._get_next_offset(response, metadata)

            yield response

            if next_offset:
                params[meta_offset_name] = next_offset
            else:
                break

    def request_all_pages(
        self,
        method,
        path,
        params,
        meta_offset_name=DEFAULT_META_OFFSET_NAME,
        max_pages=DEFAULT_ALL_PAGES
    ):
        """Attempt to exhaust all pages from the API response and return a the
        results in a list.

        :param method: The method for the HTTP call ("GET", "POST", etc...)
        :param path: The path to make the request on ("/sample/route", "/data"...)
        :param params: Parameters (dict) to use in the request
        :param meta_offset_name: The name of the subsequent param used to request the next page
        :param max_pages: The number of pages to fetch (-1 means all pages)
        :returns: A list of paginated responses.
        :rtype: list
        """

        return [
            d for d in self.request(
                method, path, params, max_pages=max_pages, meta_offset_name=meta_offset_name
            )
        ]
