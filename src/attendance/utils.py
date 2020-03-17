from __future__ import annotations
from typing import List
from typing import Set
from typing import Tuple
from uuid import getnode


class CGIParamStringBuilder:

    def __init__(self):
        self._variables: Set[str] = set()

    def build(self) -> str:
        return '&'.join(self._variables)

    def _add(self, key: str, val: str) -> None:
        self._variables.add(key + '=' + val)

    def add(self, key: str, value: str) -> CGIParamStringBuilder:
        self._add(key, value)
        return self

    def addList(self, key: str, values: List[str]) -> CGIParamStringBuilder:
        for val in values:
            self._add(key, val)
        return self


def get_mac_address() -> str:
    return ':'.join(("%012X" % getnode())[i:i+2] for i in range(0, 12, 2))
