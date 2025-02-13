import pygame
from functools import lru_cache
from map import Map
from math import ceil, floor, sqrt
from dataclasses import dataclass
from interface.const import triangle_width, triangle_height, height_factor, camera_max_move_distance,\
                            camera_discretization_factor, map_canvas_rect
from time import time


@dataclass
class Camera:
    position: [float, float]
    fixed_position: [int, int] = (0, 0)
    is_moving: bool = False
    speed: int = 1000
    visible_margin: int = 2
    visible_height_margin: int = 20
    last_frame_move = time()
    suspend_motion = False

    def move(self, pressed_state, map_object: Map):

        if self.suspend_motion:
            self.suspend_motion = False
            self.fixed_position = self.fixed_postion_update()
            return

        move = [0, 0]

        if pressed_state[pygame.K_UP] and not pressed_state[pygame.K_DOWN]:      move[1] = -1
        elif pressed_state[pygame.K_DOWN] and not pressed_state[pygame.K_UP]:    move[1] = 1
        if pressed_state[pygame.K_LEFT] and not pressed_state[pygame.K_RIGHT]:   move[0] = -1
        elif pressed_state[pygame.K_RIGHT] and not pressed_state[pygame.K_LEFT]: move[0] = 1

        if move[0] != 0 and move[1] != 0:
            speed_effective = self.speed / sqrt(2)
        else:
            speed_effective = self.speed

        current_time = time()
        delta_time = (current_time - self.last_frame_move)

        old_position = [self.position[0],
                        self.position[1]]

        move_vector = [move[0] * speed_effective * delta_time,
                       move[1] * speed_effective * delta_time]
        move_distance_squared = move_vector[0]**2 + move_vector[1]**2

        if move_distance_squared > camera_max_move_distance ** 2:
            move_vector[0] *= abs(camera_max_move_distance ** 2 / move_distance_squared)
            move_vector[1] *= abs(camera_max_move_distance ** 2 / move_distance_squared)

        self.position[0] += move_vector[0]
        self.position[1] += move_vector[1]

        self.warp(map_object)
        self.fixed_position = self.fixed_postion_update()
        self.is_moving = (old_position != self.position)
        self.last_frame_move = current_time

    def fixed_postion_update(self):
        if camera_discretization_factor == 0:
            return tuple(self.position)
        return round(self.position[0] / (triangle_width * camera_discretization_factor)) * \
                                            camera_discretization_factor * triangle_width, \
               round(self.position[1] / (triangle_width * camera_discretization_factor)) * \
                                            camera_discretization_factor * triangle_width

    @staticmethod
    def get_camera_bounds(map_object: Map):
        return (0, map_object.map_width * triangle_width), (0, map_object.map_height * triangle_height)

    def warp(self, map_object: Map):

        bounds_x, bounds_y = self.get_camera_bounds(map_object)

        if self.position[0] < bounds_x[0]:   self.position[0] = bounds_x[0]
        elif self.position[0] > bounds_x[1]: self.position[0] = bounds_x[1]
        if self.position[1] < bounds_y[0]:   self.position[1] = bounds_y[0]
        elif self.position[1] > bounds_y[1]: self.position[1] = bounds_y[1]

    def draw_coordinates(self, coordinates, map_object: Map, include_canvas_offset: bool = False):
        coordinates = point_coordinates(coordinates, map_object)
        if include_canvas_offset:
            return floor(coordinates[0] - self.fixed_position[0] + map_canvas_rect[0] + (map_canvas_rect[2] // 2)), \
                   floor(coordinates[1] - self.fixed_position[1] + map_canvas_rect[1] + (map_canvas_rect[3] // 2))
        else:
            return floor(coordinates[0] - self.fixed_position[0] + (map_canvas_rect[2] // 2)), \
                   floor(coordinates[1] - self.fixed_position[1] + (map_canvas_rect[3] // 2))

    def visible_range(self, map_object: Map, *, count_minor_vertices=True):
        x_range = floor((self.fixed_position[0] - (map_canvas_rect[2] / 2)) / triangle_width)  - self.visible_margin, \
                   ceil((self.fixed_position[0] + (map_canvas_rect[2] / 2)) / triangle_width)  + self.visible_margin
        y_range = floor((self.fixed_position[1] - (map_canvas_rect[3] / 2)) / triangle_height) - self.visible_margin, \
                   ceil((self.fixed_position[1] + (map_canvas_rect[3] / 2)) / triangle_height) + \
                                                                                              self.visible_height_margin
        if count_minor_vertices:
            x_range = max((0, x_range[0])), min((x_range[1], map_object.map_width))
            y_range = max((0, y_range[0])), min((y_range[1], map_object.map_height))
        else:
            x_range = max((0, x_range[0])) // 2, min((x_range[1], map_object.map_width))  // 2
            y_range = max((0, y_range[0])) // 2, min((y_range[1], map_object.map_height)) // 2

        for y in range(*y_range):
            for x in range(*x_range):
                yield x, y

    @property
    def position_on_map(self):
        return self.position[0] // triangle_width, self.position[1] // triangle_height


@lru_cache(maxsize=None)
def point_coordinates(coordinates, map_object: Map):
    x, y = coordinates

    if (x % 2 == 0 and y % 4 == 0) or (x % 2 == 1 and y % 4 == 2):
        x = coordinates[0] * triangle_width + (coordinates[1] % 2) * floor(0.5 * triangle_width)
        y = coordinates[1] * triangle_height - height_factor * \
            map_object.mhei[(coordinates[1] % map_object.map_height) * map_object.map_width // 4 +
                            (coordinates[0] % map_object.map_width) // 2]
        return x, y

    elif (x % 2 == 1 and y % 4 == 0) or (x % 2 == 0 and y % 4 == 2):
        vertices = (x - 1, y), (x + 1, y)
    elif (x % 2 == 0 and y % 4 == 1) or (x % 2 == 1 and y % 4 == 3):
        vertices = (x, y - 1), (x + 1, y + 1)
    elif (x % 2 == 1 and y % 4 == 1) or (x % 2 == 0 and y % 4 == 3):
        vertices = (x + 1, y - 1), (x, y + 1)

    else:
        raise IndexError  # this case should be unobtainable

    x1, y1 = point_coordinates(vertices[0], map_object)
    x2, y2 = point_coordinates(vertices[1], map_object)

    return (x1 + x2) // 2, (y1 + y2) // 2


def clear_point_coordinates_cache():
    point_coordinates.cache_clear()
