import numpy as np
from map import Map
from typing import Literal
from interface.horizont import void_margin

border_mep_id = 126


def update_map_border(editor):
    mhei_ndarray = np.frombuffer(editor.map.mhei, dtype=np.ubyte).reshape((editor.map.map_height//2,
                                                                           editor.map.map_width//2))
    mepa_ndarray = np.frombuffer(editor.map.mepa, dtype=np.ushort).reshape((editor.map.map_height//2,
                                                                            editor.map.map_width//2))
    mepb_ndarray = np.frombuffer(editor.map.mepb, dtype=np.ushort).reshape((editor.map.map_height//2,
                                                                            editor.map.map_width//2))

    mhei_ndarray[:void_margin, :] = 0
    mhei_ndarray[-void_margin:, :] = 0
    mhei_ndarray[:, :void_margin] = 0
    mhei_ndarray[:, -void_margin:] = 0
    mepa_ndarray[:2, :] = border_mep_id
    mepa_ndarray[-3:, :] = border_mep_id
    mepa_ndarray[np.arange(0, mepa_ndarray.shape[0], 2), :3] = border_mep_id
    mepa_ndarray[np.arange(0, mepa_ndarray.shape[0], 2), -2:] = border_mep_id
    mepa_ndarray[np.arange(1, mepa_ndarray.shape[0], 2), :2] = border_mep_id
    mepa_ndarray[np.arange(1, mepa_ndarray.shape[0], 2), -3:] = border_mep_id
    mepb_ndarray[:2, :] = border_mep_id
    mepb_ndarray[-3:, :] = border_mep_id
    mepb_ndarray[:, :2] = border_mep_id
    mepb_ndarray[:, -3:] = border_mep_id

    editor.map.mepa = bytearray(mepa_ndarray.tobytes()) if isinstance(editor.map.mepa, bytearray) \
                                                        else mepa_ndarray.tobytes()
    editor.map.mepb = bytearray(mepb_ndarray.tobytes()) if isinstance(editor.map.mepa, bytearray) \
                                                        else mepb_ndarray.tobytes()
    editor.map.mhei = bytearray(mhei_ndarray.tobytes()) if isinstance(editor.map.mhei, bytearray) \
                                                        else mhei_ndarray.tobytes()

def is_triangle_in_border(coordinates, triangle_type: Literal["a", "b"], map_object: Map):
    x, y = coordinates

    if y < 2 or y > map_object.map_height // 2 - 4:
        return True

    match triangle_type:
        case "a":
            if y % 2 == 0: return x < 3 or x > map_object.map_width // 2 - 3
            else:          return x < 2 or x > map_object.map_width // 2 - 4
        case "b": return x < 2 or x > map_object.map_width // 2 - 4
        case _: raise ValueError


def is_major_vertex_in_border(coordinates, map_object: Map):
    x, y = coordinates
    return x < void_margin or x >= map_object.map_width  // 2 - void_margin or\
           y < void_margin or y >= map_object.map_height // 2 - void_margin
