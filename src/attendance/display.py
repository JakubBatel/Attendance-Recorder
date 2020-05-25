from .resources.config import config

from abc import ABC
from luma.core.device import device as luma_device
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from pkg_resources import resource_filename
from time import sleep
from multiprocessing import Process
from typing import Final
from typing import Optional
from typing import Tuple


class IDisplay(ABC):
    """Interface for a display which can show two messages at once."""

    def clear(self) -> None:
        """Clear the display."""
        pass

    def show(self, msga: str, msgb: str = '') -> None:
        """Display given two messages where the second one is optional.

        Args:
            msga: Text which will be displayed at the first line.
            msgb: Text which will be displayed at the second line.
        """
        pass


class OLEDdisplay(IDisplay):
    """Class for work with OLED display from luma library.

    The display can be configured using the config.ini file in resources folder.
    """

    MONOCHROMATIC: Final = '1'
    WHITE: Final = 255
    BLACK: Final = 0

    def __init__(self, device: luma_device):
        """Init class based on config."""
        font_filename: str = resource_filename(
            'attendance.resources', config['Display']['font'])
        font_size: int = int(config['Display']['fontsize'])

        self.FONT: Final = ImageFont.truetype(font_filename, font_size)

        self._device: Final = device

        self._buffer: Image = Image.new(OLEDdisplay.MONOCHROMATIC,
                                        (self._device.width, self._device.height))

        self._buffer_draw: ImageDraw.Draw = ImageDraw.Draw(self._buffer)
        self._process: Optional[Process] = None
        self._previous_args: Optional[Tuple[str, str]] = None
        self.clear(buffer_only=False)

    def clear(self, buffer_only: bool = True) -> None:
        """Clear display screen and buffer.

        Args:
            buffer_only: If true then only buffer is cleared (faster clean).
        """
        self._buffer_draw.rectangle(
            (0, 0, self._device.width, self._device.height), fill=OLEDdisplay.BLACK)
        if not buffer_only:
            self._device.clear()

    def _draw_text_to_buffer(self, text: str, left: int, top: int) -> None:
        self._buffer_draw.text(
            (left, top), text, font=self.FONT, fill=OLEDdisplay.WHITE)

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

    def _show(self, msga: str, msgb: str) -> None:
        """Display given two lines in scrolling mode (from right to left).

        Args:
            msga: Text which will be displayed at the first line.
            msgb: Text which will be displayed at the second line.
        """
        # Calculate actual width of text
        text_width: int = max(
            self._get_text_width(msga),
            self._get_text_width(msgb))
        # Calculate actual height of text and offset for second line
        text_height: int = self._get_text_height(msga)
        snd_line_offset: int = 2 * text_height
        second_offset: int = max(text_width, self._device.width) + 10

        while True:
            for offset in range(0, text_width, 10):
                # Clear display
                self.clear()

                # Draw the text
                self._draw_text_to_buffer(msga, -offset, 0)
                self._draw_text_to_buffer(msgb, -offset, snd_line_offset)

                self._draw_text_to_buffer(msga, second_offset - offset, 0)
                self._draw_text_to_buffer(
                    msgb, second_offset - offset, snd_line_offset)

                # Display image
                self._device.display(self._buffer)

                sleep(0.05)

    def show(self, msga: str, msgb: str = '') -> None:
        """Display given two lines in scrolling mode (from right to left).

        The process is run in parallel so is non blocking operation.

        Args:
            msga: Text which will be displayed at the first line.
            msgb: Text which will be displayed at the second line.
        """
        if self._previous_args is not None and self._previous_args == (msga, msgb):
            return

        if self._process is not None:
            self._process.terminate()

        self._previous_args = (msga, msgb)
        self._process = Process(target=self._show, args=(msga, msgb))
        self._process.start()
