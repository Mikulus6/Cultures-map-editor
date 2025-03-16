import numpy as np
from interface.undo_redo import undo_redo_memory


void_margin = 2
max_steepness = 16


def enforce_horizonless_heightmap(editor):

    for x in (*range(void_margin), *range(editor.map.map_width // 2 - 1 - void_margin,
                                          editor.map.map_width // 2 - 1)):
        for y in range(0, editor.map.map_height // 2):
            editor.update_height((x, y), 0)
    for y in (*range(void_margin), *range(editor.map.map_height // 2 - 1 - void_margin,
                                          editor.map.map_height // 2 - 1)):
        for x in range(0, editor.map.map_width // 2):
            editor.update_height((x, y), 0)

    mhei_ndarray = np.frombuffer(editor.map.mhei, dtype=np.ubyte).reshape((editor.map.map_height//2,
                                                                           editor.map.map_width//2))

    for y in range(void_margin, editor.map.map_height // 2 - void_margin):
        for x in range(void_margin, editor.map.map_width//2 - void_margin):
            old_height = mhei_ndarray[y, x]
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
            if old_height != mhei_ndarray[y, x]:
                undo_redo_memory.add_entry("mhei", (x, y), int(old_height), int(mhei_ndarray[y, x]))

    editor.map.mhei = bytearray(mhei_ndarray.tobytes()) if isinstance(editor.map.mhei, bytearray) \
                                                        else mhei_ndarray.tobytes()
    undo_redo_memory.update()
