import os
import numpy as np
from PIL import Image
from scripts.animation import Animation
from scripts.buffer import BufferGiver, BufferTaker
from scripts.flags import warp_sign
from scripts.image import get_rgb_negative
from supplements.read import read
from supplements.remaptables import RemapTable, remaptable_default, remaptable_direct


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
        if os.path.dirname(filepath) != "":
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

    def from_image(self, filepath, remaptable: RemapTable = None):
        with Image.open(filepath).convert("RGBA") as img:
            width, height = img.size
            pixels = img.load()

            self.data = []
            for y in range(height):
                row = []
                for x in range(width):
                    r, g, b, a = pixels[x, y]
                    if a == 0: value = (0, 0)
                    else:      value = (remaptable.palette.inversed[(r, g, b)], 255)
                    row.append(value)
                self.data.append(row)
        self.rect[2] = width
        self.rect[3] = height


class Bitmap(dict):
    def __init__(self):
        super().__init__()
        self.font_metadata = [0, 0]  # Important only for *.fnt files.

    def load(self, filename: str, font_header=False):

        # Following code written below was initially constructed in year 2013 on XeNTaX forum.
        # Original discussion was available here: https://forum.xentax.com/viewtopic.php?t=10705

        buffer =  BufferGiver(read(filename, mode="rb"))

        if font_header:
            assert buffer.unsigned(length=4) == 40
            self.font_metadata[0] = buffer.unsigned(length=2)
            self.font_metadata[1] = buffer.unsigned(length=2)

        assert buffer.unsigned(length=4) == 25
        buffer.unsigned(4)
        number_of_frames = buffer.unsigned(4)
        number_of_pixels = buffer.unsigned(4)
        number_of_rows = buffer.unsigned(4)
        if not font_header:
            assert number_of_rows == buffer.unsigned(4)
        else:
            buffer.unsigned(4)
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
                    # None of lanscapes and fonts from games "Cultures: Discovery of Vinland" and "Cultures: The Revenge
                    # of the Rain God" use this type of frame when parameters "FirstBob" and "Elements" are considered.
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

                    frame_data.append(row)
                    number_of_rows_counted += 1

            except NotImplementedError:
                self[frame_index] = None
                has_unreadable_parts = True

            else:
                self[frame_index] = Frame(frame_type=frame_type,
                                          rect=(offset_x, offset_y, width, height),
                                          data=frame_data)
        if not has_unreadable_parts and not font_header:
            assert number_of_pixels == number_of_pixels_counted
            assert number_of_rows == number_of_rows_counted

    def save(self, filename: str, font_header=False):

        # This function is meant to be used only for bitmaps consisting of frames with frame type equal to 0 or 1.

        buffer_header = BufferTaker()

        if font_header:
            buffer_header.unsigned(40, length=4)
            buffer_header.unsigned(self.font_metadata[0], length=2)
            buffer_header.unsigned(self.font_metadata[1], length=2)

        buffer_header.unsigned(25, length=4)
        buffer_header.unsigned(0, length=4)
        number_of_frames = max((*self.keys(), -1)) + 1
        buffer_header.unsigned(number_of_frames, length=4)
        number_of_pixels = 0
        number_of_rows = 0
        buffer_section_0, buffer_section_1, buffer_section_2 = [BufferTaker() for _ in range(3)]

        def insert_pixels():
            nonlocal frame, row, row_to_add, number_of_pixels
            match frame.frame_type:  # noqa
                case 1: row.extend([len(row_to_add), *row_to_add])
                case 2: row.append(len(row_to_add))
                case 3: raise ValueError
                case 4: raise ValueError
                case _: raise ValueError

        for frame_index in range(number_of_frames):
            frame = self.get(frame_index, None)

            if not isinstance(frame, Frame) or frame.frame_type == 0:
                buffer_section_0.unsigned(0, length=28)
                continue

            buffer_section_0.unsigned(frame.frame_type, length=4)
            for i in range(4):
                buffer_section_0.signed(frame.rect[i], length=4)
            buffer_section_0.unsigned(len(buffer_section_2) // 4, length=4)
            buffer_section_0.unsigned(0, length=4)

            number_of_rows += frame.rect[3]

            for row_index in range(frame.rect[3]):

                current_alpha = True
                pixels_count = 0
                row_to_add = []
                row = []

                for x in range(frame.rect[2]):
                    color, alpha = frame.data[row_index][x]

                    match frame.frame_type:
                        case 1: color = color if alpha != 0 else alpha_index
                        case 2: raise NotImplementedError
                        case 3: raise NotImplementedError
                        case 4: raise NotImplementedError
                        case _: raise ValueError

                    if color == alpha_index:
                        if not current_alpha and pixels_count > 0:
                            insert_pixels()
                            row_to_add = []
                            pixels_count = 0
                        pixels_count += 1
                        if pixels_count == 127:
                            row.append(-1)
                            pixels_count = 0
                        current_alpha = True
                    else:
                        if current_alpha and pixels_count > 0:
                            row.append((pixels_count - 128) % 256)
                            pixels_count = 0
                        row_to_add.append(color)
                        pixels_count += 1
                        if pixels_count == 127:
                            insert_pixels()
                            row_to_add = []
                            pixels_count = 0
                        current_alpha = False

                if pixels_count > 0 and not current_alpha:
                    insert_pixels()

                if len(row) == 0:
                    indent = -1
                elif row[0] == -1:
                    raise NotImplementedError
                elif row[0] > 128:
                    indent = row.pop(0) - 128
                else:
                    indent = 0

                while len(row) > 0 and row[-1] == -1:
                    row.pop(-1)

                if indent != -1:
                    row.append(0)

                indent_bin_str = bin(indent % 1024)[2:]
                indent_bin_str = "0" * (10 - len(indent_bin_str)) + indent_bin_str
                header_offset_str = bin(len(buffer_section_1))[2:]
                header_offset_str= "0" * (22 - len(header_offset_str)) + header_offset_str

                buffer_section_2.unsigned(int(indent_bin_str+header_offset_str, 2), length=4)

                buffer_section_1.iterable(row)

        buffer_giver_section_0 = BufferGiver(bytes(buffer_section_0))
        buffer_giver_section_1 = BufferGiver(bytes(buffer_section_1))

        for frame_index in range(number_of_frames):  # This loop is only to calculate number of pixels, it might be
                                                     # possible to integrate it into the previous loop.
            frame = self.get(frame_index, None)

            if not isinstance(frame, Frame):
                continue

            buffer_giver_section_0.unsigned(length=20)
            buffer_inverse_section_2 = BufferGiver(bytes(buffer_section_2))
            buffer_inverse_section_2.skip(buffer_giver_section_0.unsigned(length=4) * 4)
            buffer_giver_section_0.unsigned(length=4)

            for _ in range(frame.rect[3]):

                row_header = buffer_inverse_section_2.binary(length=4, byteorder="little")
                indent = warp_sign(int(row_header[:10], 2), 10)

                if indent == -1:
                    head = 0
                else:

                    buffer_giver_section_1 = BufferGiver(bytes(buffer_section_1))
                    buffer_giver_section_1.skip(int(row_header[10:], 2))
                    head = -1  # This value can be anything else than zero.

                while head != 0:
                    head = buffer_giver_section_1.signed(length=1)  # noqa

                    number_of_pixels += 1

                    if head > 0:
                        match frame.frame_type:
                            case 1: buffer_giver_section_1.skip(head)
                            case 3: buffer_giver_section_1.skip(1)
                            case 4: buffer_giver_section_1.skip(head * 2)

                        match frame.frame_type:
                            case 1: number_of_pixels += head
                            case 2: number_of_pixels += 0
                            case 3: number_of_pixels += 1
                            case 4: number_of_pixels += head * 2

                    elif head < 0:
                        head += 128
                    else:
                        pass

        buffer_header.unsigned(number_of_pixels, length=4)
        buffer_header.unsigned(number_of_rows, length=4)
        buffer_header.unsigned(number_of_rows, length=4)
        buffer_header.unsigned(0, length=8)

        if number_of_frames != 0:
            for buffer_section in (buffer_section_0, buffer_section_1, buffer_section_2):
                buffer_header.unsigned(10, length=4)
                buffer_header.unsigned(len(buffer_section), length=4)
                buffer_header.bytes(bytes(buffer_section))

        with open(filename, "wb") as file:
            file.write(bytes(buffer_header))

    def extract(self, filename: str, remaptable: RemapTable = None, shading_factor=255,
                first_bob = 0, elements = 1, frame_duration=animation_frame_duration):
        if os.path.dirname(filename) != "":
            os.makedirs(os.path.dirname(filename), exist_ok=True)

        animation = self.to_animation(remaptable, shading_factor, first_bob, elements)
        animation.save(filename, frame_duration=frame_duration)

    def _extract_to_raw_data(self, directory: str):
        metadata_string = f"{self.font_metadata[0]},{self.font_metadata[1]}\n"
        for frame_index in range(max(self.keys())+1):
            frame = self.get(frame_index, None)
            if not isinstance(frame, Frame) or frame.frame_type == 0:
                metadata_string += "0,0,0,0,0\n"
                continue
            metadata_string += f"{frame.frame_type},{','.join(map(str, frame.rect))}\n"
            frame.extract(os.path.join(directory, f"{frame_index}.png"), remaptable=remaptable_direct)

        with open(os.path.join(directory, "meta.csv"), "w") as file:
            file.write(metadata_string.rstrip("\n"))

    def _load_from_raw_data(self, directory: str):
        with open(os.path.join(directory, "meta.csv")) as file:
            file_content = file.read().rstrip("\n").split("\n")
            self.font_metadata = list(map(int, file_content[0].split(",")))
            for frame_index, line in enumerate(file_content[1:]):

                frame_type, offset_x, offset_y, width, height = map(int, line.split(","))

                if frame_type != 0:
                    frame = Frame(frame_type=frame_type,
                                  rect=[offset_x, offset_y, width, height],
                                  data=[])
                    frame.from_image(os.path.join(directory, f"{frame_index}.png"),
                                     remaptable=remaptable_direct)
                    assert tuple(frame.rect[2:4]) == (width, height)

                    self[frame_index] = frame
                else:
                    self[frame_index] = None

    def to_animation(self, remaptable: RemapTable = None, shading_factor=255,
                     first_bob = 0, elements = 1, high_color_shading_mode = 0, masked_file: bool = False):

        animation = Animation()
        animation.from_bitmap_dict(self, remaptable, shading_factor, first_bob,
                                   elements, high_color_shading_mode, masked_file)
        return animation
