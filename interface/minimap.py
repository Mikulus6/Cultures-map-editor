import pygame
import numpy as np
from map import Map
from math import ceil, pi, sin
from interface.const import map_canvas_rect, triangle_width, triangle_height, background_color, minimap_frequency
from interface.camera import Camera
from interface.triangles import get_major_triangle_texture, get_major_triangle_light_values
import time


class Minimap:

    def __init__(self, rect, map_object: Map = None):
        self.rect = rect
        self.mouse_pressed_inside = False
        self.mouse_hover = False
        if map_object is None:
            self.image_ndarray = None
        else:
            self.image_ndarray = np.zeros(shape=(map_object.map_width // 2,
                                                 map_object.map_height // 2,
                                                 3), dtype=np.ubyte)
        self.surface = pygame.Surface(rect[2:])
        if map_object is not None:
            self.update_image(map_object)

    def draw(self, surface, map_object: Map, camera: Camera):
        surface.blit(self.surface, self.rect[:2])
        x = camera.position_on_map[0] * self.rect[2] / map_object.map_width  + self.rect[0]
        y = camera.position_on_map[1] * self.rect[3] / map_object.map_height + self.rect[1]

        rect = [ceil(x - map_canvas_rect[2] / (2 * triangle_width)),
                ceil(y - map_canvas_rect[3] / (2 * triangle_height)),
                ceil(map_canvas_rect[2] / triangle_width),
                ceil(map_canvas_rect[3] / triangle_height)]

        if rect[0] < self.rect[0]:
            rect[2] -= self.rect[0] - rect[0]
            rect[0] = self.rect[0]
        if rect[1] < self.rect[1]:
            rect[3] -= self.rect[1] - rect[1]
            rect[1] = self.rect[1]
        if rect[0] + rect[2] >= self.rect[0] + self.rect[2]:
            rect[2] = self.rect[0] + self.rect[2] - rect[0]
        if rect[1] + rect[3] >= self.rect[1] + self.rect[3]:
            rect[3] = self.rect[1] + self.rect[3] - rect[1]

        shade = min(max(round((sin(2*pi * minimap_frequency * time.time()) + 1) * 128), 0), 255)
        pygame.draw.rect(surface, (shade, shade, shade), rect, 2)

    def update_image(self, map_object: Map, *, x_range_start: int = None, x_range_stop: int = None,
                                               y_range_start: int = None, y_range_stop: int = None):
        if self.image_ndarray is None:
            self.image_ndarray = np.zeros(shape=(map_object.map_width // 2,
                                                 map_object.map_height // 2,
                                                 3), dtype=np.ubyte)
        if x_range_start is None: x_range_start = 0
        if x_range_stop  is None: x_range_stop  = map_object.map_width // 2
        if y_range_start is None: y_range_start = 0
        if y_range_stop  is None: y_range_stop  = map_object.map_height // 2

        for y in range(y_range_start, y_range_stop):
            for x in range(x_range_start, x_range_stop):
                # Only triangles from 'mepa' section are responsible for minimap in-game.
                texture = get_major_triangle_texture((x, y), "a", map_object)

                if texture.average_color is None:
                    self.image_ndarray[x, y] = background_color
                    continue

                light_value = get_major_triangle_light_values((x, y), "a", map_object)[0]


                average_color = (round(min(max(texture.average_color[0] * (light_value + 1), 0), 255)),
                                 round(min(max(texture.average_color[1] * (light_value + 1), 0), 255)),
                                 round(min(max(texture.average_color[2] * (light_value + 1), 0), 255)))

                self.image_ndarray[x, y] = average_color

        pygame.transform.scale(pygame.surfarray.make_surface(self.image_ndarray), self.rect[2:], self.surface)

    def update_camera(self, map_object: Map, camera: Camera, mouse_pos, left_press, left_press_old):

        # This function must be called when map is being loaded and when mepa section is being updated.

        if not(self.rect[0] < mouse_pos[0] <= self.rect[0] + self.rect[2] and
               self.rect[1] < mouse_pos[1] <= self.rect[1] + self.rect[3]):
            self.mouse_hover = False
            return
        self.mouse_hover = True

        if not left_press:
            self.mouse_pressed_inside = False
            return


        if left_press and not left_press_old:
            self.mouse_pressed_inside = True

        if self.mouse_pressed_inside:

            bounds_x, bounds_y = camera.get_camera_bounds(map_object)

            camera.position = [(bounds_x[1] - bounds_x[0]) * (mouse_pos[0] - self.rect[0]) / self.rect[2] + bounds_x[0],
                               (bounds_y[1] - bounds_y[0]) * (mouse_pos[1] - self.rect[1]) / self.rect[3] + bounds_y[0]]
            camera.is_moving = True
            camera.suspend_motion = True
