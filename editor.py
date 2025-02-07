import pygame
from map import Map
from math import floor
from interface.camera import Camera
from interface.const import animation_frames_per_second, background_color, frames_per_second, resolution, window_name, \
    lru_cache_triangles_maxsize
from interface.cursor import get_closest_vertex, get_touching_triange
from interface.landscapes_light import adjust_opacity_pixels
from interface.interpolation import get_data_interpolated
from interface.projection import draw_projected_triangle, clear_triangle_projection_cache
from interface.timeout import timeout_handler
from interface.triangles import get_major_triangle_texture, get_major_triangle_corner_vertices, \
                                get_major_triangle_light_values
from supplements.animations import animations
from supplements.textures import textures
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
        textures.pygame_convert()

        pygame.display.set_caption(window_name)

        self.map = Map()

        self.camera = Camera(position=[0.0, 0.0])

        self.pressed_state = pygame.key.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_pos_old = self.mouse_pos

        self.cursor_vertex = None
        self.cursor_triangle = None

        self.clock = pygame.time.Clock()

    def loop(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.update_input()

            self.camera.move(self.pressed_state, self.map)

            self.draw_background()
            self.draw_terrain()
            self.draw_landscapes()

            self.draw_cursor_triangle()
            self.draw_cursor_vertex()

            pygame.display.flip()
            self.clock.tick(frames_per_second)

    def load(self, filepath):
        self.map.load(filepath)
        if lru_cache_triangles_maxsize is None:
            self.cache_map_triangles()

    @staticmethod
    def exit():
        pygame.quit()
        sys_exit()

    def update_input(self):

        self.pressed_state = pygame.key.get_pressed()
        self.mouse_pos_old = self.mouse_pos
        self.mouse_pos = pygame.mouse.get_pos()

        if self.mouse_pos != self.mouse_pos_old or self.camera.is_moving:

            self.cursor_vertex = get_closest_vertex(self.mouse_pos, self.camera, self.map)
            self.cursor_triangle = get_touching_triange(self.mouse_pos, self.camera, self.map)

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

        timeout_handler.get_camera_move_status(self.camera)
        timeout_handler.start()

        for coordinates in self.camera.visible_range(self.map, count_minor_vertices=False):
            for triangle_type in ("a", "b"):
                corners = get_major_triangle_corner_vertices(coordinates, triangle_type)
                draw_corners = tuple(map(lambda coords: self.camera.draw_coordinates(coords, self.map), corners))

                texture = get_major_triangle_texture(coordinates, triangle_type, self.map)
                light_values = get_major_triangle_light_values(coordinates, triangle_type, self.map)
                draw_projected_triangle(self.root, texture, draw_corners, light_values)

                triangles_on_screen += 1

    def draw_cursor_vertex(self):
        if self.cursor_vertex is not None:
            draw_cursor_vertex = self.camera.draw_coordinates(self.cursor_vertex, self.map)

            # This code is meant to mimic cursor icon present in editor from game "Cultures - Northland".
            pygame.draw.circle(self.root, (0, 0, 0),       draw_cursor_vertex, 7, 1)
            pygame.draw.circle(self.root, (255, 255, 255), draw_cursor_vertex, 6, 1)
            pygame.draw.circle(self.root, (0, 0, 0),       draw_cursor_vertex, 5, 1)

    def draw_cursor_triangle(self):
        if self.cursor_triangle is not None:

            draw_corners = tuple(map(lambda coords: self.camera.draw_coordinates(coords, self.map),
                                     get_major_triangle_corner_vertices(*self.cursor_triangle)))

            pygame.draw.polygon(self.root, (255, 255, 255), draw_corners, width=1)

    def cache_map_triangles(self):
        clear_triangle_projection_cache()

        # Warning: this method is very slow, it is not recommended to use it.

        for x in range(0, self.map.map_width//2):
            for y in range(0, self.map.map_height//2):
                for triangle_type in ("a", "b"):
                    corners = get_major_triangle_corner_vertices((x, y), triangle_type)
                    draw_corners = tuple(map(lambda coords: self.camera.draw_coordinates(coords, self.map), corners))

                    texture = get_major_triangle_texture((x, y), triangle_type, self.map)
                    light_values = get_major_triangle_light_values((x, y), triangle_type, self.map)
                    draw_projected_triangle(self.root, texture, draw_corners, light_values)

        self.root.fill((0, 0, 0))
