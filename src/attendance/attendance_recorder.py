from attendance.display import Display
from attendance.card_reader import CardReader


class AttendanceRecorder:

    def __init__(self, display: Display, reader: CardReader):
        self._display = display
        self._reader = reader

    def start(self):
        self._display.show()


def main():
    AttendanceRecorder(Display(), CardReader()).start()


if __name__ == "__main__":
    main()
