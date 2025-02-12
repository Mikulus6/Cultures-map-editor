import pygame
from map import Map
from math import floor

from interface.camera import Camera
from interface.const import animation_frames_per_second, background_color, frames_per_second, resolution, window_name, \
                            lru_cache_triangles_maxsize, lru_cache_landscapes_light_maxsize
from interface.cursor import get_closest_vertex, get_touching_triange
from interface.landscapes_light import adjust_opacity_pixels
from interface.interpolation import get_data_interpolated
from interface.projection import draw_projected_triangle, projection_report
from interface.structures import get_structure
from interface.timeout import timeout_handler
from interface.transitions import transitions_gen, reposition_transition_vertices, permutate_corners
from interface.triangles import get_major_triangle_texture, get_major_triangle_corner_vertices, \
                                get_major_triangle_light_values, get_triangle_corner_vertices, \
                                get_minor_triangle_light_values

from supplements.animations import animations
from supplements.textures import patterndefs_textures, transition_textures
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

        self.terrain_surface = pygame.Surface(resolution)
        self.terrain_loaded = False

        animations.pygame_convert()
        patterndefs_textures.pygame_convert()
        transition_textures.pygame_convert()

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

            if self.camera.is_moving or not self.terrain_loaded:
                self.terrain_loaded = False
                self.terrain_surface.fill(background_color)
                self.draw_terrain()

            self.root.fill(background_color)
            self.root.blit(self.terrain_surface)
            self.draw_landscapes()

            self.draw_cursor_triangle()
            self.draw_cursor_vertex()

            projection_report.draw_loading_bar(self.root)

            pygame.display.flip()
            self.clock.tick(frames_per_second)

    def load(self, filepath):
        self.map.load(filepath)

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

    def draw_landscapes(self):
        assert animations.__class__.pygame_converted

        landscapes_on_screen = 0

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

            if landscapes_on_screen >= lru_cache_landscapes_light_maxsize:
                break

    def draw_terrain(self):
        assert animations.__class__.pygame_converted

        triangles_on_screen = 0

        projection_report.reset()
        timeout_handler.get_camera_move_status(self.camera)
        timeout_handler.start()

        transitions_to_draw = []
        for coordinates in self.camera.visible_range(self.map, count_minor_vertices=False):
            for triangle_type in ("a", "b"):
                corners = get_major_triangle_corner_vertices(coordinates, triangle_type)
                draw_corners = tuple(map(lambda coords: self.camera.draw_coordinates(coords, self.map), corners))

                texture = get_major_triangle_texture(coordinates, triangle_type, self.map)
                light_values = get_major_triangle_light_values(coordinates, triangle_type, self.map)
                draw_projected_triangle(self.terrain_surface, texture, draw_corners, light_values)
                triangles_on_screen += 1

                for transition_texture, transition_key in transitions_gen(coordinates, triangle_type, self.map):
                    transitions_to_draw.append((transition_texture, transition_key, draw_corners, light_values))

        for transition_texture, transition_key, draw_corners, light_values in transitions_to_draw:
            transition_draw_corners = reposition_transition_vertices(draw_corners, transition_key)
            transition_light_values = permutate_corners(light_values, transition_key)
            draw_projected_triangle(self.terrain_surface, transition_texture, transition_draw_corners,
                                    transition_light_values)
            triangles_on_screen += 1

        if not self.camera.is_moving:
            # Structures are ignored when camera is in motion, to make it smooth.

            for coordinates in self.camera.visible_range(self.map):
                for triangle_type, texture in get_structure(coordinates, self.map).items():
                    corners = get_triangle_corner_vertices(coordinates, triangle_type)
                    draw_corners = tuple(map(lambda coords: self.camera.draw_coordinates(coords, self.map), corners))
                    light_values = get_minor_triangle_light_values(coordinates, triangle_type, self.map)
                    draw_projected_triangle(self.terrain_surface, texture, draw_corners, light_values)
                    triangles_on_screen += 1

        try:
            timeout_handler.check()
            self.terrain_loaded = True
        except TimeoutError:
            pass

        if triangles_on_screen > lru_cache_triangles_maxsize:
            self.terrain_loaded = True

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
