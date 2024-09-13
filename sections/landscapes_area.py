import numpy as np
from typing import Literal
from scripts.flags import bool_ndarray_to_flag
from scripts.data_loader import landscapedefs


# Letter case might be incorrect in original maps.
landscapedefs_lowercase = dict()
for key, value in list(landscapedefs.items()):
    assert key == key.lower() or key.lower() not in landscapedefs.keys()
    landscapedefs_lowercase[key.lower()] = value


def landscapes_area_flag(llan, map_width, map_height,
                         area_type: Literal["Base", "Extended", "Special"]):
    assert area_type in ("Base", "Extended", "Special")
    landscapes_presence_ndarray = np.zeros(shape=(map_height, map_width), dtype=np.bool_)
    for coordinates, landscape_name in llan.items():
        landscape_data = landscapedefs_lowercase[landscape_name.lower()]

        base_area = landscape_data.get(area_type+"Area", [])
        for triplet in base_area:
            x, y, offset = triplet
            x += coordinates[0]
            y += coordinates[1]
            for x_offset in range(x, x+offset):

                if y % 2 == 0 and coordinates[1] % 2 == 1:
                    x_real = x_offset + 1
                else:
                    x_real = x_offset

                landscapes_presence_ndarray[(y % map_height, x_real % map_width)] = True

    return bool_ndarray_to_flag(landscapes_presence_ndarray)
