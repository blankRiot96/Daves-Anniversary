"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import enum


class States(enum.Enum):
    """
    Enum for game states
    """

    MAIN_MENU = "main menu"
    LEVEL = "level"
    DIALOGUE = "dialogue"
    ENDING = "ending"
    CREDITS = "credits"


class Dimensions(enum.Enum):
    """
    Enum for dimensions
    """

    PARALLEL_DIMENSION = "parallel_dimension"
    VOLCANIC_DIMENSION = "volcanic_dimension"
    ALIEN_DIMENSION = "alien_dimension"
    WATER_DIMENSION = "water_dimension"
    MOON_DIMENSION = "moon_dimension"
    HOMELAND_DIMENSION = "homeland_dimension"
