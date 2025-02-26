import pygame
import numpy as np
from functools import lru_cache
from interface.const import background_color, lru_cache_triangles_maxsize, resolution, map_canvas_rect
from interface.timeout import timeout_handler
from supplements.textures import Texture, rect_bound


epsylon = 1e-16


def draw_projected_triangle(surface: pygame.Surface, texture: Texture, corners: tuple, light_corners: tuple, *,
                            suspend_loading_textures: bool = False):

    bounds_x, bounds_y = rect_bound(corners)

    if map_canvas_rect[0] + map_canvas_rect[2] < bounds_x[0] or bounds_x[1] < 0 or\
       map_canvas_rect[1] + map_canvas_rect[3] < bounds_y[0] or bounds_y[1] < 0:
        return # Triangle canvas are outside of visible screen

    relative_corners = ((corners[0][0] - bounds_x[0], corners[0][1] - bounds_y[0]),
                        (corners[1][0] - bounds_x[0], corners[1][1] - bounds_y[0]),
                        (corners[2][0] - bounds_x[0], corners[2][1] - bounds_y[0]))

    if texture.average_color is None:
        return # If average color of texture is not defined, it means that the whole texture is transparent,
               # and it is unnecessary to project it.

    projection_report.triangles_total += 1
    try:
        if suspend_loading_textures:
            raise TimeoutError

        surface.blit(project_triangle(texture, relative_corners, light_corners), (bounds_x[0], bounds_y[0]))
        projection_report.triangles_textured += 1

    except TimeoutError:

        average_light = sum(light_corners) / 3

        average_color = (round(min(max(texture.average_color[0] * (average_light + 1), 0), 255)),
                         round(min(max(texture.average_color[1] * (average_light + 1), 0), 255)),
                         round(min(max(texture.average_color[2] * (average_light + 1), 0), 255)))

        pygame.draw.polygon(surface, average_color, corners)

