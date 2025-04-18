from map import Map
from interface.const import transition_stretch_factor
from interface.triangles import get_neighbouring_triangles
from supplements.patterns import patterndefs_normal, transitions
from supplements.textures import transition_textures
from typing import Literal


# Prepare lookup table for quickly finding correct transition textures.
transitions_by_group = dict()
for transition in transitions.values():
    src_key = transition["SrcGroup"].lower()
    dest_key = transition["DestGroup"].lower()
    textures = transition_textures[transition["Name"].lower()]

    transitions_by_group.setdefault(src_key, dict())
    transitions_by_group[src_key][dest_key] = textures


def transitions_gen(coordinates, triangle_type: Literal["a", "b"], map_object: Map):

    value_index = coordinates[1] * map_object.map_width + coordinates[0] * 2
    triangle_type_dest = "b" if triangle_type == "a" else "a"

    match triangle_type:
        case "a": mep_id_src = int.from_bytes(map_object.mepa[value_index: value_index+2], byteorder="little")
        case "b": mep_id_src = int.from_bytes(map_object.mepb[value_index: value_index+2], byteorder="little")
        case _: raise ValueError

    source_group = patterndefs_normal[mep_id_src]["Group"]
    source_maingroup = patterndefs_normal[mep_id_src]["MainGroup"]

    destinations_group_dict = transitions_by_group.get(source_group)
    destinations_maingroup_dict = transitions_by_group.get(source_maingroup)

    if (destinations_group_dict or destinations_maingroup_dict) is None:
        return

    for trans_coordinates, trans_type in zip(get_neighbouring_triangles(coordinates, triangle_type), ("a", "b", "c")):

        trans_index = (trans_coordinates[1] % (map_object.map_height//2)) * map_object.map_width + \
                      (trans_coordinates[0] % (map_object.map_width//2)) * 2
        match triangle_type_dest:
            case "a": mep_id_dest = int.from_bytes(map_object.mepa[trans_index: trans_index+2], byteorder="little")
            case "b": mep_id_dest = int.from_bytes(map_object.mepb[trans_index: trans_index+2], byteorder="little")
            case _: raise ValueError

        destination_group = patterndefs_normal[mep_id_dest]["Group"]
        destination_maingroup = patterndefs_normal[mep_id_dest]["MainGroup"]

        textures_dict = None
        if destinations_group_dict is not None:
            textures_dict = destinations_group_dict.get(destination_group) or \
                            destinations_group_dict.get(destination_maingroup)
        if destinations_maingroup_dict is not None and textures_dict is None:
            textures_dict = destinations_maingroup_dict.get(destination_group) or \
                            destinations_maingroup_dict.get(destination_maingroup)
        if textures_dict is None:
            continue

        trans_key = triangle_type+trans_type

        if "TPixelCoords" in textures_dict.keys():
            texture = textures_dict["aa"]  # All values of dictionary should be the same.
        else:
            texture = textures_dict[trans_key]
        yield texture, trans_key

def reposition_transition_vertices(corners, key: Literal["aa", "ab", "ac", "ba", "bb", "bc"]):

    corners = permutate_corners(corners, key)
    midpoint = (corners[0][0] + corners[1][0])/2,\
               (corners[0][1] + corners[1][1])/2

    # If transition_strech_factor is set to 1/3, following procedure is exactly the same as finding center of triangle.
    center = round(corners[2][0] * transition_stretch_factor + midpoint[0] * (1 - transition_stretch_factor)),\
             round(corners[2][1] * transition_stretch_factor + midpoint[1] * (1 - transition_stretch_factor))

    corners = corners[0], corners[1], center

    return corners

def permutate_corners(corners, key: Literal["aa", "ab", "ac", "ba", "bb", "bc"]):

    match key:
        case "aa": return corners[2], corners[0], corners[1]
        case "ab": return corners[0], corners[1], corners[2]
        case "ac": return corners[1], corners[2], corners[0]
        case "ba": return corners[0], corners[1], corners[2]
        case "bb": return corners[2], corners[0], corners[1]
        case "bc": return corners[1], corners[2], corners[0]
        case _: raise ValueError
