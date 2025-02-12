import pygame
from functools import lru_cache
from interface.const import landscape_dark_factor, landscape_light_factor, lru_cache_landscapes_light_maxsize
import numpy as np


@lru_cache(maxsize=lru_cache_landscapes_light_maxsize)
def adjust_opaque_pixels(surface: pygame.Surface, factor: int):

    assert 0 <= factor <= 255 and isinstance(factor, int)

    if factor == 127:
        return surface

    surface = surface.convert_alpha()
    pixel_array = pygame.surfarray.pixels3d(surface)
    opaque_mask = (pygame.surfarray.pixels_alpha(surface) == 255)
    factor = (factor - 127)/128 * (landscape_light_factor if factor > 127 else landscape_dark_factor)

    if factor < 0: pixel_array[opaque_mask] = np.clip(pixel_array[opaque_mask] * (factor + 1), 0, 255).astype(np.uint8)
    else:          pixel_array[opaque_mask] = np.clip(pixel_array[opaque_mask] + ((255 - pixel_array[opaque_mask]) *
                                                                                  factor), 0, 255).astype(np.uint8)
    return surface
