import numpy as np
from typing import Literal
from scripts.data_loader import landscapedefs
from scripts.flags import bool_ndarray_to_flag, sequence_to_flags
from scripts.image import bits_difference_to_image


# Letter case might be incorrect in original maps.
landscapedefs_lowercase = dict()
for key, value in list(landscapedefs.items()):
    assert key == key.lower() or key.lower() not in landscapedefs.keys()
    landscapedefs_lowercase[key.lower()] = value
del key, value


def landscapes_area_flag(llan, map_width, map_height,
                         area_type: Literal["Base", "Extended", "Special"]):

    # Following function will not always return correct results for maps created before 22nd August 2002. It is most
    # likely caused by different patterndefs_normal.ini file being used when those maps were under development. This is
    # most clearly visible when one would compare maps from older game "Cultures: Discovery of Vinland" to maps from
    # newer game "Cultures: The Revenge of the Rain God". Those inacuracies are present only in maps from older game.
    # Further this can be verified in game by testing some of the same landscapes on different maps and getting
    # different area blockades pattern from them, which itself shows that this is indeed also an in-game inconsistency.

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


def draw_derivation_difference(mgfs, llan, map_width, map_height, area_type: Literal["Base", "Extended"],
                               filename, expand=False):
    mgfs_flags = sequence_to_flags(mgfs)
    mgfs_flag_1 = mgfs_flags[7] if area_type == "Base" else mgfs_flags[5]
    mgfs_flag_2 = landscapes_area_flag(llan, map_width, map_height, area_type)
    bits_difference_to_image(mgfs_flag_1, mgfs_flag_2, filename, map_width,
                             expansion_mode="hexagon" if expand else None)
