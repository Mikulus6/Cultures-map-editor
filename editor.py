import pygame
from map import Map
from math import floor
from interface.camera import Camera
from interface.const import animation_frames_per_second, background_color, frames_per_second, resolution, window_name
from interface.landscapes_light import adjust_opacity_pixels
from interface.interpolation import get_data_interpolated
from interface.triangles import get_major_triangle_color, get_major_triangle_corner_vertices
from supplements.animations import animations
from sys import exit as sys_exit
import time


class Editor:
    initialized = False

    def __init__(self):
        if self.__class__.initialized:
            raise ValueError(f"{self.__class__.__name__} is a singleton.")
        self.__class__.initialized = True

        pygame.init()
        pygame.display.init()

        self.root = pygame.display.set_mode(resolution)

        animations.pygame_convert()

        pygame.display.set_caption(window_name)

        self.map = Map()

        self.camera = Camera(position=[0.0, 0.0])
        self.clock = pygame.time.Clock()
        self.pressed_state = pygame.key.get_pressed()

    def loop(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.pressed_state = pygame.key.get_pressed()

            self.camera.move(self.pressed_state, self.map)

            self.draw_background()
            self.draw_terrain()
            self.draw_landscapes()

            pygame.display.flip()
            self.clock.tick(frames_per_second)

    @staticmethod
    def exit():
        pygame.quit()
        sys_exit()

    def draw_background(self):
        self.root.fill(background_color)

    def draw_landscapes(self):
        landscapes_on_screen = 0
        assert animations.__class__.pygame_converted
        for coordinates in self.camera.visible_range(self.map):
            draw_coordinates = self.camera.draw_coordinates(coordinates, self.map)

            landscape_name = self.map.llan.get(coordinates, None)

            if landscape_name is not None:
                animation = animations[landscape_name]
                frame = floor(time.time() * animation_frames_per_second) % len(animation.images)
                image = adjust_opacity_pixels(animation.images[frame], get_data_interpolated(coordinates,
                                                                                             (self.map.map_width,
                                                                                              self.map.map_height),
                                                                                             self.map.mlig))
                self.root.blit(image, (draw_coordinates[0] + animation.rect[0],
                                       draw_coordinates[1] + animation.rect[1]))

                landscapes_on_screen += 1

    def draw_terrain(self):
        triangles_on_screen = 0
        assert animations.__class__.pygame_converted
        for coordinates in self.camera.visible_range(self.map, count_minor_vertices=False):
            for triangle_type in ("a", "b"):
                corners = get_major_triangle_corner_vertices(coordinates, triangle_type)
                draw_corners = tuple(map(lambda coords: self.camera.draw_coordinates(coords, self.map), corners))

                # TODO: this code is temporary. Terrain triangles must be composed of stretched textures and shading.
                color = get_major_triangle_color(coordinates, triangle_type, self.map)

                pygame.draw.polygon(self.root, color, draw_corners)

                triangles_on_screen += 1
