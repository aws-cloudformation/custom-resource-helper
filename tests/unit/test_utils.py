from unittest.mock import Mock
from crhelper import utils
import unittest
import logging


class TestLogHelper(unittest.TestCase):

    def test_send_response(self):
        p = Mock()
        utils._send_response("test_url", {}, put=p)
        p.assert_called_once()
        p = Mock()
        utils._send_response("test_url", p, put=p)
        p.assert_called_with(
            'test_url',
            data='{"Status": "FAILED", "Data": {}, "Reason": "Failed to convert response to json: Object of type \'Mock\' is not JSON serializable"}',
            headers={'content-type': '', 'content-length': '128'}
        )
