import math


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

