# -*- coding: utf-8 -*-
"""
Module for unit testing connection class
"""
from unittest import mock, TestCase

from cryptnoxpy import Connection, ReaderException, CardException, \
    ConnectionException, DataValidationException, FirmwareException, \
    PinException, PukException, SecureChannelException, KeyAlreadyGenerated


@mock.patch("cryptnoxpy.connection.reader.Reader")
@mock.patch("cryptnoxpy.connection.Card")
@mock.patch("cryptnoxpy.connection.reader.get")
class TestConnection(TestCase):
    """
    Class used for testing connection.
    """
    def test_connection_establishing(self, reader_get, card, reader):
        # pylint: disable=R0201
        """
        Tests if connection is establishing.
        """
        reader_get.return_value = reader
        with Connection() as connection:
            reader.connect.assert_called()
            card.assert_called_with(connection, False)

    def test_connection_reader_exception(self, reader_get, _1, _2):
        """
        Tests if exception is thrown when there are no readers.
        """
        reader_get.side_effect = ReaderException()
        with self.assertRaises(ReaderException):
            with Connection():
                pass

    def test_connection_card_exception(self, reader_get, _1, reader):
        """
        Tests if exception is thrown when there are no cards.
        """
        reader_get.side_effect = reader
        reader.side_effect = CardException()
        with self.assertRaises(CardException):
            with Connection():
                pass

    def test_connection_exception(self, reader_get, _1, reader):
        """
        Tests if ConnectionException is raised correctly.
        """
        reader_get.return_value = reader
        with Connection() as connection:
            reader.send.return_value = ([], 0x69, 0x82)
            with self.assertRaises(ConnectionException):
                connection.send_apdu([])

    def test_data_validation_exception(self, reader_get, _1, reader):
        """
        Tests if DataValidationException is raised correctly.
        """
        reader_get.return_value = reader
        with Connection() as connection:
            reader.send.return_value = ([], 0x6A, 0x80)
            with self.assertRaises(DataValidationException):
                connection.send_apdu([])

    def test_firmware_exception(self, reader_get, _1, reader):
        """
        Tests if FirmwareException is raised correctly.
        """
        reader_get.return_value = reader
        with Connection() as connection:
            reader.send.return_value = ([], 0x6A, 0x82)
            with self.assertRaises(FirmwareException):
                connection.send_apdu([])

    def test_pin_exception(self, reader_get, _1, reader):
        """
        Tests if PinException is raised correctly.
        """
        reader_get.return_value = reader
        with Connection() as connection:
            reader.send.return_value = ([], 0x63, 0xC0)
            with self.assertRaises(PinException):
                connection.send_apdu([])

    def test_puk_exception(self, reader_get, _1, reader):
        """
        Tests if PinException is raised correctly.
        """
        reader_get.return_value = reader
        with Connection() as connection:
            reader.send.return_value = ([], 0x98, 0x40)
            with self.assertRaises(PukException):
                connection.send_apdu([])

    def test_secure_channel_exception(self, reader_get, _1, reader):
        """
        Tests if SecureChannelException is raised correctly.
        """
        reader_get.return_value = reader
        with Connection() as connection:
            reader.send.return_value = ([], 0x69, 0x85)
            with self.assertRaises(SecureChannelException):
                connection.send_apdu([])

    def test_key_already_generated(self, reader_get, _1, reader):
        """
        Tests if KeyAlreadyGenerated is raised accordingly.
        """
        reader_get.return_value = reader
        with Connection() as connection:
            reader.send.return_value = ([], 0x69, 0x86)
            with self.assertRaises(KeyAlreadyGenerated):
                connection.send_apdu([])

