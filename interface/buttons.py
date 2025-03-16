import pygame
from math import ceil
from interface.const import resolution, map_canvas_rect

button_initial_offset = (2, 2)
button_tile_size = (24, 24)
buttons_margin = 0
buttons_per_row = 11
buttons_tileset_path = "interface\\images\\buttons.png"


def image_to_tileset_dict(image: pygame.Surface, tile_size: (int, int), tileset_flags = 0):
    img_size_x, img_size_y = image.get_size()
    tile_size_x, tile_size_y = tile_size

    width = ceil(img_size_x/tile_size_x)
    height = ceil(img_size_y/tile_size_y)

    tileset_dict = dict()

    for y in range(height):
        tile_height = min((img_size_y - y * tile_size_y, tile_size_y))
        for x in range(width):
            tile_width = min((img_size_x - x*tile_size_x, tile_size_x))

            tileset_dict[x, y] = pygame.Surface((tile_width, tile_height), tileset_flags)

            surface_x = -x*tile_size_x
            surface_y = -y*tile_size_y

            tileset_dict[x, y].blit(image, (surface_x, surface_y))

    return tileset_dict


class Button:

    def __init__(self, parent_editor, position: (int, int),
                 image: pygame.Surface, image_hover: pygame.Surface = None,
                 click_function = lambda editor: None, hover_text: str = ""):

        if image_hover is None:
            image = image_hover

        self.editor = parent_editor
        self.rect = (*position, *image.size)
        self.image = image
        self.image_hover = image_hover
        self.click_function = click_function
        self.hover_text = hover_text

        assert image.size == image_hover.size

    def check_hover(self):
        return self.rect[0] <= self.editor.mouse_pos[0] < self.rect[0] + self.rect[2] and\
               self.rect[1] <= self.editor.mouse_pos[1] < self.rect[1] + self.rect[3]

    def check_click(self):
        return self.check_hover() and self.editor.mouse_press_left and not self.editor.mouse_press_left_old

    def draw(self):
        self.editor.root.blit(self.image_hover if self.check_hover() else self.image, self.rect[:2])

        if self.check_hover() and self.editor.font_text is None:
            self.editor.font_text = self.hover_text

    def action(self):
        if self.check_click():
            self.click_function(self.editor)


buttons_data = (0, "new", "create new map (Ctrl + N)"),\
               (1, "open", "open map file (Ctrl + O)"),\
               (2, "save", "save map file (Ctrl + S)"),\
               (3, "save_as", "save map file as (Ctrl + Shift + S)"),\
               (4, "pack", "import from external data"),\
               (5, "extract", "export to external data"),\
               (6, "terrain_textures", "disable / enable terrain textures"),\
               (7, "invisible_landscapes", "show / hide invisible landscapes"),\
               (8, "invisible_blocks", "show / hide blockades"),\
               (9, "mark_area", "mark hexagonal area"),\
               (10, "undo", "undo action (Ctrl + Z)"),\
               (11, "resize", "resize map"),\
               (12, "pattern_single", "modify terrain by singular pattern"),\
               (13, "pattern_group", "modify terrain by pattern group"),\
               (14, "triangle_transition", "fix triangle transitions"),\
               (15, "height", "modify height"),\
               (16, "enforce_height", "enforce horizonless heightmap"),\
               (17, "landscape_single", "modify landscapes by singular element"),\
               (18, "landscape_group", "modify landscapes by edit group"),\
               (19, "brush_adjust", "adjust brush parameters"),\
               (20, "structures", "modify structures"),\
               (21, "redo", "redo action (Ctrl + Y)")

def load_buttons(parent_editor):

    tileset = image_to_tileset_dict(pygame.image.load(buttons_tileset_path), button_tile_size,
                                    tileset_flags=pygame.SRCALPHA)

    result_buttons = list()

    for index_value, method_name, hover_text in buttons_data:
        button = Button(parent_editor,
                        (button_initial_offset[0] + (index_value % buttons_per_row) * \
                                                    (button_tile_size[0] + buttons_margin),
                         button_initial_offset[1] + (index_value // buttons_per_row) * \
                                                    (button_tile_size[1] + buttons_margin)),
                        tileset[index_value, 0], tileset[index_value, 1],
                        lambda editor, method=method_name: getattr(editor, method)(), hover_text)
        result_buttons.append(button)

    return tuple(result_buttons)


background_path = "interface\\images\\background.png"
background = pygame.image.load(background_path)
assert background.size == (resolution[0] - map_canvas_rect[2], resolution[1])
