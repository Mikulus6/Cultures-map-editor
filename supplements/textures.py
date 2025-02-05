from io import BytesIO
import os
from PIL import Image, ImageDraw
from scripts.data_loader import patterndefs_normal
from supplements.read import read
from typing import Literal

textures_path_free = "data_v\\ve_graphics\\textures1\\free"
textures_path_sys  = "data_v\\ve_graphics\\textures1\\sys"


def rect_bound(coordinates):
    min_x = min(map(lambda coords: coords[0], coordinates))
    max_x = max(map(lambda coords: coords[0], coordinates))
    min_y = min(map(lambda coords: coords[1], coordinates))
    max_y = max(map(lambda coords: coords[1], coordinates))

    return (min_x, max_x), (min_y, max_y)


class Texture:

    def __init__(self, pixel_coords, set_id, source_type: Literal["free", "sys"] = "free"):

        assert set_id < 1000  # SetId can be composed of only three digits in decimal system.

        bounds_x, bounds_y = rect_bound(pixel_coords)
        self.size = (bounds_x[1] - bounds_x[0], bounds_y[1] - bounds_y[0])
        self.pixel_coords = tuple(map(lambda coords: (coords[0] - bounds_x[0],
                                                      coords[1] - bounds_y[0]), pixel_coords))
        match source_type:
            case "free": textures_path = textures_path_free
            case "sys":  textures_path = textures_path_sys
            case _: raise ValueError

        image_path = os.path.join(textures_path, ("text_" + "%03d" % set_id)+".pcx")
        bounds = (bounds_x[0], bounds_y[0], bounds_x[1], bounds_y[1])
        image_texture = (Image.open(BytesIO(read(image_path, mode="rb"))).crop(bounds).convert('RGBA'))
        mask = Image.new("L", image_texture.size, 0)
        ImageDraw.Draw(mask).polygon(self.pixel_coords, fill=255)

        self.image = Image.new("RGBA", image_texture.size, (0, 0, 0, 0))
        self.image.paste(image_texture, mask=mask)

    def pygame_convert(self):
        import pygame
        self.image = pygame.image.frombytes(self.image.tobytes(), size=self.size, format="RGBA").convert_alpha()


class Textures(dict):
    initialized = False
    pygame_converted = False

    def __init__(self):
        super().__init__(dict())
        if self.__class__.initialized:
            raise ValueError(f"{self.__class__.__name__} is a singleton.")
        self.__class__.initialized = True
        self.__class__.pygame_converted = False

        self.load()

    def load(self, *, pygame_convert: bool = False):
        super().clear()
        for patterndef in patterndefs_normal.values():
            a_pixel_coords = self.flat_pixel_coords_to_pairs(patterndef["APixelCoords"])
            b_pixel_coords = self.flat_pixel_coords_to_pairs(patterndef["BPixelCoords"])

            texture_a = Texture(a_pixel_coords, patterndef["SetId"])
            texture_b = Texture(b_pixel_coords, patterndef["SetId"])

            if pygame_convert:
                texture_a.pygame_convert()
                texture_b.pygame_convert()

            mep_id = patterndef["Id"] + patterndef["SetId"] * 256

            self[mep_id] = {"a": texture_a, "b": texture_b}

        self.__class__.pygame_converted = pygame_convert

    def pygame_convert(self):

        for key in self.keys():
            self[key]["a"].pygame_convert()
            self[key]["b"].pygame_convert()

        self.__class__.pygame_converted = True

    @staticmethod
    def flat_pixel_coords_to_pairs(pixel_coords):
        return (pixel_coords[0], pixel_coords[1]), \
               (pixel_coords[2], pixel_coords[3]), \
               (pixel_coords[4], pixel_coords[5])


textures = Textures()
