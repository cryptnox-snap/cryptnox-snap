"""
This is the module for continuous testing the cards functionality and logging potential error
It's running in multithreading - each card one thread
"""

import concurrent.futures
import logging
import os
import random
import re
import string
import sys
import time
from contextlib import ExitStack
from logging.handlers import TimedRotatingFileHandler
from typing import List

from appdirs import user_data_dir
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

import cryptnoxpy

LOG_DIR = CURRENT_DIR if os.access(CURRENT_DIR, os.W_OK) else \
    user_data_dir("cryptnox_card_tester")

FORCE_EXIT = False
LOOPS = {}

_PIN_CODE = "0" * 9
_PUK_CODE = "0" * 15


class LevelFilter(logging.Filter):
    """
    Filters messages bellow level Error (>= 40)
    """

    def filter(self, record):
        return record.levelno < logging.ERROR


def card_initialization(connection: cryptnoxpy.Connection) -> None:
    """
    Initialize the card

    :param Connection connection: Connection on which will card be initialized
    """
    cryptnoxpy.init(connection, "Test", "test@test.com", _PIN_CODE, _PUK_CODE)


def seed_initialization(connection: cryptnoxpy.Connection) -> None:
    """
    Generate and load the seed

    :param Connection connection: Connection on which will card be initialized
    """
    cryptnoxpy.check_pin(connection, "0" * 9)

    cryptnoxpy.generate_seed(connection)


def run_init(card_serial: int) -> None:
    """
    Check if card is initialized and if not call initialization

    :param int card_serial: serial number of card which needs to be initialized
    """
    index = cryptnoxpy.get_card_index(card_serial)

    try:
        with cryptnoxpy.Connection(index) as conn:
            cryptnoxpy.check_init(conn)
    except cryptnoxpy.InitializationException:
        with cryptnoxpy.Connection(index) as conn:
            card_initialization(conn)
        with cryptnoxpy.Connection(index) as conn:
            seed_initialization(conn)


def generate_message() -> bytes:
    """
    Generate random 32 char message

    :return: 32 byte long message
    :rtype: bytes
    """
    letters = string.ascii_lowercase
    return bytes("".join(random.choice(letters) for _ in range(32)), "ascii")


def encrypt_message(message: bytes) -> bytes:
    """
    Encrypt message with SHA256 algorithm

    :param bytes message: Message in bytes which will be encrypted

    :return: Encrypted message in bytes
    :rtype: bytes
    """
    digest = hashes.Hash(hashes.SHA256())
    digest.update(message)
    return digest.finalize()


def log_error(logger: logging.Logger, error: Exception) -> None:
    """
    Logs error in two files and sleeps for 5 seconds

    :param Logger logger: Logger to which message will be logged
    :param Exception error: Error which will be logged to logger
    """
    logger.exception(error)

    LOOPS[int(logger.name)]["error"] += 1
    logger.info(f"Finished loop {LOOPS[int(logger.name)]['error']} "
                f"with error: {error}")
    time.sleep(5)


def get_log_files(card_serial) -> List[str]:
    """
    Gives list of log files for given card ordered desc

    :param card_serial: Serial number of card for which log files are needed

    :return: List of log files
    :rtype: List[str]
    """
    file_list = []

    for file in os.listdir(LOG_DIR + f"/Card_{card_serial}"):
        if file.startswith("log_debug"):
            file_list.append(file)

    file_list.pop(0)

    return file_list[::-1]


def get_last_row_num(card_serial, log_type: str) -> int:
    """
    Checks in log files for last successful row number for given card

    :param card_serial: Serial number of card for which last row number will be
                        returned
    :param log_type: string success/error

    :return: Index of last successful/error row
    """
    all_logs = get_log_files(card_serial)

    # add current log to top of the list
    all_logs.insert(0, "log_debug")

    for log in all_logs:
        try:
            log_file = open(LOG_DIR + f"/Card_{card_serial}/{log}", "rb")
        except IOError:
            break

        with log_file:
            for line in reversed(log_file.readlines()):
                regex = re.search(f"loop (.*) with {log_type}", line.decode())
                if regex:
                    return int(regex[1])
    return 0


