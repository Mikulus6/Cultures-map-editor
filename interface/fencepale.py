import pygame
from map import Map
from interface.brushes import is_in_bounds
from interface.camera import Camera
from interface.interpolation import get_data_interpolated
from sections.mesh_points import get_neighbouring_vertices
from supplements.gouraud import gouraud
from supplements.landscapedefs import default_shading_factor, landscapedefs
from supplements.remaptables import remaptable_default

fencepale_landscape_mode = 30
fencepale_palette_index = 60
fencepale_endpoints_vertical_offsets = ((-6, -6), (-7, -7), (-14, -6), (-6, -14), (-14, -14), (-15, -15))


def get_fencepale_color(map_object: Map, coordinates_1):
    factor = get_data_interpolated(coordinates_1, (map_object.map_width, map_object.map_height), map_object.mlig)
    shading_factor = landscapedefs[map_object.llan[coordinates_1]].get("ShadingFactor", default_shading_factor)

    palette_index = round((factor - 128) * (shading_factor / 256) * (gouraud.array.shape[0] / 256)) + \
                    gouraud.array.shape[0] // 2

    return remaptable_default[gouraud.array[max(min(palette_index, gouraud.array.shape[0] - 1), 0),
                                            fencepale_palette_index]]

def draw_fencepale(surface: pygame.Surface, map_object: Map, camera:Camera, coordinates_1, coordinates_2):
    draw_coordinates_1 = camera.draw_coordinates(coordinates_1, map_object, include_canvas_offset=True)
    draw_coordinates_2 = camera.draw_coordinates(coordinates_2, map_object, include_canvas_offset=True)
    color = get_fencepale_color(map_object, coordinates_1)

    for endpoints_vertical_offsets_pair in fencepale_endpoints_vertical_offsets:

        pygame.draw.line(surface, color,
            start_pos = (draw_coordinates_1[0], draw_coordinates_1[1] + endpoints_vertical_offsets_pair[0]),
            end_pos   = (draw_coordinates_2[0], draw_coordinates_2[1] + endpoints_vertical_offsets_pair[1]))

def check_draw_fencepale(map_object: Map, coordinates_1, coordinates_2):

    landscape_1 = map_object.llan.get(coordinates_1, None)
    landscape_2 = map_object.llan.get(coordinates_2, None)

    if None in (landscape_1, landscape_2):
        return False
    elif landscapedefs[landscape_1]["Mode"] == landscapedefs[landscape_2]["Mode"] == fencepale_landscape_mode:
        return True
    else:
        return False

def handle_drawing_fencepale(surface: pygame.Surface, map_object: Map, camera:Camera, coordinates):
    for neighbour in get_neighbouring_vertices(coordinates):
        if not(is_in_bounds(map_object, neighbour)):
            continue

        if check_draw_fencepale(map_object, coordinates, neighbour) and (sorted((coordinates, neighbour),
           key=lambda coords: coords[1] * map_object.map_width + coords[0])[0] == coordinates):

            draw_fencepale(surface, map_object, camera, coordinates, neighbour)
