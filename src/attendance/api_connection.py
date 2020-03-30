from attendance.resources.config import config
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


class ISConnection:

    def __init__(self, mac_address: str, token: Optional[str] = None):
        self.logger: Logger = getLogger(__name__)

        self._baseurl: str = config['Connection']['baseurl']
        self.logger.info('Base url set to {0}'.format(self._baseurl))

        self._url: str = config['Connection']['url']
        self.logger.info('Url set to {0}'.format(self._url))

        self._data: Dict[str, Union[str, List[str]]] = {'mac': mac_address}
        self.logger.info('Mac address set to {0}'.format(mac_address))

        if token is not None:
            self.set_token(token)

    def set_token(self, token: str) -> None:
        if self._data['token'] != token:
            self.logger.info('Connection token set to {0}'.format(token))
            self._data['token'] = token

    def is_available(self) -> bool:
        available: bool = is_site_up(self._baseurl)
        if available:
            self.logger.info('Connection to IS MUNI succeeded.')
        else:
            self.logger.warn('Connection to IS MUNI failed.')
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
