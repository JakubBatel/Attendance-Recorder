from PIL import Image, ImageDraw, ImageFont
from pkg_resources import resource_filename
from typing import Final

from attendance.resources.config import config

import adafruit_ssd1306 as adafruit
import board
import digitalio
import time
import resources


class Display:

    WIDTH: Final = config['Display']['width']
    HEIGHT: Final = config['Display']['height']
    ADDRESS: Final = 0x3c
    RESET_PIN: Final = digitalio.DigitalInOut(board.D4)
    MONOCHROMATIC: Final = '1'
    WHITE: Final = 255
    BLACK: Final = 0

    def __init__(self):
        font_filename: str = resource_filename(
            resources.__name__, config['Display']['font'])
        font_size: int = int(config['Display']['fontsize'])

        self.FONT: Final = ImageFont.truetype(font_filename, font_size)
        self._display: Final = adafruit.SSD1306_I2C(
            Display.WIDTH, Display.HEIGHT, board.I2C(), addr=Display.ADDRESS,
            reset=Display.RESET_PIN)

        self._buffer: Image = Image.new(
            Display.MONOCHROMATIC, (Display.WIDTH, Display.HEIGHT))
        self._draw = ImageDraw.Draw(self._buffer)
        self.clear(screen_only=True)

    def clear(self, screen_only: bool = False):
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

            time.sleep(0.05)

        time.sleep(1)
        self.clear()
