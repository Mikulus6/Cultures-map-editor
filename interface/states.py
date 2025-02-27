from interface.brushes import generate_major_triangles, Brush


class StatesMachine:
    initialized = False
    def __init__(self):
        if self.__class__.initialized:
            raise ValueError(f"{self.__class__.__name__} is a singleton.")
        self.__class__.initialized = True

        self.state = None
        self.possible_states = (None, "pattern_single", "pattern_group", "height",
                                "landscapes_single", "landscapes_group", "structures")

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


states_machine = StatesMachine()
