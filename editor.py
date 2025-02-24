import copy
import os
import pygame
from map import Map
from math import floor
from sections.walk_sector_points import sector_width
from supplements.animations import animations
from supplements.textures import patterndefs_textures, transition_textures
from sys import exit as sys_exit
import time
from typing import Literal

from interface.brushes import Brush, warp_coordinates_in_bounds, warp_to_major
from interface.buttons import load_buttons
from interface.camera import Camera, clear_point_coordinates_cache
from interface.const import *
from interface.cursor import get_closest_vertex, get_touching_triange
from interface.external import askopenfilename, asksaveasfilename, ask_new_map, ask_resize_map
from interface.interpolation import get_data_interpolated
from interface.landscapes_light import adjust_opaque_pixels
from interface.light import update_light_local
from interface.message import message, set_font_text, one_frame_popup
from interface.minimap import Minimap
from interface.projection import draw_projected_triangle, projection_report
from interface.structures import get_structure, update_structures
from interface.timeout import timeout_handler
from interface.transitions import transitions_gen, reposition_transition_vertices, permutate_corners
from interface.triangles import get_major_triangle_texture, get_major_triangle_corner_vertices, \
                                get_major_triangle_light_values, get_triangle_corner_vertices, \
                                get_minor_triangle_light_values


