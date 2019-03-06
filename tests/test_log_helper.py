from crhelper.log_helper import *
import unittest
import logging


class TestLogHelper(unittest.TestCase):

    def test_logging_no_formatting(self):
        logger = logging.getLogger('1')
        handler = logging.StreamHandler()
        logger.addHandler(handler)
        orig_formatters = []
        for c in range(len(logging.root.handlers)):
            orig_formatters.append(logging.root.handlers[c].formatter)
        setup(level='DEBUG', formatter_cls=None, boto_level='CRITICAL')
        new_formatters = []
        for c in range(len(logging.root.handlers)):
            new_formatters.append(logging.root.handlers[c].formatter)
        self.assertEqual(orig_formatters, new_formatters)

    def test_logging_boto_explicit(self):
        logger = logging.getLogger('2')
        handler = logging.StreamHandler()
        logger.addHandler(handler)
        setup(level='DEBUG', formatter_cls=None, boto_level='CRITICAL')
        for t in ['boto', 'boto3', 'botocore', 'urllib3']:
            b_logger = logging.getLogger(t)
            self.assertEqual(b_logger.level, 50)

    def test_logging_json(self):
        logger = logging.getLogger('3')
        handler = logging.StreamHandler()
        logger.addHandler(handler)
        setup(level='DEBUG', formatter_cls=JsonFormatter, RequestType='ContainerInit')
        for handler in logging.root.handlers:
            self.assertEqual(JsonFormatter, type(handler.formatter))

    def test_logging_boto_implicit(self):
        logger = logging.getLogger('4')
        handler = logging.StreamHandler()
        logger.addHandler(handler)
        setup(level='DEBUG', formatter_cls=JsonFormatter, RequestType='ContainerInit')
        for t in ['boto', 'boto3', 'botocore', 'urllib3']:
            b_logger = logging.getLogger(t)
            self.assertEqual(b_logger.level, 10)

    def test_logging_json_keys(self):
        with self.assertLogs() as ctx:
            logger = logging.getLogger()
            handler = logging.StreamHandler()
            logger.addHandler(handler)
            setup(level='DEBUG', formatter_cls=JsonFormatter, RequestType='ContainerInit')
            logger.info("test")
            logs = json.loads(ctx.output[0])
        self.assertEqual(["timestamp", "level", "location", "RequestType", "message"], list(logs.keys()))

    def test_logging_json_parse_message(self):
        with self.assertLogs() as ctx:
            logger = logging.getLogger()
            handler = logging.StreamHandler()
            logger.addHandler(handler)
            setup(level='DEBUG', formatter_cls=JsonFormatter, RequestType='ContainerInit')
            logger.info("{}")
            logs = json.loads(ctx.output[0])
        self.assertEqual({}, logs["message"])

    def test_logging_json_exception(self):
        with self.assertLogs() as ctx:
            logger = logging.getLogger()
            handler = logging.StreamHandler()
            logger.addHandler(handler)
            setup(level='DEBUG', formatter_cls=JsonFormatter, RequestType='ContainerInit')
            try:
                1 + 't'
            except Exception as e:
                logger.info("[]", exc_info=True)
            logs = json.loads(ctx.output[0])
        self.assertIn("exception", logs.keys())
