import os
import numpy as np
from PIL import Image
from scripts.animation import Animation
from scripts.buffer import BufferGiver
from scripts.flags import warp_sign
from scripts.image import get_rgb_negative
from supplements.read import read
from supplements.remaptables import RemapTable, remaptable_default


alpha_index = -1
shadow_color = (0, 0, 0)

# Following values might not be exactly correct.
high_color_shade_alpha = 92
animation_frame_duration = 0.1  # seconds


class Frame:
    def __init__(self, frame_type, rect, data: list):
        self.frame_type = frame_type
        self.rect = rect
        self.data = data

    def extract(self, filepath: str, remaptable: RemapTable = None):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.to_image(remaptable=remaptable).save(filepath)

    def to_image(self, *, remaptable: RemapTable = None, shading_factor = 255,
                 high_color_shading_mode = 0, masked_file: bool = False) -> Image:

        if tuple(self.rect[2:]) == (0, 0):
            rect = (*self.rect[:2], 1, 1)
            data = [[(0, 0)]]
        else:
            rect = self.rect
            data = self.data

        array = np.zeros((rect[3], rect[2], 4), dtype=np.uint8)
        for y, row in enumerate(data):
            for x, (value, alpha) in enumerate(row):
                alpha_effective = alpha * shading_factor // 255

                if masked_file and high_color_shading_mode and alpha != 0:
                    array[y, x] = (*get_rgb_negative(shadow_color), high_color_shade_alpha)
                elif masked_file:
                    array[y, x] = (*shadow_color, alpha_effective)
                elif remaptable is None:
                    array[y, x] = (*remaptable_default[value], alpha_effective)
                else:
                    array[y, x] = (*remaptable.palette[value], alpha_effective)
        return Image.fromarray(array, 'RGBA')


class Bitmap(dict):
    def __init__(self):
        super().__init__()

    def load(self, filename: str):

        buffer =  BufferGiver(read(filename, mode="rb"))

        assert buffer.unsigned(length=4) == 25
        buffer.unsigned(4)
        number_of_frames = buffer.unsigned(4)
        number_of_pixels = buffer.unsigned(4)
        number_of_rows = buffer.unsigned(4)
        assert number_of_rows == buffer.unsigned(4)
        buffer.unsigned(length=8)

        if number_of_frames == 0:
            return

        number_of_pixels_counted = 0
        number_of_rows_counted = 0

        has_unreadable_parts = False

        sections = []

        for _ in range(3):
            assert buffer.unsigned(length=4) == 10
            sections.append(buffer.bytes(buffer.unsigned(length=4)))

        assert len(sections[0]) == number_of_frames * 28

        buffer_section_0 = BufferGiver(sections[0])

        for frame_index in range(number_of_frames):

            try:
                frame_type = buffer_section_0.unsigned(length=4)
                offset_x = buffer_section_0.signed(length=4)
                offset_y = buffer_section_0.signed(length=4)
                width = buffer_section_0.unsigned(length=4)
                height = buffer_section_0.unsigned(length=4)

                assert frame_type in range(5)
                assert frame_type != 0 or (width == height == 0)

                buffer_section_2 = BufferGiver(sections[2])
                buffer_section_2.skip(buffer_section_0.unsigned(length=4) * 4)
                buffer_section_0.unsigned(length=4)

                if frame_type == 3:
                    # None of lanscapes from games "Cultures: Discovery of Vinland" and "Cultures: The Revenge of the
                    # Rain God" uses this type of frame when parameters "FirstBob" and "Elements" are considered.
                    raise NotImplementedError

                frame_data = []

                for _ in range(height):

                    row = []

                    row_header = buffer_section_2.binary(length=4, byteorder="little")
                    indent = warp_sign(int(row_header[:10], 2), 10)

                    if indent == -1:
                        match frame_type:
                            case 1: row = [alpha_index] * width
                            case 2: row = [alpha_index] * width
                            case 3: row = [alpha_index] * width
                            case 4: row = [alpha_index, 0] * width
                        head = 0

                    else:
                        match frame_type:
                            case 1: row = [alpha_index] * indent
                            case 2: row = [alpha_index] * indent
                            case 3: row = [alpha_index] * indent
                            case 4: row = [alpha_index, 0] * indent

                        buffer_section_1 = BufferGiver(sections[1])
                        buffer_section_1.skip(int(row_header[10:], 2))
                        head = -1  # This value can be anything else than zero.

                    while head != 0:
                        head = buffer_section_1.signed(length=1)  # noqa

                        if indent != -1:
                            number_of_pixels_counted += 1

                        if head > 0:
                            match frame_type:
                                case 1: row_to_add = buffer_section_1.iterable(length=head)
                                case 2: row_to_add = [0] * head
                                case 3: row_to_add = buffer_section_1.iterable(length=1) * head
                                case 4: row_to_add = buffer_section_1.iterable(length=head * 2)

                            match frame_type:
                                case 1: number_of_pixels_counted += head
                                case 2: number_of_pixels_counted += 0
                                case 3: number_of_pixels_counted += 1
                                case 4: number_of_pixels_counted += head * 2

                        elif head < 0:
                            head += 128
                            match frame_type:
                                case 1: row_to_add = [alpha_index] * head
                                case 2: row_to_add = [alpha_index] * head
                                case 3: raise NotImplementedError
                                case 4: row_to_add = [alpha_index, 0] * head
                        else:
                            match frame_type:
                                case 1: row_to_add = [alpha_index] * (width - len(row))
                                case 2: row_to_add = [alpha_index] * (width - len(row))
                                case 3: row_to_add = [alpha_index] * (width - len(row))
                                case 4: row_to_add = [alpha_index, 0] * (width - len(row) // 2)

                        row += row_to_add  # noqa

                    match frame_type:
                        case 1: row = [(color, 255) if color != alpha_index else (0, 0) for color in row]
                        case 2: row = [(0, 255) if color != alpha_index else (0, 0) for color in row]
                        case 3: row = [(alpha, 255) if alpha not in (alpha_index, 255) else (0, 0) for alpha in row]
                        case 4: row = [(row[i] if row[i] != alpha_index else 0, row[i + 1]) for i in range(0, len(row), 2)]

                    assert len(row) == width
                    assert all(map(lambda pixel: isinstance(pixel, tuple) and len(pixel) == 2 and
                                                 all(map(lambda var: 0 <= var <= 255, pixel)), row))

                    frame_data.append(row)
                    number_of_rows_counted += 1

            except NotImplementedError:
                self[frame_index] = None
                has_unreadable_parts = True

            else:
                self[frame_index] = Frame(frame_type=frame_type,
                                          rect=(offset_x, offset_y, width, height),
                                          data=frame_data)
        if not has_unreadable_parts:
            assert number_of_pixels == number_of_pixels_counted
            assert number_of_rows == number_of_rows_counted

    def extract(self, filename: str, remaptable: RemapTable = None, shading_factor=255,
                first_bob = 0, elements = 1, frame_duration=animation_frame_duration):
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        animation = self.to_animation(remaptable, shading_factor, first_bob, elements)
        animation.save(filename, frame_duration=frame_duration)

    def to_animation(self, remaptable: RemapTable = None, shading_factor=255,
                     first_bob = 0, elements = 1, high_color_shading_mode = 0, masked_file: bool = False):

        animation = Animation()
        animation.from_bitmap_dict(self, remaptable, shading_factor, first_bob,
                                   elements, high_color_shading_mode, masked_file)
        return animation