class Editor:
    initialized = False

    def __init__(self):
        if self.__class__.initialized:
            raise ValueError(f"{self.__class__.__name__} is a singleton.")
        self.__class__.initialized = True

        pygame.init()
        pygame.display.init()

        self.root = pygame.display.set_mode(resolution)

        self.terrain_surface = pygame.Surface(map_canvas_rect[2:])
        self.terrain_loaded = False

        self.font = pygame.font.SysFont(font_name, font_size)
        self.font_text = ""

        animations.pygame_convert()
        patterndefs_textures.pygame_convert()
        transition_textures.pygame_convert()

        pygame.display.set_caption(window_name)

        self.map = Map()
        self.map.empty((sector_width, sector_width))
        self.minimap = Minimap(minimap_rect, self.map)

        self.map_filepath: str = None

        self.camera = Camera(position=[0.0, 0.0])
        self.buttons_list = load_buttons(self)

        self.pressed_state = pygame.key.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_pos_old = self.mouse_pos

        self.ignore_minor_vertices = True

        self.cursor_vertex = None
        self.cursor_triangle = None

        self.mouse_press_left = False
        self.mouse_press_left_old = False
        self.mouse_press_right = False
        self.mouse_press_right_old = False
        self.scroll_delta = 0
        self.scroll_radius = 0

        self.clock = pygame.time.Clock()

    def loop(self):
        running = True

        while running:

            self.mouse_press_left_old = self.mouse_press_left
            self.mouse_press_right_old = self.mouse_press_right

            button_left_detected = False
            button_right_detected = False
            scroll_detected = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and not button_left_detected:
                       self.mouse_press_left = True
                       button_left_detected = True
                    if event.button == 3 and not button_right_detected:
                       self.mouse_press_right = True
                       button_right_detected = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and not button_left_detected:
                       self.mouse_press_left = False
                       button_left_detected = True
                    if event.button == 3 and not button_right_detected:
                       self.mouse_press_right = False
                       button_right_detected = True

                elif event.type == pygame.MOUSEWHEEL:
                    scroll_detected = True
                    self.scroll_delta = event.y

            pressed_state = pygame.mouse.get_pressed(3)
            if not button_left_detected:
                self.mouse_press_left = pressed_state[0]
            if not button_right_detected:
                self.mouse_press_right = pressed_state[2]
            if not scroll_detected:
                self.scroll_delta = 0

            self.update_input()

            self.minimap.update_camera(self. map, self.camera,
                                       self.mouse_pos, self.mouse_press_left,
                                       self.mouse_press_left_old)
            self.camera.move(self.pressed_state, self.map)

            if self.camera.is_moving or not self.terrain_loaded:
                self.terrain_loaded = False
                self.terrain_surface.fill(background_color)
                self.draw_terrain()

            self.root.fill(background_color)
            self.root.blit(self.terrain_surface, map_canvas_rect[:2])
            self.draw_landscapes()

            self.draw_cursor_vertex()
            self.draw_cursor_hexagonal_radius()

            self.draw_user_interface()

            clear_point_coordinates_cache()
            projection_report.draw_loading_bar(self.root)

            for button in self.buttons_list:
                button.action()

            pygame.display.flip()
            self.clock.tick(frames_per_second)

    @staticmethod
    def exit():
        pygame.quit()
        sys_exit()

    def update_input(self):

        self.pressed_state = pygame.key.get_pressed()
        self.mouse_pos_old = self.mouse_pos
        self.mouse_pos = pygame.mouse.get_pos()

        if self.mouse_pos != self.mouse_pos_old or self.camera.is_moving:

            self.cursor_vertex = get_closest_vertex(self.mouse_pos, self.camera, self.map,
                                                    ignore_minor_vertices=self.ignore_minor_vertices)
            self.cursor_triangle = get_touching_triange(self.mouse_pos, self.camera, self.map)

        old_scroll_radius = self.scroll_radius
        if self.ignore_minor_vertices and self.scroll_delta % 2 != 0:
            if self.scroll_radius % 2 != 0:
                self.scroll_radius = (self.scroll_radius // 2) * 2
            self.scroll_delta *= 2

        if self.cursor_vertex is not None and self.scroll_delta != 0:
            self.scroll_radius = min(max(self.scroll_radius - self.scroll_delta, 0), max_scroll_radius)

        if old_scroll_radius != self.scroll_radius:
            if self.ignore_minor_vertices:
                message.set_message(f"major brush radius: {self.scroll_radius // 2}")
            else:
                message.set_message(f"minor brush radius: {self.scroll_radius}")

    # ================================  functionalities  ================================

    def new(self, size: tuple[int, int] = None):
        if size is None:
            size = ask_new_map()
        old_map = copy.deepcopy(self.map)
        try:
            one_frame_popup(self, "Creating new map...")
            self.map.empty(size)
            self._update()
            self.map_filepath = None
        except TypeError:
            self.map = old_map
            message.set_message(f"Error: Couldn't create map.")

    def open(self, filepath: str = None):
        if filepath is None:
            filepath = askopenfilename(title="Open map", default="*.map", filetypes=(("map files", "*.map"),
                                                                                     ("all files", "*.*")))
        old_map = copy.deepcopy(self.map)
        try:
            one_frame_popup(self, "Opening map...")
            self.map.load(filepath)
            self._update()
            self.map_filepath = os.path.abspath(filepath)
            message.set_message(f"Map has been opened.")
        except (FileNotFoundError, TypeError, NotImplementedError):
            self.map = old_map
            message.set_message(f"Error: Couldn't open map file.")

    def save(self):
        if self.map_filepath is None:
            self.save_as()
        else:
            try:
                self.map.from_bytearrays()
                one_frame_popup(self, "Saving map...")
                self.map.update_all()
                self.map.save(self.map_filepath)
                message.set_message(f"Map has been saved.")
            except TypeError:
                message.set_message(f"Error: Couldn't save map file.")

    def save_as(self, filepath: str = None):
        if filepath is None:
            filepath = asksaveasfilename(title="Save map", default=self.map_filepath, filetypes=(("map files", "*.map"),
                                                                                                 ("all files", "*.*")))
        try:
            if filepath is None:
                raise TypeError
            one_frame_popup(self, "Saving map...")
            self.map.from_bytearrays()
            self.map.update_all()
            self.map.save(filepath)
            self.map_filepath = filepath
            message.set_message(f"Map has been saved.")
        except TypeError:
            message.set_message(f"Error: Couldn't save map file.")

    def resize(self, deltas : (int, int, int, int) = None):
        # deltas = (top, bottom, left, right)
        if deltas is None:
            deltas = ask_resize_map(self.map.map_width, self.map.map_height)
        try:
            one_frame_popup(self, "Resizing map...")
            camera_old_pos = self.camera.position
            self.map.resize_visible(deltas)
            self._update()
            self.camera.position = [camera_old_pos[0] + deltas[3] * triangle_width,
                                    camera_old_pos[1] + deltas[0] * triangle_height]
            for x in (0, self.map.map_width - 1):
                for y in range(0, self.map.map_height):
                    self.update_structures((x, y), None)
            for y in (0, self.map.map_height - 1):
                for x in range(0, self.map.map_width):
                    self.update_structures((x, y), None)
        except TypeError:
            message.set_message(f"Error: Couldn't resize map.")

    def _update(self):
        """Update editor data according to external change in map object."""
        self.map.to_bytearrays()
        self.camera = Camera(position=[0.0, 0.0])
        self.camera.set_to_center(self.map)
        self.minimap = Minimap(minimap_rect, self.map)
        self.minimap.update_image(self.map)
        self.terrain_loaded = False

    # ====================================  visuals  ====================================

    def draw_landscapes(self):
        assert animations.__class__.pygame_converted

        landscapes_on_screen = 0

        for coordinates in self.camera.visible_range(self.map):
            draw_coordinates = self.camera.draw_coordinates(coordinates, self.map, include_canvas_offset=True)

            landscape_name = self.map.llan.get(coordinates, None)

            if landscape_name is not None:
                animation = animations[landscape_name]
                frame = floor(time.time() * animation_frames_per_second) % len(animation.images)
                image = adjust_opaque_pixels(animation.images[frame], get_data_interpolated(coordinates,
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
                draw_corners = (self.camera.draw_coordinates(corners[0], self.map),
                                self.camera.draw_coordinates(corners[1], self.map),
                                self.camera.draw_coordinates(corners[2], self.map))

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

            # TODO: when terrain is very steep structures and landscapes aren't displayed correctly
            #  (they are on top of triangles which have higher y coordinate)
            for coordinates in self.camera.visible_range(self.map):
                for triangle_type, texture in get_structure(coordinates, self.map).items():
                    corners = get_triangle_corner_vertices(coordinates, triangle_type)
                    draw_corners = (self.camera.draw_coordinates(corners[0], self.map),
                                    self.camera.draw_coordinates(corners[1], self.map),
                                    self.camera.draw_coordinates(corners[2], self.map))
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
            if self.ignore_minor_vertices:
                cursor_vertex = (self.cursor_vertex[0] * 2 + (self.cursor_vertex[1] % 2),
                                 self.cursor_vertex[1] * 2)
            else:
                cursor_vertex = self.cursor_vertex

            draw_cursor_vertex = self.camera.draw_coordinates(cursor_vertex, self.map, include_canvas_offset=True)

            # This code is meant to mimic cursor icon present in editor from game "Cultures - Northland".
            pygame.draw.circle(self.root, (0, 0, 0),       draw_cursor_vertex, 7, 1)
            pygame.draw.circle(self.root, (255, 255, 255), draw_cursor_vertex, 6, 1)
            pygame.draw.circle(self.root, (0, 0, 0),       draw_cursor_vertex, 5, 1)

    def draw_cursor_triangle(self):
        if self.cursor_triangle is not None:

            corners = get_major_triangle_corner_vertices(*self.cursor_triangle)

            draw_corners = (self.camera.draw_coordinates(corners[0], self.map, include_canvas_offset=True),
                            self.camera.draw_coordinates(corners[1], self.map, include_canvas_offset=True),
                            self.camera.draw_coordinates(corners[2], self.map, include_canvas_offset=True))


            pygame.draw.polygon(self.root, (255, 255, 255), draw_corners, width=1)

    def draw_cursor_hexagonal_radius(self, draw_if_major_radius_zero: bool = True):
        if self.ignore_minor_vertices and draw_if_major_radius_zero and self.scroll_radius == 0:
            self.draw_cursor_triangle()
            return
        elif self.scroll_radius == 0 or self.cursor_vertex is None:
            return

        points, edge_points = Brush.get_points_and_edge_points(self.map, self.cursor_vertex, self.scroll_radius,
                                                               ignore_minor_vertices=self.ignore_minor_vertices)

        for edge_point_1, edge_point_2 in zip(edge_points, [*edge_points[1:], edge_points[0]]):

            if self.ignore_minor_vertices and \
               not edge_point_1[1] % 2 == 0 and edge_point_2[1] % 2 == 0:
                continue

            edge_point_1 = warp_coordinates_in_bounds(self.map, edge_point_1)
            edge_point_2 = warp_coordinates_in_bounds(self.map, edge_point_2)

            if self.ignore_minor_vertices:

                # Major triangles on the edge on the map, which have some of their vertices out of bounds, are excluded
                # from hexagonal radius due to edge being displayed based on in-bound major vertices. This would be a
                # significant issue if maps would mean to be editable there, but since there is void margin present
                # there anyway, it is not that much of a problem.

                edge_point_1 = warp_to_major(edge_point_1)
                edge_point_2 = warp_to_major(edge_point_2)

            edge_point_1_draw = self.camera.draw_coordinates(edge_point_1, self.map, include_canvas_offset=True)
            edge_point_2_draw = self.camera.draw_coordinates(edge_point_2, self.map, include_canvas_offset=True)

            pygame.draw.line(self.root, (255, 255, 255), edge_point_1_draw, edge_point_2_draw)

    def draw_user_interface(self):

        pygame.draw.rect(self.root, (101, 67, 33), (0, 0, 267, 600))
        pygame.draw.rect(self.root, (50, 33, 16),  (0, 0, 267, 600), 6)

        self.font_text = None

        for button in self.buttons_list:
            button.draw()

        set_font_text(self)

        self.root.blit(self.font.render(self.font_text, antialias=font_antialias, color=font_color),
                       (10, resolution[1] - 40))

        self.minimap.draw(self.root, self.map, self.camera)

    # ====================================  updates  ====================================

    def update_triange(self, coordinates, triangle_type: Literal["a", "b"], mep_id: int):
        index_bytes = coordinates[1] * self.map.map_width + coordinates[0] * 2
        match triangle_type:
            case "a": self.map.mepa[index_bytes: index_bytes + 2] = int.to_bytes(mep_id, length=2, byteorder="little")
            case "b": self.map.mepb[index_bytes: index_bytes + 2] = int.to_bytes(mep_id, length=2, byteorder="little")
        self.terrain_loaded = False

    def update_height(self, coordinates, height_delta: int = 1):
        index_value = coordinates[1] * (self.map.map_width // 2) + coordinates[0]
        self.map.mhei[index_value] = min(max(self.map.mhei[index_value] + height_delta, 0), 255)
        self.terrain_loaded = False

    def update_landscape(self, coordinates, landscape_name: str | None):
        if landscape_name is None and (*coordinates,) in self.map.llan.keys():
            del self.map.llan[*coordinates]
        else:
            self.map.llan[*coordinates] = landscape_name

    def update_structures(self, coordinates, structure_type: Literal[None, "road", "river", "snow"]):
        update_structures(self.map, coordinates, structure_type)
        self.terrain_loaded = False

    def update_local_secondary_data(self, coordinates, margin: int = 1):

        update_light_local(self.map, x_range_start=coordinates[0] - margin, x_range_stop=coordinates[0] + margin,
                                     y_range_start=coordinates[1] - margin, y_range_stop=coordinates[1] + margin)
        self.minimap.update_image(self.map, x_range_start=coordinates[0] - margin, x_range_stop=coordinates[0] + margin,
                                            y_range_start=coordinates[1] - margin, y_range_stop=coordinates[1] + margin)
        self.terrain_loaded = False
