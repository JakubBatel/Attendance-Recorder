from .resources.config import config

from abc import ABC
from abc import abstractmethod
from logging import getLogger
from logging import Logger
from time import sleep
from typing import Final

import RPi.GPIO as GPIO


class IBuzzer(ABC):
    """Buzzer interface with buzz method.

    It can produce two different sounds for correct and incorrect signalization.
    """

    @abstractmethod
    def buzz(self, correct: bool) -> None:
        """Make sound based on input value.

        Args:
            correct: if true sound for correct input is made, for incorrect otherwise.
        """
        pass


class Buzzer(IBuzzer):
    """Buzzer interface implementation.

    It works with a physical buzzer connected to the GPIO pin.
    The pin can be configured using the config.ini located at the resources folder.
    """

    def __init__(self):
        """Initialize class and read pin from config then set it to be an output pin."""
        self.logger: Logger = getLogger(__name__)
        self._pin: Final = int(config['Buzzer']['pin'])

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self._pin, GPIO.OUT)
        self.logger('{0} pin set as output pin.'.format(self._pin))

    def buzz(self, correct: bool) -> None:
        """Make sound based on input value.

        Single beep for correct and double beep for incorrect.

        Args:
            correct: if true sound for correct input is made, for incorrect otherwise.
        """
        if correct:
            self.logger.debug('Making correct sound response.')
            for _ in range(300):
                GPIO.output(self._pin, GPIO.HIGH)
                GPIO.output(self._pin, GPIO.LOW)
                sleep(0.00075)
        else:
            self.logger.debug('Making incorrect sound response.')
            for _ in range(2):
                for __ in range(1000):
                    GPIO.output(self._pin, GPIO.HIGH)
                    GPIO.output(self._pin, GPIO.LOW)
                    sleep(0.00025)
                sleep(0.3)
