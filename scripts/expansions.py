from PIL import Image
from typing import Literal
import numpy as np


hexagon_shadow_filepath = "scripts/shadows/hexagon.png"
triangle_a_shadow_filepath = "scripts/shadows/triangle_up.png"
triangle_b_shadow_filepath = "scripts/shadows/triangle_down.png"

# === hexagonal expansion ===


hex_image = Image.open(hexagon_shadow_filepath).convert(mode="RGB")
hex_shadow = np.array([1 if x == (255, 255, 255) else 0 for x in hex_image.getdata()]).reshape(hex_image.size[1],
                                                                                               hex_image.size[0])
del hex_image
vertical_cut = tuple(hex_shadow.transpose()[0]).index(1)

def expand_image_object_to_hexagons(image_object: Image.Image) -> Image.Image:

    new_image = Image.new(mode=image_object.mode,
                          size=(image_object.size[0] * hex_shadow.shape[1] + hex_shadow.shape[0]//2,
                                image_object.size[1] * (hex_shadow.shape[0] - vertical_cut) +  vertical_cut),
                          color=(0, 0, 0) if image_object.mode == "RGB" else 0)

    for y in range(image_object.size[1]):
        for x in range(image_object.size[0]):

            pixel_color = image_object.getpixel((x, y))

            for y_shadow in range(hex_shadow.shape[0]):
                for x_shadow in range(hex_shadow.shape[1]):

                    if hex_shadow[y_shadow, x_shadow] == 0:
                        continue

                    y_real = y * (hex_shadow.shape[0] - vertical_cut) + y_shadow
                    x_real = x * hex_shadow.shape[1] + x_shadow + (hex_shadow.shape[1]//2 if y % 2 else 0)


                    new_image.putpixel((x_real, y_real), pixel_color)

    return new_image


# === triangular expansion ===

triangle_a_image = Image.open(triangle_a_shadow_filepath).convert(mode="RGB")
triangle_b_image = Image.open(triangle_b_shadow_filepath).convert(mode="RGB")
triangle_a_shadow = np.array([1 if x == (255, 255, 255) else 0 for x in
                              triangle_a_image.getdata()]).reshape(triangle_a_image.size[1], triangle_a_image.size[0])
triangle_b_shadow = np.array([1 if x == (255, 255, 255) else 0 for x in
                              triangle_b_image.getdata()]).reshape(triangle_b_image.size[1], triangle_b_image.size[0])
del triangle_a_image
del triangle_b_image
assert triangle_a_shadow.shape == triangle_a_shadow.shape

def expand_image_object_to_triangles(image_object: Image.Image,
                                     parallelogramic_collumn_duplication=False) -> Image.Image:


    new_image = Image.new(mode=image_object.mode,
                          size=((image_object.size[0] * triangle_a_shadow.shape[1] // 2 + triangle_a_shadow.shape[1]) *\
                                (2 if parallelogramic_collumn_duplication else 1),
                                image_object.size[1] * triangle_a_shadow.shape[0]),
                          color=(0, 0, 0) if image_object.mode == "RGB" else 0)

    for y in range(image_object.size[1]):
        for x in range(image_object.size[0] * (2 if parallelogramic_collumn_duplication else 1)):

            pixel_color = image_object.getpixel(((x//2 if parallelogramic_collumn_duplication else x), y))

            for y_shadow in range(triangle_a_shadow.shape[0]):
                for x_shadow in range(triangle_a_shadow.shape[1]):

                    if x % 2 == 0:
                        triangle_shadow = triangle_a_shadow
                    else:
                        triangle_shadow = triangle_b_shadow

                    if triangle_shadow[y_shadow, x_shadow] == 0:
                        continue

                    if y % 2 != 0:
                        x_shadow += triangle_a_shadow.shape[1] // 2

                    y_real = y * triangle_a_shadow.shape[0] + y_shadow
                    x_real = x * triangle_a_shadow.shape[1] // 2 + x_shadow

                    new_image.putpixel((x_real, y_real), pixel_color)
    return new_image

def expand_image(image: Image.Image, expansion_mode: Literal[None, "hexagon", "triangle", "pallalelogram"]=None):

    match expansion_mode:
        case None: return image
        case "hexagon": return expand_image_object_to_hexagons(image)
        case "triangle": return expand_image_object_to_triangles(image)
        case "parallelogram": return expand_image_object_to_triangles(image, parallelogramic_collumn_duplication=True)
        case _: raise ValueError
