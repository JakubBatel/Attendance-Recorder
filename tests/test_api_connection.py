from src.attendance.api_connection import APIConnectionException
from src.attendance.api_connection import ISConnectionBuilder

from .utils.server_mock import server

from multiprocessing import Process
from unittest import TestCase

import time


class TestISConnectionOnlineModeWithConnectionAvailable(TestCase):

    @classmethod
    def setUpClass(cls):
        cls._server_process = Process(target=server.run)
        cls._server_process.start()
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls._server_process.terminate()

    def setUp(self):
        builder = ISConnectionBuilder()
        builder.set_mac_address('42:97:0b:27:53:86')
        builder.set_baseurl('http://127.0.0.1:5000')
        builder.set_url('http://127.0.0.1:5000/testonline')
        self.connection = builder.build()

    def test_is_available(self):
        self.assertTrue(self.connection.is_available())

    def test_init_call_correct(self):
        expected_result = {
            'msga': 'Tasha Samson',
            'msgb': 'TEST SUCCESS',
            'token': 'thXtKt_2q7T77PsWD3hLJT34xCexmsaY',
            'state': 'online'
        }

        result = self.connection.send_organizator_data('0cb90021f6')
        self.assertEqual(result, expected_result)

    def test_init_call_incorrect(self):
        expected_result = {
            'msga': 'No recording started for abcdef0123',
            'msgb': 'TEST SUCCESS',
            'err': '1'
        }

        result = self.connection.send_organizator_data('abcdef0123')
        self.assertEqual(result, expected_result)

    def test_call_correct_1(self):
        expected_result = {
            'msga': 'Sofia Chadwick',
            'msgb': 'TEST SUCCESS',
            'token': 'EG7I52PehLKrWB9SzKibyNVAwFKbZKi0'
        }

        self.connection.set_token('thXtKt_2q7T77PsWD3hLJT34xCexmsaY')
        result = self.connection.send_data('f8a400ca45')
        self.assertEqual(result, expected_result)

    def test_call_correct_2(self):
        expected_result = {
            'msga': 'Salomon Hershey',
            'msgb': 'TEST SUCCESS',
            'token': 'EG7I52PehLKrWB9SzKibyNVAwFKbZKi0'
        }

        self.connection.set_token('EG7I52PehLKrWB9SzKibyNVAwFKbZKi0')
        result = self.connection.send_data('f64dcf480d')
        self.assertEqual(result, expected_result)

    def test_call_incorrect_token(self):
        expected_result = {
            'msga': 'Invalid token l9YYcRYPNw79oGCtXkolbYHp6civE1CO',
            'msgb': 'TEST SUCCESS',
            'err': '1'
        }

        self.connection.set_token('l9YYcRYPNw79oGCtXkolbYHp6civE1CO')
        result = self.connection.send_data('f64dcf480d')
        self.assertEqual(result, expected_result)

    def test_call_incorrect_card(self):
        expected_result = {
            'msga': 'No recording started for f8a400ca45',
            'msgb': 'TEST SUCCESS',
            'err': '1',
            'token': 'EG7I52PehLKrWB9SzKibyNVAwFKbZKi0'
        }

        self.connection.set_token('EG7I52PehLKrWB9SzKibyNVAwFKbZKi0')
        result = self.connection.send_data('f8a400ca45')
        self.assertEqual(result, expected_result)

    def test_call_multiple_cards(self):
        expected_result = {
            'msga': 'Sofia Chadwick',
            'msgb': 'TEST SUCCESS',
            'token': 'EG7I52PehLKrWB9SzKibyNVAwFKbZKi0'
        }

        self.connection.set_token('thXtKt_2q7T77PsWD3hLJT34xCexmsaY')
        result = self.connection.send_data('f8a400ca45', ['f64dcf480d'])
        self.assertEqual(result, expected_result)


class TestISConnectionOnlineModeWithoutConnection(TestCase):

    def setUp(self):
        builder = ISConnectionBuilder()
        builder.set_mac_address('42:97:0b:27:53:86')
        builder.set_baseurl('http://127.0.0.1:5000')
        builder.set_url('http://127.0.0.1:5000/testonline')
        self.connection = builder.build()

    def test_is_available(self):
        self.assertFalse(self.connection.is_available())

    def test_init_call(self):
        with self.assertRaises(APIConnectionException):
            self.connection.send_organizator_data('0cb90021f6')

    def test_call(self):
        with self.assertRaises(APIConnectionException):
            self.connection.send_data('f8a400ca45')


class TestISConnectionOfflineMode(TestCase):

    @classmethod
    def setUpClass(cls):
        cls._server_process = Process(target=server.run)
        cls._server_process.start()
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls._server_process.terminate()

    def setUp(self):
        builder = ISConnectionBuilder()
        builder.set_mac_address('42:97:0b:27:53:86')
        builder.set_baseurl('http://127.0.0.1:5000')
        builder.set_url('http://127.0.0.1:5000/testoffline')
        self.connection = builder.build()

    def test_init_call(self):
        expected_result = {
            'msga': 'Tasha Samson',
            'msgb': 'TEST SUCCESS',
            'token': 'thXtKt_2q7T77PsWD3hLJT34xCexmsaY',
            'state': 'offline'
        }

        result = self.connection.send_organizator_data('0cb90021f6')
        self.assertEqual(result, expected_result)

    def test_call_send_cached(self):
        expected_result = {
            'msga': 'Sofia Chadwick',
            'msgb': 'TEST SUCCESS',
            'token': 'EG7I52PehLKrWB9SzKibyNVAwFKbZKi0'
        }

        self.connection.set_token('thXtKt_2q7T77PsWD3hLJT34xCexmsaY')
        result = self.connection.send_cached_data_only(
            ['0cb90021f6', 'f8a400ca45'])
        self.assertEqual(result, expected_result)
