import pygame
import time
from interface.const import message_duration, one_frame_popup_rect_size, one_frame_popup_rect_margin, resolution, \
                            font_color, font_antialias


class Message:
    initialized = False
    def __init__(self):
        if self.__class__.initialized:
            raise ValueError(f"{self.__class__.__name__} is a singleton.")
        self.__class__.initialized = True

        self.last_time = time.time() - 2 * message_duration
        self.text = ""
        self.grey_out = False

    def set_message(self, text):
        self.text = text
        self.last_time = time.time()

    def get_message(self):
        if time.time() - self.last_time > message_duration:
            return None
        return self.text

    def reset_grey_out(self):
        self.grey_out = False


def set_font_text(editor):

    if editor.font_text is not None:
        pass
    elif editor.cursor_vertex is not None and editor.ignore_minor_vertices:
        editor.font_text = f"macro vertex coordinates: ({editor.cursor_vertex[0]}, {editor.cursor_vertex[1]})"
    elif editor.cursor_vertex is not None and not editor.ignore_minor_vertices:
        editor.font_text = f"micro vertex coordinates: ({editor.cursor_vertex[0]}, {editor.cursor_vertex[1]})"
    elif editor.minimap.mouse_hover:
        editor.font_text = "minimap (click or hold to move)"


def one_frame_grey_out(editor):
    if message.grey_out:
        return
    shape_surf = pygame.Surface(pygame.Rect((0, 0, *resolution)).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, (128, 128, 128, 128), shape_surf.get_rect())
    editor.root.blit(shape_surf, (0, 0, *resolution))
    pygame.display.flip()
    message.grey_out = True


def one_frame_popup(editor, text):
    """Show message for one frame when application is about to get a one-frame lag spike (e.g. loading message)."""
    rect = (resolution[0] - one_frame_popup_rect_size[0]) // 2,\
           (resolution[1] - one_frame_popup_rect_size[1]) // 2,\
           *one_frame_popup_rect_size
    rect_without_margin = (resolution[0] - one_frame_popup_rect_size[0] + one_frame_popup_rect_margin) // 2,\
                          (resolution[1] - one_frame_popup_rect_size[1] + one_frame_popup_rect_margin) // 2,\
                          (one_frame_popup_rect_size[0] - one_frame_popup_rect_margin),\
                          (one_frame_popup_rect_size[1] - one_frame_popup_rect_margin),\

    pygame.draw.rect(editor.root, (64, 64, 64), rect)
    pygame.draw.rect(editor.root, (128, 128, 128), rect_without_margin)
    rendered_text = editor.font.render(text, font_antialias, font_color)
    position = (resolution[0] - rendered_text.width) // 2,\
               (resolution[1] - rendered_text.height) // 2,\

    editor.root.blit(rendered_text, position)
    pygame.display.flip()


message = Message()
