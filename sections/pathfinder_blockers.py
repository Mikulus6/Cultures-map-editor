import numpy as np
from PIL import Image, ImageDraw
from typing import Literal
from scripts.expansions import triangle_a_shadow
from scripts.flags import bool_ndarray_to_flag, flag_to_bool_ndarray, sequence_to_flags
from sections.mesh_points import get_adjacent_mep_coordinates
from sections.terrain_full_ids import land_full_ids

maximum_allowed_steepness = 30


def get_shift_vector(flag_index):
    match flag_index:
        case 0: return -1, 1
        case 1: return 0, 1
        case 2: return 1, 0
        case _: raise ValueError


def pathfinder_blockers_area_shifted(mgfs_7th_flag, mepa, mepb, mhei, map_width, map_height, *,
                                     flag_index=Literal[0, 1, 2]):

    shift_vector = get_shift_vector(flag_index)
    mepa_ndarray = np.frombuffer(mepa, dtype=np.ushort).reshape((map_height//2, map_width//2))
    mepb_ndarray = np.frombuffer(mepb, dtype=np.ushort).reshape((map_height//2, map_width//2))
    mgfs_7_ndarray = flag_to_bool_ndarray(mgfs_7th_flag, map_width=map_width)
    steepness_blockades = calculate_steepness(mhei, map_width, map_height, shift_vector)
    build_vertices_ndarray = np.zeros(shape=(map_height, map_width), dtype=np.bool_)

    for y in range(map_height):
        for x in range(map_width):

            if y % 2 == shift_vector[1] % 2 == 1: local_shift_vector = shift_vector[0] + 1, shift_vector[1]
            else:                                 local_shift_vector = shift_vector

            displacement = [x + local_shift_vector[0],
                            y + local_shift_vector[1]]

            if mep_walkability((x, y), displacement, mepa_ndarray, mepb_ndarray, map_width, map_height):
                build_vertices_ndarray[y, x] = True

            for coordinates in ([x, y], displacement):
                coordinates[0] %= map_width
                coordinates[1] %= map_height

                if mgfs_7_ndarray[*coordinates[::-1]] == 1 or steepness_blockades[y, x]:
                    build_vertices_ndarray[y, x] = False

    return bool_ndarray_to_flag(build_vertices_ndarray)


def mep_walkability(coordinates_1, coordinates_2, mepa_ndarray, mepb_ndarray, map_width, map_height):

    mepa_triangles_1, mepb_triangles_1 = get_adjacent_mep_coordinates(coordinates_1)
    mepa_triangles_2, mepb_triangles_2 = get_adjacent_mep_coordinates(coordinates_2)

    mepa_triangles_common = [(x % (map_width//2), y % (map_height//2)) for x, y in mepa_triangles_1 if (x, y) in mepa_triangles_2]
    mepb_triangles_common = [(x % (map_width//2), y % (map_height//2)) for x, y in mepb_triangles_1 if (x, y) in mepb_triangles_2]

    for mep_ndarray, mep_triangles_common in zip((mepa_ndarray, mepb_ndarray),
                                                 (mepa_triangles_common, mepb_triangles_common)):
        for common_triangle in mep_triangles_common:
            if mep_ndarray[*common_triangle[::-1]] in land_full_ids:
                return True
    return False


def interpolate_hexagonal_ndarray(ndarray: np.ndarray) -> np.ndarray:
    assert len(ndarray.shape) == 2

    ndarray_new = np.zeros((ndarray.shape[0] * 2, ndarray.shape[1] * 2), dtype=ndarray.dtype)
    ndarray_new.fill(0)

    for x in range(ndarray_new.shape[1]):
        for y in range(ndarray_new.shape[0]):

            # Following conditions might look unintuitive, but those are only responsible for handling different
            # neighbouring conditions for bilinear bisection of vertices from regular triangular grid.

            if (x % 2 == 0 and y % 4 == 0) or (x % 2 == 1 and y % 4 == 2):
                ndarray_new[y, x] = ndarray[y // 2, x // 2] # do not interpolate
                continue

            elif (x % 2 == 1 and y % 4 == 0) or (x % 2 == 0 and y % 4 == 2):
                vertices = [x - 1, y], [x + 1, y]
            elif (x % 2 == 0 and y % 4 == 1) or (x % 2 == 1 and y % 4 == 3):
                vertices = [x, y - 1], [x + 1, y + 1]
            elif (x % 2 == 1 and y % 4 == 1) or (x % 2 == 0 and y % 4 == 3):
                vertices = [x + 1, y - 1], [x, y + 1]

            else:
                raise IndexError  # this case should be unobtainable

            vertices = [[value//2 % bound for value, bound in zip(vertex, ndarray.shape[::-1])] for vertex in vertices]

            ndarray_new[y, x] = (int(ndarray[*(vertices[0])[::-1]]) + int(ndarray[*(vertices[1])[::-1]]))//2

    return ndarray_new


def calculate_steepness(mhei, map_width, map_height, shift_vector=(0, 0)):
    mhei_interpolated = interpolate_hexagonal_ndarray(np.frombuffer(mhei, dtype=np.ubyte).reshape((map_height//2,
                                                                                                   map_width//2)))
    steepness_blockades = np.zeros_like(mhei_interpolated, dtype=np.bool_)

    for y in range(map_height):
        for x in range(map_width):

            if y % 2 == shift_vector[1] % 2 == 1: local_shift_vector = shift_vector[0] + 1, shift_vector[1]
            else:                                 local_shift_vector = shift_vector

            new_coordinates = [(x + local_shift_vector[0]) % map_width,
                               (y + local_shift_vector[1]) % map_height]

            steepness_blockades[y, x] = True if abs(int(mhei_interpolated[*new_coordinates[::-1]])-\
                                                    int(mhei_interpolated[y, x])) > maximum_allowed_steepness else False
    return steepness_blockades


def draw_pathfinder_blockers(mgfs, map_width: int, map_height: int, color_connections=(255, 255, 255),
                             unit_size=triangle_a_shadow.shape[::-1]):

    image = ImageDraw.Draw(Image.new("RGB", size=(map_width * unit_size[0],
                                                  map_height * unit_size[1]), color=(0, 0, 0)))
    mgfs_flags = sequence_to_flags(mgfs)

    get_draw_coords = lambda x_, y_: ((unit_size[0] // 2 - 1 if y_ % 2 == 0 else unit_size[0] - 1) + x_ * unit_size[0],
                                       unit_size[1] * y_)

    mgfs_0 = flag_to_bool_ndarray(mgfs_flags[0], map_width=map_width)
    mgfs_1 = flag_to_bool_ndarray(mgfs_flags[1], map_width=map_width)
    mgfs_2 = flag_to_bool_ndarray(mgfs_flags[2], map_width=map_width)

    del mgfs_flags
    mgfs_ndarrays = [mgfs_0, mgfs_1, mgfs_2]

    for y in range(map_height):
        for x in range(map_width):
            for flag_index in range(3):

                if mgfs_ndarrays[flag_index][y, x]:

                    shift_vector = get_shift_vector(flag_index)

                    if y % 2 == shift_vector[1] % 2 == 1: local_shift_vector = shift_vector[0] + 1, shift_vector[1]
                    else:                                 local_shift_vector = shift_vector

                    line = get_draw_coords(x, y), get_draw_coords(x + local_shift_vector[0],
                                                                  y + local_shift_vector[1])
                    image.line(line, fill=color_connections)

    return image._image # noqa
