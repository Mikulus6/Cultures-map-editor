import itertools
import sys

alpha_index = -1

def bytes_buffer(bytes_obj):
    for byte in bytes_obj:
        yield byte

def bytes_to_bits_string(bytes_obj):
    string = str(bin(bytes_to_int(bytes_obj)))[2:]
    return "0"*(8*len(bytes_obj) - len(string)) + string

nexts = lambda iterable, var: bytes(list(itertools.islice(iterable, var)))                       # noqa: E731
bytes_to_int = lambda bytes_obj: int.from_bytes(bytes_obj, byteorder="little")                   # noqa: E731
int_to_signed = lambda value, length: ((value+(2**(length-1))) % (2**length))-(2**(length-1))    # noqa: E731
bytes_to_list_of_ints = lambda bytes_obj: [byte for byte in bytes_obj]                           # noqa: E731

def get_bytes_gen(bytes_obj):
    buffer = bytes_buffer(bytes_obj)

    def gen_bytes(n):
        return nexts(buffer, n)
    return gen_bytes


def read_bmd_file(file_path, fnt_file=False):
    with open(file_path, "rb") as bmd_file:
        bytes_gen_file = get_bytes_gen(bmd_file.read())

    # Values 'fnt_unknown_1', 'fnt_unknown_2' and 'unknown' aren't important for reading *.bmd files, however they would
    # be important in case of writing *.bmd files.

    if fnt_file:
        fnt_file_id   = bytes_gen_file(4)   # noqa: E222 E221
        fnt_zero_1    = bytes_gen_file(4)   # noqa: E222 E221
        fnt_unknown_1 = bytes_gen_file(4)   # noqa
        fnt_unknown_2 = bytes_gen_file(4)   # noqa

        assert fnt_file_id == b'\xf5\x03\x00\x00'
        assert fnt_zero_1 == b'\x00' * len(fnt_zero_1)

    file_id       =              bytes_gen_file(4)   # noqa: E222 E221
    zero_1        =              bytes_gen_file(8)   # noqa: E222 E221
    num_frames    = bytes_to_int(bytes_gen_file(4))  # noqa: E222 E221
    num_pixels    = bytes_to_int(bytes_gen_file(4))  # noqa: E222 E221
    num_rows      = bytes_to_int(bytes_gen_file(4))  # noqa: E222 E221
    num_rows_dup  = bytes_to_int(bytes_gen_file(4))  # noqa: E222 E221
    unknown       = bytes_to_int(bytes_gen_file(4))  # noqa
    zero_2        =              bytes_gen_file(4)   # noqa: E222 E221

    assert file_id == b'\xf4\x03\x00\x00'
    assert zero_1 == b'\x00' * len(zero_1)
    assert zero_2 == b'\x00' * len(zero_2)
    assert num_rows == num_rows_dup

    counted_rows = 0
    counted_pixels = 0

    frames_list = []

    if num_frames == 0:
        return frames_list

    sections = []

    for _ in range(3):
        section_id     =              bytes_gen_file(4)               # noqa: E222 E221
        zero_3         =              bytes_gen_file(4)               # noqa: E222 E221
        section_length = bytes_to_int(bytes_gen_file(4))              # noqa: E222 E221
        section_bytes  =              bytes_gen_file(section_length)  # noqa: E222 E221

        assert section_id == b'\xe9\x03\x00\x00'
        assert zero_3 == b'\x00\x00\x00\x00'

        sections.append(section_bytes)
    else:
        assert len(bytes_gen_file(sys.maxsize)) == 0

    section_1 = sections[0]
    section_2 = sections[1]
    section_3 = sections[2]

    del sections, bytes_gen_file

    assert len(section_1) == num_frames*24

    bytes_gen_section_1 = get_bytes_gen(section_1)

    for frame_index in range(num_frames):
        frame_type       =               bytes_to_int(bytes_gen_section_1(4))       # noqa: E222 E221
        offset_x         = int_to_signed(bytes_to_int(bytes_gen_section_1(4)), 32)  # noqa: E222 E221
        offset_y         = int_to_signed(bytes_to_int(bytes_gen_section_1(4)), 32)  # noqa: E222 E221
        width            =               bytes_to_int(bytes_gen_section_1(4))       # noqa: E222 E221
        length           =               bytes_to_int(bytes_gen_section_1(4))       # noqa: E222 E221
        offset_section_3 =               bytes_to_int(bytes_gen_section_1(4))       # noqa: E222 E221

        assert frame_type in range(5)

        bytes_gen_section_3_offset = get_bytes_gen(section_3[offset_section_3 * 4:])

        frame = []
        row = []
        row_to_add = []

        for _ in range(length):
            frame_row = bytes_to_bits_string(bytes_gen_section_3_offset(4))

            indent =           int_to_signed(int(frame_row[:10], 2), 10)  # noqa: E222 E221
            offset_section_2 =               int(frame_row[10:], 2)       # noqa: E222 E221

            bytes_gen_section_2_offset = get_bytes_gen(section_2[offset_section_2:])

            match frame_type:
                case 0: raise ValueError
                case 1: row = [alpha_index] * indent
                case 2: row = [alpha_index] * indent
                case 3: row = [alpha_index] * indent
                case 4: row = [alpha_index, 0] * indent

            while True:
                head = int_to_signed(bytes_to_int(bytes_gen_section_2_offset(1)), 8)

                if indent != -1:
                    counted_pixels += 1

                if head > 0:
                    match frame_type:
                        case 0: raise ValueError
                        case 1: row_to_add = bytes_to_list_of_ints(bytes_gen_section_2_offset(head))
                        case 2: row_to_add = [0] * head
                        case 3: row_to_add = [bytes_to_int(bytes_gen_section_2_offset(1))] * head
                        case 4: row_to_add = bytes_to_list_of_ints(bytes_gen_section_2_offset(head * 2))

                    match frame_type:
                        case 0: raise ValueError
                        case 1: counted_pixels += len(row_to_add)
                        case 2: counted_pixels += 0
                        case 3: counted_pixels += 1
                        case 4: counted_pixels += len(row_to_add)

                elif head < 0:
                    head += 128
                    match frame_type:
                        case 0: raise ValueError
                        case 1: row_to_add = [alpha_index] * head
                        case 2: row_to_add = [alpha_index] * head
                        case 3: raise ValueError
                        case 4: row_to_add = [alpha_index, 0] * head
                else:
                    match frame_type:
                        case 0: raise ValueError
                        case 1: row_to_add = [alpha_index] * (width - len(row))
                        case 2: row_to_add = [alpha_index] * (width - len(row))
                        case 3: row_to_add = [alpha_index] * (width - len(row))
                        case 4: row_to_add = [alpha_index, 0] * (width - len(row) // 2)

                row += row_to_add

                if head == 0:
                    break

            match frame_type:
                case 0: raise ValueError
                case 1:
                    if fnt_file: row = [(255, color) if color != alpha_index else (0, 0) for color in row]  # noqa: E701
                    else: row = [(color, 255) if color != alpha_index else (0, 0) for color in row]         # noqa: E701
                case 2: row = [(0, 128) if color != alpha_index else (0, 0) for color in row]
                case 3: row = [(0, alpha) if alpha not in (alpha_index, 255) else (0, 0) for alpha in row]
                case 4: row = [(row[i] if row[i] != alpha_index else 0, row[i + 1]) for i in range(0, len(row), 2)]

            assert len(row) == width
            assert all(map(lambda pixel: isinstance(pixel, tuple) and len(pixel) == 2 and
                           all(map(lambda var: 0 <= var <= 255, pixel)), row))

            frame.append(row)
            counted_rows += 1

        frames_list.append({"index": frame_index,
                            "type": frame_type,
                            "offset_x": offset_x,
                            "offset_y": offset_y,
                            "frame": frame})

    assert num_rows == counted_rows
    assert num_pixels == counted_pixels
    assert num_frames == len(frames_list)

    return frames_list
