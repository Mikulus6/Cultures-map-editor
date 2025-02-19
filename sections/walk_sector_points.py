import numpy as np
from PIL import Image, ImageDraw
from sections.continents2 import void_marker, land_marker
from scripts.expansions import expand_image
from scripts.flags import sequence_to_flags, flag_to_bool_ndarray
from scripts.image import get_rgb_hue_tuple

sector_width = 20
max_search_radius = 21


def check_sectors_coherency(mco2: bytes, sectors: list, map_width: int, map_height: int):

    mco2_ndarray = np.frombuffer(mco2, dtype=np.ubyte).reshape((map_height, map_width))
    sectors_width = map_width // sector_width + (1 if map_width % sector_width != 0 else 0)
    sectors_height = map_height // sector_width + (1 if map_height % sector_width != 0 else 0)

    try:
        for index_value, sector in enumerate(sectors):
            sector_type, sector_value, coordinates = sector

            if sector_type == 0:
                assert sector_value == "00000000"

            sector_x, sector_y = index_value % sectors_width, index_value // sectors_width

            neighbours = [[sector_x + 1, sector_y - 1],
                          [sector_x, sector_y - 1],
                          [sector_x - 1, sector_y - 1],
                          [sector_x - 1, sector_y],
                          [sector_x - 1, sector_y + 1],
                          [sector_x, sector_y + 1],
                          [sector_x + 1, sector_y + 1],
                          [sector_x + 1, sector_y]]

            for neighbour_relative_index, neighbour in enumerate(neighbours):
                neighbour_sector_index = neighbour[1] * sectors_width + neighbour[0]

                if not(0 <= neighbour[0] < sectors_width and 0 <= neighbour[1] < sectors_height):
                    assert int(sector_value[neighbour_relative_index]) == 0
                    continue

                neighbour_type, neighbour_value, neighbour_coordinates = sectors[neighbour_sector_index]

                if neighbour_type == 0:
                    assert neighbour_value == "00000000"
                assert sector_value[neighbour_relative_index] == neighbour_value[(neighbour_relative_index + 4) % 8]

                if int(sector_value[neighbour_relative_index]) == 1:
                    assert mco2_ndarray[*coordinates[::-1]] == mco2_ndarray[*neighbour_coordinates[::-1]]

    except AssertionError:
        return False
    return True


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


