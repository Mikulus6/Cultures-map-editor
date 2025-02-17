from interface.camera import Camera
from interface.const import triangle_width, triangle_height, map_canvas_rect
from interface.triangles import get_major_triangle_corner_vertices
from itertools import product
from map import Map


def area_of_triangle(corners):
    return abs(corners[0][0] * (corners[1][1] - corners[2][1]) +
               corners[1][0] * (corners[2][1] - corners[0][1]) +
               corners[2][0] * (corners[0][1] - corners[1][1])) // 2

def coordinates_prediction(cursor_coordinates, camera: Camera):
    return round((cursor_coordinates[0] - map_canvas_rect[0] - map_canvas_rect[2] // 2 +
                  camera.position[0]) // triangle_width),\
           round((cursor_coordinates[1] - map_canvas_rect[1] - map_canvas_rect[3] // 2 +
                  camera.position[1]) // triangle_height)

def get_closest_vertex(cursor_coordinates, camera: Camera, map_object: Map, ignore_minor_vertices: bool = False):

    if not cursor_on_canvas(cursor_coordinates):
        return None

    prediction_vertex = coordinates_prediction(cursor_coordinates, camera)
    closest_distance_squared = float("inf")
    closest_vertex = None

    for x, y in product(range(prediction_vertex[0] - camera.visible_margin,
                              prediction_vertex[0] + camera.visible_margin),
                        range(prediction_vertex[1] - camera.visible_margin,
                              prediction_vertex[1] + camera.visible_height_margin)):
        if ignore_minor_vertices and not is_vertex_major((x, y)):
            continue

        if not(0 <= x < map_object.map_width and 0 <= y < map_object.map_height):
            continue  # out of bounds

        draw_x, draw_y = camera.draw_coordinates((x, y), map_object, include_canvas_offset=True)
        distance_squared = (cursor_coordinates[0] - draw_x) ** 2 +\
                           (cursor_coordinates[1] - draw_y) ** 2

        if distance_squared < closest_distance_squared:
            closest_distance_squared = distance_squared
            closest_vertex = (x, y)

    if closest_distance_squared > 2 * (triangle_width ** 2 + triangle_height ** 2):
        return None

    if ignore_minor_vertices:
        closest_vertex = (closest_vertex[0] // 2, closest_vertex[1] // 2)

    return closest_vertex

def get_touching_triange(cursor_coordinates, camera: Camera, map_object: Map):

    if not cursor_on_canvas(cursor_coordinates):
        return None

    prediction_vertex = coordinates_prediction(cursor_coordinates, camera)
    prediction_vertex = (prediction_vertex[0] // 2, prediction_vertex[1] // 2)

    smallest_error = float("inf")
    triangle_found = None

    for triangle_type in ("a", "b"):

        for x, y in product(range(prediction_vertex[0] - camera.visible_margin,
                                  prediction_vertex[0] + camera.visible_margin),
                            range(prediction_vertex[1] - camera.visible_margin,
                                  prediction_vertex[1] + camera.visible_height_margin)):

            vertices = get_major_triangle_corner_vertices((x, y), triangle_type)

            draw_vertices = tuple(map(lambda coords: camera.draw_coordinates(coords, map_object,
                                                                             include_canvas_offset=True), vertices))

            reference_area = area_of_triangle(draw_vertices)

            triangles = [(draw_vertices[0], draw_vertices[1], cursor_coordinates),
                         (draw_vertices[0], draw_vertices[2], cursor_coordinates),
                         (draw_vertices[1], draw_vertices[2], cursor_coordinates)]

            error_margin = abs(sum(map(area_of_triangle, triangles)) - reference_area)

            if error_margin < smallest_error:
                smallest_error = error_margin
                triangle_found = ((x, y), triangle_type)

    if triangle_found is not None and not(0 <= triangle_found[0][0] < map_object.map_width  // 2 and
                                          0 <= triangle_found[0][1] < map_object.map_height // 2):
        triangle_found = None

    return triangle_found


def cursor_on_canvas(cursor_coordinates):
    return (map_canvas_rect[0] <= cursor_coordinates[0] < map_canvas_rect[0] + map_canvas_rect[2] and
            map_canvas_rect[1] <= cursor_coordinates[1] < map_canvas_rect[1] + map_canvas_rect[3])

def is_vertex_major(coordinates):
    return (coordinates[0] % 2 == 0 and coordinates[1] % 4 == 0) or\
           (coordinates[0] % 2 == 1 and coordinates[1] % 4 == 2)
