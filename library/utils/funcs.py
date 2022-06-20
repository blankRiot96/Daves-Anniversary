import math
import time
from typing import Sequence

import pygame


def circle_surf(radius, color):
    surf = pygame.Surface((radius * 2, radius * 2))
    pygame.draw.circle(surf, color, (radius, radius), radius)
    # surf.set_colorkey((0, 0, 0))

    return surf


def camerify(coord, camera):
    """
    Converts a coordinate to camera relative position

    :return: Converted coordinate
    """
    return coord[0] - camera[0], coord[1] - camera[1]


def rotate(extract, angle):
    dump = [pygame.transform.rotate(img, angle) for img in extract]

    return dump


def mod_alpha(extract, alpha):
    for surf in extract:
        surf.set_alpha(alpha)


def resize(extract: Sequence[pygame.Surface], scale: float):
    width, height = (
        extract[0].get_width() * scale,
        extract[0].get_height() * scale,
    )
    scaled = [pygame.transform.scale(img, (width, height)) for img in extract]

    return scaled


def flip_images(extract: Sequence):
    flipped_images = [pygame.transform.flip(img, True, False) for img in extract]

    return flipped_images


def get_movement(angle: float, speed) -> tuple[int, int]:
    """

    :param angle: Angle in radians
    :param speed:
    :return: Required change in x and y to move towards angle
    """
    # Change in x and y
    dx = math.cos(angle) * speed
    dy = math.sin(angle) * speed

    return dx, dy