def check_connection(mgfs_ndarrays, coordinates_start, coordinates_end):

    min_x = (min(coordinates_start[0], coordinates_end[0]) // sector_width) * sector_width
    min_y = (min(coordinates_start[1], coordinates_end[1]) // sector_width) * sector_width
    max_x = ((max(coordinates_start[0], coordinates_end[0]) // sector_width) + 1) * sector_width - 1
    max_y = ((max(coordinates_start[1], coordinates_end[1]) // sector_width) + 1) * sector_width - 1

    queue = [coordinates_start]
    visited = {coordinates_start}

    while len(queue) > 0:
        coordinates = queue.pop(0)

        if coordinates == coordinates_end:
            return True

        for direction in range(6):
            x, y = get_tile_in_direction(*coordinates, direction)

            if (min_x <= x <= max_x and min_y <= y <= max_y) and (x, y) not in visited:

                match direction:
                    case 0: path_exist = mgfs_ndarrays[2][*coordinates[::-1]]
                    case 1: path_exist = mgfs_ndarrays[1][*coordinates[::-1]]
                    case 2: path_exist = mgfs_ndarrays[0][*coordinates[::-1]]
                    case 3: path_exist = mgfs_ndarrays[2][*(get_tile_in_direction(*coordinates, direction)[::-1])]
                    case 4: path_exist = mgfs_ndarrays[1][*(get_tile_in_direction(*coordinates, direction)[::-1])]
                    case 5: path_exist = mgfs_ndarrays[0][*(get_tile_in_direction(*coordinates, direction)[::-1])]
                    case _: raise ValueError

                if path_exist:
                    visited.add((x, y))
                    queue.append((x, y))

    return False


def derive_connections(mgfs, sectors, map_width, map_height):

    sectors_width = map_width // sector_width + (1 if map_width % sector_width != 0 else 0)
    sectors_height = map_height // sector_width + (1 if map_height % sector_width != 0 else 0)

    mgfs_flags = sequence_to_flags(mgfs)

    mgfs_0_ndarray = flag_to_bool_ndarray(mgfs_flags[0], map_width=map_width)
    mgfs_1_ndarray = flag_to_bool_ndarray(mgfs_flags[1], map_width=map_width)
    mgfs_2_ndarray = flag_to_bool_ndarray(mgfs_flags[2], map_width=map_width)

    mgfs_ndarrays = [mgfs_0_ndarray,
                     mgfs_1_ndarray,
                     mgfs_2_ndarray]

    for index_value, sector in enumerate(sectors):
        sector_type, sector_value, coordinates = sector

        if sector_type == 0:
            continue

        sector_x, sector_y = index_value % sectors_width, index_value // sectors_width

        neighbours = [[sector_x + 1, sector_y - 1],
                      [sector_x, sector_y - 1],
                      [sector_x - 1, sector_y - 1],
                      [sector_x - 1, sector_y],
                      [sector_x - 1, sector_y + 1],
                      [sector_x, sector_y + 1],
                      [sector_x + 1, sector_y + 1],
                      [sector_x + 1, sector_y]]

        for neighbour_relative_index, neighbour in enumerate(neighbours):
            neighbour_sector_index = neighbour[1] * sectors_width + neighbour[0]

            if not(0 <= neighbour[0] < sectors_width and 0 <= neighbour[1] < sectors_height):
                continue

            neighbour_type, neighbour_value, neighbour_coordinates = sectors[neighbour_sector_index]

            if neighbour_type == 0:
                continue

            if check_connection(mgfs_ndarrays, coordinates, neighbour_coordinates):

                sectors[index_value][1] = sectors[index_value][1][:neighbour_relative_index] + "1" + \
                                          sectors[index_value][1][neighbour_relative_index+1:]

    return sectors


def update_sectors(mgfs, mco2, xcot, map_width, map_height):

    mco2_ndarray = np.frombuffer(mco2, dtype=np.ubyte).reshape((map_height, map_width))
    mgfs_flag_7 = flag_to_bool_ndarray(sequence_to_flags(mgfs)[7], map_width=map_width)

    sectors = []
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

        try:
            if xcot[largest_continent_id][0] == land_marker:
                validity_subarray = np.logical_and(mco2_subarray == largest_continent_id, mgfs_flag_7_subarray == False)
            else:
                validity_subarray = np.zeros_like(mco2_subarray).astype(np.bool_)

            coordinates = search_valid_coordinates(validity_subarray)
            coordinates = (coordinates[0] + sector_x, coordinates[1] + sector_y)
            sector_type = 1
        except (IndexError, ValueError):
            coordinates = (0, 0)
            sector_type = 0

        sectors.append([sector_type, "00000000", coordinates])

    return derive_connections(mgfs, sectors, map_width, map_height)


def draw_sectors_connections(mco2: bytes, sectors: list, map_width: int, map_height: int, expansion_mode=None):

    mco2_ndarray = np.frombuffer(mco2, dtype=np.ubyte).reshape((map_height, map_width))
    sectors_width = map_width // sector_width + (1 if map_width % sector_width != 0 else 0)
    sectors_height = map_height // sector_width + (1 if map_height % sector_width != 0 else 0)

    image = ImageDraw.Draw(Image.new("RGB", size=(map_width, map_height), color=(0, 0, 0)))

    # color palette generation - start
    continents_with_sectors = set()
    for sector in sectors:
        sector_type, sector_value, coordinates = sector
        if sector_type == 0:
            continue
        continents_with_sectors.add(int(mco2_ndarray[coordinates[::-1]]))

    colors_primary = tuple(map(lambda x: get_rgb_hue_tuple(x),
                               tuple(np.linspace(0, 1, len(continents_with_sectors)+1)[:-1])))
    colors_secondary = tuple(map(lambda x: tuple(map(lambda y: round(y/2), x)), colors_primary))

    continents_colors = {continent_id: (color_1, color_2) for continent_id, color_1, color_2
                         in zip(sorted(continents_with_sectors),colors_primary, colors_secondary)}
    del colors_primary, colors_secondary
    # color palette generation - end

    for index_value, sector in enumerate(sectors):
        sector_type, sector_value, coordinates = sector

        if sector_type == 0:
            continue

        sector_x, sector_y = index_value % sectors_width, index_value // sectors_width

        neighbours = [[sector_x + 1, sector_y - 1],
                      [sector_x, sector_y - 1],
                      [sector_x - 1, sector_y - 1],
                      [sector_x - 1, sector_y],
                      [sector_x - 1, sector_y + 1],
                      [sector_x, sector_y + 1],
                      [sector_x + 1, sector_y + 1],
                      [sector_x + 1, sector_y]]

        for neighbour_relative_index, neighbour in enumerate(neighbours):
            neighbour_sector_index = neighbour[1] * sectors_width + neighbour[0]

            if not (0 <= neighbour[0] < sectors_width and 0 <= neighbour[1] < sectors_height):
                continue

            neighbour_type, neighbour_value, neighbour_coordinates = sectors[neighbour_sector_index]

            if neighbour_type == 0:
                continue

            color_primary, color_secondary = continents_colors[int(mco2_ndarray[coordinates[::-1]])]

            if int(sector_value[neighbour_relative_index]) == 1:
                # Warning: rectangular line can became discontinuous when interpreted on hexagonal grid.
                image.line((coordinates, neighbour_coordinates), fill=color_secondary)

    for sector in sectors:
        sector_type, sector_value, coordinates = sector
        if sector_type == 0:
            continue
        color_primary, color_secondary = continents_colors[int(mco2_ndarray[coordinates[::-1]])]
        image.point(coordinates, fill=color_primary)

    return expand_image(image._image, expansion_mode=expansion_mode) # noqa
