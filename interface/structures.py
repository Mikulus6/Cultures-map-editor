from map import Map
from supplements.textures import patterndefs_textures
from supplements.patterns import road

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
