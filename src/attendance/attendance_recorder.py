from attendance.api_connection import ISConnection
from attendance.api_connection import ISConnectionException
from attendance.card_reader import CardReader
from attendance.display import Display
from attendance.resources.config import config
from attendance.utils import create_cache_folder
from attendance.utils import get_cache_file_path
from attendance.utils import get_mac_address

from logging import getLogger
from logging import Logger
from time import sleep
from typing import Final
from typing import List

import re


class AttendanceRecorder:

    CARD_REGEX: Final = re.compile('^[0-9A-F]{10}$')

    def __init__(self, display: Display, reader: CardReader):
        self.logger: Logger = getLogger(__name__)
        self._display: Display = display
        self._reader: CardReader = reader
        self._connection: ISConnection = ISConnection(get_mac_address())
        self._init_cache_file()

    def _init_cache_file(self):
        create_cache_folder()
        self._cache_filename: str = get_cache_file_path()
        self._cards: List[str] = []
        self._load_cached_cards()

    def _load_cached_cards(self) -> None:
        with open(self._cache_filename, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                self._add_card(line.strip(), False)

    def _clear_cached_cards(self) -> None:
        with open(self._cache_filename, 'w', encoding='utf-8'):
            pass  # open file in write mode to empty it

    def _add_card(self, card: str, cache: bool = True) -> None:
        if AttendanceRecorder.CARD_REGEX.match(card):
            self._cards.append(card)
            if cache:
                with open(self._cache_filename, 'a', encoding='utf-8') as f:
                    f.write(card + '\n')

    def _show_initial_message(self) -> None:
        while True:
            if self._connection.is_available():
                self._display.show()
                return
            self._display.show()
            sleep(5)

    def _show_result(self, result):
        pass

    def _show_connection_unavailable(self):
        pass

    def _read_cards(self) -> None:
        while True:
            self._display.show()
            self._add_card(self._reader.read_card())
            try:
                result = self._connection.send_data(self._cards)
                self._clear_cached_cards()
                self._show_result(result)
            except ISConnectionException:
                self._show_connection_unavailable()

    def start(self) -> None:
        self._show_initial_message()
        self._read_cards()


if __name__ == "__main__":
    AttendanceRecorder(Display(), CardReader()).start()
