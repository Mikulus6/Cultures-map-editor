import pygame
from map import Map
from math import ceil, floor, sqrt
from dataclasses import dataclass
from interface.const import resolution
from interface.interpolation import get_data_interpolated
from time import time


@dataclass
class Camera:
    position: [float, float]
    triangle_width: int = 32
    triangle_height: int = 16
    height_factor: int = 1
    speed: int = 1000
    visible_margin: int = 2
    visible_height_margin: int = 20
    last_frame_move = time()

    def move(self, pressed_state, map_object: Map):
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

        self.position[0] += move[0] * speed_effective * delta_time
        self.position[1] += move[1] * speed_effective * delta_time

        self.last_frame_move = current_time

        self.warp(map_object)

    def warp(self, map_object: Map):

        max_pos_x = map_object.map_width  * self.triangle_width
        max_pos_y = map_object.map_height * self.triangle_height

        if self.position[0] < 0:           self.position[0] = 0
        elif self.position[0] > max_pos_x: self.position[0] = max_pos_x
        if self.position[1] < 0:           self.position[1] = 0
        elif self.position[1] > max_pos_y: self.position[1] = max_pos_y

    def draw_coordinates(self, coordinates, map_object: Map):
        coordinates = self.point_coordinates(coordinates, map_object)
        return floor(coordinates[0] - self.position[0] + (resolution[0] // 2)), \
               floor(coordinates[1] - self.position[1] + (resolution[1] // 2))

    def point_coordinates(self, coordinates, map_object: Map):
        x = coordinates[0] * self.triangle_width + (coordinates[1] % 2) * floor(0.5 * self.triangle_width)
        y = coordinates[1] * self.triangle_height - self.height_factor * get_data_interpolated(coordinates,
                                                                                               (map_object.map_width,
                                                                                                map_object.map_height),
                                                                                               map_object.mhei)
        return x, y

    def visible_range(self, map_object: Map, *, count_minor_vertices=True):
        x_range = floor((self.position[0] - (resolution[0] / 2)) / self.triangle_width)  - self.visible_margin, \
                   ceil((self.position[0] + (resolution[0] / 2)) / self.triangle_width)  + self.visible_margin
        y_range = floor((self.position[1] - (resolution[1] / 2)) / self.triangle_height) - self.visible_margin, \
                   ceil((self.position[1] + (resolution[1] / 2)) / self.triangle_height) + self.visible_height_margin

        if count_minor_vertices:
            x_range = max((0, x_range[0])), min((x_range[1], map_object.map_width))
            y_range = max((0, y_range[0])), min((y_range[1], map_object.map_height))
        else:
            x_range = max((0, x_range[0])) // 2, min((x_range[1], map_object.map_width))  // 2
            y_range = max((0, y_range[0])) // 2, min((y_range[1], map_object.map_height)) // 2

        for y in range(*y_range):
            for x in range(*x_range):
                yield x, y
