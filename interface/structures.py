from map import Map
from supplements.textures import patterndefs_textures
from supplements.patterns import road
from typing import Literal


def get_structure(coordinates, map_object: Map):
    value_index = coordinates[1] * map_object.map_width + coordinates[0]
    mstr_value = int.from_bytes(map_object.mstr[2 * value_index: 2 * value_index + 2], byteorder="little")
    result_dict = {}

    type_a = (mstr_value & 0b0011_0000) // 16
    type_b = (mstr_value & 0b1100_0000) // 64
    corners_value = mstr_value & 0b1111

    assert mstr_value & 0b1111_1110_0000_0000 == 0
    assert type_a != 3 and type_b != 3

    if corners_value == 0:
        return result_dict

    for triangle_type in ("a", "b"):
        match (type_a if triangle_type == "a" else type_b):
            case 0: structure_data = road["road"]
            case 1: structure_data = road["river"]
            case 2: structure_data = road["snow"]
            case _: raise ValueError

        match triangle_type:
            case "a": corners = 4*(corners_value & 0b0001) + \
                                2*(corners_value & 0b1000) // 8 + \
                                  (corners_value & 0b0100) // 4
            case "b": corners = 4*(corners_value & 0b0001) + \
                                2*(corners_value & 0b1000) // 8 + \
                                  (corners_value & 0b0010) // 2
            case _: raise ValueError

        if corners == 0:   continue
        elif corners == 7: corners = 0

        pattern_data = structure_data["patterna"] if triangle_type == "a" else structure_data["patternb"]
        mep_id = pattern_data[2*corners] * 256 + pattern_data[1::2].index(corners)
        result_dict[triangle_type] = patterndefs_textures[mep_id][triangle_type]

    return result_dict

def get_structure_type_of_vertex(map_object: Map, coordinates) -> Literal[None, "road", "river", "snow"]:

    value_index = (coordinates[1] % map_object.map_height) * map_object.map_width + \
                  (coordinates[0] % map_object.map_width)
    mstr_value = int.from_bytes(map_object.mstr[2 * value_index: 2 * value_index + 2], byteorder="little")

    type_a = (mstr_value & 0b0011_0000) // 16
    corners_value = mstr_value & 0b1111

    if corners_value & 0b0001 == 0:
        return None

    match type_a:
        case 0: return "road"
        case 1: return "river"
        case 2: return "snow"

def update_structures(map_object: Map, coordinates, structure_type: Literal[None, "road", "river", "snow"]):
    x, y = coordinates

    if y % 2 == 0:
        parallelograms = (x-1, y-1), (x, y-1), (x-1, y), (x, y)
        surroundings = (x, y), (x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1), (x - 1, y + 1), (x - 1, y - 1)
    else:
        parallelograms = (x, y-1), (x+1, y-1), (x-1, y), (x, y)
        surroundings = (x, y), (x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1), (x + 1, y + 1), (x + 1, y - 1)

    remove_structure = False
    if structure_type is None:
        remove_structure = True

    else:
        for surroundings_coordinates in surroundings:
            vertex_type = get_structure_type_of_vertex(map_object, surroundings_coordinates)
            if vertex_type not in (None, structure_type):
                return  # Updating structure in this case would break continuity conditions.

    match structure_type:
        case None:    structure_num = 0  # This value is not important.
        case "road":  structure_num = 0
        case "river": structure_num = 1
        case "snow":  structure_num = 2
        case _: raise ValueError

    for index_value, coordinates in enumerate(parallelograms):
        x_sub, y_sub = coordinates
        x_sub %= map_object.map_width
        y_sub %= map_object.map_height

        mstr_index = y_sub * map_object.map_width + x_sub
        mstr_value = int.from_bytes(map_object.mstr[2 * mstr_index: 2 * mstr_index + 2], byteorder="little")

        type_a = (mstr_value & 0b0011_0000) // 16
        type_b = (mstr_value & 0b1100_0000) // 64
        corners_value = mstr_value & 0b1111

        match index_value, remove_structure:
            case 0, False:
                result_type_a = structure_num
                result_type_b = structure_num
                result_corners = corners_value | 0b1000
            case 1, False:
                result_type_a = structure_num
                result_type_b = type_b
                result_corners = corners_value | 0b0100
            case 2, False:
                result_type_a = type_a
                result_type_b = structure_num
                result_corners = corners_value | 0b0010
            case 3, False:
                result_type_a = structure_num
                result_type_b = structure_num
                result_corners = corners_value | 0b0001
            case 0, True:
                result_type_a = type_a
                result_type_b = type_b
                result_corners = corners_value & 0b0111
            case 1, True:
                result_type_a = type_a
                result_type_b = type_b
                result_corners = corners_value & 0b1011
            case 2, True:
                result_type_a = type_a
                result_type_b = type_b
                result_corners = corners_value & 0b1101
            case 3, True:
                result_type_a = type_a
                result_type_b = type_b
                result_corners = corners_value & 0b1110
            case _:
                raise ValueError

        map_object.mstr[2 * mstr_index: 2 * mstr_index + 2] = \
            int.to_bytes(result_type_b * 64 + result_type_a * 16 + result_corners, length=2, byteorder="little")
