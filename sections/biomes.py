from typing import Literal
import numpy as np
from scripts.flags import sequence_to_flags, flags_to_sequence
from supplements.patterns import patterndefs_normal

structural_bonus_value = 10

def derive_biomes(mepa, mepb, mstr, map_width, map_height):

    nutrition_ndarray = derive_biome_parameter_ndarray(mepa, mepb, map_width, map_height, parameter="MaxNutritional")
    water_ndarray = derive_biome_parameter_ndarray(mepa, mepb, map_width, map_height, parameter="MaxWater") + \
                    derive_structural_bonus_ndarray(mstr, map_width, map_height)

    # Note that turning ndarrays with entry per byte to flags with entry per four bits forces modulo 16.

    return flags_to_sequence([*sequence_to_flags(water_ndarray.tobytes())[4:],
                              *sequence_to_flags(nutrition_ndarray.tobytes())[4:]])


def derive_biome_parameter_ndarray(mepa, mepb, map_width, map_height, *,
                                   parameter: str = Literal["MaxNutritional", "MaxWater"]) -> np.ndarray:

    mepa_ndarray = np.frombuffer(mepa, dtype=np.ushort).reshape((map_height//2, map_width//2))
    mepb_ndarray = np.frombuffer(mepb, dtype=np.ushort).reshape((map_height//2, map_width//2))

    value_ndarray = np.zeros(shape=(map_height // 2, map_width // 2), dtype=np.byte)

    for y in range(map_height//2):
        for x in range(map_width//2):

            base_value = patterndefs_normal[mepa_ndarray[y, x]].get(parameter, 0) + \
                         patterndefs_normal[mepb_ndarray[y, x]].get(parameter, 0)

            if y % 2 == 0:
                neighbours = [(x + 1, y), (x, y + 1), (x - 1, y),
                              (x, y - 1), (x - 1, y + 1), (x - 1, y - 1)]
            else:
                neighbours = [(x + 1, y), (x, y + 1), (x - 1, y),
                              (x, y - 1), (x + 1, y + 1), (x + 1, y - 1)]

            neighbours_bonus = 0

            for coordinates in neighbours:
                coordinates = (coordinates[0] % (map_width // 2), coordinates[1] % (map_height // 2))

                neighbours_bonus += patterndefs_normal[mepa_ndarray[*coordinates[::-1]]].get(parameter, 0)
                neighbours_bonus += patterndefs_normal[mepb_ndarray[*coordinates[::-1]]].get(parameter, 0)

            value_ndarray[y, x] = ((neighbours_bonus // 6) + base_value) // 4

    return value_ndarray


def derive_structural_bonus_ndarray(mstr, map_width, map_height) -> np.ndarray:

    mstr_ndarray = np.frombuffer(mstr, dtype=np.ushort).reshape((map_height, map_width))

    bonus_ndarray = np.zeros(shape=(map_height // 2, map_width // 2), dtype=np.byte)

    for y_base in range(map_height//2):
        for x_base in range(map_width//2):

            x = x_base * 2
            y = y_base * 2

            if y_base % 2 == 0:
                surroundings  = [(x, y),
                                 (x + 1, y), (x, y + 1), (x - 1, y),
                                 (x, y - 1), (x - 1, y + 1), (x - 1, y - 1)]
            else:
                surroundings  = [(x + 1, y),
                                 (x + 2, y), (x, y + 1), (x, y), # Row with entries (x+n, y) is shifted to the right.
                                 (x, y - 1), (x + 1, y + 1), (x + 1, y - 1)]

            for coordinates in surroundings:
                coordinates = (coordinates[0] % map_width, coordinates[1] % map_height)

                value = (mstr_ndarray[*coordinates[::-1]])

                if value & 1 != 0 and value & 48 == 16:
                    bonus_ndarray[y_base, x_base] += structural_bonus_value

    return bonus_ndarray
