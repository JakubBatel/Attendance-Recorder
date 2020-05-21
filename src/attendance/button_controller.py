from .resources.config import config

from abc import ABC
from abc import abstractmethod
from logging import getLogger
from logging import Logger
from typing import Final

import RPi.GPIO as GPIO


class IButtonController(ABC):
    """Button interface with single method is_pushed."""

    @abstractmethod
    def is_pushed(self) -> bool:
        """Check if the button is pushed or not.

        Returns:
            True if the button is pushed.
        """
        pass


class ButtonController(IButtonController):
    """Button interface implementation which works with physical button."""

    def __init__(self):
        """Initialize class and setup the pins.

        Pins can be specified in config.ini located at resources folder.
        """
        self.logger: Logger = getLogger(__name__)
        self._pin: Final = int(config['Button']['in_pin'])

        out_pin: int = int(config['Button']['out_pin'])
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self._pin, GPIO.IN)
        GPIO.setup(out_pin, GPIO.OUT)
        GPIO.output(out_pin, GPIO.HIGH)

    def is_pushed(self) -> bool:
        """Check if the button is pushed or not.

        Returns:
            True if the button is pushed.
        """
        if GPIO.input(self._pin) == GPIO.HIGH:
            self.logger.debug('Button was pushed.')
            return True
        return False
