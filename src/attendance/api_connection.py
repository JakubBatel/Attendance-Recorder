from __future__ import annotations

from attendance.utils import is_site_up

from logging import getLogger
from logging import Logger
from requests import Response
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import json
import requests


class ISConnectionException(Exception):
    """Custom connection exception."""

    def __init__(self, message):
        """Init exception with message.

        Args:
            message: Error message.
        """
        super().__init__(message)


class ISConnectionBuilderException(Exception):
    """Custom connection builder exception."""

    def __init__(self, message):
        """Init exception with message.

        Args:
            message: Error message.
        """
        super().__init__(message)


class ISConnectionBuilder:
    """Class used to build ISConnection."""

    def __init__(self):
        """Init all params with None."""
        self.mac_address: Optional[str] = None
        self.token: Optional[str] = None
        self.baseurl: Optional[str] = None
        self.url: Optional[str] = None

    def get_mac_address(self) -> str:
        """Acquire mac address.

        Returns:
            Mac address as string.

        Raises:
            ISConnectionBuilderException: If mac address is not set.
        """
        if self.mac_address is None:
            raise ISConnectionBuilderException('Mac address can not be None.')
        return self.mac_address

    def set_mac_address(self, mac_address: str) -> ISConnectionBuilder:
        """Set mac address.

        Args:
            mac_address: String representation of mac address to set.

        Returns:
            Itself with updated mac_address.
        """
        self.mac_address = mac_address
        return self

    def get_token(self) -> Optional[str]:
        """Acquire connection token.

        Returns:
            Token as string if there is any, None otherwise.
        """
        return self.token

    def set_token(self, token: str) -> ISConnectionBuilder:
        """Set connection token.

        Args:
            token: Connection token as string.

        Returns:
            Itself with updated token.
        """
        self.token = token
        return self

    def get_baseurl(self) -> str:
        """Acquire base URL.

        Returns:
            Base URL if exists, full URL otherwise.

        Raises:
            ISConnectionBuilderException: If get_url() raises one.
        """
        if self.baseurl is None:
            return self.get_url()
        return self.baseurl

    def set_baseurl(self, baseurl: str) -> ISConnectionBuilder:
        """Set base URL.

        Args:
            baseurl: Base URL of the connection.

        Returns:
            Itself with updated base URL.
        """
        self.baseurl = baseurl
        return self

    def get_url(self) -> str:
        """Acquire full URL.

        Returns:
            Full URL as string.

        Raises:
            ISConnectionBuilderException: If there is no URL.
        """
        if self.url is None:
            raise ISConnectionBuilderException('URL can not be None.')
        return self.url

    def set_url(self, url: str) -> ISConnectionBuilder:
        """Set full URL.

        Args:
            url: String representation of full URL.
        """
        self.url = url
        return self

    def build(self) -> ISConnection:
        """Build ISConnection.

        Returns:
            New ISConnection build by current parameters.

        Raises:
            ISConnectionBuilderException: If build failed (some of the required parameters is not set).
        """
        return ISConnection(self)


class ISConnection:
    """Class representation of connection to the IS MUNI REST API.

    It is used to send card data to the API and acquire response.
    It uses Requests library to make connections.
    """

    def __init__(self, builder: ISConnectionBuilder):
        """Init class based on builder."""
        self.logger: Logger = getLogger(__name__)
        self._baseurl: str = builder.get_baseurl()
        self.logger.info('Base url set to {0}'.format(self._baseurl))

        self._url: str = builder.get_url()
        self.logger.info('Url set to {0}'.format(self._url))

        mac_address: str = builder.get_mac_address()
        self._data: Dict[str, Union[str, List[str]]] = {'mac': mac_address}
        self.logger.info('Mac address set to {0}'.format(mac_address))

        token: Optional[str] = builder.get_token()
        if token is not None:
            self.set_token(token)

    def set_token(self, token: str) -> None:
        """Update connection token.

        Args:
            token: New connection token.
        """
        if self._data['token'] != token:
            self.logger.info('Connection token set to {0}'.format(token))
            self._data['token'] = token

    def is_available(self) -> bool:
        """Verify if API server is reachable.

        Returns:
            True if connection to the server succeeded, false otherwise.
        """
        available: bool = is_site_up(self._baseurl)
        if available:
            self.logger.info('Connection to the server is available.')
        else:
            self.logger.warn('Connection to the server failed.')
        return available

    def send_data(self, cardIDs: List[str]) -> Dict[str, Any]:
        """Send card data to the API.

        Args:
            cardIDs: List of all card IDs to send.

        Returns:
            JSON response as dictionary.

        Raises:
            ISConnectionException: If connection failed for any reason (no internet, timeout, ...)
        """
        self._data['cardid'] = cardIDs
        try:
            response: Response = requests.post(self._url, data=self._data)
            response.raise_for_status()
            self.logger.info("Successfuly sent ")

            json_response: Dict[str, Any] = json.loads(response.text)
            self.set_token(json_response['token'])
            return json_response
        except requests.ConnectionError:
            msg = "Connection to {0} failed.".format(self._url)
            self.logger.warn(msg)
            raise ISConnectionException(msg)
        except requests.Timeout:
            msg = "Connection to {0} timed out.".format(self._url)
            self.logger.warn(msg)
            raise ISConnectionException(msg)
        except requests.HTTPError as e:
            msg = "Connection to {0} failed. Status code was {1}.".format(
                self._url, e.response.status_code)
            self.logger.warn(msg)
            raise ISConnectionException(msg)
