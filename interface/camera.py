import pygame
from functools import lru_cache
from map import Map
from math import ceil, floor, sqrt
from dataclasses import dataclass
from interface.const import triangle_width, triangle_height, height_factor, camera_max_move_distance,\
                            camera_discretization_factor, map_canvas_rect, middle_button_speed_factor, \
                            camera_perspective_shift_cooldown, triangle_width_shifted, triangle_height_shifted, \
                            height_factor_shifted
from time import time


@dataclass
class Camera:
    position: list[float]
    position_before_shift_change: list[float]
    fixed_position: list[int] = (0, 0)
    is_moving: bool = False
    speed: int = 1000
    visible_margin: int = 2
    perspective_shifted: bool = False
    last_frame_move: float = time()
    last_perspective_shift = time() - camera_perspective_shift_cooldown - 1e-16
    time_now = time()
    is_perspective_mid_change: bool = False
    suspend_motion = False

    def move(self, pressed_state, map_object: Map, move_by_middle, relative_mouse_movement):

        if self.suspend_motion:
            self.suspend_motion = False
            self.fixed_position_update()
            return

        if move_by_middle:
            self.position[0] += relative_mouse_movement[0] * middle_button_speed_factor
            self.position[1] += relative_mouse_movement[1] * middle_button_speed_factor
            self.position_before_shift_change[0] += relative_mouse_movement[0] * middle_button_speed_factor
            self.position_before_shift_change[1] += relative_mouse_movement[1] * middle_button_speed_factor

        move = [0, 0]

        if pressed_state[pygame.K_UP] and not pressed_state[pygame.K_DOWN]:      move[1] = -1
        elif pressed_state[pygame.K_DOWN] and not pressed_state[pygame.K_UP]:    move[1] = 1
        if pressed_state[pygame.K_LEFT] and not pressed_state[pygame.K_RIGHT]:   move[0] = -1
        elif pressed_state[pygame.K_RIGHT] and not pressed_state[pygame.K_LEFT]: move[0] = 1

        if move[0] != 0 and move[1] != 0:
            speed_effective = self.speed / sqrt(2)
        else:
            speed_effective = self.speed

        delta_time = (self.time_now - self.last_frame_move)

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
        self.position_before_shift_change[0] += move_vector[0]
        self.position_before_shift_change[1] += move_vector[1]

        self.warp(map_object)
        self.fixed_position_update()
        self.is_moving = (old_position != self.position or self.is_perspective_mid_change)
        self.last_frame_move = self.time_now

    def update_time(self, time_now: float = None):
        if time_now is None: self.time_now = time()
        else:                self.time_now = time_now

    def fixed_position_update(self):
        if camera_discretization_factor == 0:
            self.fixed_position = [*self.position]
        else:
            current_triangle_width, current_triangle_height, _ = self.get_current_perspective_parameters()
            self.fixed_position = [round(self.position[0] / (current_triangle_width * camera_discretization_factor)) *
                                                             current_triangle_width * camera_discretization_factor,
                                   round(self.position[1] / (current_triangle_height * camera_discretization_factor)) *
                                                             current_triangle_height * camera_discretization_factor]

    def get_camera_bounds(self, map_object: Map):
        current_triangle_width, current_triangle_height, current_height_factor = \
            self.get_current_perspective_parameters()

        return (0, map_object.map_width * current_triangle_width), \
               (0, map_object.map_height * current_triangle_height)

    def set_to_center(self, map_object: Map):
        bounds = self.get_camera_bounds(map_object)
        self.position[0] = (bounds[0][0] + bounds[0][1]) // 2
        self.position[1] = (bounds[1][0] + bounds[1][1]) // 2

    def warp(self, map_object: Map):

        bounds_x, bounds_y = self.get_camera_bounds(map_object)

        if self.position[0] < bounds_x[0]:   self.position[0] = bounds_x[0]
        elif self.position[0] > bounds_x[1]: self.position[0] = bounds_x[1]
        if self.position[1] < bounds_y[0]:   self.position[1] = bounds_y[0]
        elif self.position[1] > bounds_y[1]: self.position[1] = bounds_y[1]

    def draw_coordinates(self, coordinates, map_object: Map, include_canvas_offset: bool = False):
        coordinates = point_coordinates(coordinates, map_object, self.perspective_factor)
        if include_canvas_offset:
            return floor(coordinates[0] - self.fixed_position[0] + map_canvas_rect[0] + (map_canvas_rect[2] // 2)), \
                   floor(coordinates[1] - self.fixed_position[1] + map_canvas_rect[1] + (map_canvas_rect[3] // 2))
        else:
            return floor(coordinates[0] - self.fixed_position[0] + (map_canvas_rect[2] // 2)), \
                   floor(coordinates[1] - self.fixed_position[1] + (map_canvas_rect[3] // 2))

    @property
    def visible_height_margin(self):
        _, current_triangle_height, current_height_factor = self.get_current_perspective_parameters()
        return ceil((256 * current_height_factor) / current_triangle_height)

    def visible_range(self, map_object: Map, *, count_minor_vertices=True):
        current_triangle_width, current_triangle_height, _ = self.get_current_perspective_parameters()
        x_range = floor((self.fixed_position[0] - (map_canvas_rect[2] / 2)) / current_triangle_width)  - self.visible_margin, \
                   ceil((self.fixed_position[0] + (map_canvas_rect[2] / 2)) / current_triangle_width)  + self.visible_margin
        y_range = floor((self.fixed_position[1] - (map_canvas_rect[3] / 2)) / current_triangle_height) - self.visible_margin, \
                   ceil((self.fixed_position[1] + (map_canvas_rect[3] / 2)) / current_triangle_height) + \
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

    def get_current_perspective_parameters(self, perspective_factor: float = None):
        if perspective_factor is None: return get_current_perspective_parameters_static(self.perspective_factor)
        else:                          return get_current_perspective_parameters_static(perspective_factor)

    @property
    def position_on_map(self):
        current_triangle_width, current_triangle_height, _ = self.get_current_perspective_parameters()
        return self.position[0] // current_triangle_width, self.position[1] // current_triangle_height

    @staticmethod
    def position_in_canvas_rect(position):
        return map_canvas_rect[0] <= position[0] < map_canvas_rect[0] + map_canvas_rect[2] and \
               map_canvas_rect[1] <= position[1] < map_canvas_rect[1] + map_canvas_rect[3]

    def handle_shift_perspective(self, editor, *, forbid_new_shift: bool = False):
        if (not self.is_perspective_mid_change) and (not forbid_new_shift):
            if self.position_in_canvas_rect(editor.mouse_pos):
                if   editor.scroll_delta < 0 and not self.perspective_shifted: self.is_perspective_mid_change = True
                elif editor.scroll_delta > 0 and     self.perspective_shifted: self.is_perspective_mid_change = True

            if self.is_perspective_mid_change:
                self.perspective_shifted = not self.perspective_shifted
                self.last_perspective_shift = self.time_now
                self.position_before_shift_change = [*self.position]

        elif self.is_perspective_mid_change:
            self.recenter_camera_mid_perspective_shift()

    @property
    def perspective_factor(self):
        time_fraction = min(max(((self.time_now - self.last_perspective_shift) /
                                  camera_perspective_shift_cooldown, 0.0)), 1.0)
        if self.perspective_shifted: return time_fraction
        else:                        return 1.0 - time_fraction

    def recenter_camera_mid_perspective_shift(self):
        if self.time_now == self.last_perspective_shift:
            return # recenter is not necessary

        new_triangle_width, new_triangle_height, new_height_factor = \
            self.get_current_perspective_parameters(perspective_factor=float(self.perspective_shifted))
        old_triangle_width, old_triangle_height, old_current_height_factor = \
            self.get_current_perspective_parameters(perspective_factor=float(not self.perspective_shifted))

        time_fraction = min(max(((self.time_now - self.last_perspective_shift) /
                                  camera_perspective_shift_cooldown, 0.0)), 1.0)

        if time_fraction == 1.0:
            self.is_perspective_mid_change = False

        new_position = [self.position_before_shift_change[0] * (new_triangle_width / old_triangle_width),
                        self.position_before_shift_change[1] * (new_triangle_height / old_triangle_height)]

        self.position[0] = new_position[0] * time_fraction + self.position_before_shift_change[0] * (1 - time_fraction)
        self.position[1] = new_position[1] * time_fraction + self.position_before_shift_change[1] * (1 - time_fraction)
        self.fixed_position_update()

def get_current_perspective_parameters_static(perspective_factor: float):
        assert 0.0 <= perspective_factor <= 1.0
        current_triangle_width  = triangle_width * (1 - perspective_factor) +\
                                  triangle_width_shifted * perspective_factor
        current_triangle_height = triangle_height * (1 - perspective_factor) +\
                                  triangle_height_shifted * perspective_factor
        current_height_factor   = height_factor * (1 - perspective_factor) +\
                                  height_factor_shifted * perspective_factor

        return current_triangle_width, current_triangle_height, current_height_factor


@lru_cache(maxsize=None)
def point_coordinates(coordinates, map_object: Map, perspective_factor: float):

    x, y = coordinates
    current_triangle_width, current_triangle_height, current_height_factor = \
        get_current_perspective_parameters_static(perspective_factor)

    if (x % 2 == 0 and y % 4 == 0) or (x % 2 == 1 and y % 4 == 2):
        x = coordinates[0] * current_triangle_width + (coordinates[1] % 2) * floor(0.5 * current_triangle_width)
        y = floor(coordinates[1] * current_triangle_height - current_height_factor * \
            map_object.mhei[(coordinates[1] % map_object.map_height) * map_object.map_width // 4 +
                            (coordinates[0] % map_object.map_width) // 2])
        return x, y

    elif (x % 2 == 1 and y % 4 == 0) or (x % 2 == 0 and y % 4 == 2):
        vertices = (x - 1, y), (x + 1, y)
    elif (x % 2 == 0 and y % 4 == 1) or (x % 2 == 1 and y % 4 == 3):
        vertices = (x, y - 1), (x + 1, y + 1)
    elif (x % 2 == 1 and y % 4 == 1) or (x % 2 == 0 and y % 4 == 3):
        vertices = (x + 1, y - 1), (x, y + 1)

    else:
        raise IndexError  # this case should be unobtainable

    x1, y1 = point_coordinates(vertices[0], map_object, perspective_factor)
    x2, y2 = point_coordinates(vertices[1], map_object, perspective_factor)

    return (x1 + x2) // 2, (y1 + y2) // 2


def clear_point_coordinates_cache():
    point_coordinates.cache_clear()
