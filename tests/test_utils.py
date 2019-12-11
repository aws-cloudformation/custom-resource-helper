import json
from unittest.mock import patch, Mock
from crhelper import utils
import unittest


class TestLogHelper(unittest.TestCase):
    TEST_URL = "https://test_url/this/is/the/url?query=123#aaa"

    @patch('crhelper.utils.HTTPSConnection', autospec=True)
    def test_send_succeeded_response(self, https_connection_mock):
        utils._send_response(self.TEST_URL, {})
        https_connection_mock.assert_called_once_with("test_url")
        https_connection_mock.return_value.request.assert_called_once_with(
            body='{}',
            headers={"content-type": "", "content-length": "2"},
            method="PUT",
            url="/this/is/the/url?query=123#aaa",
        )

    @patch('crhelper.utils.HTTPSConnection', autospec=True)
    def test_send_failed_response(self, https_connection_mock):
        utils._send_response(self.TEST_URL, Mock())
        https_connection_mock.assert_called_once_with("test_url")
        response = json.loads(https_connection_mock.return_value.request.call_args[1]["body"])
        expected_body = '{"Status": "FAILED", "Data": {}, "Reason": "' + response["Reason"] + '"}'
        https_connection_mock.return_value.request.assert_called_once_with(
            body=expected_body,
            headers={"content-type": "", "content-length": str(len(expected_body))},
            method="PUT",
            url="/this/is/the/url?query=123#aaa",
        )
