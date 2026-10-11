"""
Simple client server unit test
"""

import logging
import threading
import unittest

import myClientServer as clientserver
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)


class TestEchoService(unittest.TestCase):
    """The test"""
    _server = clientserver.Server()  # create single server in class variable
    _server_thread = threading.Thread(target=_server.serve)  # define thread for running server

    @classmethod
    def setUpClass(cls):
        cls._server_thread.start()  # start server loop in a thread (called only once)

    def setUp(self):
        super().setUp()
        self.client = clientserver.Client()  # create new client for each test

    def test_srv_call_1(self):  # each test_* function is a test
        """Test simple call 1"""
        msg = self.client.call("Get;Bob")
        self.assertEqual(msg, "Return;0187")

    def test_srv_call_2(self):  # each test_* function is a test
        """Test simple call 2"""
        msg = self.client.call("Get;Rob")
        self.assertEqual(msg, "Return;0123")

    def test_srv_call_lower_case(self):  # each test_* function is a test
        """Test call with lower case"""
        msg = self.client.call("Get;bob")
        self.assertEqual(msg, "Return;0187")

    def test_srv_call_space(self):  # each test_* function is a test
        """Test call with spaces"""
        msg = self.client.call("Get;   Bob    ")
        self.assertEqual(msg, "Return;0187")

    def test_srv_call_empty_space(self):  # each test_* function is a test
        """Test call with empty spaces"""
        msg = self.client.call("Get;   ")
        self.assertEqual(msg, "Error;no name given")

    def test_srv_call_empty(self):  # each test_* function is a test
        """Test call with empty input"""
        msg = self.client.call("Get;")
        self.assertEqual(msg, "Error;no name given")

    def test_srv_call_invalid(self):  # each test_* function is a test
        """Test call with invalid name"""
        msg = self.client.call("Get;Ali")
        self.assertEqual(msg, "Error;invalid name")

    def test_srv_call_symbols(self):  # each test_* function is a test
        """Test call with symbols"""
        msg = self.client.call("Get;Bob$")
        self.assertEqual(msg, "Error;invalid name")

    def test_srv_get(self):  # each test_* function is a test
        """Test simple get"""
        self.assertIsNone(self.client.get("Bob"))

    def test_srv_get_space(self):  # each test_* function is a test
        """Test get with spaces"""
        self.assertIsNone(self.client.get("   Bob    "))
    
    def test_srv_get_empty_space(self):  # each test_* function is a test
        """Test get with empty spaces"""
        self.assertIsNone(self.client.get("   "))
    
    def test_srv_get_invalid(self):  # each test_* function is a test
        """Test get with invalid name"""
        self.assertIsNone(self.client.get("Ali"))

    def test_srv_getAll(self):  # each test_* function is a test
        """Test simple getAll"""
        self.assertIsNone(self.client.getAll())

    def test_srv_call_symbols(self):  # each test_* function is a test
        """Test call with symbols"""
        self.assertIsNone(self.client.get("Bob$"))

    def tearDown(self):
        self.client.close()  # terminate client after each test

    @classmethod
    def tearDownClass(cls):
        cls._server._serving = False  # break out of server loop. pylint: disable=protected-access
        cls._server_thread.join()  # wait for server thread to terminate


if __name__ == '__main__':
    unittest.main()
