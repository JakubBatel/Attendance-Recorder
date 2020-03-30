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

    def __init__(self, message):
        super().__init__(message)


class ISConnectionBuilderException(Exception):

    def __init__(self, message):
        super().__init__(message)


class ISConnectionBuilder:

    def __init__(self):
        self.mac_address: Optional[str] = None
        self.token: Optional[str] = None
        self.baseurl: Optional[str] = None
        self.url: Optional[str] = None

    def get_mac_address(self) -> str:
        if self.mac_address is None:
            raise ISConnectionBuilderException('Mac address can not be None.')
        return self.mac_address

    def set_mac_address(self, mac_address: str) -> ISConnectionBuilder:
        self.mac_address = mac_address
        return self

    def get_token(self) -> Optional[str]:
        return self.token

    def set_token(self, token: str) -> ISConnectionBuilder:
        self.token = token
        return self

    def get_baseurl(self) -> str:
        if self.baseurl is None:
            return self.get_url()
        return self.baseurl

    def set_baseurl(self, baseurl: str) -> ISConnectionBuilder:
        self.baseurl = baseurl
        return self

    def get_url(self) -> str:
        if self.url is None:
            raise ISConnectionBuilderException('Url can not be None.')
        return self.url

    def set_url(self, url: str) -> ISConnectionBuilder:
        self.url = url
        return self

    def build(self) -> ISConnection:
        return ISConnection(self)


class ISConnection:

    def __init__(self, builder: ISConnectionBuilder):
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
        if self._data['token'] != token:
            self.logger.info('Connection token set to {0}'.format(token))
            self._data['token'] = token

    def is_available(self) -> bool:
        available: bool = is_site_up(self._baseurl)
        if available:
            self.logger.info('Connection to the server is available.')
        else:
            self.logger.warn('Connection to the server failed.')
        return available

    def send_data(self, cardIDs: List[str]) -> Dict[str, Any]:
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