def init_log(card_serial) -> logging.Logger:
    """
    Initializes logger with two file handlers

    One handler has messages bellow Error level (<40)
    Other has messages Error level and above (>=40)

    :param card_serial: Card for which log will be initialized

    :return: Logger for usage
    :rtype: Logger
    """
    os.makedirs(LOG_DIR + f"/Card_{card_serial}", exist_ok=True)

    logs = logging.getLogger(str(card_serial))
    logs.setLevel(logging.DEBUG)

    log_format = "%(levelname)s %(asctime)s %(message)s @ P: %(process)d " \
                 "T:%(thread)d"

    debug_handler = TimedRotatingFileHandler(
        f"{LOG_DIR}/Card_{card_serial}/log_debug",
        when="midnight", backupCount=30)
    debug_handler.formatter = logging.Formatter(log_format)
    debug_handler.addFilter(LevelFilter())

    error_handler = TimedRotatingFileHandler(
        f"{LOG_DIR}/Card_{card_serial}/log_error",
        when="midnight", backupCount=30)
    error_handler.formatter = logging.Formatter(log_format)
    error_handler.setLevel(logging.ERROR)

    logs.addHandler(debug_handler)
    logs.addHandler(error_handler)

    return logs


def card_actions(connection: cryptnoxpy.Connection,
                 logs: logging.Logger) -> None:
    """
    Do planed actions on the given card.

    :param Connection connection: Connection on which actions will be performed
    :param Logger logs: main logger
    """
    paths = ["m/44'/60'/0'/0", "m/44'/0'/0'/0", "m/44'/194'/0'/0"]

    success_loops = LOOPS[connection.card.serial_number]['success']
    current_key = cryptnoxpy.Derivation.DERIVE if success_loops % 5 == 0 \
        else cryptnoxpy.Derivation.CURRENT_KEY

    try:
        path = random.choice(list(paths))
    except Exception as error:
        log_error(logs, error)
        return

    try:
        cryptnoxpy.operation.check_pin(connection, "0" * 9)
    except Exception as error:
        log_error(logs, error)
        return

    try:
        public_key = cryptnoxpy.get_public_key(connection=connection,
                                               derivation=current_key,
                                               path=path)
    except Exception as error:
        log_error(logs, error)
        return

    try:
        public_key = ec.EllipticCurvePublicKey.from_encoded_point(
            ec.SECP256K1(), bytes.fromhex(public_key))
    except Exception as error:
        log_error(logs, error)
        return

    message = generate_message()
    message_hash = encrypt_message(message)

    try:
        signature = cryptnoxpy.operation.sign(connection=connection,
                                              sign_hash=message_hash,
                                              derivation=current_key,
                                              path=path)
    except Exception as error:
        log_error(logs, error)
        return

    # verify signature
    try:
        public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
    except InvalidSignature as error:
        log_error(logs, error)
        return

    LOOPS[connection.card.serial_number]["success"] += 1
    logs.info(f"Finished loop {success_loops + 1} with success (Path {path})")


def print_dict() -> None:
    """
    Prints dictionary with data to terminal
    """
    printout = []
    for elem in LOOPS:
        percentage = "{:6.2f}".format(100 - (LOOPS[elem]["error"] * 100 / LOOPS[elem]["success"]))
        LOOPS[elem]["success-rate"] = str(percentage) + "%"
        printout.append(f"{elem} = success: {LOOPS[elem]['success']:,}; "
                        f"error: {LOOPS[elem]['error']:,}; "
                        f"success-rate: {percentage}%")
    print("\r" + "; ".join(printout), end="")

    time.sleep(1)


def test_card(card_serial: int, index: int) -> None:
    """
    Main function for testing the card

    :param int card_serial: serial number of card which is testing
    :param int index: index of card in reader
    """
    logs = init_log(card_serial)

    LOOPS[card_serial] = {
        "success": get_last_row_num(card_serial, "success"),
        "error": get_last_row_num(card_serial, "error")
    }

    while not FORCE_EXIT:
        with ExitStack() as stack:
            try:
                connection = stack.enter_context(cryptnoxpy.Connection(index))
            except (cryptnoxpy.ReaderException,
                    cryptnoxpy.CardException,
                    Exception) as error:
                log_error(logs, error)
            else:
                try:
                    card_actions(connection=connection, logs=logs)
                except Exception as error:
                    log_error(logs, error)


if __name__ == "__main__":
    cards = cryptnoxpy.get_cards_info()
    for card in cards:
        run_init(card["serial_number"])
    with ExitStack() as stack:
        try:
            executor = stack.enter_context(
                concurrent.futures.ThreadPoolExecutor(max_workers=len(cards)))
        except ValueError:
            print("No cards have been detected")
            input("Press enter to exit application")
        else:
            futures = []
            for card in cards:
                card_index = cryptnoxpy.get_card_index(card["serial_number"])
                futures.append(executor.submit(test_card,
                                               card["serial_number"],
                                               card_index))

            _, not_done = concurrent.futures.wait(futures, timeout=0)

            time.sleep(5)
            try:
                while not_done:
                    print_dict()
            except KeyboardInterrupt:
                FORCE_EXIT = True
