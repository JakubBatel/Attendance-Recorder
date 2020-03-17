from attendance.resources.config import config
from attendance.utils import CGIParamStringBuilder
from attendance.utils import get_mac_address

from socket import create_connection
from socket import socket
from ssl import SSLSocket
from ssl import wrap_socket
from typing import List
from typing import Optional


class ISConnection:

    _REQUEST_TEMPLATE: str = \
        'POST /{path} HTTP/1.1\r\n\
        Host: {host}\r\n\
        Connection:\r\n\
        \r\n\
        {data}\r\n'

    _BUFFER_SIZE: int = 1024

    def __init__(self, mac_address: str, token: Optional[str] = None):
        self._hostname: str = config['Connection']['hostname']
        self._path: str = config['Connection']['path']
        self._port: int = int(config['Connection']['port'])
        self._encoding: str = config['Connection']['encoding']
        self._mac_address: str = mac_address
        self._token: Optional[str] = token
        self._socket: Optional[socket] = None
        self._tunel: Optional[SSLSocket] = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.close()

    def connect(self):
        self._socket = create_connection((self._hostname, self._port))
        self._tunel = wrap_socket(self._socket)

    def close(self):
        if self._socket is not None:
            self._socket.close()
        if self._tunel is not None:
            self._tunel.close()

    def _build_data_string(self, cardIDs: List[str]) -> str:
        builder: CGIParamStringBuilder = CGIParamStringBuilder()
        builder.add('mac', self._mac_address)
        if self._token is not None:
            builder.add('token', self._token)
        if len(cardIDs) != 0:
            builder.addList('cardid', cardIDs)
        return builder.build()

    def send_data(self, cardIDs: List[str]) -> None:
        if self._tunel is None:
            raise TypeError

        data_string: str = self._build_data_string(cardIDs)
        request_string: str = ISConnection._REQUEST_TEMPLATE.format(
            host=self._hostname, path=self._path, data=data_string)
        request: bytes = request_string.encode('ascii')
        self._tunel.sendall(request)

    def recieve_data(self) -> str:
        if self._tunel is None:
            raise TypeError

        data: List[bytes] = []
        while True:
            buffer: bytes = self._tunel.recv(ISConnection._BUFFER_SIZE)
            if not buffer:
                break
            data.append(buffer)
        return b''.join(data).decode(self._encoding)
