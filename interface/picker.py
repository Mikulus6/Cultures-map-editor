from interface.catalogue import catalogue_rect
from interface.const import font_antialias, font_color, picker_text_margin, picker_text_warning_color
from interface.states import states_machine
from interface.structures import get_structure_type_of_vertex
from supplements.landscapedefs import landscapedefs

pattern_picking_states   = ("pattern_single", "pattern_group")
landscape_picking_states = ("landscape_single", "landscape_group")
structure_picking_states = ("structures", )

unused_picking_states = tuple(set(states_machine.possible_states) - \
                              set(pattern_picking_states)         - \
                              set(landscape_picking_states)       - \
                              set(structure_picking_states))

pattern_state_final   = "pattern_single"
landscape_state_final = "landscape_single"
structure_state_final = "structures"

assert pattern_state_final in pattern_picking_states
assert landscape_state_final in landscape_picking_states
assert structure_state_final in structure_picking_states

all_substates_nested = (landscape_picking_states, pattern_picking_states, structure_picking_states)

# sum of substates is a subset of all states and intersection of any two substates is an empty set
assert all(map(lambda substates: set(substates).issubset(states_machine.possible_states), all_substates_nested))
assert all(map(lambda state: sum(map(lambda substates: int(state in substates), all_substates_nested)) <= 1,
               states_machine.possible_states))


def handle_picking(editor):

    if not editor.pick_by_middle:
        return

    quadruplets_of_objects = \
        ((pattern_picking_states,   pattern_state_final,   editor.patterns_catalogue,   get_pattern),
         (landscape_picking_states, landscape_state_final, editor.landscapes_catalogue, get_landscape),
         (structure_picking_states, structure_state_final, editor.structures_catalogue, get_structure))

    cursor_data = editor.cursor_triangle if editor.ignore_minor_vertices else editor.cursor_vertex

    if editor.mouse_press_middle and cursor_data is not None:
        for states_subset, state_final, catalogue, get_item in quadruplets_of_objects:
            if states_machine.state in states_subset:
                states_machine.set_state(state_final)
                catalogue.set_entry_and_jump_scroll(get_item(editor))

def get_pattern(editor):
    coordinates, triangle_type = editor.cursor_triangle
    x, y = coordinates
    index_bytes = y * editor.map.map_width + x * 2

    match triangle_type:
        case "a": mep_id = editor.map.mepa[index_bytes: index_bytes++2]
        case "b": mep_id = editor.map.mepb[index_bytes: index_bytes++2]
        case _: raise ValueError

    return int.from_bytes(mep_id, byteorder="little")

def get_landscape(editor):
    landscape_name = editor.map.llan.get(editor.cursor_vertex, None)
    if landscape_name is None:
        return None
    return landscapedefs[str.lower(landscape_name)]

def get_structure(editor):
    return get_structure_type_of_vertex(editor.map, editor.cursor_vertex)

def draw_picker_text(editor):
    text_color = picker_text_warning_color if editor.mouse_press_middle and \
                                              editor.camera.position_in_canvas_rect(editor.mouse_pos) else\
                                              font_color
    text_object = editor.font.render(f"Open any catalogue to use picker.", font_antialias, text_color)
    editor.root.blit(text_object,(catalogue_rect[0],
                                  catalogue_rect[1] + catalogue_rect[3] - picker_text_margin - text_object.height))
