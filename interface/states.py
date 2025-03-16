from dataclasses import dataclass
from random import random
import time
from typing import Literal
from interface.border import is_triangle_in_border, is_major_vertex_in_border
from interface.brushes import generate_major_triangles, Brush
from interface.const import font_color, font_color_out_of_focus, font_antialias, font_row_vertical_pos_diff
from interface.triangle_transitions import update_triangles
from supplements.groups import get_random_group_entry
from supplements.patterns import patterndefs_normal_by_name


@dataclass
class LandscapesDrawParameters:
    density: float = 0.1
    legacy_randomness: bool = False
    consider_base_area: bool = False
    consider_extended_area: bool = False
    tickrate: float = 10.0
    last_tick_time = time.time() - 1 / tickrate


@dataclass
class HeightDrawParameters:
    mode: Literal["absolute", "delta higher", "delta deeper", "random", "smoothing"] = "delta higher"
    value_absolute: int = 5
    value_delta: int = 5
    value_random: int = 5
    threshold_smoothing: int = 1
    total_smoothing: bool = True
    tickrate: float = 20.0
    last_tick_time = time.time() - 1 / tickrate


landscapes_draw_parameters = LandscapesDrawParameters()
height_draw_parameters = HeightDrawParameters()
height_mode_options = ("absolute", "delta higher", "delta deeper", "random", "smoothing")


