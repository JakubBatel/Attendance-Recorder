from __future__ import annotations
from typing import List
from typing import Set
from typing import Tuple
from uuid import getnode


def get_mac_address() -> str:
    return ':'.join(("%012X" % getnode())[i:i+2] for i in range(0, 12, 2))
