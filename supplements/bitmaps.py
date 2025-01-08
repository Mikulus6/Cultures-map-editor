import os
import numpy as np
from PIL import Image
from scripts.buffer import BufferGiver
from scripts.flags import warp_sign

alpha_index = -1
shadow_alpha_value = 128


class Frame:
    def __init__(self, frame_type, rect, data: list):
        self.frame_type = frame_type
        self.rect = rect
        self.data = data

    def extract(self, filepath: str):

        if tuple(self.rect[:2]) == (0, 0):
            raise NotImplementedError  # Cannot export image with size 0 x 0.

        array = np.zeros((self.rect[1], self.rect[0], 4), dtype=np.uint8)
        for y, row in enumerate(self.data):
            for x, (value, alpha) in enumerate(row):
                array[y, x] = (value, value, value, alpha)
        img = Image.fromarray(array, 'RGBA')
        img.save(filepath)


class BitmapData(dict):
    def __init__(self):
        super().__init__()

    def load(self, filename: str):

        with open(filename, "rb") as file:
            buffer =  BufferGiver(file.read())

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
        ignore_global_assertions = False

        sections = []

        for _ in range(3):
            assert buffer.unsigned(length=4) == 10
            sections.append(buffer.bytes(buffer.unsigned(length=4)))

        assert len(sections[0]) == number_of_frames * 28

        buffer_section_0 = BufferGiver(sections[0])

        for frame_index in range(number_of_frames):

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

            frame_data = []
            ignore_assertions = False

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
                            case 3: row_to_add = [alpha_index] * head ;\
                                    ignore_assertions = True          ;\
                                    ignore_global_assertions = True   # uncertain line
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
                    case 2: row = [(0, shadow_alpha_value) if color != alpha_index else (0, 0) for color in row]
                    case 3: row = [(alpha, 255) if alpha not in (alpha_index, 255) else (0, 0) for alpha in row]
                    case 4: row = [(row[i] if row[i] != alpha_index else 0, row[i + 1]) for i in range(0, len(row), 2)]

                if not ignore_assertions:
                    assert len(row) == width

                assert all(map(lambda pixel: isinstance(pixel, tuple) and len(pixel) == 2 and
                                             all(map(lambda var: 0 <= var <= 255, pixel)), row))

                frame_data.append(row)
                number_of_rows_counted += 1

            self[frame_index] = Frame(frame_type=frame_type,
                                      rect=(width, height, offset_x, offset_y),
                                      data=frame_data)

        if not ignore_global_assertions:
            assert number_of_pixels == number_of_pixels_counted
            assert number_of_rows == number_of_rows_counted

    def extract(self, directory: str, extension: str = "png"):
        os.makedirs(directory, exist_ok=True)

        for frame_index, frame in self.items():
            try:
                frame.extract(os.path.join(directory, f"{frame_index}.{extension}"))
            except NotImplementedError:
                pass
