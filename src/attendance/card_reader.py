from attendance.resources.config import config
from attendance.utils import reverse_endianness

from logging import getLogger
from logging import Logger
from time import sleep
from typing import Final

import re
import serial


class CardReaderException(Exception):

    def __init__(self, message):
        super().__init__(message)


class CardReader:

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
        self.logger: Logger = getLogger(__name__)
        self._port = serial.Serial(
            port=CardReader.PORT,
            baudrate=CardReader.BAUDRATE,
            parity=CardReader.PARITY,
            stopbits=CardReader.STOPBITS,
            bytesize=CardReader.BYTESIZE,
            timeout=CardReader.TIMEOUT
        )

    def read_card(self) -> str:
        while True:
            byte = self._port.read()
            if byte != CardReader.INIT_BYTE:
                sleep(0.5)
                continue
            data = self._port.read(CardReader.CARD_SIZE)
            card: str = reverse_endianness(data.decode('ascii'))
            if not CardReader.CARD_REGEX.match(card):
                raise CardReaderException('Card data are invalid.')
            return card
