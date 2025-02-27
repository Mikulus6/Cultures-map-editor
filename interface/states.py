from dataclasses import dataclass
from random import random
import time
from interface.brushes import generate_major_triangles, Brush


@dataclass
class LandscapesDrawParameters:
    density: float = 0.1
    tickrate: float = 10.0
    last_tick_time = time.time() - 1 / tickrate

landscapes_draw_parameters = LandscapesDrawParameters()


class StatesMachine:
    initialized = False
    def __init__(self):
        if self.__class__.initialized:
            raise ValueError(f"{self.__class__.__name__} is a singleton.")
        self.__class__.initialized = True

        self.state = None
        self.possible_states = (None, "pattern_single", "pattern_group", "height",
                                "landscape_single", "landscape_group", "structures")

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
                    editor.update_triange(*triangle, mep_id)
                    editor.update_local_secondary_data(triangle[0], margin=2)
                break

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

                    if editor.scroll_radius != 0 and time.time() - landscapes_draw_parameters.last_tick_time > \
                                                      1 / landscapes_draw_parameters.tickrate:
                        for point in Brush.get_points_and_edge_points(editor.map,
                                                                      editor.cursor_vertex,
                                                                      editor.scroll_radius,
                                                                      ignore_minor_vertices=False)[0]:
                            if (landscapes_draw_parameters.density != 1 and random() >
                                landscapes_draw_parameters.density) or landscapes_draw_parameters.density == 0:
                                continue
                            editor.update_landscape(point, name)
                        landscapes_draw_parameters.last_tick_time = time.time()
                    elif editor.scroll_radius == 0:
                        editor.update_landscape(editor.cursor_vertex, name)
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

states_machine = StatesMachine()
