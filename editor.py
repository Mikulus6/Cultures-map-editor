import copy
from datetime import datetime
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

from interface.border import update_map_border, remove_landscapes_from_border, remove_structures_from_border
from interface.brushes import Brush, warp_coordinates_in_bounds, warp_to_major, edge_coordinates_ordered_in_radius
from interface.buttons import load_buttons, background
from interface.camera import Camera, clear_point_coordinates_cache
from interface.catalogue import load_patterns_catalogue, load_landscapes_catalogue, load_structures_catalogue, \
                                load_landscapes_groups_catalogue, load_patterns_groups_catalogue
from interface.const import *
from interface.cursor import get_closest_vertex, get_touching_triange, is_vertex_major
from interface.external import askopenfilename, asksaveasfilename, ask_new_map, askdirectory, ask_resize_map, \
                               ask_brush_parameters, ask_enforce_height, ask_area_mark, warning_too_many_area_marks ,\
                               ask_save_changes
from interface.horizont import enforce_horizonless_heightmap
from interface.interpolation import get_data_interpolated
from interface.invisible import transparent_landscapes_color_match, color_circle_radius, render_legend
from interface.landscapes_area import AreaTable
from interface.landscapes_light import adjust_opaque_pixels
from interface.light import update_light_local
from interface.message import message, set_font_text, one_frame_popup
from interface.minimap import Minimap
from interface.projection import draw_projected_triangle, projection_report
from interface.states import states_machine
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

        pygame.display.set_caption(window_name)
        pygame.display.set_icon(pygame.image.load(window_icon_filepath))

        self.invisible_landscapes_display = False
        self.invisible_blocks_display = False
        self.terrian_textures_suspension = False
        self.terrain_surface = pygame.Surface(map_canvas_rect[2:])
        self.terrain_loaded = False

        self.font = pygame.font.SysFont(font_name, font_size)
        self.font_text = ""

        animations.pygame_convert()
        patterndefs_textures.pygame_convert()
        transition_textures.pygame_convert()
        self.invisible_landscapes_legend = render_legend(self)
        self.patterns_catalogue = load_patterns_catalogue()
        self.patterns_group_catalogue = load_patterns_groups_catalogue()
        self.landscapes_catalogue = load_landscapes_catalogue()
        self.landscapes_group_catalogue = load_landscapes_groups_catalogue()
        self.structures_catalogue = load_structures_catalogue()

        self.map = Map()
        self.map.empty((sector_width, sector_width))
        self.map.to_bytearrays()
        self.minimap = Minimap(minimap_rect, self.map)
        self.progress_saved = True

        self.base_area     = AreaTable(self.map.map_width, self.map.map_height, area_type="Base")
        self.extended_area = AreaTable(self.map.map_width, self.map.map_height, area_type="Extended")

        self.map_filepath: str = None

        self.camera = Camera(position=[0.0, 0.0])
        self.camera.set_to_center(self.map)
        self.hexagonal_area_marks = set()

        self.buttons_list = load_buttons(self)

        self.pressed_state = pygame.key.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_pos_old = self.mouse_pos

        self.ignore_minor_vertices = False
        self.ignore_singular_triangle = True

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
                    if self.progress_saved or ask_save_changes(on_quit=True):
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
            if self.invisible_blocks_display:
                self.draw_invisible_blocks()

            if self.scroll_radius > 0 or self.ignore_singular_triangle:
                self.draw_cursor_vertex()
            self.draw_marked_areas()
            self.draw_cursor_hexagonal_radius()

            self.draw_user_interface()

            if self.invisible_landscapes_display:
                self.root.blit(self.invisible_landscapes_legend, (map_canvas_rect[0] + invisible_legend_draw_margin,
                                                                  map_canvas_rect[1] + invisible_legend_draw_margin))

            clear_point_coordinates_cache()
            projection_report.draw_loading_bar(self.root)

            states_machine.run_current_state(self)

            for button in self.buttons_list:
                button.action()

            self.draw_message()

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

        if not(self.progress_saved or ask_save_changes()):
            return

        if size is None:
            size = ask_new_map()
        old_map = copy.deepcopy(self.map)
        try:
            one_frame_popup(self, "Creating new map...")
            self.map.empty(size)
            self._update()
            self.map_filepath = None
            self.hexagonal_area_marks = set()
            self.base_area.reset_and_resize(self.map.map_width, self.map.map_height)
            self.extended_area.reset_and_resize(self.map.map_width, self.map.map_height)
            self.progress_saved = False
        except TypeError:
            self.map = old_map
            message.set_message(f"error: couldn't create map.")

    def open(self, filepath: str = None):
        if filepath is None:
            if self.progress_saved or ask_save_changes():
                filepath = askopenfilename(title="Open map", default="*.map", filetypes=(("map files", "*.map"),
                                                                                         ("all files", "*.*")))
        old_map = copy.deepcopy(self.map)
        try:
            one_frame_popup(self, "Opening map...")
            self.map.load(filepath)
            self._update()
            self.map_filepath = os.path.abspath(filepath)
            self.hexagonal_area_marks = set()
            self.progress_saved = True
            self.base_area.reset_and_resize(self.map.map_width, self.map.map_height)
            self.base_area.update_landscapes_presence_ndarray(self.map)
            self.extended_area.reset_and_resize(self.map.map_width, self.map.map_height)
            self.extended_area.update_landscapes_presence_ndarray(self.map)
            message.set_message(f"Map has been opened.")
        except (FileNotFoundError, TypeError, NotImplementedError):
            self.map = old_map
            message.set_message(f"error: couldn't open map file.")

    def save(self):
        if self.map_filepath is None:
            self.save_as()
        else:
            try:
                self.map.from_bytearrays()
                one_frame_popup(self, "Saving map...")
                self.map.update_all()
                self.map.save(self.map_filepath)
                self.progress_saved = True
                message.set_message(f"Map has been saved.")
            except TypeError:
                message.set_message(f"error: couldn't save map file.")
        self.map.to_bytearrays()

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
            self.progress_saved = True
            message.set_message(f"Map has been saved.")
        except TypeError:
            message.set_message(f"error: couldn't save map file.")
        self.map.to_bytearrays()

    def extract(self):
        dirpath = askdirectory()

        try:
            one_frame_popup(self, "Exporting map...")
            dirpath = os.path.join(dirpath, datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
            self.map.extract(dirpath)
            message.set_message(f"Map has been exported.")
        except TypeError:
            message.set_message(f"error: couldn't export map.")

    def pack(self):

        if not(self.progress_saved or ask_save_changes()):
            return

        dirpath = askdirectory()

        try:
            one_frame_popup(self, "Importing map...")
            self.map.pack(dirpath)
            message.set_message(f"Map has been imported.")
            self._update()
            self.map_filepath = None
            self.hexagonal_area_marks = set()
            self.base_area.reset_and_resize(self.map.map_width, self.map.map_height)
            self.base_area.update_landscapes_presence_ndarray(self.map)
            self.extended_area.reset_and_resize(self.map.map_width, self.map.map_height)
            self.extended_area.update_landscapes_presence_ndarray(self.map)
        except (FileNotFoundError, TypeError):
            message.set_message(f"error: couldn't import map.")

    def terrain_textures(self):
        self.terrian_textures_suspension = not self.terrian_textures_suspension
        self.terrain_loaded = False
        if self.terrian_textures_suspension:
            message.set_message(f"Terrain textures are now disabled.")
        else:
            message.set_message(f"Terrain textures are now enabled.")

    def invisible_landscapes(self):
        self.invisible_landscapes_display = not self.invisible_landscapes_display
        if self.invisible_landscapes_display:
            message.set_message(f"Invisible landscapes are now shown.")
        else:
            message.set_message(f"Invisible landscapes are now hidden.")

    def invisible_blocks(self):
        self.invisible_blocks_display = not self.invisible_blocks_display
        if self.invisible_blocks_display:
            message.set_message(f"Blockades are now shown.")
        else:
            message.set_message(f"Blockades are now hidden.")

    def mark_area(self):
        entry = ask_area_mark()
        if entry is None:
            return
        elif entry == "remove":
            self.hexagonal_area_marks = set()
        elif len(self.hexagonal_area_marks) >= lru_cache_edges_maxsize and entry not in self.hexagonal_area_marks:
            warning_too_many_area_marks()
        else:
            self.hexagonal_area_marks.add(entry)

    def resize(self, deltas : (int, int, int, int) = None):
        # deltas = (top, bottom, left, right)
        old_mstr = copy.copy(self.map.mstr)
        data = ask_resize_map(self.map.map_width, self.map.map_height) if deltas is None else (deltas, False, False)
        try:
            deltas, remove_landscapes, remove_structures = data
            if tuple(deltas) != (0, 0, 0, 0):
                one_frame_popup(self, "Resizing map...")
                camera_old_pos = self.camera.position

                self.map.resize_visible(deltas)
                update_map_border(self)
                self.map.update_light()
                self._update()
                self.camera.position = [camera_old_pos[0] + deltas[2] * triangle_width,
                                        camera_old_pos[1] + deltas[0] * triangle_height]
                self.hexagonal_area_marks = set((x + deltas[2], y + deltas[0], radius)
                                                for x, y, radius in self.hexagonal_area_marks)

                self.progress_saved = False
            if remove_landscapes:
                remove_landscapes_from_border(self.map)
                self.progress_saved = False
            if remove_structures:
                remove_structures_from_border(self)
                self.progress_saved = False

            if tuple(deltas) != (0, 0, 0, 0) or remove_structures:
                for x in (0, self.map.map_width - 1):
                    for y in range(0, self.map.map_height):
                        self.update_structures((x, y), None)
                for y in (0, self.map.map_height - 1):
                    for x in range(0, self.map.map_width):
                        self.update_structures((x, y), None)

            if tuple(deltas) != (0, 0, 0, 0) or remove_landscapes:
                self.base_area.reset_and_resize(self.map.map_width, self.map.map_height)
                self.base_area.update_landscapes_presence_ndarray(self.map)
                self.extended_area.reset_and_resize(self.map.map_width, self.map.map_height)
                self.extended_area.update_landscapes_presence_ndarray(self.map)

        except TypeError:
            self.map.mstr = old_mstr
            message.set_message(f"error: couldn't resize map.")

    def pattern_single(self):
        if self.scroll_radius % 2 != 0: self.scroll_radius -= 1
        states_machine.set_state("pattern_single")

    def pattern_group(self):
        if self.scroll_radius % 2 != 0: self.scroll_radius -= 1
        states_machine.set_state("pattern_group")

    def height(self):
        if self.scroll_radius % 2 != 0: self.scroll_radius -= 1
        states_machine.set_state("height")

    def enforce_height(self):
        if ask_enforce_height():
            enforce_horizonless_heightmap(self)
            one_frame_popup(self, "Modifying height...")
            self.terrain_loaded = False
            self.map.update_light()
            self.minimap.update_image(self.map)
            self.map.to_bytearrays()
            self.progress_saved = False

    @staticmethod
    def landscape_single():
        states_machine.set_state("landscape_single")

    @staticmethod
    def landscape_group():
        states_machine.set_state("landscape_group")

    @staticmethod
    def brush_adjust():
        ask_brush_parameters()

    @staticmethod
    def structures():
        states_machine.set_state("structures")

    def close_tool(self):
        self.ignore_minor_vertices = False
        self.ignore_singular_triangle = True
        states_machine.set_state(None)

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

            if self.invisible_landscapes_display and landscape_name in transparent_landscapes_color_match.keys():

                pygame.draw.circle(self.root, transparent_landscapes_color_match[landscape_name], draw_coordinates,
                                   color_circle_radius)


            elif landscape_name is not None:
                animation = animations[landscape_name.lower()]
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

        for coordinates in self.camera.visible_range(self.map, count_minor_vertices=True):
            if is_vertex_major(coordinates):
                for triangle_type in ("a", "b"):
                    coordinates_major = (coordinates[0] // 2, coordinates[1]//2)
                    corners = get_major_triangle_corner_vertices(coordinates_major, triangle_type)
                    draw_corners = (self.camera.draw_coordinates(corners[0], self.map),
                                    self.camera.draw_coordinates(corners[1], self.map),
                                    self.camera.draw_coordinates(corners[2], self.map))

                    texture = get_major_triangle_texture(coordinates_major, triangle_type, self.map)
                    light_values = get_major_triangle_light_values(coordinates_major, triangle_type, self.map)
                    draw_projected_triangle(self.terrain_surface, texture, draw_corners, light_values,
                                            suspend_loading_textures=self.terrian_textures_suspension)
                    triangles_on_screen += 1

                    if not self.camera.is_moving:  # This condition is only for lag reduction.
                        for transition_texture, transition_key in transitions_gen(coordinates_major,
                                                                                  triangle_type, self.map):
                            transition_draw_corners = reposition_transition_vertices(draw_corners, transition_key)
                            transition_light_values = permutate_corners(light_values, transition_key)
                            draw_projected_triangle(self.terrain_surface, transition_texture, transition_draw_corners,
                                                    transition_light_values,
                                                    suspend_loading_textures=self.terrian_textures_suspension)
                            triangles_on_screen += 1

            for triangle_type, texture in get_structure(coordinates, self.map).items():
                corners = get_triangle_corner_vertices(coordinates, triangle_type)
                draw_corners = (self.camera.draw_coordinates(corners[0], self.map),
                                self.camera.draw_coordinates(corners[1], self.map),
                                self.camera.draw_coordinates(corners[2], self.map))
                light_values = get_minor_triangle_light_values(coordinates, triangle_type, self.map)
                draw_projected_triangle(self.terrain_surface, texture, draw_corners, light_values,
                                        suspend_loading_textures = self.terrian_textures_suspension)
                triangles_on_screen += 1

        try:
            timeout_handler.check()
            self.terrain_loaded = True
        except TimeoutError:
            pass

        if triangles_on_screen > lru_cache_triangles_maxsize:
            self.terrain_loaded = True

    def draw_invisible_blocks(self):

        for coordinates in self.camera.visible_range(self.map, count_minor_vertices=True):
            draw_base = self.base_area.ndarray[coordinates[::-1]]
            draw_extended = self.extended_area.ndarray[coordinates[::-1]]

            if draw_base or draw_extended:
                draw_coordinates = self.camera.draw_coordinates(coordinates, self.map, include_canvas_offset=True)
                if draw_base:     pygame.draw.circle(self.root, (255, 0, 0), draw_coordinates, 8, 2)
                if draw_extended: pygame.draw.circle(self.root, (0, 0, 255), draw_coordinates, 6, 2)

        self.terrain_loaded = False

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

    def draw_hexagonal_radius(self, coordinates, radius, ignore_minor_vertices,
                              color=(255, 255, 255), *, use_precalculated: bool = True):

        if use_precalculated:
            edge_points = Brush.get_points_and_edge_points(self.map, coordinates, radius,
                                                           ignore_minor_vertices=ignore_minor_vertices)[1]
        else:
            edge_points = edge_coordinates_ordered_in_radius(coordinates, radius,
                                                             ignore_minor_vertices=ignore_minor_vertices)

        for edge_point_1, edge_point_2 in zip(edge_points, [*edge_points[1:], edge_points[0]]):

            if ignore_minor_vertices and not edge_point_1[1] % 2 == 0 and edge_point_2[1] % 2 == 0:
                continue

            edge_point_1 = warp_coordinates_in_bounds(self.map, edge_point_1)
            edge_point_2 = warp_coordinates_in_bounds(self.map, edge_point_2)

            if ignore_minor_vertices:

                # Major triangles on the edge on the map, which have some of their vertices out of bounds, are excluded
                # from hexagonal radius due to edge being displayed based on in-bound major vertices. This would be a
                # significant issue if maps would mean to be editable there, but since there is void margin present
                # there anyway, it is not that much of a problem.

                edge_point_1 = warp_to_major(edge_point_1)
                edge_point_2 = warp_to_major(edge_point_2)

            edge_point_1_draw = self.camera.draw_coordinates(edge_point_1, self.map, include_canvas_offset=True)
            edge_point_2_draw = self.camera.draw_coordinates(edge_point_2, self.map, include_canvas_offset=True)

            pygame.draw.line(self.root, color, edge_point_1_draw, edge_point_2_draw)

    def draw_cursor_hexagonal_radius(self, draw_if_major_radius_zero: bool = True):
        if self.ignore_minor_vertices and draw_if_major_radius_zero and self.scroll_radius == 0:
            if not self.ignore_singular_triangle: self.draw_cursor_triangle()
            return
        elif self.scroll_radius == 0 or self.cursor_vertex is None:
            return

        self.draw_hexagonal_radius(self.cursor_vertex, self.scroll_radius, self.ignore_minor_vertices, (255, 255, 255))

    def draw_marked_areas(self):
        for x, y, radius in self.hexagonal_area_marks:
            if radius > 0:
                self.draw_hexagonal_radius((x, y), radius, ignore_minor_vertices=False, color=(255, 0, 0, 128),
                                           use_precalculated=False)
            draw_coordinates = self.camera.draw_coordinates((x, y), self.map, include_canvas_offset=True)
            pygame.draw.circle(self.root, (255, 0, 0), draw_coordinates, 7, 3)

    def draw_user_interface(self):

        self.root.blit(background, (0, 0))

        self.font_text = None
        self.font_text = message.get_message()

        for button in self.buttons_list:
            button.draw()

        set_font_text(self)

        self.minimap.draw(self.root, self.map, self.camera)

    def draw_message(self):
        if self.font_text is None:
            self.font_text = font_default_text
        self.root.blit(self.font.render(self.font_text, antialias=font_antialias, color=font_color),
                       (10, resolution[1] - 40))

    # ====================================  updates  ====================================

    def update_triange(self, coordinates, triangle_type: Literal["a", "b"], mep_id: int):
        index_bytes = coordinates[1] * self.map.map_width + coordinates[0] * 2
        match triangle_type:
            case "a": self.map.mepa[index_bytes: index_bytes + 2] = int.to_bytes(mep_id, length=2, byteorder="little")
            case "b": self.map.mepb[index_bytes: index_bytes + 2] = int.to_bytes(mep_id, length=2, byteorder="little")
        self.terrain_loaded = False
        self.progress_saved = False

    def update_height(self, coordinates, height_value: float | int = 0, as_delta: bool = False):
        index_value = coordinates[1] * (self.map.map_width // 2) + coordinates[0]
        self.map.mhei[index_value] = min(max(self.map.mhei[index_value] + round(height_value), 0), 255) \
                                     if as_delta else min(max(round(height_value), 0), 255)
        self.terrain_loaded = False
        self.progress_saved = False

    def update_landscape(self, coordinates, landscape_name: str | None):
        landscape_name_old = self.map.llan.get(coordinates, None)
        if landscape_name is None and (*coordinates,) in self.map.llan.keys():
            del self.map.llan[*coordinates]
            self.progress_saved = False
            self.base_area.update_on_landscape_change(landscape_name_old, landscape_name, coordinates, self.map)
            self.extended_area.update_on_landscape_change(landscape_name_old, landscape_name, coordinates, self.map)
        elif landscape_name is not None:
            self.map.llan[*coordinates] = landscape_name
            self.progress_saved = False
            self.base_area.update_on_landscape_change(landscape_name_old, landscape_name, coordinates, self.map)
            self.extended_area.update_on_landscape_change(landscape_name_old, landscape_name, coordinates, self.map)

    def update_structures(self, coordinates, structure_type: Literal[None, "road", "river", "snow"]):
        update_structures(self.map, coordinates, structure_type)
        self.terrain_loaded = False
        self.progress_saved = False

    def update_local_secondary_data(self, coordinates, margin: int = 1):

        update_light_local(self.map, x_range_start=coordinates[0] - margin, x_range_stop=coordinates[0] + margin,
                                     y_range_start=coordinates[1] - margin, y_range_stop=coordinates[1] + margin)
        self.minimap.update_image(self.map, x_range_start=coordinates[0] - margin, x_range_stop=coordinates[0] + margin,
                                            y_range_start=coordinates[1] - margin, y_range_stop=coordinates[1] + margin)
        self.terrain_loaded = False
