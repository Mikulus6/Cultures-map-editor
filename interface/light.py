from math import floor
from map import Map
from sections.light import shadow_kernel, shadow_kernel_center, min_value, inversed_slope, intercept, round_fix
from sections.terrain_full_ids import border_full_ids

kernel_height, kernel_width = shadow_kernel.shape


def update_light_local(map_object: Map, x_range_start: int = None, x_range_stop: int = None,
                                        y_range_start: int = None, y_range_stop: int = None):

    if x_range_start is None or x_range_start < 0:                         x_range_start = 0
    if x_range_stop  is None or x_range_stop > map_object.map_width // 2:  x_range_stop = map_object.map_width // 2
    if y_range_start is None or y_range_start < 0:                         y_range_start = 0
    if y_range_stop  is None or y_range_stop > map_object.map_height // 2: y_range_stop = map_object.map_height // 2

    for y in range(y_range_start, y_range_stop):
        for x in range(x_range_start, x_range_stop):
            x_real, y_real = x - shadow_kernel_center[0], y - shadow_kernel_center[1]
            conv_item = 0
            for y_shift in range(0, kernel_height):
                for x_shift in range(0, kernel_width):
                    x_real_shifted = x_real + x_shift
                    y_real_shifted = y_real + y_shift

                    if y % 2 == 0 or y_shift == 0:
                        kernel_item = shadow_kernel[y_shift, x_shift]
                    elif x_shift != 0:
                        kernel_item = shadow_kernel[y_shift, x_shift - 1]
                    else:
                        kernel_item = 0

                    index_shifted = (y_real_shifted % (map_object.map_height // 2)) * (map_object.map_width // 2) + \
                                     x_real_shifted % (map_object.map_width // 2)

                    conv_item += kernel_item * map_object.mhei[index_shifted]

            conv_item = min(max(int(conv_item) + 127, 0), 255)

            if conv_item >= min_value:
                conv_item = floor(conv_item / inversed_slope + intercept + round_fix)

            if y % 2 == 0:
                mepa_coordinates = ((x, y), (x, y - 1), (x - 1, y - 1))
                mepb_coordinates = ((x, y), (x - 1, y), (x - 1, y - 1))
            else:
                mepa_coordinates = ((x, y), (x, y - 1), (x + 1, y - 1))
                mepb_coordinates = ((x, y), (x, y - 1), (x - 1, y))

            try:
                for coordinates in mepb_coordinates:
                    index = coordinates[1] * map_object.map_width + coordinates[0] * 2
                    if int.from_bytes(map_object.mepb[index: index+2], byteorder='little') in border_full_ids:
                        raise ValueError

                for coordinates in mepa_coordinates:
                    index = coordinates[1] * map_object.map_width + coordinates[0] * 2
                    if int.from_bytes(map_object.mepa[index: index+2], byteorder='little') in border_full_ids:
                        raise ValueError

            except ValueError:
                conv_item = 0

            map_object.mlig[y * (map_object.map_width // 2) + x] = conv_item
