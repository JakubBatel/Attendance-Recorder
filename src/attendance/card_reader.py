from .resources.config import config
from .utils import reverse_endianness

from abc import ABC
from abc import abstractmethod
from logging import getLogger
from logging import Logger
from time import sleep
from typing import Final
from typing import Optional

import re
import serial


class ICardReader(ABC):
    """Class representation of card reader."""

    @abstractmethod
    def read_card(self, raise_if_no_data: bool = False) -> str:
        """Read one card and returns the data as a hex string.

        Args:
            raise_if_no_data: If True the NoDataException is raised if no data are present.

        Returns:
            Hex string representation of the data.

        Raises:
            NoDataException: If raise_if_no_data is set to True and no data was read.
        """
        pass


class InvalidDataException(Exception):
    """Exception used when card data are not valid."""

    def __init__(self, message):
        """Init exception with message.

        Args:
            message: Error message.
        """
        super().__init__(message)


class NoDataException(Exception):
    """Exception used when no card data was read."""

    def __init__(self, message):
        """Init exception with message.

        Args:
            message: Error message.
        """
        super().__init__(message)


class CardReader(ICardReader):
    """Class representation of physical card reader.

    It reads data from physical card reader using serial communication.
    It is configured using config file (config.ini in resources folder).
    """

    INIT_BYTE: Final = b'\x02'
    CARD_SIZE: Final = 10
    PORT: Final = config['CardReader']['devPath']
    BAUDRATE: Final = int(config['CardReader']['baudrate'])
    PARITY: Final = getattr(serial, config['CardReader']['parity'])
    STOPBITS: Final = getattr(serial, config['CardReader']['stopbits'])
    BYTESIZE: Final = getattr(serial, config['CardReader']['bytesize'])
    TIMEOUT: Final = float(config['CardReader']['timeout'])
    CARD_REGEX: Final = re.compile('^[0-9a-f]{10}$')

    def __init__(self):
        """Init logger and create new Serial object for serial communication based on configuration."""
        self.logger: Logger = getLogger(__name__)
        self._port = serial.Serial(
            port=CardReader.PORT,
            baudrate=CardReader.BAUDRATE,
            parity=CardReader.PARITY,
            stopbits=CardReader.STOPBITS,
            bytesize=CardReader.BYTESIZE,
            timeout=CardReader.TIMEOUT
        )
        self._previous_card: Optional[str] = None

    def read_card(self, raise_if_no_data: bool = False) -> str:
        """Read one card using serial communication.

        This method ends only when some data are red or until times out.
        If no card data are present operation is retried 0.5 second later. 

        Args:
            raise_if_no_data: If true the NoDataException is raised if no data are present.

        Returns:
            Hex string representation of card data.

        Raises:
            NoDataException: If raise_if_no_data is set to True and no data was read.
            InvalidDataException: If card data are corrupted.
        """
        while True:
            byte = self._port.read()

            if byte == b'':
                self.logger.debug('No card data.')
                if raise_if_no_data:
                    raise NoDataException('No card data was read.')
                else:
                    sleep(0.5)
                    continue

            if byte != CardReader.INIT_BYTE:
                raise InvalidDataException(
                    'Card data are invalid - invalid initial sequence.')

            data = self._port.read(CardReader.CARD_SIZE)
            card: str = reverse_endianness(data.decode('ascii'))

            if not CardReader.CARD_REGEX.match(card):
                raise InvalidDataException(
                    'Card data are invalid - incomplete or corrupted data.')

            self.logger.debug(card + ' was read')

            if card == self._previous_card:
                sleep(0.5)
                continue

            self._previous_card = card
            return card
