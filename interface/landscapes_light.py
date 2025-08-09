import pygame
from functools import lru_cache
from interface.const import lru_cache_landscapes_light_maxsize
from supplements.landscapedefs import landscapedefs
from supplements.gouraud import gouraud
import numpy as np

def check_remap_disability(landscape_name: str) -> bool:
    match landscapedefs[landscape_name.lower()].get("RemapDisable", 0):
        case 0: return False
        case 1: return True
        case _: raise ValueError

@lru_cache(maxsize=lru_cache_landscapes_light_maxsize)
def adjust_opaque_pixels(surface: pygame.Surface, factor: int):

    surface = surface.convert_alpha()
    pixel_array = pygame.surfarray.pixels3d(surface)

    brightened_pixels = pixel_array.astype(np.int16)
    brightened_pixels[::] += round((factor - 127) * gouraud.shading_factor)
    brightened_pixels = np.clip(brightened_pixels, 0, 255).astype(np.uint8)

    pixel_array[::] = brightened_pixels[::]

    return surface
