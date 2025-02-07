import pygame
from map import Map
from math import ceil, floor, sqrt
from dataclasses import dataclass
from interface.const import resolution, camera_max_move_distance, camera_discretization_factor
from time import time


@dataclass
class Camera:
    position: [float, float]
    fixed_position: [int, int] = (0, 0)
    is_moving: bool = False
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
        self.fixed_position = self.fixed_postion_update()

        self.warp(map_object)

        self.is_moving = (old_position != self.position)
        self.last_frame_move = current_time

    def fixed_postion_update(self):
        if camera_discretization_factor == 0:
            return self.position
        return round(self.position[0] / (self.triangle_width * camera_discretization_factor)) * \
                                            camera_discretization_factor * self.triangle_width, \
               round(self.position[1] / (self.triangle_width * camera_discretization_factor)) * \
                                            camera_discretization_factor * self.triangle_width

    def warp(self, map_object: Map):

        max_pos_x = map_object.map_width  * self.triangle_width
        max_pos_y = map_object.map_height * self.triangle_height

        if self.position[0] < 0:           self.position[0] = 0
        elif self.position[0] > max_pos_x: self.position[0] = max_pos_x
        if self.position[1] < 0:           self.position[1] = 0
        elif self.position[1] > max_pos_y: self.position[1] = max_pos_y

    def draw_coordinates(self, coordinates, map_object: Map):
        coordinates = self.point_coordinates(coordinates, map_object)
        return floor(coordinates[0] - self.fixed_position[0] + (resolution[0] // 2)), \
               floor(coordinates[1] - self.fixed_position[1] + (resolution[1] // 2))

    def point_coordinates(self, coordinates, map_object: Map):

        x, y = coordinates

        if (x % 2 == 0 and y % 4 == 0) or (x % 2 == 1 and y % 4 == 2):
            x = coordinates[0] * self.triangle_width + (coordinates[1] % 2) * floor(0.5 * self.triangle_width)
            y = coordinates[1] * self.triangle_height - self.height_factor * \
                map_object.mhei[(coordinates[1] % map_object.map_height) * map_object.map_width // 4 +
                                (coordinates[0] % map_object.map_width) // 2]
            return x, y

        elif (x % 2 == 1 and y % 4 == 0) or (x % 2 == 0 and y % 4 == 2):
            vertices = [x - 1, y], [x + 1, y]
        elif (x % 2 == 0 and y % 4 == 1) or (x % 2 == 1 and y % 4 == 3):
            vertices = [x, y - 1], [x + 1, y + 1]
        elif (x % 2 == 1 and y % 4 == 1) or (x % 2 == 0 and y % 4 == 3):
            vertices = [x + 1, y - 1], [x, y + 1]

        else:
            raise IndexError  # this case should be unobtainable

        x1, y1 = self.point_coordinates(vertices[0], map_object)
        x2, y2 = self.point_coordinates(vertices[1], map_object)

        return (x1 + x2) // 2, (y1 + y2) // 2

    def visible_range(self, map_object: Map, *, count_minor_vertices=True):
        x_range = floor((self.fixed_position[0] - (resolution[0] / 2)) / self.triangle_width)  - self.visible_margin, \
                   ceil((self.fixed_position[0] + (resolution[0] / 2)) / self.triangle_width)  + self.visible_margin
        y_range = floor((self.fixed_position[1] - (resolution[1] / 2)) / self.triangle_height) - self.visible_margin, \
                   ceil((self.fixed_position[1] + (resolution[1] / 2)) / self.triangle_height) + \
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
