"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path

import pygame

logger = logging.getLogger()


pygame.mixer.init()


@dataclass
class SoundObj:
    sound: pygame.mixer.Sound
    original_volume: float


def load_sfx(state: str) -> dict:
    assets = {}
    path = Path("assets/audio/")

    json_files = path.rglob("*.json")
    for metadata_f in json_files:
        metadata = json.loads(metadata_f.read_text())
        for file, data in metadata.items():
            if state not in data["states"]:
                continue

            complete_path = metadata_f.parent / file
            logger.critical(f"Loaded {complete_path}")

            sound = pygame.mixer.Sound(complete_path)

            sound.set_volume(data["volume"])

            asset = SoundObj(sound, data["volume"])
            file_extension = file[file.find(".") :]
            assets[file.replace(file_extension, "")] = asset

    return assets


class SFXManager:
    def __init__(self, state: str):
        self.sounds = load_sfx(state)

    def play(self, sound_key: str):
        sound_obj = self.sounds[sound_key]
        sound = sound_obj.sound
        sound.play()

    def set_volume(self, percentage: float):
        for sound_obj in self.sounds.values():
            volume = (percentage / 100) * sound_obj.original_volume
            sound_obj.sound.set_volume(volume)
