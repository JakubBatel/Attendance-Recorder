from .resources.config import config

from luma.core.device import device as luma_device

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

    MONOCHROMATIC: Final = '1'
    WHITE: Final = 255
    BLACK: Final = 0

    def __init__(self, device: luma_device):
        """Init class based on config."""
        font_filename: str = resource_filename(
            resources.__name__, config['Display']['font'])
        font_size: int = int(config['Display']['fontsize'])

        self.FONT: Final = ImageFont.truetype(font_filename, font_size)

        self._device: Final = device

        self._buffer: Image = Image.new(Display.MONOCHROMATIC,
                                        (self._device.width, self._device.height))

        self._buffer_draw: ImageDraw.Draw = ImageDraw.Draw(self._buffer)
        self.clear(screen_only=True)

    def clear(self, screen_only: bool = False) -> None:
        """Clear display screen and buffer.

        Args:
            screen_only: If true then buffer is not cleared.
        """
        if not screen_only:
            self._buffer_draw.rectangle(
                (0, 0, self._device.width, self._device.height), fill=Display.BLACK)
        self._device.clear()

    def _draw_text_to_buffer(self, text: str, left: int, top: int) -> None:
        self._buffer_draw.text(
            (left, top), text, font=self.FONT, fill=Display.WHITE)

    def _get_text_width(self, text: str) -> int:
        """Get width of the text in pixels for used font.

        Args:
            text: Text which width will be measured.

        Returns:
            Width of the text in pixels.
        """
        return self._buffer_draw.textsize(text, font=self.FONT)[0]

    def _get_text_height(self, text: str) -> int:
        """Get height of the text in pixels for used font.

        Args:
            text: Text which height will be measured.

        Returns:
            Height of the text in pixels.
        """
        return self._buffer_draw.textsize(text, font=self.FONT)[1]

    def show(self, fst_line: str, snd_line: str = "") -> None:
        """Display given two lines in scrolling mode (from right to left).

        Args:
            fst_line: Text which will be displayed at the first line.
            snd_line: Text which will be displayed at the second line.
        """
        # Calculate actual width of text
        text_width: int = max(
            self._get_text_width(fst_line),
            self._get_text_width(snd_line))
        # Calculate actual height of text and offset for second line
        text_height: int = self._get_text_height(fst_line)
        snd_line_offset: int = 2 * text_height

        for offset in range(0, text_width, 5):
            # Clear display
            self.clear()

            # Draw the text
            self._draw_text_to_buffer(fst_line, -offset, 0)
            self._draw_text_to_buffer(fst_line, -offset, snd_line_offset)

            # Display image
            self._device.display(self._buffer)

            sleep(0.05)

        self.clear()
