import json

mstr_colormap_filepath = "scripts/colormaps/mstr.json"
mep_colormap_filepath = "scripts/colormaps/mep.json"  # This color map is based on in-game minimap display, however
                                                      # due to duplication of some RGB values there, some of colors are
                                                      # slightly modified in order to have unique value for each type
                                                      # of mep terrain triangle.


inverse_dictionary = lambda dict_: {value: key for key, value in dict_.items()}


class ColorMap(dict):
    def __init__(self, dict_):
        super().__init__(dict_)
        assert all(map(lambda key: isinstance(key, int) and isinstance(self[key], tuple), self.keys()))
        self.inversed = inverse_dictionary(dict_)


def load_colormap(filepath):
    dict_new = dict()
    with open(filepath) as file:
        dict_loaded = json.loads(file.read())
    for key, value in dict_loaded.items():
        dict_new[int(key)] = tuple(value)
    return ColorMap(dict_new)

def apply_colormap(list_: list, colormap: ColorMap | dict) -> list:
    return [colormap[element] for element in list_]

def remove_colormap(list_: list, colormap: ColorMap | dict) -> list:
    return apply_colormap(list_, colormap.inversed)

def apply_colormap_to_shorts(sequence: bytes, colormap: ColorMap) -> list:
    return [(colormap[byte1 + byte2 * 256]) for byte1, byte2 in zip(sequence[::2], sequence[1::2])]

def remove_colormap_to_shorts(list_: list, colormap: ColorMap) -> bytes:
    return b"".join(int.to_bytes(colormap.inversed[element[:3]], length=2, byteorder="little") for element in list_)


mstr_colormap = load_colormap(mstr_colormap_filepath)
mep_colormap = load_colormap(mep_colormap_filepath)
