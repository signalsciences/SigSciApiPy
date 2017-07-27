from __future__ import print_function
import unittest
import mock

from SigSciApiPy.SigSci import SigSciAPI


def mocked_requests_get(*args, **kwargs):
    class MockResponse(object):
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            # TODO: add an actual "next" URI to make sure looping works etc.
            self.text = '{"next": {"uri": ""}, "data": {"id": "testid", "serverHostname": "testhost"}}'

        def json(self):
            return self.json_data

    return MockResponse({"key1": "value1"}, 200)


def mocked_requests_post(*args, **kwargs):
    class MockResponse(object):
        def __init__(self, json_data, status_code):
            self.status_code = status_code
            self.json_data = json_data
            self.cookies = {}

        def json(self):
            return self.json_data

    return MockResponse({"token": "testtoken"}, 200)


class TestSigSciAPI(unittest.TestCase):

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    @mock.patch("requests.post", side_effect=mocked_requests_post)
    def test_fetch(self, mock_get, mock_post):
        # Assert requests.get calls
        sigsci = SigSciAPI()
        sigsci.email = "testemail"
        sigsci.password = "testpass"
        sigsci.corp = "testcorp"
        sigsci.site = "testsite"
        sigsci.authenticate()
        sigsci.get_feed_requests()
        sigsci.get_list_events()


if __name__ == "__main__":
    unittest.main()
