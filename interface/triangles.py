from map import Map
from typing import Literal
from interface.const import terrain_light_factor
from interface.interpolation import get_data_interpolated
from supplements.textures import patterndefs_textures


def get_major_triangle_corner_vertices(coordinates, triangle_type: Literal["a", "b"]):
    x, y = coordinates
    match triangle_type, y % 2:
        case "a", 0: return (2*x, 2*y), (2*x+1, 2*y+2), (2*x-1, 2*y+2)
        case "b", 0: return (2*x, 2*y), (2*x+2, 2*y), (2*x+1, 2*y+2)
        case "a", 1: return (2*x+1, 2*y), (2*x+2, 2*y+2), (2*x, 2*y+2)
        case "b", 1: return (2*x+1, 2*y), (2*x+3, 2*y), (2*x+2, 2*y+2)
        case _: raise ValueError

def get_triangle_corner_vertices(coordinates, triangle_type: Literal["a", "b"]):
    # This is correct for both major/minor triangles when major/minor coordinates are being used respectively.
    x, y = coordinates
    match triangle_type, y % 2:
        case "a", 0: return (x, y), (x, y+1), (x-1, y+1)
        case "b", 0: return (x, y), (x+1, y), (x, y+1)
        case "a", 1: return (x, y), (x+1, y+1), (x, y+1)
        case "b", 1: return (x, y), (x+1, y), (x+1, y+1)
        case _: raise ValueError

def get_neighbouring_triangles(coorinates, triangle_type: Literal["a", "b"]):
    x, y = coorinates
    match triangle_type, y % 2:
        case "a", 0: return (x-1, y), (x, y), (x-1, y+1)
        case "b", 0: return (x, y-1), (x, y), (x+1, y)
        case "a", 1: return (x-1, y), (x, y), (x, y+1)
        case "b", 1: return (x+1, y-1), (x, y), (x+1, y)
        case _: raise ValueError

def get_major_triangle_texture(coordinates, triangle_type: Literal["a", "b"], map_object: Map):
    index_bytes = coordinates[1] * map_object.map_width + coordinates[0] * 2
    match triangle_type:
        case "a": value = int.from_bytes(map_object.mepa[index_bytes: index_bytes+2], byteorder="little")
        case "b": value = int.from_bytes(map_object.mepb[index_bytes: index_bytes+2], byteorder="little")
        case _: raise ValueError
    return patterndefs_textures[value][triangle_type]

def get_major_triangle_light_values(coordinates, triangle_type: Literal["a", "b"], map_object: Map):

    light_values = []
    for corner in get_triangle_corner_vertices(coordinates, triangle_type):

        light_value = map_object.mlig[(corner[1] % (map_object.map_height // 2)) * map_object.map_width // 2 +
                                      (corner[0] % (map_object.map_width  // 2))]

        light_value = terrain_light_factor * (light_value - 127) / 128
        light_values.append(light_value)

    return tuple(light_values)

def get_minor_triangle_light_values(coordinates, triangle_type: Literal["a", "b"], map_object: Map):

    light_values = []
    for corner in get_triangle_corner_vertices(coordinates, triangle_type):
        light_value = get_data_interpolated(corner, (map_object.map_width, map_object.map_height), map_object.mlig)
        light_value = terrain_light_factor * (light_value - 127) / 128
        light_values.append(light_value)

    return tuple(light_values)
