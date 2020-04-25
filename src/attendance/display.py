from attendance.resources.config import config

from adafruit_ssd1306 import SSD1306_I2C
from board import D4
from board import I2C
from digitalio import DigitalInOut
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from pkg_resources import resource_filename
from time import sleep
from typing import Final

import resources


class Display:
    """Class for work with OLED display (SSD1306).

    It works with physical display using I2C communication and Adafruit SSD1306 library.
    It is configured using config file (config.ini in resources folder).
    """

    WIDTH: Final = config['Display']['width']
    HEIGHT: Final = config['Display']['height']
    ADDRESS: Final = 0x3c
    RESET_PIN: Final = DigitalInOut(D4)
    MONOCHROMATIC: Final = '1'
    WHITE: Final = 255
    BLACK: Final = 0

    def __init__(self):
        """Init class based on config."""
        font_filename: str = resource_filename(
            resources.__name__, config['Display']['font'])
        font_size: int = int(config['Display']['fontsize'])

        self.FONT: Final = ImageFont.truetype(font_filename, font_size)

        self._display: Final = SSD1306_I2C(Display.WIDTH,
                                           Display.HEIGHT,
                                           I2C(),
                                           addr=Display.ADDRESS,
                                           reset=Display.RESET_PIN)

        self._buffer: Image = Image.new(Display.MONOCHROMATIC,
                                        (Display.WIDTH, Display.HEIGHT))

        self._draw = ImageDraw.Draw(self._buffer)
        self.clear(screen_only=True)

    def clear(self, screen_only: bool = False) -> None:
        """Clear display screen and buffer.

        Args:
            screen_only: If true then buffer is not cleared.
        """
        if not screen_only:
            self._draw.rectangle(
                (0, 0, Display.WIDTH, Display.HEIGHT), fill=Display.BLACK)
        self._display.fill(Display.BLACK)
        self._display.show()

    def show(self):
        text = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        text_width = self._draw.textsize(text, font=self.FONT)[0]
        step = 5
        top = -2
        for i in range(0, -text_width, -step):

            # Clear display
            self.clear()

            # Draw the text
            self._draw.text((top + i, top), text,
                            font=self.FONT, fill=Display.WHITE)
            self._draw.text((top + i + text_width, top), text,
                            font=self.FONT, fill=Display.WHITE)

            # Display image
            self._display.image(self._buffer)
            self._display.show()

            sleep(0.05)

        sleep(1)
        self.clear()
