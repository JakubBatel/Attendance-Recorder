# Attendance recorder

Application which records attendance using RFID cards and Raspberry Pi Zero W.
The device reads ISICs and send them to the Information System of the Masaryk University.
The application is part of the Bachelor thesis written at Masaryk University.

## Installation

### Clone repository

```
$ git clone https://github.com/JakubBatel/Attendance-Recorder.git
```

### Configuration

Application can be configured using ```src/attendance/resources/config.ini```

### Install application

```
$ cd Attendance-Recorder
# make all
```

This command will build code, setup environment and install linux service which can be enabled

```
# systemctl enable attendance-recoreder.service
```

Application can be run using

```
$ attendance_recorder
```

### Tests

To run tests of the connection the Flask will be installed.

Run tests with

```
$ make test
```

## 3D print case

Part of the thesis is also a model which can be 3D printed. All the required files are located at ```model``` folder


## Used libraries

For work with the display (SH1106) the [luma](https://luma-oled.readthedocs.io/en/latest/intro.html) and [Pillow](https://pillow.readthedocs.io/en/stable/) is used.

For work with the card reader (RDM6300) the [pyserial](https://pyserial.readthedocs.io/en/latest/pyserial.html) is used.

Data are sent to the REST API using [requests](https://requests.readthedocs.io/en/master/) library.

