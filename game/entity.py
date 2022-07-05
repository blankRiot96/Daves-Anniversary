"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import enum


class EntityStates(enum.Enum):
    WALK = enum.auto()
    IDLE = enum.auto()
    JUMP = enum.auto()
