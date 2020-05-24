from __future__ import annotations

from .utils import is_site_up

from abc import ABC
from abc import abstractmethod
from copy import deepcopy
from logging import getLogger
from logging import Logger
from requests import Response
from typing import Any
from typing import Dict
from typing import Final
from typing import List
from typing import Optional
from typing import Union

import json
import requests


class APIConnectionException(Exception):
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


class IConnection(ABC):
    """Connection to the API.

    Stores authentication token from the API and receives data as JSON.
    """

    @abstractmethod
    def set_token(self, token: str) -> None:
        """Update connection token.

        Args:
            token: New connection token.
        """
        pass

    @abstractmethod
    def get_token(self) -> Any:
        """Return token if it is set."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Verify if API server is reachable.

        Returns:
            True if connection to the server succeeded, false otherwise.
        """
        pass

    @abstractmethod
    def send_cached_data_only(self, card_ids: List[str]) -> Dict[str, Any]:
        """Send cached data without actual card.

        Args:
            card_ids: Cached card IDs.

        Returns:
            JSON response as dictionary.

        Raises:
            ISConnectionException: If connection failed for any reason(no internet, timeout, ...)
        """
        pass

    @abstractmethod
    def send_data(self, actual_card_id: str, previous_card_ids: List[str] = []) -> Dict[str, Any]:
        """Send card data to the API.

        Args:
            actual_card_id: Currently read card.
            previous_card_ids: List of all cached card IDs to send.

        Returns:
            JSON response as dictionary.
        """
        pass

    @abstractmethod
    def send_organizator_data(self, organizator_card_id: str, card_ids: List[str] = []) -> Dict[str, Any]:
        """Send card data of the organizator to the API.

        Args:
            organizator_card_id: Card ID of the organizator.
            card_ids: List of all cached card IDs to send.

        Returns:
            JSON response as dictionary.
        """
        pass


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
            ISConnectionBuilderException: If build failed(some of the required parameters is not set).
        """
        return ISConnection(self)


class ISConnection(IConnection):
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
        self.logger.info('Connection token set to {0}'.format(token))
        self._data['token'] = token

    def get_token(self) -> Any:
        """Return token if it is set."""
        return self._data.get('token')

    def is_available(self) -> bool:
        """Verify if API server is reachable.

        Returns:
            True if connection to the server succeeded, false otherwise.
        """
        available: bool = is_site_up(self._baseurl)
        if available:
            self.logger.info('Connection to the server is available.')
        else:
            self.logger.warning('Connection to the server failed.')
        return available

    def _send_data(self, timeout: tuple = (3, 10)) -> Dict[str, Any]:
        """Send data to the REST API.

        Args:
            timeout: Connection timeout.

        Returns:
            JSON response as dictionary.

        Raises:
            APIConnectionException: If connection failed for any reason(no internet, timeout, ...)
        """
        try:
            response: Response = requests.post(
                self._url, params=self._data, timeout=timeout)
            response.raise_for_status()
            self.logger.info("Successfuly sent ")

            json_response: Dict[str, Any] = json.loads(response.text)
            if 'token' in json_response:
                self.set_token(json_response['token'])
            return json_response
        except requests.ConnectionError:
            msg = "Connection to {0} failed.".format(self._url)
            self.logger.warning(msg)
            raise APIConnectionException(msg)
        except requests.Timeout:
            msg = "Connection to {0} timed out.".format(self._url)
            self.logger.warning(msg)
            raise APIConnectionException(msg)
        except requests.HTTPError as e:
            msg = "Connection to {0} failed. Status code was {1}.".format(
                self._url, e.response.status_code)
            self.logger.warning(msg)
            raise APIConnectionException(msg)

    def send_cached_data_only(self, card_ids: List[str]) -> Dict[str, Any]:
        """Send cached data without actual card.

        Args:
            card_ids: Cached card IDs.

        Returns:
            JSON response as dictionary.

        Raises:
            APIConnectionException: If connection failed for any reason(no internet, timeout, ...)
        """
        self._data['cardid'] = deepcopy(card_ids)
        return self._send_data()

    def send_data(self, actual_card_id: str, previous_card_ids: List[str] = []) -> Dict[str, Any]:
        """Send card data to the API.

        Args:
            actual_card_id: Currently read card.
            previous_card_ids: List of all cached card IDs to send.

        Returns:
            JSON response as dictionary.

        Raises:
            APIConnectionException: If connection failed for any reason(no internet, timeout, ...)
        """
        self.logger.debug('Sending card: ' + actual_card_id +
                          ', previous cards' + str(previous_card_ids))
        card_ids: List[str] = deepcopy(previous_card_ids)
        card_ids.append(actual_card_id)
        self._data['cardid'] = card_ids
        if len(self._data['cardid']) > 5:
            # Use extended timeout if many data are send
            return self._send_data((10, 30))
        return self._send_data()

    def send_organizator_data(self, organizator_card_id: str, card_ids: List[str] = []) -> Dict[str, Any]:
        """Send card data of the organizator to the API.

        Args:
            organizator_card_id: Card ID of the organizator.
            card_ids: List of all cached card IDs to send.

        Returns:
            JSON response as dictionary.

        Raises:
             APIConnectionException: If connection failed for any reason(no internet, timeout, ...)
        """
        self.logger.debug('Sending organizator card: ' + organizator_card_id)
        self._data['init'] = '1'
        return self.send_data(organizator_card_id, card_ids)
