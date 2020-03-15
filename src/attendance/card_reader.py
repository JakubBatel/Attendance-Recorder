from typing import Final

from attendance.resources.config import config

import serial
import time


class CardReader:

    TRANSLATION: Final = str.maketrans('0123456789ABCDEF', '084C2A6E195D3B7F')
    INIT_BYTE: Final = b'\x02'
    CARD_SIZE: Final = 10

    def __init__(self):
        self._port = serial.Serial(
            port=config['CardReader']['devPath'],
            baudrate=int(config['CardReader']['baudrate']),
            parity=getattr(serial, config['CardReader']['parity']),
            stopbits=getattr(serial, config['CardReader']['stopbits']),
            bytesize=getattr(serial, config['CardReader']['bytesize']),
            timeout=float(config['CardReader']['timeout'])
        )

    def read_card(self) -> str:
        while True:
            byte = self._port.read()
            if byte == CardReader.INIT_BYTE:
                data = self._port.read(CardReader.CARD_SIZE)
                if len(data) != CardReader.CARD_SIZE:
                    raise ValueError
                return CardReader.reverse_endianness(data.decode('ascii'))
            time.sleep(0.5)

    @staticmethod
    def reverse_endianness(string: str) -> str:
        return string.translate(CardReader.TRANSLATION)
