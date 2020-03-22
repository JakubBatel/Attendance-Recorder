from attendance.resources.config import config
from attendance.utils import is_site_up

from requests import Response
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import json
import requests


class ISConnectionException(Exception):

    def __init__(self, message):
        super().__init__(message)


class ISConnection:

    def __init__(self, mac_address: str, token: Optional[str] = None):
        self._hostname: str = config['Connection']['hostname']
        self._url: str = config['Connection']['url']
        self._encoding: str = config['Connection']['encoding']
        self._data: Dict[str, List[str]] = {'mac': [mac_address]}
        if token is not None:
            self._data['token'] = [token]

    def set_token(self, token: str) -> None:
        self._data['token'] = [token]

    def is_available(self) -> bool:
        return is_site_up(self._hostname)

    def send_data(self, cardIDs: List[str]) -> Dict[str, Any]:
        self._data['cardid'] = cardIDs
        response: Optional[Response] = None
        try:
            response = requests.post(self._url, data=self._data)
        except requests.ConnectionError:
            raise ISConnectionException(
                "Connection to {0} failed".format(self._url))
        except requests.Timeout:
            raise ISConnectionException(
                "Connection to {0} timed out.".format(self._url))

        if not response.ok:
            raise ISConnectionException(
                "Connection failed. Status code was {0}."
                .format(response.status_code))
        json_response: Dict[str, Any] = json.loads(response.text)
        self.set_token(json_response['token'])
        return json_response
