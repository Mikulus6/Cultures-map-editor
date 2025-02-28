import numpy as np


void_margin = 2
max_steepness = 16


def enforce_horizonless_heightmap(editor):
    mhei_ndarray = np.frombuffer(editor.map.mhei, dtype=np.ubyte).reshape((editor.map.map_height//2,
                                                                           editor.map.map_width//2))
    mhei_ndarray[:void_margin, :] = 0
    mhei_ndarray[-void_margin:, :] = 0
    mhei_ndarray[:, :void_margin] = 0
    mhei_ndarray[:, -void_margin:] = 0

    for y in range(void_margin, editor.map.map_height // 2 - void_margin):
        for x in range(void_margin, editor.map.map_width//2 - void_margin):
            match y:
                case 2: mhei_ndarray[y, x] = min(mhei_ndarray[y, x], 2 * max_steepness)
                case 3: mhei_ndarray[y, x] = min(mhei_ndarray[y, x], 3 * max_steepness - 1)
                case _:
                    if y % 2 == 0:
                        mhei_ndarray[y, x] = min(int(mhei_ndarray[y-1, x-1]) + max_steepness,
                                                 int(mhei_ndarray[y-1, x]) + max_steepness,
                                                 mhei_ndarray[y, x])
                    else:
                        mhei_ndarray[y, x] = min(int(mhei_ndarray[y-1, x]) + max_steepness,
                                                 int(mhei_ndarray[y-1, x+1]) + max_steepness,
                                                 mhei_ndarray[y, x])

    editor.map.mhei = bytearray(mhei_ndarray.tobytes()) if isinstance(editor.map.mhei, bytearray) \
                                                        else mhei_ndarray.tobytes()
