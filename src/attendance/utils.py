"""Module containing various utility functions."""
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
    """Find mac address and convert it to string.

    Returns:
        Mac address as string separated by ':'.
    """
    return ':'.join(("%012x" % getnode())[i:i+2] for i in range(0, 12, 2))


def get_cache_folder_path() -> str:
    """Get absolute cache folder path as string.

    As cache folder is used ~/.cache/AttendanceRecorder

    This function expands the path and convert it to string.

    Returns:
        Absolute path to cache folder as string.
    """
    return path.join(Path.home(), '.cache', 'AttendanceRecorder')


def get_cache_file_path() -> Path:
    """Get cache file path.

    Returns:
        Absolute path to cache file.
    """
    return Path(get_cache_folder_path(), 'cache')


def create_cache_folder() -> None:
    """Create cache folder acquired from get_cache_folder_path()."""
    cache_folder_path: str = get_cache_folder_path()
    if not path.exists(cache_folder_path):
        logger.debug(
            'cache folder ({0}) did\'t exist'.format(cache_folder_path))
        makedirs(cache_folder_path)
        logger.info(
            'cache folder ({0}) was created'.format(cache_folder_path))


def is_site_up(url: str, timeout: float = 5.0) -> bool:
    """Verify if given URL is accessible.

    Args:
        url: String representation of URL to verify.
        timeout: Timeout for the request.

    Returns:
        True if URL is accessible, false otherwise.
    """
    try:
        result: Response = requests.get(url, timeout=timeout)
        result.raise_for_status()
        logger.info('site {0} is accessible'.format(url))
        return True
    except requests.ConnectionError:
        logger.warning(
            'site {0} is not accessible, no internet connection'.format(url))
        return False
    except requests.HTTPError as e:
        logger.warning('site {0} is not accessible, status code was {1}'.format(
            url, e.response.status_code))
        return False
    except requests.Timeout:
        logger.warning(
            'site {0} is not accessible, connection timed out'.format(url))
        return False


def reverse_endianness(string: str) -> str:
    """Convert hex string to hex string with opposite endianness.

    E.g.
    Little endian -> Big endian,
    Big endian -> Little endian

    Result for non hex string is undefined, no validation is done.

    Args:
        string: Hex string to convert.

    Returns:
        Hex lower case string with reverse endianness.
    """
    translation: Dict[int, Union[int, None]] = str.maketrans(
        '0123456789abcdef', '084c2a6e195d3b7f')
    return string.lower().translate(translation)
