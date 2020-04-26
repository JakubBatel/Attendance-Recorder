from attendance.api_connection import ISConnection
from attendance.api_connection import ISConnectionBuilder
from attendance.api_connection import ISConnectionException
from attendance.card_reader import CardReader
from attendance.card_reader import CardReaderException
from attendance.display import Display
from attendance.resources.config import config
from attendance.utils import create_cache_folder
from attendance.utils import get_cache_file_path
from attendance.utils import get_mac_address

from logging import getLogger
from logging import Logger
from time import sleep
from typing import Any
from typing import Dict
from typing import Final
from typing import Set

import re


class AttendanceRecorder:
    """Attendance recorder application.

    Contains everything needed to read cards and send data to IS MUNI.
    Red cards are saved to cached file until they are successfuly send.
    """

    CARD_REGEX: Final = re.compile('^[0-9A-F]{10}$')

    def __init__(self,
                 display: Display,
                 reader: CardReader,
                 connection: ISConnection):
        """Inject display, card reader, connection and init cache folder file."""
        self.logger: Logger = getLogger(__name__)
        self._display: Display = display
        self._reader: CardReader = reader
        self._connection: ISConnection = connection
        self._init_cache_file()

    def _init_cache_file(self) -> None:
        create_cache_folder()
        self._cache_filename: str = get_cache_file_path()
        self._cards: Set[str] = set()
        self._load_cached_cards()

    def _load_cached_cards(self) -> None:
        with open(self._cache_filename, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                self._add_card(line.strip(), False)

    def _clear_cached_cards(self) -> None:
        """Empty cache file."""
        with open(self._cache_filename, 'w', encoding='utf-8'):
            pass  # open file in write mode to empty it
        self.logger.info('Cache file cleared.')

    def _add_card(self, card: str, cache: bool = True) -> None:
        """Add card to set of red cards.

        Args:
            card: Card to add.
            cache: If true then card will be also saved to cache file.
        """
        if AttendanceRecorder.CARD_REGEX.match(card):
            if card in self._cards:
                self.logger.debug('Card {0} already contained.'.format(card))
                return
            self._cards.add(card)
            if not cache:
                self.logger.info('Card {0} prepared to be send.'.format(card))
            else:
                with open(self._cache_filename, 'a', encoding='utf-8') as f:
                    f.write(card + '\n')
                self.logger.info(
                    'Card {0} cached and prepared to be send.'.format(card))

    def _show_initial_message(self) -> None:
        while True:
            if self._connection.is_available():
                self._display.show()  # TODO
                return
            self._display.show()  # TODO
            sleep(5)

    def _show_result(self, result: Dict[str, Any]) -> None:
        pass

    def _show_connection_unavailable(self) -> None:
        pass

    def _read_cards(self) -> None:
        """Start reading cards and sending them to IS MUNI."""
        self.logger.info('Reading cards started.')
        while True:
            self._display.show()  # TODO
            try:
                card: str = self._reader.read_card()
                self._add_card(card)
            except CardReaderException:
                self._display.show()  # TODO
                continue
            try:
                result: Dict[str, Any] = self._connection.send_data(
                    list(self._cards))
                self._clear_cached_cards()
                self._show_result(result)
            except ISConnectionException:
                self._show_connection_unavailable()

    def start(self) -> None:
        self.logger.info('Attendance recoreder started.')
        self._show_initial_message()
        self._read_cards()


if __name__ == "__main__":
    builder: ISConnectionBuilder = ISConnectionBuilder()
    builder.set_mac_address(get_mac_address())
    builder.set_baseurl(config['Connection']['baseurl'])
    builder.set_url(config['Connection']['url'])
    AttendanceRecorder(Display(), CardReader(), builder.build()).start()
