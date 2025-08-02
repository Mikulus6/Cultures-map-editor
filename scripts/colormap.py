import json
from collections import OrderedDict
from collections.abc import Iterable
from scripts.abs_path import abs_path

template_editgroups_palette_filepath = "assets\\colormaps\\template_editgroups.json"  # This palette is arbitrary.

inverse_dictionary = lambda dict_: {value: key for key, value in dict_.items()}


class ColorMap(dict):
    def __init__(self, dict_=None):
        if dict_ is None:
            dict_ = dict()
        super().__init__(dict_)
        assert all(map(lambda key: isinstance(key, int) and isinstance(self[key], tuple), self.keys()))

    @property
    def inversed(self):
        return inverse_dictionary(self)

    def deduplicate_colors(self):
        values_found = set()
        for key, value in self.items():
            if value in values_found:
                self[key] = find_closest_color(value, excluded_colors=self.values())
            values_found.add(self[key])
        assert len(self.values()) == len(set(self.values()))

def load_colormap(filepath):
    dict_new = dict()
    with open(abs_path(filepath)) as file:
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

def remove_colormap_from_shorts(list_: list, colormap: ColorMap) -> bytes:
    return b"".join(int.to_bytes(colormap.inversed[element[:3]], length=2, byteorder="little") for element in list_)

def find_closest_color(color: tuple[int, int, int], *,
                       excluded_colors: Iterable[tuple[int, int, int]] = ()) -> tuple[int, int, int]:

    color_type = type(color)
    color = tuple(color)
    excluded_colors = tuple(map(tuple, excluded_colors))

    norm = lambda v1: (v1[0] - color[0])**2 + \
                      (v1[1] - color[1])**2 + \
                      (v1[2] - color[2])**2

    def expansion(v1):
        offsets = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (-1, 0, 0), (0, -1, 0), (0, 0, -1))
        new_vectors = tuple(tuple((v1[i] + o[i]) for i in range(3)) for o in offsets)
        return tuple(new_vector for new_vector in new_vectors if min(new_vector) >= 0 and max(new_vector) <= 255)

    to_search = OrderedDict({color: norm(color)})
    to_search_new = OrderedDict()

    norm_radius_bound = 0
    color_found = None

    while color_found is None:

        for current_color, distance in to_search.items():
            for new_color in expansion(current_color):
                if distance < norm_radius_bound or new_color in to_search.keys():
                    continue
                to_search_new[new_color] = norm(new_color)

        norm_radius_bound = min(to_search_new.values())

        for current_color, distance in to_search.items():
            if distance >= norm_radius_bound or current_color == color or current_color in excluded_colors:
                continue
            color_found = current_color
            norm_radius_bound = distance

        to_search = OrderedDict(tuple(to_search.items()) + tuple(to_search_new.items()))
        to_search_new = OrderedDict()

    return color_type(color_found)

with open(abs_path(template_editgroups_palette_filepath)) as palette_file:
    template_editgroups_palette = json.loads(palette_file.read())
template_editgroups_palette = {key: tuple(value) for key, value in template_editgroups_palette.items()}
