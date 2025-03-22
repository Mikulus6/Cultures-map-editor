import pygame
from math import floor
from dataclasses import dataclass
from interface.const import font_antialias, font_color, frame_color
from interface.projection import draw_projected_triangle
from scripts.abs_path import abs_path
from supplements.animations import animations
from supplements.groups import landscapes_edit_group, pattern_edit_group
from supplements.landscapedefs import landscapedefs
from supplements.patterns import patterndefs_normal, road, patterndefs_normal_by_name
from supplements.textures import patterndefs_textures
from typing import Literal

entries_per_row = 4
entry_size = (55, 55)
entry_margin = 2
entry_background_color = (0, 0, 0, 128)
catalogue_rect = (8, 51, 230, 255)
catalogue_slider_rect = 242, 51, 16, 255
catalogue_slider_hand_size = 16, 16
highlight_width = 4
highlight_text_offset = 5, 5
margin = 1
icon_margin = 5

catalogue_background_path = "assets\\images\\catalogue_background.png"
catalogue_slider_background_path = "assets\\images\\catalogue_slider_background.png"
catalogue_slider_hand_path = "assets\\images\\catalogue_slider_hand.png"
catalogue_background = pygame.image.load(abs_path(catalogue_background_path))
catalogue_slider_background = pygame.image.load(abs_path(catalogue_slider_background_path))
catalogue_slider_hand = pygame.image.load(abs_path(catalogue_slider_hand_path))
assert catalogue_background.size == catalogue_rect[2:]
assert catalogue_slider_background.size == catalogue_slider_rect[2:]
assert catalogue_slider_hand.size == catalogue_slider_hand_size

temp_entry_surface = pygame.Surface(entry_size, pygame.SRCALPHA)


@dataclass
class CatalogueEntry:
    name: str
    identificator: str | int
    image: pygame.Surface

    def draw(self, editor, surface, coordinates, highlight_type: Literal[None, "left", "right", "both"] = None):

        if highlight_type is not None:
            temp_entry_surface.fill((0, 0, 0, 0))
            temp_entry_surface.blit(self.image, (0, 0))
            pygame.draw.rect(temp_entry_surface, (255, 255, 255), (0, 0, *entry_size), highlight_width)

        image = self.image if highlight_type is None else temp_entry_surface

        match highlight_type:
            case "left": highlight_text = "L"
            case "right": highlight_text = "R"
            case "both": highlight_text = "L+R"
            case _: highlight_text = None


        if highlight_type is not None:
            image.blit(editor.font.render(highlight_text, font_antialias, font_color), highlight_text_offset)

        if coordinates[1] < catalogue_rect[1]:
            surface.blit(image, (coordinates[0], catalogue_rect[1]),
                         (0, (catalogue_rect[1] - coordinates[1]), entry_size[0], entry_size[1]))
        elif coordinates[1] + entry_size[1] > catalogue_rect[1] + catalogue_rect[3]:
            surface.blit(image, coordinates,
                         (0, 0, entry_size[0], (catalogue_rect[1] + catalogue_rect[3] - coordinates[1])))
        else:
            surface.blit(image, coordinates)


def check_entry_hover(editor, coordinates):
    return coordinates[0] <= editor.mouse_pos[0] < coordinates[0] + entry_size[0] and\
           coordinates[1] <= editor.mouse_pos[1] < coordinates[1] + entry_size[1]


