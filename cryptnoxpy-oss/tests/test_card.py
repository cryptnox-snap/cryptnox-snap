# -*- coding: utf-8 -*-
"""
Module for unit testing card class
"""
from copy import deepcopy
from unittest import mock, TestCase
from unittest.mock import call

from cryptnoxpy.card import Card

from cryptnoxpy import DataException, CardTypeException, DataValidationException

valid_apdu_request = {
    "info": [0, 164, 4, 0, 7, 160, 0, 0, 16, 0, 1, 1],
    "certificate_one": [128, 247, 0, 0, 0],
    "certificate_two": [128, 247, 0, 1, 0],
    "init": [128, 254, 0, 0, 1, 1]
}
valid_apdu_response = {
    "info": ([66, 0, 9, 2, 7, 145, 126, 108, 217, 101,
              192, 252, 15, 212, 96, 13, 251, 195, 154,
              10, 139, 90, 0, 189, 85, 98, 5, 96, 109, 17,
              17, 112, 95, 196, 25, 161], 144, 0),
    "certificate_one":
        ([1, 30, 48, 130, 1, 26, 48, 129, 193, 160, 3, 2, 1, 2, 2, 9, 0,
          206, 33, 238, 10, 10, 210, 131, 221, 48, 10, 6, 8, 42, 134, 72,
          206, 61, 4, 3, 2, 48, 19, 49, 17, 48, 15, 6, 3, 85, 4, 3, 19, 8,
          67, 114, 121, 112, 116, 110, 111, 120, 48, 30, 23, 13, 50, 49,
          48, 49, 49, 51, 49, 50, 53, 57, 50, 51, 90, 23, 13, 50, 52, 49,
          50, 51, 49, 50, 51, 53, 57, 53, 57, 90, 48, 19, 49, 17, 48, 15,
          6, 3, 85, 4, 3, 19, 8, 67, 114, 121, 112, 116, 110, 111, 120,
          48, 89, 48, 19, 6, 7, 42, 134, 72, 206, 61, 2, 1, 6, 8, 42, 134,
          72, 206, 61, 3, 1, 7, 3, 66, 0, 4, 190, 189, 160, 153, 2, 134,
          219, 95, 11, 241, 216, 135, 236, 149, 84, 74, 216, 143, 132,
          158, 8, 71, 107, 228, 156, 184, 15, 237, 139, 187, 25, 210, 182,
          134, 159, 162, 99, 161, 249, 31, 247, 241, 131, 229, 214, 178,
          145, 127, 92, 254, 43, 44, 237, 158, 75, 94, 120, 129, 108, 88,
          201, 139, 21, 191, 48, 10, 6, 8, 42, 134, 72, 206, 61, 4, 3, 2,
          3, 72, 0, 48, 69, 2, 32, 75, 32, 16, 155, 141, 11, 13, 10, 82,
          210, 2, 228, 136, 134, 34, 86, 186, 252, 219, 84, 181, 185, 69,
          218, 198, 76, 105, 180, 128, 53, 90, 28, 2, 33], 144, 0),
    "certificate_two":
        ([0, 130, 61, 147, 8, 171, 162, 74, 49, 71, 4, 16, 242, 75, 223,
          42, 9, 10, 40, 149, 139, 121, 84, 36, 210, 193, 156, 45, 103,
          119, 69, 187, 72], 144, 0),
    "init": ([], 109, 0)

}


@mock.patch("cryptnoxpy.connection.Connection")
class TestCard(TestCase):
    """
    Class used for testing card.
    """
    def test_card(self, connection):
        """
        Checks if instance of Card class is initialized correctly.
        """
        # pylint: disable=no-self-use
        connection.send_apdu.side_effect = \
            [valid_apdu_response[response] for response in valid_apdu_response]
        Card(connection, False)
        calls = [call(valid_apdu_request[request])
                 for request in valid_apdu_request]
        connection.send_apdu.assert_has_calls(calls)

    def test_card_initialized(self, connection):
        """
        Tests if card is initialized.
        """
        connection.send_apdu.side_effect = \
            [valid_apdu_response["info"],
             valid_apdu_response["certificate_one"],
             valid_apdu_response["certificate_two"],
             ([], 109, 0)
             ]
        card = Card(connection, False)
        self.assertEqual(True, card.initialized)

    def test_card_not_answering(self, connection):
        """
        Tests if card is not returning data.
        """
        connection.send_apdu.return_value = ([], 144, 0)
        with self.assertRaises(DataException):
            Card(connection, False)

    def test_card_wrong_card_type(self, connection):
        """
        Tests if card is of wrong type.
        """
        wrong_card = deepcopy(valid_apdu_response["info"])
        wrong_card[0][0] = 67
        connection.send_apdu.return_value = wrong_card
        with self.assertRaises(CardTypeException):
            Card(connection, False)

    def test_card_wrong_certificate_response(self, connection):
        """
        Tests if card can't get certificate.
        """
        connection.send_apdu.return_value = valid_apdu_response["info"]
        with self.assertRaises(AssertionError):
            Card(connection, False)

    def test_card_wrong_certificate_response_length(self, connection):
        """
        Tests if certificate is of wrong length.
        """
        wrong_card = deepcopy(valid_apdu_response["certificate_two"])
        del wrong_card[0][15]
        connection.send_apdu.side_effect = \
            [valid_apdu_response["info"],
             wrong_card,
             valid_apdu_response["certificate_two"]
             ]
        with self.assertRaises(AssertionError):
            Card(connection, False)

    def test_card_not_initialized(self, connection):
        """
        Tests if card is not initialized.
        """
        connection.send_apdu.side_effect = \
            [valid_apdu_response["info"],
             valid_apdu_response["certificate_one"],
             valid_apdu_response["certificate_two"],
             DataValidationException
             ]
        card = Card(connection, False)
        self.assertEqual(False, card.initialized)

    def test_card_not_initialized_wrong_response(self, connection):
        """
        Tests if card is not initialized.
        """
        connection.send_apdu.side_effect = \
            [valid_apdu_response["info"],
             valid_apdu_response["certificate_one"],
             valid_apdu_response["certificate_two"],
             ([], 1, 3)
             ]
        card = Card(connection, False)
        self.assertEqual(False, card.initialized)