@lru_cache(maxsize=lru_cache_triangles_maxsize)
def project_triangle(texture: Texture, relative_corners: tuple, light_corners: tuple = (0, 0, 0)):

    # Function was inspired by this repository: https://github.com/FinFetChannel/SimplePython3DEngine

    timeout_handler.check()

    texture_uv = np.array([
        [texture.pixel_coords[0][0] / texture.size[0], texture.pixel_coords[0][1] / texture.size[1]],
        [texture.pixel_coords[1][0] / texture.size[0], texture.pixel_coords[1][1] / texture.size[1]],
        [texture.pixel_coords[2][0] / texture.size[0], texture.pixel_coords[2][1] / texture.size[1]]])

    bounds_x, bounds_y = rect_bound(relative_corners)
    assert bounds_x[0] == bounds_y[0] == 0

    frame = np.full((bounds_x[1] * 2, bounds_y[1] * 2, 3), background_color, dtype='uint8')

    sorted_y = np.argsort([relative_corners[0][1], relative_corners[1][1], relative_corners[2][1]])

    x_start, y_start = relative_corners[sorted_y[0]]
    x_middle, y_middle = relative_corners[sorted_y[1]]
    x_stop, y_stop = relative_corners[sorted_y[2]]

    brightness_start, brightness_middle, brightness_stop = (light_corners[sorted_y[0]] + 1,
                                                            light_corners[sorted_y[1]] + 1,
                                                            light_corners[sorted_y[2]] + 1)

    x_slope_1 = (x_stop - x_start) / (y_stop - y_start + epsylon)
    x_slope_2 = (x_middle - x_start) / (y_middle - y_start + epsylon)
    x_slope_3 = (x_stop - x_middle) / (y_stop - y_middle + epsylon)

    uv_start, uv_middle, uv_stop = texture_uv[sorted_y[0]], texture_uv[sorted_y[1]], texture_uv[sorted_y[2]]
    uv_slope_1 = (uv_stop - uv_start) / (y_stop - y_start + epsylon)
    uv_slope_2 = (uv_middle - uv_start) / (y_middle - y_start + epsylon)
    uv_slope_3 = (uv_stop - uv_middle) / (y_stop - y_middle + epsylon)

    brightness_slope_1 = (brightness_stop - brightness_start) / (y_stop - y_start + epsylon)
    brightness_slope_2 = (brightness_middle - brightness_start) / (y_middle - y_start + epsylon)
    brightness_slope_3 = (brightness_stop - brightness_middle) / (y_stop - y_middle + epsylon)

    for y in range(y_start, y_stop):
        x1 = x_start + int((y - y_start) * x_slope_1)
        uv1 = uv_start + (y - y_start) * uv_slope_1
        brightness1 = brightness_start + (y - y_start) * brightness_slope_1

        if y < y_middle:
            x2 = x_start + int((y - y_start) * x_slope_2)
            uv2 = uv_start + (y - y_start) * uv_slope_2
            brightness2 = brightness_start + (y - y_start) * brightness_slope_2
        else:
            x2 = x_middle + int((y - y_middle) * x_slope_3)
            uv2 = uv_middle + (y - y_middle) * uv_slope_3
            brightness2 = brightness_middle + (y - y_middle) * brightness_slope_3

        if x1 > x2:
            x1, x2 = x2, x1
            uv1, uv2 = uv2, uv1
            brightness1, brightness2 = brightness2, brightness1

        uv_slope = (uv2 - uv1) / (x2 - x1 + epsylon)
        brightness_slope = (brightness2 - brightness1) / (x2 - x1 + epsylon)

        x_range = np.arange(x1, x2)
        uv_range = uv1 + (x_range - x1)[:, None] * uv_slope
        brightness_range = brightness1 + (x_range - x1) * brightness_slope

        u_valid = np.clip(uv_range[:, 0] * texture.size[0], 0, texture.size[0] - 1).astype(int)
        v_valid = np.clip(uv_range[:, 1] * texture.size[1], 0, texture.size[1] - 1).astype(int)

        frame[x_range, y, :] = np.clip(texture.image[u_valid, v_valid] * brightness_range[:, None], 0, 255)

    surf = pygame.surfarray.make_surface(frame)
    surf.set_colorkey(background_color)
    return surf

def clear_triangle_projection_cache():
    project_triangle.cache_clear()


class ProjectionReport:
    initialized = False
    def __init__(self, rect, margin):
        if self.__class__.initialized:
            raise ValueError(f"{self.__class__.__name__} is a singleton.")
        self.__class__.initialized = True
        self.rect = rect
        self.margin = margin

        self.triangles_textured = 0
        self.triangles_total = 0

    def reset(self):
        self.triangles_textured = 0
        self.triangles_total = 0

    @property
    def is_loading(self):
        return timeout_handler.calls > 0

    @property
    def loading_value(self):
        try:
            return self.triangles_textured / self.triangles_total
        except ZeroDivisionError:
            return 1

    def draw_loading_bar(self, surface):
        pygame.draw.rect(surface, (0, 0, 0), self.rect)
        pygame.draw.rect(surface, (85, 85, 85), (self.rect[0] + self.margin, self.rect[1] + self.margin,
                                                 self.rect[2] - 2 * self.margin, self.rect[3] - 2 * self.margin))
        if self.loading_value == 1: color = (137, 224, 118)
        elif self.is_loading:       color = (255, 255, 255)
        else:                       color = (171, 171, 171)

        pygame.draw.rect(surface, color, (self.rect[0] + self.margin, self.rect[1] + self.margin,
                                         (self.rect[2] - 2 * self.margin) * self.loading_value,
                                          self.rect[3] - 2 * self.margin))

_rect_screen_margin = 9
_rect_size = (((resolution[0] - map_canvas_rect[2]) - 2*_rect_screen_margin), 10)

projection_report = ProjectionReport(rect = (_rect_screen_margin, resolution[1] - _rect_screen_margin - _rect_size[1],
                                             *_rect_size), margin=1)
