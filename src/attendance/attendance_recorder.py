from .api_connection import APIConnectionException
from .api_connection import IConnection
from .api_connection import ISConnection
from .api_connection import ISConnectionBuilder
from .button_controller import ButtonController
from .button_controller import IButtonController
from .buzzer import Buzzer
from .buzzer import IBuzzer
from .card_reader import CardReader
from .card_reader import ICardReader
from .card_reader import InvalidDataException
from .card_reader import NoDataException
from .display import IDisplay
from .display import OLEDdisplay
from .resources.config import config
from .utils import create_cache_folder
from .utils import get_cache_file_path
from .utils import get_mac_address

from luma.core.interface.serial import i2c
from luma.oled.device import sh1106

from enum import Enum
from logging import getLogger
from logging import Logger
from pathlib import Path
from time import sleep
from typing import Any
from typing import Dict
from typing import Final
from typing import Optional
from typing import Set

import json
import logging
import re


class State(Enum):
    """Enumeration of possible states of recording."""

    ONLINE = 'online'
    OFFLINE = 'offline'


class AttendanceRecorder:
    """Attendance recorder application.

    Contains everything needed to read cards and send data to IS MUNI.
    Red cards are saved to cached file until they are successfuly send.
    """

    CARD_REGEX: Final = re.compile('^[0-9A-F]{10}$')

    def __init__(self,
                 display: IDisplay,
                 reader: ICardReader,
                 connection: IConnection,
                 buzzer: IBuzzer,
                 button_controller: IButtonController):
        """Inject display, card reader, connection and init cache folder file."""
        self.logger: Logger = getLogger(__name__)
        self._display: IDisplay = display
        self._reader: ICardReader = reader
        self._connection: IConnection = connection
        self._buzzer: IBuzzer = buzzer
        self._button_controller: IButtonController = button_controller
        self._state: State = State.ONLINE
        self._init_cache_file()

    def _init_cache_file(self) -> None:
        """Initialize cache file.

        Create cache folder if doesn't exist.
        If cache file already exist loads all previously cached cards.
        """
        create_cache_folder()
        self._cache_file_path: Path = Path(get_cache_file_path())
        self._cards: Set[str] = set()
        self._load_cached_data()

    def _load_cached_data(self) -> None:
        """Load cached cards and token from cache file."""
        if not self._cache_file_path.exists():
            return
        with open(self._cache_file_path, 'r', encoding='utf-8') as json_file:
            data: Dict[str, Any] = json.load(json_file)
            if 'token' in data:
                self._connection.set_token(data['token'])
            if 'cards' in data:
                for card in data['cards']:
                    self._add_card(card, cache=False)

    def _clear_cached_cards(self) -> None:
        """Empty cache file."""
        with open(self._cache_file_path, 'w', encoding='utf-8') as f:
            f.write('{}\n')
        self.logger.debug('Cache file cleared.')

    def _add_card(self, card: str, cache: bool = True) -> None:
        """Add card to set of read cards.

        Args:
            card: Card to add.
            cache: If true then card will be also saved to cache file.
        """
        if AttendanceRecorder.CARD_REGEX.match(card):
            if card in self._cards:
                self.logger.debug('Card {0} already contained.'.format(card))
                return
            self._cards.add(card)
            if cache:
                with open(self._cache_file_path, 'w', encoding='utf-8') as json_file:
                    json.dump({
                        'token': self._connection.get_token(),
                        'cards': list(self._cards)
                    }, json_file)
                self.logger.info('Card {0} cached.'.format(card))

    def _show_initial_message(self) -> None:
        """Display the initial message and verify internet connection."""
        while True:
            if self._connection.is_available():
                self._display.show('Connection successful')
                return
            self._display.show('Connection failed!',
                               'Retry in 5 seconds ...', False)

    def _show_result(self, result: Dict[str, Any], err: bool) -> None:
        """Display the data received from API."""
        msga: str = result.get('msga', '')
        msgb: str = result.get('msgb', '')
        self._display.show(msga, msgb, False)
        self._buzzer.beep(not err)

    def _show_connection_unavailable(self, error: APIConnectionException, additional_info: str = "") -> None:
        """Display exception with optional additional info."""
        self._display.show(str(error), additional_info)

    def _signalize_invalid_card(self):
        """Signalize that the card data was invalid."""
        self.logger.debug('Invalid card read.')
        self._buzzer.beep(False)
        self._display.show('INVALID CARD!', 'please try again.', False)

    def _read_organizator_card(self) -> bool:
        """Read organizator card and send it to API with all the previously read cards.

        Returns:
            True if the card was succesfuly read and send to the API without an error response.
        """
        self.logger.debug('Reading the organizator card.')
        while not self._button_controller.is_pushed():
            self._display.show('Please push the button to start.')
            sleep(0.5)
        try:
            # Show information
            self._display.show('Ready to read an organizator card.')

            # Read card
            card: str = self._reader.read_card()

            # Send data to the API
            result: Dict[str, Any] = self._connection.send_organizator_data(
                card, list(self._cards))

            self._clear_cached_cards()

            # Set state from response
            if 'state' in result:
                self._state = State(result['state'])
            err: bool = result.get('err', '0') != '0'

            if err:
                self.logger.debug('Error received from API.')
            else:
                self.logger.debug('Received response without error.')
            self._show_result(result, err)
            return not err
        except InvalidDataException:
            self._signalize_invalid_card()
        except APIConnectionException as e:
            self._show_connection_unavailable(
                e, 'Please try again.')
        return False

    def _read_participant_card_online(self) -> None:
        """Read participant card in online mode."""
        try:
            # Show information
            self._display.show('Ready to read a card.')

            # Read card
            card: str = self._reader.read_card()

            # Send card data to API
            result: Dict[str, Any] = self._connection.send_data(
                card, list(self._cards))

            self._clear_cached_cards()

            err: bool = result.get('err', '0') != '0'
            if err:
                self.logger.debug('Error received from API.')
            else:
                self.logger.debug('Received response without error.')

            # Display results
            self._show_result(result, err)

        except InvalidDataException:
            self._signalize_invalid_card()
        except APIConnectionException as e:
            self._add_card(card)
            self._show_connection_unavailable(
                e, 'Card was saved and will be send later.')

    def _read_participant_card_offline(self) -> None:
        """Read participant card in offline mode."""
        try:
            self._display.show('Ready to read a card.')
            card: str = self._reader.read_card(True)
            self._add_card(card)
            self._display.show('Card read successfully.', can_be_killed=False)
            self._buzzer.beep(True)
        except InvalidDataException:
            self._signalize_invalid_card()
        except NoDataException:
            return

    def _send_offline_data(self) -> None:
        """Send all the cached card IDs."""
        while True:
            try:
                self._connection.send_cached_data_only(list(self._cards))
                self._clear_cached_cards()
                self._display.show('Cached card IDs succesfully sent.',
                                   can_be_killed=False)
                break
            except APIConnectionException as e:
                self._display.show(
                    str(e), 'Going to try again after 5 seconds.')
                sleep(5)

    def _read_participant_card(self) -> None:
        """Read participant card based on mode (online/offline)."""
        self.logger.debug('Reading the participant card.')
        if self._state == State.ONLINE:
            self._read_participant_card_online()

        elif self._state == State.OFFLINE:
            if self._button_controller.is_pushed():
                self._send_offline_data()
            else:
                self._read_participant_card_offline()

    def _record_cards(self) -> None:
        """Start reading cards and sending them to IS MUNI."""
        self.logger.info('Reading cards started.')
        reading_organizator_card: bool = True
        while True:
            if reading_organizator_card:
                reading_organizator_card = not self._read_organizator_card()
            else:
                self._read_participant_card()

    def start(self) -> None:
        """Start recording attendance."""
        self.logger.info('Attendance recording started.')
        self._show_initial_message()
        self._record_cards()


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s -- %(name)s %(levelname)s - %(message)s')

    connection_builder: ISConnectionBuilder = ISConnectionBuilder()
    connection_builder.set_mac_address(get_mac_address())
    connection_builder.set_baseurl(config['Connection']['baseurl'])
    connection_builder.set_url(config['Connection']['url'])

    AttendanceRecorder(OLEDdisplay(sh1106(i2c())),
                       CardReader(),
                       connection_builder.build(),
                       Buzzer(),
                       ButtonController()).start()


if __name__ == '__main__':
    main()
