from __future__ import annotations
from logging import Logger
from os import makedirs
from os import path
from pathlib import Path
from requests import Response
from typing import Dict
from typing import List
from typing import Set
from typing import Tuple
from typing import Union
from uuid import getnode

import logging
import requests

logger: Logger = logging.getLogger(__name__)


def get_mac_address() -> str:
    return ':'.join(("%012X" % getnode())[i:i+2] for i in range(0, 12, 2))


def get_cache_folder_path() -> str:
    return path.join(Path.home(), '.cache', 'AttendanceRecorder')


def get_cache_file_path() -> str:
    return path.join(get_cache_folder_path(), 'cache')


def create_cache_folder() -> None:
    cache_folder_path: str = get_cache_folder_path()
    if not path.exists(cache_folder_path):
        logger.debug(
            'cache folder ({0}) did\'t exist'.format(cache_folder_path))
        makedirs(cache_folder_path)
        logger.info(
            'cache folder ({0}) was created'.format(cache_folder_path))


def is_site_up(url: str, timeout: float = 5.0) -> bool:
    try:
        result: Response = requests.get(url, timeout=timeout)
        result.raise_for_status()
        logger.info('site {0} is accessible'.format(url))
        return True
    except requests.ConnectionError:
        logger.warn(
            'site {0} is not accessible, no internet connection'.format(url))
        return False
    except requests.HTTPError as e:
        logger.warn('site {0} is not accessible, status code was {1}'.format(
            url, e.response.status_code))
        return False
    except requests.Timeout:
        logger.warn(
            'site {0} is not accessible, connection timed out'.format(url))
        return False


def reverse_endianness(string: str) -> str:
    translation: Dict[int, Union[int, None]] = str.maketrans(
        '0123456789ABCDEF', '084C2A6E195D3B7F')
    return string.translate(translation)
