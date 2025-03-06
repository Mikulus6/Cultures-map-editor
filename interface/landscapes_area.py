from dataclasses import dataclass
import numpy as np
from map import Map
from sections.landscapes_area import update_landscapes_presence_ndarray
from supplements.landscapedefs import landscapedefs
from typing import Literal

def get_bounds_described_on_all_landscapes(area_type: Literal["Base", "Extended", "Special"]):

    min_x, min_y, max_x, max_y = 0, 0, 0, 0
    for landscape_data in landscapedefs.values():
        for triplet in landscape_data.get(area_type + "Area", []):
            x, y, offset = triplet
            min_x, min_y, max_x, max_y = min(min_x, x), min(min_y, y), max(max_x, x + offset + 1), max(max_y, y)

    return min_x, min_y, max_x, max_y

global_landscapes_bounds = {area_type : get_bounds_described_on_all_landscapes(area_type)
                            for area_type in ("Base", "Extended", "Special")}


@dataclass
class AreaUpdatedBounds:
    is_empty: bool = True
    min_x: int = 0
    min_y: int = 0
    max_x: int = 0
    max_y: int = 0

    def update(self, x, y, offset):
        self.is_empty = False
        self.min_x = min(self.min_x, x)
        self.min_y = min(self.min_y, y)
        self.max_x = max(self.max_x, x + offset + 1)
        self.max_y = max(self.max_y, y)

    def reset(self):
        self.is_empty = True
        self.min_x = 0
        self.min_y = 0
        self.max_x = 0
        self.max_y = 0

    def extend_by_global_bounds(self, area_type: Literal["Base", "Extended", "Special"]):
        self.min_x += global_landscapes_bounds[area_type][0]
        self.min_y += global_landscapes_bounds[area_type][1]
        self.max_x += global_landscapes_bounds[area_type][2]
        self.max_y += global_landscapes_bounds[area_type][3]


class AreaTable:
    def __init__(self, map_width, map_height, area_type: Literal["Base", "Extended", "Special"]):
        self.area_type = area_type
        self.ndarray = np.zeros((map_height, map_width), dtype=np.bool_)
        self.area_updated_bounds = AreaUpdatedBounds()

    def reset_and_resize(self, map_width, map_height):
        self.ndarray = np.zeros((map_height, map_width), dtype=np.bool_)
        self.area_updated_bounds.reset()

    def update_on_landscape_change(self, name_old, name, coordinates, map_object: Map):

        if name == name_old:
            return

        area = tuple() if name is None else landscapedefs.get(name, dict()).get(self.area_type + "Area", tuple())
        area_old = tuple() if name_old is None else landscapedefs.get(name_old, dict()).get(self.area_type + "Area",
                                                                                            tuple())

        for area_data, flag in zip((area_old, area), (False, True)):
            for x, y, offset in area_data:
                x += coordinates[0]
                y += coordinates[1]
                for x_offset in range(x, x + offset):
                    if y % 2 == 0 and coordinates[1] % 2 == 1: x_real = x_offset + 1
                    else:                                      x_real = x_offset
                    if flag:
                        self.ndarray[(y % map_object.map_height, x_real % map_object.map_width)] = True
                if not flag:
                    self.area_updated_bounds.update(x, y, offset)

    def update_after_landscapes_changes(self, map_object: Map):

        if self.area_updated_bounds.is_empty:
            return

        for x_coords in range(self.area_updated_bounds.min_x, self.area_updated_bounds.max_x + 1):
            for y_coords in range(self.area_updated_bounds.min_y, self.area_updated_bounds.max_y + 1):
                x_coords %= map_object.map_width
                y_coords %= map_object.map_height

                self.ndarray[y_coords, x_coords] = False

        self.area_updated_bounds.extend_by_global_bounds(self.area_type)

        for x_coords in range(self.area_updated_bounds.min_x, self.area_updated_bounds.max_x + 1):
            for y_coords in range(self.area_updated_bounds.min_y, self.area_updated_bounds.max_y + 1):

                x_coords %= map_object.map_width
                y_coords %= map_object.map_height

                landscape_name = map_object.llan.get((x_coords, y_coords), None)
                if landscape_name is None:
                    continue

                for triplet in landscapedefs[landscape_name.lower()].get(self.area_type + "Area", []):
                    x, y, offset = triplet
                    x += x_coords
                    y += y_coords
                    for x_offset in range(x, x + offset):

                        if y % 2 == 0 and y_coords % 2 == 1: x_real = x_offset + 1
                        else:                                x_real = x_offset

                        coordinates = (x_real % map_object.map_width, y % map_object.map_height)
                        self.ndarray[coordinates[::-1]] = True

        self.area_updated_bounds.reset()

    def update_landscapes_presence_ndarray(self, map_object: Map):
        self.ndarray = update_landscapes_presence_ndarray(self.ndarray, map_object.llan,
                                                          map_object.map_width, map_object.map_height,
                                                          area_type=self.area_type)

    def check_overlap(self, name, coordinates, map_object: Map):
        if name is None:
            return False

        for x, y, offset in landscapedefs[name.lower()].get(self.area_type + "Area", []):
            x += coordinates[0]
            y += coordinates[1]
            for x_offset in range(x, x + offset):

                if y % 2 == 0 and coordinates[1] % 2 == 1: x_real = x_offset + 1
                else:                                      x_real = x_offset

                if self.ndarray[y % map_object.map_height, x_real % map_object.map_width]:
                    return True
        return False
