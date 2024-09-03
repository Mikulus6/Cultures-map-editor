from math import floor
import numpy as np
from sections.terrain_full_ids import border_full_ids

# shadow kernel
shadow_kernel = np.array([[-1.5, 0, 4.5],
                          [-4.5, 1.5, 0]])
shadow_kernel_center = (2, 0)

# linear interpolation
min_value = 180
inversed_slope = 6
intercept = 150
round_fix = 0.001


def convolve_hexagonal_2d(input_array, kernel_array, kernel_center=(0, 0), oob_value=0, dtype=np.int32):
    input_height, input_width = input_array.shape
    kernel_height, kernel_width = kernel_array.shape

    output_array = np.zeros(shape=input_array.shape, dtype=dtype)

    for y in range(input_height):
        for x in range(input_width):
            x_real, y_real = x - kernel_center[0], y - kernel_center[1]
            conv_item = 0
            for y_shift in range(0, kernel_height):
                for x_shift in range(0, kernel_width):
                    x_real_shifted = x_real + x_shift
                    y_real_shifted = y_real + y_shift

                    if y % 2 == 0 or y_shift == 0:
                        kernel_item = kernel_array[y_shift, x_shift]
                    elif x_shift != 0:
                        kernel_item = kernel_array[y_shift, x_shift - 1]
                    else:
                        kernel_item = 0

                    if 0 <= x_real_shifted < input_width and 0 <= y_real_shifted < input_height:
                        conv_item += kernel_item * input_array[y_real_shifted, x_real_shifted]
                    else:
                        conv_item += kernel_item * oob_value
            output_array[y, x] = conv_item

    return output_array


def derive_light_map(mhei: bytes, mepa: bytes, mepb: bytes, map_width: int, map_height: int):
    mhei_ndarray = np.frombuffer(mhei, dtype=np.ubyte).reshape((map_height//2, map_width//2))
    mepa_ndarray = np.frombuffer(mepa, dtype=np.ushort).reshape((map_height//2, map_width//2))
    mepb_ndarray = np.frombuffer(mepb, dtype=np.ushort).reshape((map_height//2, map_width//2))

    mlig = convolve_hexagonal_2d(mhei_ndarray, shadow_kernel, kernel_center=shadow_kernel_center)
    mlig += 127
    mlig = mlig.clip(0, 255)

    for y in range(0, mlig.shape[0]):
        for x in range(0, mlig.shape[1]):
            if mlig[y, x] >= min_value:
                mlig[y, x] = floor(mlig[y, x] / inversed_slope + intercept + round_fix)

            if y % 2 == 0:
                mepa_coordinates = ((x, y), (x, y-1), (x-1, y-1))
                mepb_coordinates = ((x, y), (x-1, y), (x-1, y-1))
            else:
                mepa_coordinates = ((x, y), (x, y-1), (x+1, y-1))
                mepb_coordinates = ((x, y), (x, y-1), (x-1, y))

            try:
                for coordinates in mepb_coordinates:
                    if not (0 <= coordinates[0] < mepb_ndarray.shape[1] and
                            0 <= coordinates[1] < mepb_ndarray.shape[0]):
                        raise ValueError
                    if mepb_ndarray[*coordinates[::-1]] in border_full_ids:
                        raise ValueError

                for coordinates in mepa_coordinates:
                    if not (0 <= coordinates[0] < mepa_ndarray.shape[1] and
                            0 <= coordinates[1] < mepa_ndarray.shape[0]):
                        raise ValueError
                    if mepa_ndarray[*coordinates[::-1]] in border_full_ids:
                        raise ValueError

            except ValueError:
                mlig[y, x] = 0

    return mlig.astype(dtype=mhei_ndarray.dtype).tobytes()
