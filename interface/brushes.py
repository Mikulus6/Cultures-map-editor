from map import Map
from interface.const import max_scroll_radius
from interface.cursor import is_vertex_major
from sections.structures import coordinates_in_radius
from sections.walk_sector_points import get_tile_in_direction


def warp_coordinates_in_bounds(map_object: Map, coordinates):
    if isinstance(coordinates, tuple):
        coordinates = list(coordinates)

    if coordinates[0] < 0:                        coordinates[0] = 0
    elif coordinates[0] >= map_object.map_width:  coordinates[0] = map_object.map_width - 1
    if coordinates[1] < 0:                        coordinates[1] = 0
    elif coordinates[1] >= map_object.map_height: coordinates[1] = map_object.map_height - 1

    return tuple(coordinates)

def warp_to_major(coordinates):
    match coordinates[1] % 4:
        case 0: return coordinates[0] // 2 * 2, coordinates[1]
        case 1: return coordinates[0] // 2 * 2, coordinates[1] - 1
        case 2: return coordinates[0] // 2 * 2 + 1, coordinates[1]
        case 3: return coordinates[0] // 2 * 2 + 1, coordinates[1] - 1
        case _: raise ValueError

def is_in_bounds(map_object: Map, coordinates):
    return tuple(coordinates) == warp_coordinates_in_bounds(map_object, coordinates)

def edge_coordinates_ordered_in_radius(start_position, radius, ignore_minor_vertices=False):

    assert not ignore_minor_vertices or is_vertex_major(start_position)

    result = []
    x = start_position[0]
    y = start_position[1]
    for _ in range(radius):
        x, y = get_tile_in_direction(x, y, 4)

    for direction in range(6):
        for _ in range(radius):
            x, y = get_tile_in_direction(x, y, direction)
            if not ignore_minor_vertices or is_vertex_major((x, y)):
                result.append((x, y))

    return tuple(result)


class Brush:
    instances = dict()

    def __init__(self, start_position: (int, int), radius: int):
        self.start_position = start_position
        self.event_row_start = bool(start_position[1] % 2)
        self.radius = radius
        self.points = coordinates_in_radius(self.start_position, self.radius)
        self.major_points = tuple(filter(is_vertex_major, self.points))
        self.edge_points = edge_coordinates_ordered_in_radius(self.start_position, self.radius)

        self.__class__.instances[self.event_row_start, self.radius] = self

    def __repr__(self):
        string = f"{self.__class__.__name__} "
        for name, var in vars(self).items():
            string = string + f"{name} = {var}; "
        return string

    @classmethod
    def get_points_and_edge_points(cls, map_object: Map, start_position, radius, ignore_minor_vertices=False):

        if ignore_minor_vertices:
            assert radius % 2 == 0
            start_position = (start_position[0] * 2 + (start_position[1] % 2), start_position[1] * 2)

        instance = cls.instances[bool(start_position[1] % 2), radius]
        shift_vector = (start_position[0] -  instance.start_position[0],
                        start_position[1] -  instance.start_position[1])
        points = [(x + shift_vector[0], y + shift_vector[1]) for x, y in instance.points]
        edge_points = [(x + shift_vector[0], y + shift_vector[1]) for x, y in instance.edge_points]
        if ignore_minor_vertices:
            points = [(x + shift_vector[0], y + shift_vector[1]) for x, y in instance.major_points]
            edge_points = tuple(filter(lambda coords: coords[1] % 2 == 0, edge_points))

        points = tuple(filter(lambda coords: is_in_bounds(map_object, coords), points))

        return points, edge_points


for start_pos in ((0, 0), (0, 1)):
    for current_radius in range(max_scroll_radius + 1):
        Brush(start_pos, current_radius)
