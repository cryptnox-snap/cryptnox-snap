from unittest import mock, TestCase

import cryptnoxpy
from argparse import Namespace

from cryptnoxcard.command.btc import Btc
from cryptnoxcard.command.cards import Cards
from cryptnoxcard.command.change_pin import ChangePin
from cryptnoxcard.command.config import Config
from cryptnoxcard.command.eosio import Eosio
from cryptnoxcard.command.info import Info
from cryptnoxcard.command.initialize import Initialize
from cryptnoxcard.command.reset import Reset
from cryptnoxcard.command.seed import Seed
from cryptnoxcard.command.unlock_pin import UnlockPin

INITIALIZE = Initialize(Namespace(command="init", demo=True, index=None,
                                  serial=None, verbose=False))
INFO = Info(Namespace(command='info', pin=None))
EOSIO_GET = Eosio(Namespace(
    account='cryptnoxxx44', action='get', command='eosio',
    get='account', key_type=None, path="m/44'/194'/0'/0",
    pin=None, symbol=None, url=None))
EOSIO_PAY = Eosio(Namespace(
    action='pay', amount=0.001, command='eosio', key_type=None,
    memo='', path="m/44'/194'/0'/0", pin=None, symbol=None,
    toaccount='cryptnoxxx22', url=None))
SEND_BTC = Btc(Namespace(
    action='send', address='murMmwBCCcwJ2MLVDN7j3h5fkqeUDsQH42', amount=1e-05,
    command='send', fees=None, network=None, pin=None, type='btc'))
CHANGE_PIN = ChangePin(Namespace(command='change_pin', pin=None))
KEY_CHIP = Seed(Namespace(command='key', method='chip', pin=None))
RESET = Reset(Namespace(command="reset"))
UNLOCK_PIN = UnlockPin(Namespace(command='unlock_pin'))
LIST = Cards(Namespace(command="list"))
CONFIG = Config(Namespace(command='config', key=None, section=None, value=None))


class TestAAlwaysWorkingCommands(TestCase):
    def test_list(self):
        assert LIST.execute() == 0

    def test_config(self):
        assert CONFIG.execute() == 0


class TestBInitializationException(TestCase):
    @mock.patch("cryptnoxcard.command.helper.security.getpass", return_value="")
    def setUp(self, _mock_getpass) -> None:
        with cryptnoxpy.connection.Connection(index=0) as connection:
            if connection.card.initialized:
                RESET._execute(connection)

    def test_key(self):
        with cryptnoxpy.connection.Connection(index=0) as connection:
            with self.assertRaises(cryptnoxpy.InitializationException):
                KEY_CHIP._execute(connection)

    def test_send(self):
        with cryptnoxpy.connection.Connection(index=0) as connection:
            with self.assertRaises(cryptnoxpy.InitializationException):
                SEND_BTC._execute(connection)

    def test_reset(self):
        with cryptnoxpy.connection.Connection(index=0) as connection:
            with self.assertRaises(cryptnoxpy.InitializationException):
                RESET._execute(connection)

    def test_eosio(self):
        with cryptnoxpy.connection.Connection(index=0) as connection:
            with self.assertRaises(cryptnoxpy.InitializationException):
                EOSIO_PAY._execute(connection)

    def test_info(self):
        with cryptnoxpy.connection.Connection(index=0) as connection:
            with self.assertRaises(cryptnoxpy.InitializationException):
                INFO._execute(connection)

    def test_change_pin(self):
        with cryptnoxpy.connection.Connection(index=0) as connection:
            with self.assertRaises(cryptnoxpy.InitializationException):
                CHANGE_PIN._execute(connection)

    @mock.patch("cryptnoxcard.command.helper.security.getpass", return_value="")
    def test_unlock_pin(self, _mock_getpass):
        with cryptnoxpy.connection.Connection(index=0) as connection:
            with self.assertRaises(cryptnoxpy.InitializationException):
                UNLOCK_PIN._execute(connection)


class TestCInitialization(TestCase):
    @mock.patch("cryptnoxcard.command.helper.security.getpass", return_value="")
    @mock.patch("builtins.input", return_value="y")
    def test_positive_init(self, _mock_input, _mock_getpass):
        try:
            with cryptnoxpy.connection.Connection(index=0) as connection:
                cryptnoxpy.check_init(connection)
                RESET._execute(connection)
        except cryptnoxpy.exceptions.InitializationException:
            pass
        with cryptnoxpy.connection.Connection(index=0) as connection:
            assert INITIALIZE._execute(connection) == 0

    @mock.patch("cryptnoxcard.command.helper.security.getpass", return_value="")
    @mock.patch("builtins.input", return_value="y")
    def test_negative_init(self, _mock_input, _mock_getpass):
        with cryptnoxpy.connection.Connection(index=0) as connection:
            try:
                cryptnoxpy.check_init(connection)
            except cryptnoxpy.exceptions.InitializationException:
                INITIALIZE._execute(connection)
        with cryptnoxpy.connection.Connection(index=0) as connection:
            assert INITIALIZE._execute(connection) == 1


@mock.patch("cryptnoxcard.command.helper.security.getpass", return_value="")
class TestDKeyExceptionRaised(TestCase):
    def test_1_info(self, _mock_getpass):
        with cryptnoxpy.connection.Connection(index=0) as connection:
            with self.assertRaises(cryptnoxpy.KeyException):
                INFO._execute(connection)

    def test_2_eosio_get(self, _mock_getpass):
        with cryptnoxpy.connection.Connection(index=0) as connection:
            with self.assertRaises(cryptnoxpy.KeyException):
                EOSIO_GET._execute(connection)

    def test_3_eosio_send(self, _mock_getpass):
        with cryptnoxpy.connection.Connection(index=0) as connection:
            with self.assertRaises(cryptnoxpy.KeyException):
                EOSIO_PAY._execute(connection)

    def test_4_send(self, _mock_getpass):
        with cryptnoxpy.connection.Connection(index=0) as connection:
            with self.assertRaises(cryptnoxpy.KeyException):
                SEND_BTC._execute(connection)

    def test_5_change_pin(self, _mock_getpass):
        with cryptnoxpy.connection.Connection(index=0) as connection:
            with self.assertRaises(cryptnoxpy.KeyException):
                CHANGE_PIN._execute(connection)

    def test_6_key(self, _mock_getpass):
        with mock.patch("builtins.print") as mock_print:
            with cryptnoxpy.connection.Connection(index=0) as connection:
                KEY_CHIP._execute(connection)
        mock_print.assert_called_with("New key generated in card.")
