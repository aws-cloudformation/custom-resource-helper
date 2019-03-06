from unittest.mock import Mock
from crhelper import utils
import unittest
import json


class TestLogHelper(unittest.TestCase):

    def test_send_response(self):
        p = Mock()
        utils._send_response("test_url", {}, put=p)
        p.assert_called_once()
        p = Mock()
        utils._send_response("test_url", p, put=p)
        response = json.loads(p.call_args[1]['data'])
        self.assertEqual("FAILED", response['Status'])
        self.assertEqual({}, response['Data'])
