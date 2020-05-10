from src.attendance.api_connection import ISConnectionBuilder

from .utils.server_mock import server

from multiprocessing import Process
from unittest import TestCase

import time


class TestISConnectionWithConnectionAvailable(TestCase):

    @classmethod
    def setUpClass(cls):
        cls._server_process = Process(target=server.run)
        cls._server_process.start()
        # time.sleep(5)

    @classmethod
    def tearDownClass(cls):
        cls._server_process.terminate()

    def setUp(self):
        builder = ISConnectionBuilder()
        builder.set_mac_address('')
        builder.set_baseurl('http://127.0.0.1:5000')
        builder.set_url('http://127.0.0.1:5000/testconnection')
        self.connection = builder.build()

    def test_is_available(self):
        self.assertTrue(self.connection.is_available())

    def test_send_data(self):
        result = self.connection.send_data(['0123456789'])
        self.assertTrue('msg' in result)
        self.assertTrue(result['msg'] == 'Test successful')


class TestISConnectionWithoutConnection(TestCase):

    def setUp(self):
        builder = ISConnectionBuilder()
        builder.set_mac_address('')
        builder.set_baseurl('http://127.0.0.1:5000')
        builder.set_url('http://127.0.0.1:5000/testconnection')
        self.connection = builder.build()

    def test_is_available(self):
        self.assertFalse(self.connection.is_available())