class StatesMachine:
    initialized = False
    def __init__(self):
        if self.__class__.initialized:
            raise ValueError(f"{self.__class__.__name__} is a singleton.")
        self.__class__.initialized = True

        self.state = None
        self.possible_states = (None, "pattern_single", "pattern_group", "triangle_transition",
                                "height", "landscape_single", "landscape_group", "structures")

    def set_state(self, state: None | str):
        assert state in self.possible_states
        self.state = state

    def run_current_state(self, editor):
        if self.state is None: return

        getattr(self, self.state)(editor)

    @staticmethod
    def pattern_single(editor):
        editor.ignore_singular_triangle = False
        editor.ignore_minor_vertices = True
        editor.patterns_catalogue.update_and_draw(editor)

        for pressed, selected_pattern in zip((editor.mouse_press_left, editor.mouse_press_right),
                                             (editor.patterns_catalogue.selected_index_left,
                                              editor.patterns_catalogue.selected_index_right)):
            if pressed:
                mep_id = editor.patterns_catalogue.items[selected_pattern].identificator
                if editor.scroll_radius > 0 and editor.cursor_vertex is not None:
                    triangles = generate_major_triangles(editor.map, editor.cursor_vertex, editor.scroll_radius,
                                                         Brush.get_points_and_edge_points(editor.map,
                                                                                          editor.cursor_vertex,
                                                                                          editor.scroll_radius,
                                                                                          ignore_minor_vertices=True)[0]
                                                         )
                elif editor.scroll_radius == 0 and editor.cursor_triangle is not None:
                    triangles = (editor.cursor_triangle, )
                else:
                    triangles = tuple()

                for triangle in triangles:
                    if not is_triangle_in_border(*triangle, editor.map):
                        editor.update_triange(*triangle, mep_id)

                if editor.cursor_vertex is not None:
                    editor.update_local_secondary_data(editor.cursor_vertex, margin=editor.scroll_radius + 2)
                break

    @staticmethod
    def pattern_group(editor):
        editor.ignore_singular_triangle = False
        editor.ignore_minor_vertices = True
        editor.patterns_group_catalogue.update_and_draw(editor)
        for pressed, selected_pattern in zip((editor.mouse_press_left, editor.mouse_press_right),
                                             (editor.patterns_group_catalogue.selected_index_left,
                                              editor.patterns_group_catalogue.selected_index_right)):
            if pressed:
                group = editor.patterns_group_catalogue.items[selected_pattern].identificator
                if editor.scroll_radius > 0 and editor.cursor_vertex is not None:
                    triangles = generate_major_triangles(editor.map, editor.cursor_vertex, editor.scroll_radius,
                                                         Brush.get_points_and_edge_points(editor.map,
                                                                                          editor.cursor_vertex,
                                                                                          editor.scroll_radius,
                                                                                          ignore_minor_vertices=True)[0]
                                                         )
                elif editor.scroll_radius == 0 and editor.cursor_triangle is not None:
                    triangles = (editor.cursor_triangle, )
                else:
                    triangles = tuple()

                for triangle in triangles:
                    if not is_triangle_in_border(*triangle, editor.map):
                        pattern = patterndefs_normal_by_name[get_random_group_entry(group).lower()]
                        editor.update_triange(*triangle, pattern["Id"] + pattern["SetId"] * 256)

                if editor.cursor_vertex is not None:
                    editor.update_local_secondary_data(editor.cursor_vertex, margin=editor.scroll_radius + 2)

    @staticmethod
    def triangle_transition(editor):
        editor.ignore_singular_triangle = False
        editor.ignore_minor_vertices = True

        text_position = [8, 56]
        editor.root.blit(editor.font.render(f"Transitions brush is active.",
                                            font_antialias, font_color), text_position)
        if editor.mouse_press_left:
            if editor.scroll_radius > 0 and editor.cursor_vertex is not None:
                triangles = generate_major_triangles(editor.map, editor.cursor_vertex, editor.scroll_radius,
                                                     Brush.get_points_and_edge_points(editor.map,
                                                                                      editor.cursor_vertex,
                                                                                      editor.scroll_radius,
                                                                                      ignore_minor_vertices=True)[0]
                                                     )
            elif editor.scroll_radius == 0 and editor.cursor_triangle is not None:
                triangles = (editor.cursor_triangle,)
            else:
                return
            update_triangles(editor, tuple(triangles))
            editor.terrain_loaded = False
            editor.progress_saved = False

    @staticmethod
    def landscape_single(editor):
        editor.ignore_singular_triangle = True
        editor.ignore_minor_vertices = False
        editor.landscapes_catalogue.update_and_draw(editor)
        if editor.cursor_vertex is not None:
            for pressed, selected_pattern in zip((editor.mouse_press_left, editor.mouse_press_right),
                                                 (editor.landscapes_catalogue.selected_index_left,
                                                  editor.landscapes_catalogue.selected_index_right)):
                if pressed:

                    name = editor.landscapes_catalogue.items[selected_pattern].identificator["Name"] \
                           if editor.landscapes_catalogue.items[selected_pattern].identificator is not None else None

                    if time.time() - landscapes_draw_parameters.last_tick_time > \
                                     1 / landscapes_draw_parameters.tickrate:
                        if editor.scroll_radius != 0:
                            for point in Brush.get_points_and_edge_points(editor.map,
                                                                          editor.cursor_vertex,
                                                                          editor.scroll_radius,
                                                                          ignore_minor_vertices=False)[0]:
                                if (landscapes_draw_parameters.density != 1 and random() >
                                    landscapes_draw_parameters.density) or landscapes_draw_parameters.density == 0:
                                    continue
                                if (landscapes_draw_parameters.consider_base_area and
                                    editor.base_area.check_overlap(name, point, editor.map)) or \
                                   (landscapes_draw_parameters.consider_extended_area and
                                    editor.extended_area.check_overlap(name, point, editor.map)):
                                    continue

                                editor.update_landscape(point, name)
                        elif editor.scroll_radius == 0:

                            if (landscapes_draw_parameters.consider_base_area and
                                editor.base_area.check_overlap(name, editor.cursor_vertex, editor.map)) or \
                               (landscapes_draw_parameters.consider_extended_area and
                                editor.extended_area.check_overlap(name, editor.cursor_vertex, editor.map)):
                                break

                            editor.update_landscape(editor.cursor_vertex, name)
                        landscapes_draw_parameters.last_tick_time = time.time()
                    break

        editor.base_area.update_after_landscapes_changes(editor.map)
        editor.extended_area.update_after_landscapes_changes(editor.map)

    @staticmethod
    def landscape_group(editor):
        editor.ignore_singular_triangle = True
        editor.ignore_minor_vertices = False
        editor.landscapes_group_catalogue.update_and_draw(editor)
        if editor.cursor_vertex is not None:
            for pressed, selected_pattern in zip((editor.mouse_press_left, editor.mouse_press_right),
                                                 (editor.landscapes_group_catalogue.selected_index_left,
                                                  editor.landscapes_group_catalogue.selected_index_right)):
                if pressed:

                    group = editor.landscapes_group_catalogue.items[selected_pattern].identificator \
                            if editor.landscapes_group_catalogue.items[selected_pattern].identificator is not None \
                            else None

                    if time.time() - landscapes_draw_parameters.last_tick_time > \
                                     1 / landscapes_draw_parameters.tickrate:
                        if editor.scroll_radius != 0:
                            for point in Brush.get_points_and_edge_points(editor.map,
                                                                          editor.cursor_vertex,
                                                                          editor.scroll_radius,
                                                                          ignore_minor_vertices=False)[0]:

                                name = get_random_group_entry(group,
                                               legacy_randomness=landscapes_draw_parameters.legacy_randomness).lower() \
                                               if group is not None else None

                                if (landscapes_draw_parameters.density != 1 and random() >
                                    landscapes_draw_parameters.density) or landscapes_draw_parameters.density == 0:
                                    continue
                                if (landscapes_draw_parameters.consider_base_area and
                                    editor.base_area.check_overlap(name, point, editor.map)) or \
                                   (landscapes_draw_parameters.consider_extended_area and
                                    editor.extended_area.check_overlap(name, point, editor.map)):
                                    continue

                                editor.update_landscape(point, name)
                        elif editor.scroll_radius == 0:

                            name = get_random_group_entry(group,
                                           legacy_randomness=landscapes_draw_parameters.legacy_randomness).lower() \
                                           if group is not None else None

                            if (landscapes_draw_parameters.consider_base_area and
                                editor.base_area.check_overlap(name, editor.cursor_vertex, editor.map)) or \
                               (landscapes_draw_parameters.consider_extended_area and
                                editor.extended_area.check_overlap(name, editor.cursor_vertex, editor.map)):
                                break

                            editor.update_landscape(editor.cursor_vertex, name)
                        landscapes_draw_parameters.last_tick_time = time.time()
                    break

        editor.base_area.update_after_landscapes_changes(editor.map)
        editor.extended_area.update_after_landscapes_changes(editor.map)

    @staticmethod
    def structures(editor):
        editor.ignore_singular_triangle = True
        editor.ignore_minor_vertices = False
        editor.structures_catalogue.update_and_draw(editor)
        if editor.cursor_vertex is not None:
            for pressed, selected_pattern in zip((editor.mouse_press_left, editor.mouse_press_right),
                                                 (editor.structures_catalogue.selected_index_left,
                                                  editor.structures_catalogue.selected_index_right)):
                if pressed:
                    name = editor.structures_catalogue.items[selected_pattern].identificator

                    if editor.scroll_radius != 0:
                        for point in Brush.get_points_and_edge_points(editor.map,
                                                                      editor.cursor_vertex,
                                                                      editor.scroll_radius,
                                                                      ignore_minor_vertices=False)[0]:
                            editor.update_structures(point, name)
                    else:
                        editor.update_structures(editor.cursor_vertex, name)

    @staticmethod
    def height(editor):
        editor.ignore_singular_triangle = True
        editor.ignore_minor_vertices = True

        text_position = [8, 56]
        editor.root.blit(editor.font.render(f"Active mode: {height_draw_parameters.mode}",
                                            font_antialias, font_color ),
                         text_position),
        text_position[1] += font_row_vertical_pos_diff
        editor.root.blit(editor.font.render(f"Absolute value: {height_draw_parameters.value_absolute}",
                                            font_antialias,
                                            font_color if height_draw_parameters.mode == "absolute"
                                            else font_color_out_of_focus), text_position),
        text_position[1] += font_row_vertical_pos_diff
        editor.root.blit(editor.font.render(f"Delta value: {height_draw_parameters.value_delta}",
                                            font_antialias,
                                            font_color if height_draw_parameters.mode
                                                          in ("delta higher", "delta deeper", "smoothing")
                                            else font_color_out_of_focus), text_position),
        text_position[1] += font_row_vertical_pos_diff
        editor.root.blit(editor.font.render(f"Random value: {height_draw_parameters.value_random}",
                                            font_antialias,
                                            font_color if height_draw_parameters.mode == "random"
                                            else font_color_out_of_focus), text_position)
        text_position[1] += font_row_vertical_pos_diff
        editor.root.blit(editor.font.render(f"Smoothing treshold: {height_draw_parameters.threshold_smoothing}",
                                            font_antialias,
                                            font_color if height_draw_parameters.mode == "smoothing"
                                            else font_color_out_of_focus), text_position)
        text_position[1] += font_row_vertical_pos_diff
        editor.root.blit(editor.font.render(f"Total smoothing: " + ("true" if height_draw_parameters.total_smoothing
                                                                    else "false"),
                                            font_antialias,
                                            font_color if height_draw_parameters.mode == "smoothing"
                                            else font_color_out_of_focus), text_position)

        if editor.cursor_vertex is not None:

            for pressed, factor in zip((editor.mouse_press_left, editor.mouse_press_right), (1, -1)):

                if pressed and time.time() - height_draw_parameters.last_tick_time > \
                                             1 / height_draw_parameters.tickrate:
                    if editor.scroll_radius > 0:
                        points = Brush.get_points_and_edge_points(editor.map, editor.cursor_vertex,
                                                                  editor.scroll_radius, ignore_minor_vertices=True)[0]
                    else:
                        points = (editor.cursor_vertex, )

                    if height_draw_parameters.mode == "smoothing":
                        average_height = sum(editor.map.mhei[point[1] * editor.map.map_width // 4 + point[0] // 2]
                                             for point in points) / len(points)

                    for point in points:

                        if editor.scroll_radius > 0:
                            point = (point[0] // 2, point[1] // 2)

                        if is_major_vertex_in_border(point, editor.map):
                            continue

                        match height_draw_parameters.mode:
                            case "absolute":
                                editor.update_height(point, height_draw_parameters.value_absolute,
                                                     as_delta=False)
                            case "delta higher":
                                editor.update_height(point, height_draw_parameters.value_delta * factor,
                                                     as_delta=True)
                            case "delta deeper":
                                editor.update_height(point, - height_draw_parameters.value_delta * factor,
                                                     as_delta=True)
                            case "random":
                                editor.update_height(point,
                                                     height_draw_parameters.value_random * factor * random(),
                                                     as_delta=True)
                            case "smoothing":
                                value = editor.map.mhei[point[1] * editor.map.map_width // 2 + point[0]]

                                if height_draw_parameters.total_smoothing:
                                    local_average_height = average_height  # noqa
                                else:
                                    local_average_height = 0
                                    valid_neighbours_num = 0

                                    if point[1] % 2 == 0:
                                        neighbours = [(point[0] + 1, point[1]), (point[0], point[1] + 1),
                                                      (point[0] - 1, point[1]), (point[0], point[1] - 1),
                                                      (point[0] - 1, point[1] + 1), (point[0] - 1, point[1] - 1)]
                                    else:
                                        neighbours = [(point[0] + 1, point[1]), (point[0], point[1] + 1),
                                                      (point[0] - 1, point[1]), (point[0], point[1] - 1),
                                                      (point[0] + 1, point[1] + 1), (point[0] + 1, point[1] - 1)]
                                    for neighbour in neighbours:
                                        if 0 <= neighbour[0] < editor.map.map_width // 2 and\
                                           0 <= neighbour[1] < editor.map.map_height // 2:
                                            local_average_height += \
                                                editor.map.mhei[neighbour[1] * editor.map.map_width // 2 +
                                                                neighbour[0]]
                                            valid_neighbours_num += 1

                                    local_average_height /= valid_neighbours_num
                                if abs(value - local_average_height) < height_draw_parameters.value_delta:
                                    editor.update_height(point, local_average_height, as_delta=False)
                                elif value > local_average_height + height_draw_parameters.threshold_smoothing:
                                    editor.update_height(point, - height_draw_parameters.value_delta * factor,
                                                         as_delta=True)
                                elif value < local_average_height - height_draw_parameters.threshold_smoothing:
                                    editor.update_height(point, height_draw_parameters.value_delta * factor,
                                                         as_delta=True)

                    if editor.cursor_vertex is not None:
                        editor.update_local_secondary_data(editor.cursor_vertex, margin=editor.scroll_radius + 4)
                        height_draw_parameters.last_tick_time = time.time()
                    break

states_machine = StatesMachine()
