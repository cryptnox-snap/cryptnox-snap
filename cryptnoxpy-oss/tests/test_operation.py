# -*- coding: utf-8 -*-
"""
Module for unit testing Cryptnox operations.
"""
from unittest import mock, TestCase

from cryptnoxpy import check_init, InitializationException, check_pin, \
    PinException, CryptnoxException, generate_seed, KeyGenerationException, \
    init, GenuineCheckException, ConnectionException, sign, Derivation, \
    DerivationSelectionException, DataException, unblock_pin, \
    ReaderException, CardTypeException, CardException, get_cards_info, \
    get_card_index, reset, change_pin, change_puk

INIT_APDU_CALL = [128, 254, 0, 0, 146, 65, 4, 40, 7, 6, 179, 246, 230, 195,
                  212, 236, 102, 8, 201, 49, 32, 188, 133, 59, 249, 54, 22,
                  184, 137, 18, 128, 114, 66, 129, 26, 41, 112, 144, 8, 27, 49,
                  139, 36,
                  133, 110, 146, 224, 37, 225, 204, 90, 7, 56, 177, 17, 177,
                  22, 206, 139, 109, 5, 245, 149, 111, 227, 115, 147, 139, 9,
                  60, 193, 94, 123, 198, 118, 43, 252, 181, 21, 129, 114, 119,
                  136, 5,
                  12, 114, 234, 134, 48, 163, 241, 16, 251, 211, 131, 14,
                  184, 107, 115,
                  203, 66, 234, 211, 124, 248, 114, 241, 86, 223, 97, 89, 88,
                  237, 148, 81, 89, 234, 199, 49, 83, 23, 14, 26, 169, 99,
                  129, 72, 241, 176, 125, 130, 105, 183, 218, 23, 37, 3, 8,
                  184, 28, 126, 133, 191, 229, 66, 253, 147, 184, 208, 142, 52]
SEND_ENCRYPTED_RESPONSES = {
    "check_init": b"",
    "generate_seed": b"<\x00\t\x9e(_\xeb:\x9d\x00\xd4\x8d\xe5pto\n\xd5\x8b\xa8"
                     b"\xc1\x89z\xb4\xd7\x0e\x06\x1cj\xb2\x13\xcb"
}
SEND_APDU_RESPONSES = {
    "init": ([], 144, 0)
}
SESSION_PUBLIC_KEY =\
    "04acfe5289c62bace6928d814ab3ab5c023b45214e73b7636e1c05a841e0d840db00c239" \
    "759b7c0d9dd836f35976fc0b190d432cc06281297980db55713c92e430"
COMMON_PAIRING_DATA = b"\x00Cryptnox Basic CommonPairingData"

CARD_INFO = [
            {'serial_number': 3873336462863864728, 'applet_version': '1.1.0',
             'name': 'DEMO', 'email': 'DEMO', 'initialized': True,
             'seed': True},
            {'serial_number': 8688321800324536269, 'applet_version': '0.9.2',
             'name': '', 'email': '', 'initialized': True, 'seed': True}
        ]


