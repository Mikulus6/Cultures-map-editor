import numpy as np
from scripts.flags import bool_ndarray_to_flag, flag_to_bool_ndarray
from sections.continents2 import land_marker, derive_continents


def buildability_area_shifted(mgfs_7th_flag, mepa, mepb, map_width, map_height, *, shift_vector=(0, 0),
                              use_coastline_fix):

    build_vertices_ndarray = np.ones(shape=(map_height, map_width), dtype=np.bool_)
    area_flag_ndarray = flag_to_bool_ndarray(mgfs_7th_flag, map_width=map_width)
    pseudo_mco2, pseudo_xcot = derive_continents(mepa, mepb, map_width, map_height, minimum_area_size=0)
    mco2_ndarray = np.frombuffer(pseudo_mco2, dtype=np.ubyte).reshape((map_height, map_width))

    for y in range(map_height):
        for x in range(map_width):

            if y % 2 == shift_vector[1] % 2 == 1:
                local_shift_vector = (shift_vector[0] - 1, shift_vector[1])
            else:
                local_shift_vector = shift_vector

            displacement = (x-local_shift_vector[0],
                            y-local_shift_vector[1])

            for coordinates in ((x, y), displacement):
                coordinates[0] %= map_width
                coordinates[1] %= map_height

                if area_flag_ndarray[*coordinates[::-1]] == 1:
                    build_vertices_ndarray[y, x] = False

                if mco2_ndarray[*coordinates[::-1]] == 255:
                    build_vertices_ndarray[y, x] = False
                elif pseudo_xcot[mco2_ndarray[*coordinates[::-1]]][0] != land_marker:
                    build_vertices_ndarray[y, x] = False

            # Todo: Following part of algorithm is not complete.
            # Buildability of buildings is affected by two remaining factors which are not fully implemented here:
            #   1. shape of borders between continents
            #   2. steepness of terrain
            # However, even if this algorithm is not complete, original Cultures game fixes all of mistakes upon loading
            # any map - therefore as far as I am concerned this data is not directly responsible for the exact  content
            # of the in-game map. Following conditions were found by trials and errors, they are enough to fix roughly
            # 36% of all remaining mistakes.

            if shift_vector == (1, -1):
                if y % 2 == 0:
                    neighbour_all_waters = [[(x, y + 1), (x + 1, y + 2)],
                                            [(x, y + 1), (x + 2, y)]]
                    neighbour_all_lands = [[(x + 1, y), (x, y + 2)],
                                           [(x + 1, y), (x, y + 2)]]
                else:
                    neighbour_all_waters = [[(x - 1, y), (x - 1, y - 1)],
                                            [(x - 1, y), (x - 2, y + 1)]]
                    neighbour_all_lands = [[(x, y - 1), (x - 1, y + 1)],
                                           [(x, y - 1), (x - 1, y + 1)]]
            elif shift_vector == (0, -1):
                if y % 2 == 0:
                    neighbour_all_waters = [[(x - 1, y + 1), (x - 1, y + 2)],
                                            [(x - 1, y + 1), (x - 2, y)]]
                    neighbour_all_lands = [[(x - 1, y), (x, y + 2)],
                                           [(x - 1, y), (x, y + 2)]]
                else:
                    neighbour_all_waters = [[(x + 1, y), (x + 3, y + 1)],
                                            [(x + 1, y), (x + 2, y - 1)]]
                    neighbour_all_lands = [[(x + 1, y - 1), (x + 2, y + 1)],
                                           [(x + 1, y - 1), (x + 2, y + 1)]]

            elif shift_vector == (-1, 0):
                if y % 2 == 0:
                    neighbour_all_waters = []
                    neighbour_all_lands = []
                else:
                    neighbour_all_waters = [[(x + 1, y - 1), (x + 1, y - 2)],
                                            [(x + 1, y - 1), (x, y - 2)],
                                            [(x + 1, y + 1), (x + 1, y + 2)],
                                            [(x + 1, y + 1), (x, y + 2)]]
                    neighbour_all_lands = [[(x, y - 1), (x + 1, y)],
                                           [(x, y - 1), (x + 1, y)],
                                           [(x + 1, y), (x, y + 1)],
                                           [(x + 1, y), (x, y + 1)]]

            elif shift_vector == (0, 0):
                continue  # case only for technical purposes.

            else:
                raise NotImplementedError

            if mco2_ndarray[y, x] == 255:
                continue
            elif pseudo_xcot[mco2_ndarray[y, x]][0] != land_marker:
                continue

            for neighbour_waters, neighbour_lands in zip(neighbour_all_waters, neighbour_all_lands):
                continue_past = False
                for neighbour_water in neighbour_waters:
                    if mco2_ndarray[*neighbour_water[::-1]] == 255:
                        continue
                    elif not pseudo_xcot[mco2_ndarray[*neighbour_water[::-1]]][0] != land_marker:
                        continue_past = True
                        break

                for neighbour_land in neighbour_lands:
                    if mco2_ndarray[*neighbour_land[::-1]] == 255:
                        continue_past = True
                        break
                    elif not pseudo_xcot[mco2_ndarray[*neighbour_land[::-1]]][0] == land_marker:
                        continue_past = True
                        break

                if continue_past or not use_coastline_fix:
                    continue

                build_vertices_ndarray[y, x] = False
                break

    return bool_ndarray_to_flag(build_vertices_ndarray)
