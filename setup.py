from os import path
from setuptools import find_packages
from setuptools import setup


def read(fname):
    return open(path.join(path.dirname(__file__), fname)).read()


setup(
    name="attendance",
    package_dir={"": "src"},
    packages=find_packages("src"),
    install_requires=["pyserial", "Pillow",
                      "adafruit-circuitpython-ssd1306", "requests"],
    entry_points={
        "console_scripts": [
            "attendance_recorder = attendance.attendance_recorder:main"
        ]
    },
    package_data={
        "attendance.resources": ["*.ttf", "*.ini"]
    },
    version="0.0.1",
    author="Jakub Bateľ",
    author_email="jakub.batel.jb@gmail.com",
    description=(
        "Application which record attendance using ISIC card and sends the"
        " results to IS MUNI"),
    license="MIT",
    keywords="attendance recorder muni",
    url="",
)
