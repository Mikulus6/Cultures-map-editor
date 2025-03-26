import pygame
from functools import lru_cache
from interface.const import landscape_light_factor_inverse, lru_cache_landscapes_light_maxsize
import numpy as np

@lru_cache(maxsize=lru_cache_landscapes_light_maxsize)
def adjust_opaque_pixels(surface: pygame.Surface, factor: int):

    surface = surface.convert_alpha()
    pixel_array = pygame.surfarray.pixels3d(surface)

    brightened_pixels = pixel_array.astype(np.int16)
    brightened_pixels[::] += (factor - 127)//landscape_light_factor_inverse
    brightened_pixels = np.clip(brightened_pixels, 0, 255).astype(np.uint8)

    pixel_array[::] = brightened_pixels[::]

    return surface
