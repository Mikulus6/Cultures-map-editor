import numpy as np
from sections.sectors import sector_width
from sections.continents2 import void_marker, land_marker
from scripts.flags import sequence_to_flags, flag_to_bool_ndarray

max_search_radius = 21


def largest_land_continent_in_sector(mco2_ndarray, sector_x, sector_y, xcot):
    mco2_subarray = mco2_ndarray[sector_y: sector_y + sector_width,
                                 sector_x: sector_x + sector_width]
    count_dict = {}

    largest_continent_size = 0
    largest_continent_id = 0

    for y in range(sector_width):
        for x in range(sector_width):
            element = mco2_subarray[y, x]

            if element == void_marker:
                continue

            terrain_type = xcot[element][0]

            if terrain_type == land_marker:
                count_dict[element] = count_dict.get(element, 0) + 1

                if count_dict[element] >= largest_continent_size:
                    largest_continent_size = count_dict[element]
                    largest_continent_id = element

    return largest_continent_id


def search_valid_coordinates(validity_subarray):
    x, y = 10, 10

    if validity_subarray[y, x]:
        return x, y

    for side_length in range(1, max_search_radius + 1):
        x, y = get_tile_in_direction(x, y, 4)

        for radius in range(6):
            for _ in range(side_length):

                if (0 <= x < sector_width and
                    0 <= y < sector_width) and validity_subarray[y, x]:
                    return x, y

                x, y = get_tile_in_direction(x, y, radius)

    raise ValueError  # no valid vertex


def get_tile_in_direction(x, y, direction):
    if y % 2 == 0: return [(x + 1, y), (x, y + 1), (x - 1, y + 1), (x - 1, y), (x - 1, y - 1), (x, y - 1)][direction]
    else:          return [(x + 1, y), (x + 1, y + 1), (x, y + 1), (x - 1, y), (x, y - 1), (x + 1, y - 1)][direction]


def section_test(mgfs, mco2, xcot, sectors, map_width, map_height):
    # TODO: finish this function

    mco2_ndarray = np.frombuffer(mco2, dtype=np.ubyte).reshape((map_height, map_width))

    mgfs_flag_7 = flag_to_bool_ndarray(sequence_to_flags(mgfs)[7], map_width=map_width)

    sectors_width = map_width // sector_width + (1 if map_width % sector_width != 0 else 0)

    for index_value in range(map_width * map_height // sector_width**2):

        sector_x, sector_y = index_value % sectors_width, index_value // sectors_width
        sector_x = sector_x * sector_width
        sector_y = sector_y * sector_width

        mco2_subarray = mco2_ndarray[sector_y: sector_y + sector_width,
                                     sector_x: sector_x + sector_width]

        mgfs_flag_7_subarray = mgfs_flag_7[sector_y: sector_y + sector_width,
                                           sector_x: sector_x + sector_width]

        largest_continent_id = largest_land_continent_in_sector(mco2_ndarray, sector_x, sector_y, xcot)

        if xcot[largest_continent_id][0] == land_marker:
            validity_subarray = np.logical_and(mco2_subarray == largest_continent_id, mgfs_flag_7_subarray == False)
        else:
            validity_subarray = np.zeros_like(mco2_subarray).astype(np.bool_)

        try:
            coordinates = search_valid_coordinates(validity_subarray)
            coordinates = (coordinates[0] + sector_x, coordinates[1] + sector_y)
            sector_type = 1
        except ValueError:
            coordinates = (0, 0)
            sector_type = 0

        sector_type_check, sector_value_check, coordinates_check = sectors[index_value]

        assert sector_type == sector_type_check
        assert coordinates == coordinates_check

        # TODO: derive sector value (that is: walk sector points connections data)

        if sector_type == 0:
            assert sector_value_check == "00000000"
