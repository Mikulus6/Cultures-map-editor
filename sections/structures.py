import numpy as np
from scripts.colormap import mstr_colormap

empty_color = (0, 0, 0)
assert empty_color not in mstr_colormap.values()

def coordinates_in_radius(start_position, radius):
    coordinates_set_old = set()
    coordinates_set = {start_position}
    coordinates_set_new = set()

    for _ in range(radius):
        for coordinates in coordinates_set:
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

            coordinates_set_new.update(neighbours)
            coordinates_set_new -= coordinates_set
            coordinates_set_new -= coordinates_set_old

        coordinates_set_old.update(coordinates_set)
        coordinates_set = {*coordinates_set_new}
    coordinates_set_old.update(coordinates_set)

    return coordinates_set_old

even_row_reference = (coordinates_in_radius((0, 0), 5), (0, 0))
odd_row_reference  = (coordinates_in_radius((0, 1), 5), (0, 1))

def derive_structures_water_flag(mstr, mco2, xcot, map_width, map_height):

    mstr_ndarray = np.frombuffer(mstr, dtype=np.ushort).reshape((map_height, map_width))
    mstr_new_ndarray = np.zeros_like(mstr_ndarray)
    mco2_ndarray = np.frombuffer(mco2, dtype=np.ubyte).reshape((map_height, map_width))

    for y in range(map_height):
        for x in range(map_width):

            row_referece = even_row_reference if y % 2 == 0 else odd_row_reference

            for coordinates in row_referece[0]:
                coordinates = ((x + coordinates[0] - row_referece[1][0]) % map_width,
                               (y + coordinates[1] - row_referece[1][1]) % map_height)

                if mco2_ndarray[*coordinates[::-1]] == 255 or xcot[mco2_ndarray[*coordinates[::-1]]][0] == 0:
                    break

            else:
                mstr_new_ndarray[y, x] = 1


    return ((mstr_new_ndarray * 256) + (mstr_ndarray % 256)).tobytes()


def validate_structures_continuity(mstr, map_width, map_height):
    mstr_ndarray = np.frombuffer(mstr, dtype=np.ushort).reshape((map_height, map_width))

    try:

        for y in range(map_height):
            for x in range(map_width):

                assert mstr_ndarray[y, x] & 48 != 48
                assert mstr_ndarray[y, x] & 192 != 192

                if y % 2 == 0:
                    conditions = [(x, y, 1), (x-1, y, 2), (x, y-1, 4), (x-1, y-1, 8)]
                else:
                    conditions = [(x, y, 1), (x-1, y, 2), (x+1, y-1, 4), (x, y-1, 8)]

                state = []
                for x_temp, y_temp, mask in conditions:
                    x_temp %= map_width
                    y_temp %= map_height

                    state.append(bool(mstr_ndarray[y_temp, x_temp] & mask))

                assert not(False in state and True in state)

                if True in state:
                    value_a = mstr_ndarray[y, x] & 48
                    value_b = mstr_ndarray[y, x] & 192

                    if y % 2 == 0:
                        conditions = [(x, y, "ab"), (x-1, y, "b"), (x, y-1, "a"), (x-1, y-1, "ab")]
                    else:
                        conditions = [(x, y, "ab"), (x-1, y, "b"), (x+1, y-1, "a"), (x, y-1, "ab")]

                    for x_temp, y_temp, triangles in conditions:
                        x_temp %= map_width
                        y_temp %= map_height
                        value_a_temp = mstr_ndarray[y_temp, x_temp] & 48
                        value_b_temp = mstr_ndarray[y_temp, x_temp] & 192

                        match triangles:
                            case "ab": assert value_a == value_a_temp and value_b == value_b_temp
                            case "a": assert value_a == value_a_temp
                            case "b": assert value_b == value_b_temp
                            case _: raise ValueError

    except AssertionError:
        return False
    else:
        return True


def update_structures(mstr, mco2, xcot, map_width, map_height):
    return derive_structures_water_flag(mstr, mco2, xcot, map_width, map_height)


def structures_to_rgb(mstr, map_width, map_height):
    mstr_ndarray = np.frombuffer(mstr, dtype=np.ushort).reshape((map_height, map_width))
    rgb_data = []

    for y in range(map_height):
        for x in range(map_width):
            if y % 2 == 0:
                conditions = [(x, y, 1, "ab"), (x-1, y, 2, "b"), (x, y-1, 4, "a"), (x-1, y-1, 8, "ab")]
            else:
                conditions = [(x, y, 1, "ab"), (x-1, y, 2, "b"), (x+1, y-1, 4, "a"), (x, y-1, 8, "ab")]

            for x_temp, y_temp, mask, triangles in conditions:
                x_temp %= map_width
                y_temp %= map_height

                if mstr_ndarray[y_temp, x_temp] & mask:
                    value = (mstr_ndarray[y_temp, x_temp] & 192 if triangles == "b"
                             else mstr_ndarray[y_temp, x_temp] & 48) // 16
                    break
            else:
                value = None

            # 0 = road
            # 1 = water
            # 2 = snow

            if value is not None:
                rgb_data.append(mstr_colormap[value])
            else:
                rgb_data.append(empty_color)

    return rgb_data


def rgb_to_structures(rgb_data, mco2, xcot, map_width, map_height):
    mstr_ndarray = np.zeros((map_height, map_width), dtype=np.ushort)

    for index_value, rgb_pixel in enumerate(rgb_data):
        x, y = index_value % map_width, index_value // map_width

        rgb_pixel = tuple(rgb_pixel)[:3]
        if tuple(rgb_pixel)[:3] == empty_color:
            continue
        value = mstr_colormap.inversed[tuple(rgb_pixel)[:3]]
        
        if y % 2 == 0:
            conditions = [(x, y, 1, "ab"), (x-1, y, 2, "b"), (x, y-1, 4, "a"), (x-1, y-1, 8, "ab")]
        else:
            conditions = [(x, y, 1, "ab"), (x-1, y, 2, "b"), (x+1, y-1, 4, "a"), (x, y-1, 8, "ab")]

        for x_temp, y_temp, mask, triangles in conditions:
            x_temp %= map_width
            y_temp %= map_height

            mstr_ndarray[y_temp, x_temp] = mstr_ndarray[y_temp, x_temp] | mask

            match triangles:
                case "ab": value_flag = value * 16 + value * 64;
                case "a": value_flag = value * 16;
                case "b": value_flag = value * 64;
                case _: raise ValueError

            mstr_ndarray[y_temp, x_temp] = mstr_ndarray[y_temp, x_temp] | value_flag

    if not validate_structures_continuity(mstr_ndarray.tobytes(), map_width, map_height):
        raise ValueError("Terrain overlay is not coherent per vertex.")

    return update_structures(mstr_ndarray.tobytes(), mco2, xcot, map_width, map_height)
