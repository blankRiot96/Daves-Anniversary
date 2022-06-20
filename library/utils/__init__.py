"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

from library.utils.animation import Animation
from library.utils.classes import Expansion, Glow, Time
from functools import lru_cache
import pygame
from pathlib import Path
pygame.font.init()


@lru_cache()
def font(size=20, name=None):
    """
    Load a font from its name in the wclib/assets folder.
    If a Path object is given as the name, this path will be used instead.
    This way, you can use custom fonts that are inside your own folder.
    Results are cached.
    """

    if isinstance(name, Path) or name is None:
        path = name
    else:
        path = f"assets/fonts/{name}.ttf"
    return pygame.font.Font(path, size)