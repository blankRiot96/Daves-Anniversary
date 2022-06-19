"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import logging

import pygame

logger = logging.getLogger()


def get_images(
    sheet: pygame.Surface,
    size: tuple[int],
):
    """
    Converts a sprite sheet to a list of surfaces

    Parameters:
            sheet: A pygame.Surface that contains the sprite sheet
            rows: Amount of rows in the sprite sheet
            columns: Amount of columds in the sprite sheet
            size: Size of a sprite in the sprite sheet
    """
    images = []

    width, height = size

    # loop through all sprites in the sprite sheet
    rows = int(sheet.get_height() / height)
    columns = int(sheet.get_width() / width)

    for row in range(rows):
        for col in range(columns):
            # get the image
            image = sheet.subsurface(pygame.Rect((col * width), (row * height), *size))

            # add it to the image list
            images.append(image)

    return images


def load_assets(state: str, screen: pygame.Surface) -> dict:
    assets = {}
    path = Path("assets/sprites/")

    json_files = path.rglob("*.json")
    total_files = len(tuple(json_files))
    loading_back_rect = pygame.Rect(
        0, 0, screen.get_width() / 1.3, screen.get_height() / 8
    )
    loading_fore_rect = pygame.Rect(0, 0, 0, loading_back_rect.height)
    total_rect_width = loading_back_rect.width
    width_mult = total_files / total_rect_width
    width = total_rect_width
    loading_back_rect.center = screen.get_rect().center
    loading_fore_rect.midleft = loading_back_rect.midleft
    font = pygame.font.Font(None, 50)
    loading_text = font.render("Loading...", True, (25, 25, 25))
    r = loading_text.get_rect(midbottom=loading_back_rect.midtop)
    for metadata_f in path.rglob("*.json"):
        metadata = json.loads(metadata_f.read_text())
        for file, data in metadata.items():
            if state not in data["states"]:
                continue

            complete_path = metadata_f.parent / file
            logger.info(f"Loaded {complete_path}")
            if data["convert_alpha"]:
                image = pygame.image.load(complete_path).convert_alpha()
            else:
                image = pygame.image.load(complete_path).convert()

            if data["sprite_sheet"] is None:
                asset = image
            else:
                asset = get_images(image, *data["sprite_sheet"].values())

            file_extension = file[file.find(".") :]
            assets[file.replace(file_extension, "")] = asset
        screen.fill("black")
        width += total_rect_width * total_files
        # time.sleep(0.1)
        loading_fore_rect.width = width * width_mult
        screen.blit(loading_text, r)
        pygame.draw.rect(screen, (25, 25, 25), loading_back_rect)
        pygame.draw.rect(screen, "white", loading_fore_rect)
        pygame.display.flip()

    return assets
