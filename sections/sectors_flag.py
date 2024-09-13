import numpy as np
from scripts.flags import bool_ndarray_to_flag


def sectors_flag(xsec: list, map_width: int, map_height: int):
    walk_sector_points_presence_ndarray = np.zeros(shape=(map_height, map_width), dtype=np.bool_)

    for sector in xsec:
        sector_type, sector_value, coordintes = sector
        if sector[0] == 1:
            walk_sector_points_presence_ndarray[*coordintes[::-1]] = True
    return bool_ndarray_to_flag(walk_sector_points_presence_ndarray)
