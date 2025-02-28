import pygame
import numpy as np
from interface.const import font_antialias, font_color, invisible_background_color, font_row_vertical_pos_diff,\
                            invisible_legend_margin, invisible_text_margin
from supplements.animations import animations
from scripts.image import get_rgb_hue_tuple

predefined_colors = {"ambient wind":  (255, 255, 255),
                     "ambient water": (0, 0, 255)}
color_circle_radius = 6

transparent_landscapes_list = []
for name, animation in animations.items():
    if all(image.size == (1, 1) and image.getpixel((0, 0))[3] == 0 for image in animation.images):
        transparent_landscapes_list.append(name)



colors_primary = map(lambda x: get_rgb_hue_tuple(x),
                     tuple(np.linspace(0, 1, len(transparent_landscapes_list) - len(predefined_colors) + 1)[:-1]))

transparent_landscapes_color_match = {}
for name in transparent_landscapes_list:
    transparent_landscapes_color_match[name] = predefined_colors.get(name)
    if transparent_landscapes_color_match[name] is None:
        transparent_landscapes_color_match[name] = next(colors_primary)

def render_legend(editor):

    entries_data = []
    max_text_width = 0
    for landscape_name in transparent_landscapes_color_match.keys():
        text_object = editor.font.render(landscape_name, font_antialias, font_color)
        max_text_width = max(text_object.width, max_text_width)
        entries_data.append((landscape_name, text_object))

    legend_surf = pygame.Surface((max_text_width + invisible_text_margin + \
                                  2 * (invisible_legend_margin + color_circle_radius),
                                  len(entries_data) * font_row_vertical_pos_diff),
                                 pygame.SRCALPHA)
    legend_surf.fill(invisible_background_color)

    current_height_offset = invisible_legend_margin
    for landscape_name, text_object in entries_data:
        pygame.draw.circle(legend_surf, transparent_landscapes_color_match[landscape_name],
                           (invisible_legend_margin + color_circle_radius, current_height_offset + color_circle_radius),
                           color_circle_radius)
        legend_surf.blit(text_object, (invisible_legend_margin + 2 * color_circle_radius + invisible_text_margin,
                                       current_height_offset - color_circle_radius))
        current_height_offset += font_row_vertical_pos_diff
    return legend_surf
