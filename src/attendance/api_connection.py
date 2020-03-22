from attendance.resources.config import config

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
        self._url: str = config['Connection']['url']
        self._encoding: str = config['Connection']['encoding']
        self._data: Dict[str, List[str]] = {'mac': [mac_address]}
        if token is not None:
            self._data['token'] = [token]

    def set_token(self, token: str) -> None:
        self._data['token'] = [token]

    def send_data(self, cardIDs: List[str]) -> Dict[str, Any]:
        self._data['cardid'] = cardIDs
        response: Response = requests.post(self._url, data=self._data)
        if not response.ok:
            raise ISConnectionException
        json_response: Dict[str, Any] = json.loads(response.text)
        self.set_token(json_response['token'])
        return json_response