@dataclass
class Catalogue:
    items: list
    scroll_value: float = 0.0
    selected_index_right: int = 0
    selected_index_left: int = 1
    slider_pressed: bool = False

    @property
    def max_scroll_value(self):
        return max(len(self.items) // entries_per_row - entries_per_row + 1, 0)

    def update_and_draw(self, editor):

        if self.check_hover(editor):
            self.scroll_value -= editor.scroll_delta / 3

        if (self.check_slider_hover(editor) or self.slider_pressed) and editor.mouse_press_left and \
           (not editor.mouse_press_left_old or self.slider_pressed):
            self.scroll_value = (editor.mouse_pos[1] - catalogue_slider_rect[1] - catalogue_slider_hand_size[1] // 2) *\
                                 self.max_scroll_value / (catalogue_slider_rect[3] - catalogue_slider_hand_size[1])
            self.slider_pressed = True
            editor.cursor_vertex = None
            editor.cursor_triangle = None
        else:
            self.slider_pressed = False


        if self.scroll_value < 0: self.scroll_value = 0
        if self.scroll_value > self.max_scroll_value: self.scroll_value = self.max_scroll_value

        editor.root.blit(catalogue_background, catalogue_rect[:2])
        pygame.draw.rect(editor.root, frame_color, (catalogue_rect[0] - margin, catalogue_rect[1] - margin,
                                                    catalogue_rect[2] + margin * 2,
                                                    catalogue_rect[3] + margin * 2), width=margin)

        hover = self.check_hover(editor)

        old_selected_left, old_selected_right = self.selected_index_left, self.selected_index_right

        for index_value in self.get_visible_entries_range():
            try:
                item = self.items[index_value]
                assert isinstance(item, CatalogueEntry) and item.image.size == entry_size
                coordinates = self.get_entry_coordinates(index_value)

                if index_value == old_selected_left == old_selected_right:
                    highlight_type = "both"
                elif index_value == old_selected_left:
                    highlight_type = "left"
                elif index_value == old_selected_right:
                    highlight_type = "right"
                else:
                    highlight_type = None

                item.draw(editor, editor.root, coordinates, highlight_type=highlight_type)

                if hover and check_entry_hover(editor, coordinates):
                    if editor.font_text is None and item.name != "":
                            editor.font_text = f"\"{item.name}\""
                    if editor.mouse_press_left and not editor.mouse_press_left_old:
                        self.selected_index_left = index_value
                    if editor.mouse_press_right and not editor.mouse_press_right_old:
                        self.selected_index_right = index_value
            except IndexError:
                pass

        try:
            scroll_fraction = (self.scroll_value / self.max_scroll_value)
        except ZeroDivisionError:
            scroll_fraction = 0

        editor.root.blit(catalogue_slider_background, catalogue_slider_rect[:2])
        if self.max_scroll_value != 0:
            editor.root.blit(catalogue_slider_hand, (catalogue_slider_rect[0],
                                                     catalogue_slider_rect[1] + \
                                                     floor(scroll_fraction * \
                                                          (catalogue_slider_rect[3] - catalogue_slider_hand_size[1]))))

        pygame.draw.rect(editor.root, frame_color, (catalogue_slider_rect[0] - margin,
                                                    catalogue_slider_rect[1] - margin,
                                                    catalogue_slider_rect[2] + margin * 2,
                                                    catalogue_slider_rect[3] + margin * 2), width=margin)

    def get_entry_coordinates(self, entry_index):
        return catalogue_rect[0] + (entry_index % entries_per_row) * (entry_margin + entry_size[0]) + entry_margin,\
               floor(catalogue_rect[1] + (entry_index // entries_per_row - self.scroll_value) * \
                                         (entry_margin + entry_size[1]) + entry_margin)

    @staticmethod
    def check_hover(editor):
        return catalogue_rect[0] <= editor.mouse_pos[0] < catalogue_rect[0] + catalogue_rect[2] and\
               catalogue_rect[1] <= editor.mouse_pos[1] < catalogue_rect[1] + catalogue_rect[3]

    @staticmethod
    def check_slider_hover(editor):
        return catalogue_slider_rect[0] <= editor.mouse_pos[0] < catalogue_slider_rect[0] + \
                                                                 catalogue_slider_rect[2] and\
               catalogue_slider_rect[1] <= editor.mouse_pos[1] < catalogue_slider_rect[1] + \
                                                                 catalogue_slider_rect[3]

    def get_visible_entries_range(self):
        return range(floor(self.scroll_value) * entries_per_row,
                     floor(self.scroll_value + catalogue_rect[3]/entry_size[1] + 1) * entries_per_row)


def load_patterns_catalogue():
    assert patterndefs_textures.pygame_converted

    entries = []

    for mep_id, texture in patterndefs_textures.items():
        entry = CatalogueEntry(patterndefs_normal[mep_id]["Name"], identificator=mep_id,
                               image=pygame.Surface(entry_size, pygame.SRCALPHA))
        entry.image.fill(entry_background_color)
        draw_projected_triangle(entry.image, texture["a"],
                                ((entry_size[0] // 2, icon_margin),
                                 (entry_size[0] - icon_margin, entry_size[1] - icon_margin),
                                 (icon_margin, entry_size[1] - icon_margin)),
                                (0.5, 0.5, 0.5), suspend_timeout=True)
        entries.append(entry)

    return Catalogue(entries)


def load_patterns_groups_catalogue():
    assert patterndefs_textures.pygame_converted

    entries = []

    for name, pattern_group in pattern_edit_group.items():

        pattern = patterndefs_normal_by_name[pattern_group["Pattern"][0][0].lower()]
        mep_id = pattern["Id"] + pattern["SetId"] * 256
        texture = patterndefs_textures[mep_id]
        entry = CatalogueEntry(name, identificator=pattern_group["Pattern"],
                               image=pygame.Surface(entry_size, pygame.SRCALPHA))
        entry.image.fill(entry_background_color)
        draw_projected_triangle(entry.image, texture["a"],
                                ((entry_size[0] // 2, icon_margin),
                                 (entry_size[0] - icon_margin, entry_size[1] - icon_margin),
                                 (icon_margin, entry_size[1] - icon_margin)),
                                (0.5, 0.5, 0.5), suspend_timeout=True)
        entries.append(entry)

    return Catalogue(entries)


def load_landscapes_catalogue():
    assert animations.pygame_converted

    entries = [CatalogueEntry("", None, image=pygame.Surface(entry_size, pygame.SRCALPHA))]
    entries[0].image.fill(entry_background_color)

    for name, animation in animations.items():
        entry = CatalogueEntry(name, identificator=landscapedefs[name],
                               image=pygame.Surface(entry_size, pygame.SRCALPHA))
        entry.image.fill(entry_background_color)
        temp_entry_surface.fill((0, 0, 0, 0))
        image = animation.images[0]
        ratio = image.width / image.height
        if   ratio > 1: size = (entry_size[0] - 2 * icon_margin, round((entry_size[1] - 2 * icon_margin) / ratio))
        elif ratio < 1: size = (round((entry_size[1] - 2 * icon_margin) * ratio), entry_size[1] - 2 * icon_margin)
        else: size = (entry_size[0] - 2 * icon_margin, entry_size[1] - 2 * icon_margin)

        entry.image.blit(pygame.transform.scale(image, size),
                         ((entry_size[0] - 2 * icon_margin - size[0]) // 2,
                          (entry_size[1] - 2 * icon_margin - size[1]) // 2))
        entries.append(entry)

    return Catalogue(entries)


def load_landscapes_groups_catalogue():
    assert animations.pygame_converted

    entries = [CatalogueEntry("", None, image=pygame.Surface(entry_size, pygame.SRCALPHA))]
    entries[0].image.fill(entry_background_color)

    for name, landscape_group in landscapes_edit_group.items():


        entry = CatalogueEntry(name, identificator=landscape_group["Landscape"],
                               image=pygame.Surface(entry_size, pygame.SRCALPHA))
        entry.image.fill(entry_background_color)
        temp_entry_surface.fill((0, 0, 0, 0))

        image = animations[landscape_group["Landscape"][0][0].lower()].images[0]
        ratio = image.width / image.height
        if   ratio > 1: size = (entry_size[0] - 2 * icon_margin, round((entry_size[1] - 2 * icon_margin) / ratio))
        elif ratio < 1: size = (round((entry_size[1] - 2 * icon_margin) * ratio), entry_size[1] - 2 * icon_margin)
        else: size = (entry_size[0] - 2 * icon_margin, entry_size[1] - 2 * icon_margin)

        entry.image.blit(pygame.transform.scale(image, size),
                         ((entry_size[0] - 2 * icon_margin - size[0]) // 2,
                          (entry_size[1] - 2 * icon_margin - size[1]) // 2))
        entries.append(entry)

    return Catalogue(entries)


def load_structures_catalogue():
    assert patterndefs_textures.pygame_converted

    entries = [CatalogueEntry("", None, image=pygame.Surface(entry_size, pygame.SRCALPHA))]
    entries[0].image.fill(entry_background_color)

    for name, data in road.items():
        mep_id = data['patterna'][12] * 256 + data['patterna'][13]
        entry = CatalogueEntry(patterndefs_normal[mep_id]["Name"], identificator=name,
                               image=pygame.Surface(entry_size, pygame.SRCALPHA))
        entry.image.fill(entry_background_color)
        draw_projected_triangle(entry.image, patterndefs_textures[mep_id]["a"],
                                ((entry_size[0] // 2, icon_margin),
                                 (entry_size[0] - icon_margin, entry_size[1] - icon_margin),
                                 (icon_margin, entry_size[1] - icon_margin)),
                                (0.5, 0.5, 0.5), suspend_timeout=True)
        entries.append(entry)

    return Catalogue(entries)
