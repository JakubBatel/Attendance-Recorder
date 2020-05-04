from .resources.config import config
from .utils import reverse_endianness

from logging import getLogger
from logging import Logger
from time import sleep
from typing import Final
from typing import Optional

import re
import serial


class CardReaderException(Exception):
    """Custom card reader exception."""

    def __init__(self, message):
        """Init exception with message.

        Args:
            message: Error message.
        """
        super().__init__(message)


class CardReader:
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
    CARD_REGEX: Final = re.compile('^[0-9A-F]{10}$')

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

    def read_card(self) -> str:
        """Read one card using serial communication.

        This method ends only when some data are red or until times out.
        If no card data are present operation is retried 0.5 second later. 

        Returns:
            Hex string representation of card data.

        Raises:
            CardReaderException: If card data are corrupted.
        """
        while True:
            byte = self._port.read()
            if byte != CardReader.INIT_BYTE:
                sleep(0.5)
                continue
            data = self._port.read(CardReader.CARD_SIZE)
            card: str = reverse_endianness(data.decode('ascii'))
            if not CardReader.CARD_REGEX.match(card):
                raise CardReaderException('Card data are invalid.')
            if card == self._previous_card:
                continue
            return card
