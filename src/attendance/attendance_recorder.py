from attendance.api_connection import ISConnection
from attendance.api_connection import ISConnectionException
from attendance.card_reader import CardReader
from attendance.display import Display
from attendance.utils import get_mac_address


class AttendanceRecorder:

    def __init__(self, display: Display, reader: CardReader):
        self._display = display
        self._reader = reader
        self._connection = ISConnection(get_mac_address())

    def start(self):
        self._display.show()
        try:
            result = self._connection.send_data
        except ISConnectionException:
            pass


if __name__ == "__main__":
    AttendanceRecorder(Display(), CardReader()).start()
