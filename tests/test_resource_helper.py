import os
import crhelper
import unittest
from unittest.mock import call, patch, Mock
import threading

test_events = {
    "Create": {
        "RequestType": "Create",
        "RequestId": "test-event-id",
        "StackId": "arn/test-stack-id/guid",
        "LogicalResourceId": "TestResourceId",
        "ResponseURL": "response_url"
    },
    "Update": {
        "RequestType": "Update",
        "RequestId": "test-event-id",
        "StackId": "test-stack-id",
        "LogicalResourceId": "TestResourceId",
        "PhysicalResourceId": "test-pid",
        "ResponseURL": "response_url"
    },
    "Delete": {
        "RequestType": "Delete",
        "RequestId": "test-event-id",
        "StackId": "test-stack-id",
        "LogicalResourceId": "TestResourceId",
        "PhysicalResourceId": "test-pid",
        "ResponseURL": "response_url"
    }
}


class MockContext(object):

    function_name = "test-function"
    ms_remaining = 9000

    @staticmethod
    def get_remaining_time_in_millis():
        return MockContext.ms_remaining


class TestCfnResource(unittest.TestCase):
    def setUp(self):
        os.environ['AWS_REGION'] = 'us-east-1'

    def tearDown(self):
        os.environ.pop('AWS_REGION', None)

    @patch('crhelper.log_helper.setup', return_value=None)
    @patch('crhelper.resource_helper.CfnResource._set_timeout', Mock())
    def test_init(self, mock_method):
        crhelper.resource_helper.CfnResource()
        mock_method.assert_called_once_with('DEBUG', boto_level='ERROR', formatter_cls=None)

        crhelper.resource_helper.CfnResource(json_logging=True)
        mock_method.assert_called_with('DEBUG', boto_level='ERROR', RequestType='ContainerInit')

    @patch('crhelper.log_helper.setup', return_value=None)
    @patch('crhelper.resource_helper.CfnResource._set_timeout', Mock())
    def test_init_failure(self, mock_method):
        mock_method.side_effect = Exception("test")
        c = crhelper.resource_helper.CfnResource(json_logging=True)
        self.assertTrue(c._init_failed)

    @patch('crhelper.log_helper.setup', Mock())
    @patch('crhelper.resource_helper.CfnResource._poll_enabled', Mock(return_value=False))
    @patch('crhelper.resource_helper.CfnResource._polling_init', Mock())
    @patch('crhelper.resource_helper.CfnResource._wait_for_cwlogs', Mock())
    @patch('crhelper.resource_helper.CfnResource._send')
    @patch('crhelper.resource_helper.CfnResource._set_timeout', Mock())
    @patch('crhelper.resource_helper.CfnResource._wrap_function', Mock())
    def test_init_failure_call(self, mock_send):
        c = crhelper.resource_helper.CfnResource()
        c.init_failure(Exception('TestException'))

        event = test_events["Create"]
        c.__call__(event, MockContext)

        self.assertEqual([call('FAILED', 'TestException')], mock_send.call_args_list)

    @patch('crhelper.log_helper.setup', Mock())
    @patch('crhelper.resource_helper.CfnResource._poll_enabled', Mock(return_value=False))
    @patch('crhelper.resource_helper.CfnResource._polling_init', Mock())
    @patch('crhelper.resource_helper.CfnResource._wait_for_cwlogs', Mock())
    @patch('crhelper.resource_helper.CfnResource._send', Mock())
    @patch('crhelper.resource_helper.CfnResource._set_timeout', Mock())
    @patch('crhelper.resource_helper.CfnResource._wrap_function', Mock())
    @patch('crhelper.resource_helper.CfnResource._cfn_response', return_value=None)
    def test_call(self, cfn_response_mock):
        c = crhelper.resource_helper.CfnResource()
        event = test_events["Create"]
        c.__call__(event, MockContext)
        self.assertTrue(c._send_response)
        cfn_response_mock.assert_called_once_with(event)

        c._sam_local = True
        c._poll_enabled = Mock(return_value=True)
        c._polling_init = Mock()
        c.__call__(event, MockContext)
        c._polling_init.assert_not_called()
        self.assertEqual(1, len(cfn_response_mock.call_args_list))

        c._sam_local = False
        c._send_response = False
        c.__call__(event, MockContext)
        c._polling_init.assert_called()
        self.assertEqual(1, len(cfn_response_mock.call_args_list))

        event = test_events["Delete"]
        c._wait_for_cwlogs = Mock()
        c._poll_enabled = Mock(return_value=False)
        c.__call__(event, MockContext)
        c._wait_for_cwlogs.assert_called()

        c._send = Mock()
        cfn_response_mock.side_effect = Exception("test")
        c.__call__(event, MockContext)
        c._send.assert_called_with('FAILED', "test")

    @patch('crhelper.log_helper.setup', Mock())
    @patch('crhelper.resource_helper.CfnResource._poll_enabled', Mock(return_value=False))
    @patch('crhelper.resource_helper.CfnResource._polling_init', Mock())
    @patch('crhelper.resource_helper.CfnResource._send', Mock())
    @patch('crhelper.resource_helper.CfnResource._set_timeout', Mock())
    @patch('crhelper.resource_helper.CfnResource._wrap_function', Mock())
    @patch('crhelper.resource_helper.CfnResource._cfn_response', Mock(return_value=None))
    def test_wait_for_cwlogs(self):

        c = crhelper.resource_helper.CfnResource()
        c._context = MockContext
        s = Mock()
        c._wait_for_cwlogs(sleep=s)
        s.assert_not_called()
        MockContext.ms_remaining = 140000
        c._wait_for_cwlogs(sleep=s)
        s.assert_called_once()

    @patch('crhelper.log_helper.setup', Mock())
    @patch('crhelper.resource_helper.CfnResource._poll_enabled', Mock(return_value=False))
    @patch('crhelper.resource_helper.CfnResource._wait_for_cwlogs', Mock())
    @patch('crhelper.resource_helper.CfnResource._send', Mock())
    @patch('crhelper.resource_helper.CfnResource._set_timeout', Mock())
    @patch('crhelper.resource_helper.CfnResource._wrap_function', Mock())
    @patch('crhelper.resource_helper.CfnResource._cfn_response', Mock())
    def test_polling_init(self):
        c = crhelper.resource_helper.CfnResource()
        event = test_events['Create']
        c._setup_polling = Mock()
        c._remove_polling = Mock()
        c._polling_init(event)
        c._setup_polling.assert_called_once()
        c._remove_polling.assert_not_called()
        self.assertEqual(c.PhysicalResourceId, None)

        c.Status = 'FAILED'
        c._setup_polling.assert_called_once()
        c._setup_polling.assert_called_once()

        c = crhelper.resource_helper.CfnResource()
        event = test_events['Create']
        c._setup_polling = Mock()
        c._remove_polling = Mock()
        event['CrHelperPoll'] = "Some stuff"
        c.PhysicalResourceId = None
        c._polling_init(event)
        c._remove_polling.assert_not_called()
        c._setup_polling.assert_not_called()

        c.Status = 'FAILED'
        c._polling_init(event)
        c._remove_polling.assert_called_once()
        c._setup_polling.assert_not_called()

        c.Status = ''
        c.PhysicalResourceId = "some-id"
        c._remove_polling.assert_called()
        c._setup_polling.assert_not_called()

    @patch('crhelper.log_helper.setup', Mock())
    @patch('crhelper.resource_helper.CfnResource._poll_enabled', Mock(return_value=False))
    @patch('crhelper.resource_helper.CfnResource._wait_for_cwlogs', Mock())
    @patch('crhelper.resource_helper.CfnResource._send', Mock())
    @patch('crhelper.resource_helper.CfnResource._set_timeout', Mock())
    @patch('crhelper.resource_helper.CfnResource._wrap_function', Mock())
    def test_cfn_response(self):
        c = crhelper.resource_helper.CfnResource()
        event = test_events['Create']
        c._send = Mock()

        orig_pid = c.PhysicalResourceId
        self.assertEqual(orig_pid, '')
        c._cfn_response(event)
        c._send.assert_called_once()
        print("RID: [%s]" % [c.PhysicalResourceId])
        self.assertEqual(True, c.PhysicalResourceId.startswith('test-stack-id_TestResourceId_'))

        c._send = Mock()
        c.PhysicalResourceId = 'testpid'
        c._cfn_response(event)
        c._send.assert_called_once()
        self.assertEqual('testpid', c.PhysicalResourceId)

        c._send = Mock()
        c.PhysicalResourceId = True
        c._cfn_response(event)
        c._send.assert_called_once()
        self.assertEqual(True, c.PhysicalResourceId.startswith('test-stack-id_TestResourceId_'))

        c._send = Mock()
        c.PhysicalResourceId = ''
        event['PhysicalResourceId'] = 'pid-from-event'
        c._cfn_response(event)
        c._send.assert_called_once()
        self.assertEqual('pid-from-event', c.PhysicalResourceId)

    @patch('crhelper.log_helper.setup', Mock())
    @patch('crhelper.resource_helper.CfnResource._poll_enabled', Mock(return_value=False))
    @patch('crhelper.resource_helper.CfnResource._wait_for_cwlogs', Mock())
    @patch('crhelper.resource_helper.CfnResource._send', Mock())
    @patch('crhelper.resource_helper.CfnResource._set_timeout', Mock())
    def test_wrap_function(self):
        c = crhelper.resource_helper.CfnResource()

        def func(e, c):
            return 'testpid'

        c._wrap_function(func)
        self.assertEqual('testpid', c.PhysicalResourceId)
        self.assertNotEqual('FAILED', c.Status)

        def func(e, c):
            raise Exception('test exception')

        c._wrap_function(func)
        self.assertEqual('FAILED', c.Status)
        self.assertEqual('test exception', c.Reason)

    @patch('crhelper.log_helper.setup', Mock())
    @patch('crhelper.resource_helper.CfnResource._poll_enabled', Mock(return_value=False))
    @patch('crhelper.resource_helper.CfnResource._wait_for_cwlogs', Mock())
    @patch('crhelper.resource_helper.CfnResource._set_timeout', Mock())
    def test_send(self):
        c = crhelper.resource_helper.CfnResource()
        s = Mock()
        c._send(send_response=s)
        s.assert_called_once()

    @patch('crhelper.log_helper.setup', Mock())
    @patch('crhelper.resource_helper.CfnResource._poll_enabled', Mock(return_value=False))
    @patch('crhelper.resource_helper.CfnResource._wait_for_cwlogs', Mock())
    @patch('crhelper.resource_helper.CfnResource._send', return_value=None)
    @patch('crhelper.resource_helper.CfnResource._set_timeout', Mock())
    def test_timeout(self, s):
        c = crhelper.resource_helper.CfnResource()
        c._timeout()
        s.assert_called_with('FAILED', "Execution timed out")

    @patch('crhelper.log_helper.setup', Mock())
    @patch('crhelper.resource_helper.CfnResource._poll_enabled', Mock(return_value=False))
    @patch('crhelper.resource_helper.CfnResource._wait_for_cwlogs', Mock())
    @patch('crhelper.resource_helper.CfnResource._send', Mock())
    def test_set_timeout(self):
        c = crhelper.resource_helper.CfnResource()
        c._context = MockContext()
        def func():
            return None

        c._set_timeout()
        t = threading.Timer(1000, func)
        self.assertEqual(type(t), type(c._timer))
        t.cancel()
        c._timer.cancel()

    @patch('crhelper.log_helper.setup', Mock())
    @patch('crhelper.resource_helper.CfnResource._poll_enabled', Mock(return_value=False))
    @patch('crhelper.resource_helper.CfnResource._wait_for_cwlogs', Mock())
    @patch('crhelper.resource_helper.CfnResource._send', Mock())
    @patch('crhelper.resource_helper.CfnResource._set_timeout', Mock())
    def test_cleanup_response(self):
        c = crhelper.resource_helper.CfnResource()
        c.Data = {"CrHelperPoll": 1, "CrHelperPermission": 2, "CrHelperRule": 3}
        c._cleanup_response()
        self.assertEqual({}, c.Data)

    @patch('crhelper.log_helper.setup', Mock())
    @patch('crhelper.resource_helper.CfnResource._poll_enabled', Mock(return_value=False))
    @patch('crhelper.resource_helper.CfnResource._wait_for_cwlogs', Mock())
    @patch('crhelper.resource_helper.CfnResource._send', Mock())
    @patch('crhelper.resource_helper.CfnResource._set_timeout', Mock())
    def test_remove_polling(self):
        c = crhelper.resource_helper.CfnResource()
        c._context = MockContext()

        c._events_client.remove_targets = Mock()
        c._events_client.delete_rule = Mock()
        c._lambda_client.remove_permission = Mock()

        with self.assertRaises(Exception) as e:
            c._remove_polling()

            self.assertEqual("failed to cleanup CloudWatch event polling", str(e))
        c._events_client.remove_targets.assert_not_called()
        c._events_client.delete_rule.assert_not_called()
        c._lambda_client.remove_permission.assert_not_called()

        c._event["CrHelperRule"] = "1/2"
        c._event["CrHelperPermission"] = "1/2"
        c._remove_polling()
        c._events_client.remove_targets.assert_called()
        c._events_client.delete_rule.assert_called()
        c._lambda_client.remove_permission.assert_called()

    @patch('crhelper.log_helper.setup', Mock())
    @patch('crhelper.resource_helper.CfnResource._poll_enabled', Mock(return_value=False))
    @patch('crhelper.resource_helper.CfnResource._wait_for_cwlogs', Mock())
    @patch('crhelper.resource_helper.CfnResource._send', Mock())
    @patch('crhelper.resource_helper.CfnResource._set_timeout', Mock())
    def test_setup_polling(self):
        c = crhelper.resource_helper.CfnResource()
        c._context = MockContext()
        c._event = test_events["Update"]
        c._lambda_client.add_permission = Mock()
        c._events_client.put_rule = Mock(return_value={"RuleArn": "arn:aws:lambda:blah:blah:function:blah/blah"})
        c._events_client.put_targets = Mock()
        c._setup_polling()
        c._events_client.put_targets.assert_called()
        c._events_client.put_rule.assert_called()
        c._lambda_client.add_permission.assert_called()

    @patch('crhelper.log_helper.setup', Mock())
    @patch('crhelper.resource_helper.CfnResource._poll_enabled', Mock(return_value=False))
    @patch('crhelper.resource_helper.CfnResource._wait_for_cwlogs', Mock())
    @patch('crhelper.resource_helper.CfnResource._send', Mock())
    @patch('crhelper.resource_helper.CfnResource._set_timeout', Mock())
    def test_wrappers(self):
        c = crhelper.resource_helper.CfnResource()

        def func():
            pass

        for f in ["create", "update", "delete", "poll_create", "poll_update", "poll_delete"]:
            self.assertEqual(None, getattr(c, "_%s_func" % f))
            getattr(c, f)(func)
            self.assertEqual(func, getattr(c, "_%s_func" % f))
