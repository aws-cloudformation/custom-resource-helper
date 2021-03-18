import json
from unittest.mock import patch, Mock, ANY
from crhelper import utils
import unittest
import ssl
import tempfile


class TestLogHelper(unittest.TestCase):
    TEST_URL = "https://test_url/this/is/the/url?query=123#aaa"

    @patch('crhelper.utils.HTTPSConnection', autospec=True)
    def test_send_succeeded_response(self, https_connection_mock):
        utils._send_response(self.TEST_URL, {})
        https_connection_mock.assert_called_once_with("test_url", context=ANY)
        https_connection_mock.return_value.request.assert_called_once_with(
            body='{}',
            headers={"content-type": "", "content-length": "2"},
            method="PUT",
            url="/this/is/the/url?query=123#aaa",
        )

    @patch('crhelper.utils.HTTPSConnection', autospec=True)
    def test_send_failed_response(self, https_connection_mock):
        utils._send_response(self.TEST_URL, Mock())
        https_connection_mock.assert_called_once_with("test_url", context=ANY)
        response = json.loads(https_connection_mock.return_value.request.call_args[1]["body"])
        expected_body = '{"Status": "FAILED", "Data": {}, "Reason": "' + response["Reason"] + '"}'
        https_connection_mock.return_value.request.assert_called_once_with(
            body=expected_body,
            headers={"content-type": "", "content-length": str(len(expected_body))},
            method="PUT",
            url="/this/is/the/url?query=123#aaa",
        )

    @patch('crhelper.utils.ssl.create_default_context', autospec=True)
    @patch('crhelper.utils.HTTPSConnection', autospec=True)
    def test_send_response_no_ssl_verify(self, https_connection_mock, ssl_create_context_mock):
        ctx_mock = Mock()
        ssl_create_context_mock.return_value = ctx_mock
        utils._send_response(self.TEST_URL, {}, ssl_verify=False)
        https_connection_mock.assert_called_once_with("test_url", context=ctx_mock)
        self.assertFalse(ctx_mock.check_hostname)
        self.assertEqual(ctx_mock.verify_mode, ssl.CERT_NONE)

    @patch('crhelper.utils.ssl.create_default_context', autospec=True)
    @patch('crhelper.utils.HTTPSConnection', autospec=True)
    def test_send_response_custom_ca(self, https_connection_mock, ssl_create_context_mock):
        ctx_mock = Mock()
        ssl_create_context_mock.return_value = ctx_mock
        with tempfile.NamedTemporaryFile() as tmp:
            utils._send_response(self.TEST_URL, {}, ssl_verify=tmp.name)
        https_connection_mock.assert_called_once_with("test_url", context=ctx_mock)
        ctx_mock.load_verify_locations.assert_called_once_with(cafile=tmp.name)

    @patch('crhelper.utils.ssl.create_default_context', autospec=True)
    @patch('crhelper.utils.HTTPSConnection', autospec=True)
    def test_send_response_non_existant_custom_ca(self, https_connection_mock, ssl_create_context_mock):
        ctx_mock = Mock()
        ssl_create_context_mock.return_value = ctx_mock
        utils._send_response(self.TEST_URL, {}, ssl_verify='/invalid/path/to/ca')
        https_connection_mock.assert_called_once_with("test_url", context=ANY)
        ctx_mock.load_verify_locations.assert_not_called()
