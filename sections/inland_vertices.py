import numpy as np
from flags import bool_ndarray_to_flag
from sections.terrain_full_ids import void_full_ids, water_full_ids, underwater_full_ids


def bool_ndarray_to_bytes(bool_ndarray: np.ndarray):
    assert bool_ndarray.dtype == np.bool_
    flat_bool_array = bool_ndarray.flatten()
    padding = (8 - len(flat_bool_array) % 8) % 8
    if padding > 0:
        flat_bool_array = np.concatenate([flat_bool_array, np.zeros(padding, dtype=np.bool_)])
    bit_chunks = flat_bool_array.reshape(-1, 8)
    byte_array = np.packbits(bit_chunks, axis=1)
    return byte_array.tobytes()


def inland_vertices_flag(mepa: bytes, mepb: bytes, map_width: int, map_height: int):

    mepa_ndarray = np.frombuffer(mepa, dtype=np.ushort).reshape((map_height//2, map_width//2))
    mepb_ndarray = np.frombuffer(mepb, dtype=np.ushort).reshape((map_height//2, map_width//2))

    area_types_ndarray = np.zeros(shape=(map_height, map_width), dtype=np.bool_)
    area_types_ndarray.fill(True)

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

                if full_id in (*void_full_ids, *water_full_ids, *underwater_full_ids):
                    for coordinates in coordinates_list:
                        if not (0 <= coordinates[0] < map_width and 0 <= coordinates[1] < map_height):
                            continue  # out of bounds
                        area_types_ndarray[*coordinates[::-1]] = False

    return bool_ndarray_to_flag(area_types_ndarray)
