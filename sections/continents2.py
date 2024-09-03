import numpy as np
from sections.terrain_full_ids import void_full_ids, water_full_ids

land_marker = 0
water_marker = 1
void_marker = 255

minimum_continent_size = 10


def flood_fill_continents(area_types_ndarray: np.ndarray, *, minimum_area_size=minimum_continent_size):
    map_height, map_width = area_types_ndarray.shape

    xcot_information = []

    continent_id = 0
    map_continents_2 = np.zeros(shape=area_types_ndarray.shape, dtype=np.ubyte)
    is_filled = np.zeros(shape=area_types_ndarray.shape, dtype=np.bool_)

    for y in range(map_height):
        for x in range(map_width):

            if is_filled[y, x]:
                continue

            if area_types_ndarray[y, x] == void_marker:
                map_continents_2[y, x] = void_marker
                is_filled[y, x] = True
                continue

            value = int(area_types_ndarray[y, x])
            coordinates_to_iterate = [(x, y)]
            continent_coordinates = [(x, y)]
            map_continents_2[y, x] = continent_id
            is_filled[y, x] = True
            size = 1

            while coordinates_to_iterate:
                coordinates = coordinates_to_iterate.pop(0)

                if coordinates[1] % 2 == 0:

                    neighbours = [(coordinates[0] + 1, coordinates[1]),
                                  (coordinates[0], coordinates[1] + 1),
                                  (coordinates[0] - 1, coordinates[1]),
                                  (coordinates[0], coordinates[1] - 1),
                                  (coordinates[0] - 1, coordinates[1] + 1),
                                  (coordinates[0] - 1, coordinates[1] - 1)]
                else:
                    neighbours = [(coordinates[0] + 1, coordinates[1]),
                                  (coordinates[0], coordinates[1] + 1),
                                  (coordinates[0] - 1, coordinates[1]),
                                  (coordinates[0], coordinates[1] - 1),
                                  (coordinates[0] + 1, coordinates[1] + 1),
                                  (coordinates[0] + 1, coordinates[1] - 1)]

                for neighbour in neighbours:
                    if 0 <= neighbour[0] < map_width and 0 <= neighbour[1] < map_height and\
                       not is_filled[*neighbour[::-1]] and area_types_ndarray[*neighbour[::-1]] == value:
                        coordinates_to_iterate.append(neighbour)
                        continent_coordinates.append(neighbour)
                        map_continents_2[*neighbour[::-1]] = continent_id
                        is_filled[*neighbour[::-1]] = True
                        size += 1

            # This construction allows for saving "fake" continent if it is the last continent.
            # This is a historically accurate way to reconstruct mco2 section, but that "fake" continent is redundant.
            if continent_id == len(xcot_information):
                xcot_information.append((value, (x, y), size))
            elif continent_id < len(xcot_information):  # overwrite "fake" continent
                xcot_information[continent_id] = (value, (x, y), size)
            else:
                raise IndexError

            if size < minimum_area_size:
                for coordinates in continent_coordinates:
                    map_continents_2[*coordinates[::-1]] = 255
            else:
                continent_id += 1

            if continent_id >= void_marker:
                raise OverflowError

    return map_continents_2, xcot_information


def area_types_marker(mepa: bytes, mepb: bytes, map_width: int, map_height: int, *,
                      void_data=void_full_ids, water_data=water_full_ids):

    mepa_ndarray = np.frombuffer(mepa, dtype=np.ushort).reshape((map_height//2, map_width//2))
    mepb_ndarray = np.frombuffer(mepb, dtype=np.ushort).reshape((map_height//2, map_width//2))

    area_types_ndarray = np.zeros(shape=(map_height, map_width), dtype=np.ubyte)
    area_types_ndarray.fill(water_marker)

    for y in range(map_height//2):
        for x in range(map_width//2):

            if y % 2 == 0:
                mepa_coordinates = [(2*x, 2*y), (2*x, 2*y+1), (2*x+1, 2*y+2),
                                    (2*x, 2*y+2), (2*x-1, 2*y+2), (2*x-1, 2*y+1)]
                mepb_coordinates = [(2*x, 2*y), (2*x+1, 2*y), (2*x+2, 2*y),
                                    (2*x+1, 2*y+1), (2*x+1, 2*y+2), (2*x, 2*y+1)]
            else:
                mepa_coordinates = [(2*x+1, 2*y), (2*x+1, 2*y+1), (2*x+2, 2*y+2),
                                    (2*x+1, 2*y+2), (2*x, 2*y+2), (2*x, 2*y+1)]
                mepb_coordinates = [(2*x+1, 2*y), (2*x+2, 2*y), (2*x+3, 2*y),
                                    (2*x+2, 2*y+1), (2*x+2, 2*y+2), (2*x+1, 2*y+1)]

            mepa_full_id = int(mepa_ndarray[y, x])
            mepb_full_id = int(mepb_ndarray[y, x])

            for full_id, coordinates_list in ((mepa_full_id, mepa_coordinates), (mepb_full_id, mepb_coordinates)):

                if (full_id not in void_data) and (full_id not in water_data):
                    for coordinates in coordinates_list:
                        if not (0 <= coordinates[0] < map_width and 0 <= coordinates[1] < map_height):
                            continue  # out of bounds
                        area_types_ndarray[*coordinates[::-1]] = land_marker

                if full_id not in water_data:
                    for coordinates in coordinates_list:
                        if not (0 <= coordinates[0] < map_width and 0 <= coordinates[1] < map_height) or\
                           area_types_ndarray[*coordinates[::-1]] == land_marker:
                            continue
                        area_types_ndarray[*coordinates[::-1]] = void_marker

    return area_types_ndarray.tobytes()


def derive_continents(mepa: bytes, mepb: bytes, map_width: int, map_height: int, *,
                      minimum_area_size=minimum_continent_size):

    area_types_ndarray = np.frombuffer(area_types_marker(mepa, mepb, map_width, map_height),
                                       dtype=np.ubyte).reshape((map_height, map_width))
    map_continents_2, xcot_information = flood_fill_continents(area_types_ndarray, minimum_area_size=minimum_area_size)

    return map_continents_2.tobytes(), xcot_information
