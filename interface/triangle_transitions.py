from functools import lru_cache
from map import Map
import random
from interface.triangles import get_triangle_corner_vertices
from supplements.patterns import corner_types, patterndefs_normal, patterndefs_normal_by_groups,\
                                 triangle_transitions_by_corner_types

def update_triangles(editor, triangles: list | tuple):

    # Some of the visual triangle transitions present in game might not be correctly filled by this function due to
    # incomplete data present in files of "Cultures: Discovery of Vinland" and "Cultures: The Revenge of the Rain God".
    # It is assumed that original developers for some of the transitions used macromaps instead of algorithm like this.

    for triangle in triangles:
        vertices = get_triangle_corner_vertices(*triangle)
        local_corner_types = tuple(map(lambda vertex: get_corner_type(editor.map, vertex), vertices))
        if len(set(local_corner_types)) == 2 and None not in local_corner_types:
            try:
                transitions_list = triangle_transitions_by_corner_types[tuple(sorted(set(local_corner_types)))]
            except KeyError:
                continue  # Transition does not exist.

            transition = random.choice(transitions_list)

            value = (local_corner_types[0] == transition["corner_types"][0]) + \
                    (local_corner_types[1] == transition["corner_types"][0]) * 2 + \
                    (local_corner_types[2] == transition["corner_types"][0]) * 4 + \
                    -1

            match triangle[1]:
                case "a": transitions_mep_id = transition["transitions_a"]
                case "b": transitions_mep_id = transition["transitions_b"]
                case _: raise ValueError

            mep_id = transitions_mep_id[2 * value] * 256 + transitions_mep_id[2 * value + 1]

            editor.update_triange(*triangle, mep_id)

        elif len(set(local_corner_types)) == 1 and None not in local_corner_types:

            index_bytes = triangle[0][1] * editor.map.map_width + triangle[0][0] * 2

            match triangle[1]:
                case "a": old_mep_id = int.from_bytes(editor.map.mepa[index_bytes: index_bytes + 2], byteorder="little")
                case "b": old_mep_id = int.from_bytes(editor.map.mepb[index_bytes: index_bytes + 2], byteorder="little")
                case _: raise ValueError

            possible_mep_ids = set()
            for corner_group in corner_types[local_corner_types[0]]["groups"]:
                possible_mep_ids.update(patterndefs_normal_by_groups.get(corner_group.lower(), set()))

            if (old_mep_id in possible_mep_ids) or (corner_types[local_corner_types[0]]["number"] > 2):
                continue

            editor.update_triange(*triangle, random.choice(tuple(possible_mep_ids)))

    get_corner_type.cache_clear()  # Usage of cache here is not only for optimization purposes, but also provides a look
                                   # into original corners before any of triangles was modified in current frame.


@lru_cache(maxsize=None)
def get_corner_type(map_object: Map, major_coordinates):
    x, y = major_coordinates

    # Order of coordinates in tuple is important here due to transition triangles.
    # For deeper intuition look at textures of trinagles with names: "0" "1" "2" "x0" "x1" "x2".
    if y % 2 == 0:
        mepa_coordinates = (x - 1, y - 1), (x, y - 1), (x, y)
        mepb_coordinates = (x - 1, y), (x - 1, y - 1), (x, y)  #
    elif y % 2 == 1:
        mepa_coordinates = (x, y - 1), (x + 1, y - 1), (x, y)
        mepb_coordinates = (x - 1, y), (x, y - 1),  (x, y)
    else:
        raise ValueError

    mep_ids = list()

    for coordinates_tuple, triangle_type in zip((mepa_coordinates, mepb_coordinates), ("a", "b")):
        for coordinates_index, coordinates in enumerate(coordinates_tuple):
            if not(0 <= coordinates[0] < map_object.map_width // 2
               and 0 <= coordinates[1] < map_object.map_height // 2):
                continue

            value_index = coordinates[1] * map_object.map_width + coordinates[0] * 2

            match triangle_type:
                case "a": mep_id = int.from_bytes(map_object.mepa[value_index: value_index+2], byteorder="little")
                case "b": mep_id = int.from_bytes(map_object.mepb[value_index: value_index+2], byteorder="little")
                case _: raise ValueError

            name = patterndefs_normal[mep_id]["Name"]

            for num in range(3):
                if (name == f"{num}" and coordinates_index != num) or\
                   (name == f"x{num}" and coordinates_index == num):
                    continue

            mep_ids.append(mep_id)

    mep_groups = [patterndefs_normal[mep_id]["Group"].lower() for mep_id in mep_ids]
    mep_maingroups = [patterndefs_normal[mep_id]["MainGroup"].lower() for mep_id in mep_ids]

    for corner_type in corner_types.values():
        counts = 0
        for corner_group in corner_type["groups"]:
            groups_indices = {i for i, group in enumerate(mep_groups) if group == corner_group.lower()}
            groups_indices.update({i for i, group in enumerate(mep_maingroups) if group == corner_group.lower()})
            counts += len(groups_indices)
            if counts >= corner_type["number"]:
                return corner_type["name"]
    else:
        return None
