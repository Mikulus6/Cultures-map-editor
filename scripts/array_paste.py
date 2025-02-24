
def paste_in_bounds(big_array, small_array, x_offset, y_offset):
    bh, bw = big_array.shape
    sh, sw = small_array.shape

    x_start, x_end = max(x_offset, 0), min(x_offset + sh, bh)
    y_start, y_end = max(y_offset, 0), min(y_offset + sw, bw)

    big_array[x_start:x_end, y_start:y_end] = small_array[max(0, -x_offset): max(0, -x_offset) + (x_end - x_start),
                                                          max(0, -y_offset): max(0, -y_offset) + (y_end - y_start)]