@mock.patch("cryptnoxpy.operation.Connection")
class TestOperation(TestCase):
    """
    Class used for testing operations.
    """
    def test_check_init(self, connection):
        """
        Test for checking if card is initialized
        """
        connection.card.initialized = True
        self.assertEqual(check_init(connection), None)

    def test_check_init_card_not_initialized(self, connection):
        """
        Test for checking if card is can't be initialized
        """
        connection.card.initialized = False
        with self.assertRaises(InitializationException):
            check_init(connection)

    def test_check_pin(self, connection):
        """
        Test for checking if pin is same as on the card
        """
        connection.send_encrypted.return_value = SEND_ENCRYPTED_RESPONSES[
            "check_init"]
        self.assertEqual(check_pin(connection, "1234"), None)

    def test_check_pin_exception(self, connection):
        """
        Test for checking if PinException is raised when pin is not same as on
        the card
        """
        connection.send_encrypted.side_effect = PinException(3)
        with self.assertRaises(PinException):
            check_pin(connection, "1")

    def test_check_pin_send_exception(self, connection):
        """
        Test for checking if CryptnoxException is raised while checking the pin
        """
        connection.send_encrypted.side_effect = CryptnoxException()
        with self.assertRaises(CryptnoxException):
            check_pin(connection, "1234")

    def test_generate_seed(self, connection):
        """
        Test for checking if seed is generated correctly
        """
        connection.send_encrypted.return_value = SEND_ENCRYPTED_RESPONSES[
            "generate_seed"]
        self.assertEqual(generate_seed(connection),
                         SEND_ENCRYPTED_RESPONSES["generate_seed"])

    def test_generate_seed_wrong_response(self, connection):
        """
        Test for checking if KeyGenerationException is risen while creating seed
        """
        connection.send_encrypted.return_value = SEND_ENCRYPTED_RESPONSES[
            "generate_seed"][:-1]
        with self.assertRaises(KeyGenerationException):
            generate_seed(connection)

    def test_init(self, connection):
        """
        TODO:
        """

    def test_init_initialization_exception(self, connection):
        """
        Test if InitializationException is risen while initializing the card
        """
        connection.card.check_genuine.return_value = None
        connection.send_apdu.return_value = ([], 100, 0)
        connection.card.session_public_key = SESSION_PUBLIC_KEY
        with self.assertRaises(InitializationException):
            init(connection, "", "", "", "")

    def test_init_card_not_genuine(self, connection):
        """
        Test if GenuineCheckException is risen while initializing the card
        """
        connection.card.check_genuine.side_effect = GenuineCheckException()
        with self.assertRaises(GenuineCheckException):
            init(connection, "", "", "", "")

    def test_init_connection_exception(self, connection):
        """
        Test if ConnectionException is risen while initializing the card
        """
        connection.card.check_genuine.side_effect = None
        connection.card.session_public_key = SESSION_PUBLIC_KEY
        connection.send_apdu.side_effect = ConnectionException()
        with self.assertRaises(ConnectionException):
            init(connection, "", "", "", "")

    def test_sign(self, connection):
        """
        Test if sign function works correctly
        """
        connection.send_encrypted.return_value = b""
        self.assertEqual(sign(connection, "000000000000000".encode("ascii"),
                              Derivation.CURRENT_KEY), b"")

    def test_sign_derivation_exception(self, connection):
        """
        Test if DerivationSelectionException is risen while executing sign
        function
        """
        connection.send_encrypted.return_value = b""
        with self.assertRaises(DerivationSelectionException):
            sign(connection, "000000000000000".encode("ascii"), 4)

    def test_sign_data_exception(self, connection):
        """
        Test if DataException is risen while executing sign function
        """
        bytes_to_return = [bytes.fromhex('ff') for _ in range(0, 80)]
        bytes_to_return[70] = bytes.fromhex('30')
        connection.send_encrypted.return_value = bytes_to_return
        with self.assertRaises(DataException):
            sign(connection, "000000000000000".encode("ascii"),
                 Derivation.CURRENT_KEY)

    def test_unblock_pin(self, connection):
        """
        Test if unblock_pin function works correctly
        """
        # pylint: disable=no-self-use
        test_puk = "000000000000000"
        test_new_pin = "1234"
        test_new_pin = test_new_pin + ("\0" * (9 - len(test_new_pin)))
        unblock_pin(connection, test_puk, test_new_pin)
        connection.send_encrypted.assert_called_with(
            [0x80, 0x22, 0x00, 0x00],
            bytes(test_puk, 'ascii')
            + bytes(test_new_pin, 'ascii'))

    @mock.patch("cryptnoxpy.connection.Card")
    def test_get_cards_info(self, card, connection):
        """
        Test if get_cards_info function works correctly
        """
        type(card).info = mock.PropertyMock(side_effect=CARD_INFO)
        connection.card = card
        connection.__enter__.return_value = connection
        connection.side_effect = [connection, CardTypeException, CardException,
                                  connection,
                                  ReaderException]
        cards = get_cards_info()
        self.assertEqual(cards, CARD_INFO)

    @mock.patch("cryptnoxpy.connection.Card")
    def test_get_card_index(self, card, connection):
        """
        Test if get_card_index function works correctly when serial number is
        given as parameter
        """
        type(card).info = mock.PropertyMock(side_effect=CARD_INFO)
        type(card).serial_number = mock.PropertyMock(
            side_effect=[card["serial_number"] for card in CARD_INFO])
        connection.card = card
        connection.__enter__.return_value = connection
        connection.side_effect = [connection, CardTypeException, CardException,
                                  connection,
                                  ReaderException]
        self.assertEqual(3, get_card_index(8688321800324536269))

    @mock.patch("cryptnoxpy.connection.Card")
    def test_get_card_index_first_index(self, card, connection):
        """
       Test if get_card_index function works correctly when serial number is
       not given as parameter
       """
        type(card).info = mock.PropertyMock(side_effect=CARD_INFO)
        type(card).serial_number = mock.PropertyMock(
            side_effect=[card["serial_number"] for card in CARD_INFO])
        connection.card = card
        connection.__enter__.return_value = connection
        connection.side_effect = [CardTypeException, connection, CardException,
                                  connection,
                                  ReaderException]
        self.assertEqual(1, get_card_index())

    @mock.patch("cryptnoxpy.connection.Card")
    def test_get_card_index_card_exception(self, card, connection):
        """
       Test if get_card_index function raises CardException when no readers with
       Cryptnox cards are detected
       """
        type(card).info = mock.PropertyMock(side_effect=CARD_INFO)
        type(card).serial_number = mock.PropertyMock(
            side_effect=[card["serial_number"] for card in CARD_INFO])
        connection.card = card
        connection.__enter__.return_value = connection
        connection.side_effect = [CardTypeException, CardException,
                                  ReaderException]
        with self.assertRaises(CardException):
            get_card_index()

    @mock.patch("cryptnoxpy.connection.Card")
    def test_get_card_index_value_error(self, card, connection):
        """
       Test if get_card_index function raises ValueError when there is no card
       with given serial number
       """
        type(card).info = mock.PropertyMock(side_effect=CARD_INFO)
        type(card).serial_number = mock.PropertyMock(
            side_effect=[card["serial_number"] for card in CARD_INFO])
        connection.card = card
        connection.__enter__.return_value = connection
        connection.side_effect = [CardTypeException, connection, CardException,
                                  connection,
                                  ReaderException]
        with self.assertRaises(ValueError):
            get_card_index(123)

    def test_reset(self, connection):
        """
        Test if reset is working correctly
        """
        # pylint: disable=no-self-use
        connection.send_encrypted.return_value = b""
        reset(connection, "000000000000000")
        connection.send_encrypted.assert_called_with(
            [128, 192, 0, 0], b"000000000000000")

    def test_change_pin(self, connection):
        """
        Test if change_pin function is working correctly
        """
        # pylint: disable=no-self-use
        connection.send_encrypted.return_value = b""
        change_pin(connection, "0000")
        connection.send_encrypted.assert_called_with(
            [128, 33, 0, 0], b"0000\x00\x00\x00\x00\x00")

    def test_change_puk(self, connection):
        """
        Test if change_puk function is working correctly
        """
        # pylint: disable=no-self-use
        connection.send_encrypted.return_value = b""
        change_puk(connection, "000000000000000", "111111111111111")
        connection.send_encrypted.assert_called_with(
            [128, 33, 1, 0], b"000000000000000111111111111111")

    # TODO: Test for get_public_key
    # TODO: Test for load_seed

