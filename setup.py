import os
from setuptools import setup, find_namespace_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="attendance",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    install_requires=["pyserial", "Pillow", "adafruit-circuitpython-ssd1306"],
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
