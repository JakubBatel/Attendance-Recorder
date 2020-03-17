from attendance.api_connection import ISConnection
from attendance.card_reader import CardReader
from attendance.display import Display


class AttendanceRecorder:

    def __init__(self, display: Display, reader: CardReader):
        self._display = display
        self._reader = reader
        self._connection = ISConnection()

    def start(self):
        self._display.show()
        with self._connection as connection:
            pass


if __name__ == "__main__":
    AttendanceRecorder(Display(), CardReader()).start()
