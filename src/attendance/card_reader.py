from typing import Final

import serial
import time


class CardReader:

    TRANSLATION: Final = str.maketrans('0123456789ABCDEF', '084C2A6E195D3B7F')
    INIT_BYTE: Final = b'\x02'
    CARD_SIZE: Final = 10

    def __init__(self):
        self._port = serial.Serial(
            port='/dev/ttyAMA0',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0.5
        )

    def read_card(self):
        while True:
            byte = self._port.read()
            if byte == CardReader.INIT_BYTE:
                data = self._port.read(CardReader.CARD_SIZE)
                if len(data) != CardReader.CARD_SIZE:
                    raise ValueError
                return CardReader.reverse_endianness(data.decode('ascii'))
            time.sleep(1)

    @staticmethod
    def reverse_endianness(string: str):
        return string.translate(CardReader.TRANSLATION)
