from attendance.resources.config import config
from attendance.utils import reverse_endianness

from time import sleep
from typing import Final

import serial


class CardReader:

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
                return reverse_endianness(data.decode('ascii'))
            sleep(0.5)
