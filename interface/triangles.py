from map import Map
from typing import Literal
from scripts.colormap import mep_colormap


def get_major_triangle_corner_vertices(coordinates, triangle_type: Literal["a", "b"]):
    x, y = coordinates
    match triangle_type, y % 2:
        case "a", 0: return (2*x, 2*y), (2*x+1, 2*y+2), (2*x-1, 2*y+2)
        case "b", 0: return (2*x, 2*y), (2*x+2, 2*y), (2*x+1, 2*y+2)
        case "a", 1: return (2*x+1, 2*y), (2*x+2, 2*y+2), (2*x, 2*y+2)
        case "b", 1: return (2*x+1, 2*y), (2*x+3, 2*y), (2*x+2, 2*y+2)
        case _: raise ValueError

def get_major_triangle_color(coordinates, triangle_type: Literal["a", "b"], map_object: Map):
    # TODO: this function might be unnecessary when proper triangles rendering will be implemented.
    index_bytes = coordinates[1] * map_object.map_width + coordinates[0] * 2
    match triangle_type:
        case "a": value = int.from_bytes(map_object.mepa[index_bytes: index_bytes+2], byteorder="little")
        case "b": value = int.from_bytes(map_object.mepb[index_bytes: index_bytes+2], byteorder="little")
        case _: raise ValueError
    return mep_colormap[value]
