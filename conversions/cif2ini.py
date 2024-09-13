import itertools

newline_representation = b"\\n"

def cultures_cif_block_encoder_decoder(mode, buffer: bytes):
    # https://forum.xentax.com/viewtopic.php?t=3711 (function translated from Pascal language)
    buffer = [byte for byte in buffer]
    c = 71
    d = 126
    buffer_size = len(buffer)

    for i in range(buffer_size):
        b = buffer[i]
        if mode == 'decode':  # cif -> ini
            b = b - 1
            b = b ^ c
        elif mode == 'encode':  # ini -> cif
            b = b ^ c
            b = b + 1
        else:
            raise ValueError

        c = c + d
        d = d + 33

        char_limit = 256

        buffer[i] = b % char_limit
    return bytes(buffer)


nexts = lambda iterable, var: bytes(list(itertools.islice(iterable, var)))  # noqa


def bytes_buffer(bytes_obj):
    for byte in bytes_obj:
        yield byte


def bytes_to_integers(bytes_obj: bytes) -> list:
    bytes_obj = [bytes_obj[4 * i: 4 * i + 4] for i in range(len(bytes_obj) // 4)]
    return [int.from_bytes(bytes(el), byteorder="little") for el in bytes_obj]


def integers_to_bytes(list_obj: list) -> bytes:
    bytes_obj = b""
    for integer in list_obj:
        bytes_obj += int.to_bytes(integer, length=4, byteorder="little")
    return bytes_obj


def read_texttable(bytes_decoded_indextable, bytes_decoded_texttable):
    decoded_indextable = bytes_to_integers(bytes_decoded_indextable)

    decoded_texttable = []

    for index_value in decoded_indextable:
        decoded_texttable.append(b'')
        i = index_value
        while bytes_decoded_texttable[i] != 0:
            decoded_texttable[-1] += int.to_bytes(bytes_decoded_texttable[i], byteorder="little", length=1)
            i += 1
    return decoded_texttable


def texttable_to_list(bytes_obj: bytes, tab_file):
    bytes_lines = bytes_obj.split(b"\n")
    for index_value in range(len(bytes_lines)):
        line = bytes_lines[index_value]

        if not tab_file:
            if int.to_bytes(line[0], byteorder="little", length=1) == b'[' and\
               int.to_bytes(line[-1], byteorder="little", length=1) == b']':
                line = b"\x01"+line[1:-1]
            else:
                line = b"\x02"+line

        line = line.replace(newline_representation, b"\n")

        bytes_lines[index_value] = line
    return bytes_lines


def write_indextable(list_decoded_texttable):
    decoded_indextable = []
    len_sum = 0
    for line in list_decoded_texttable:
        decoded_indextable.append(len_sum)
        len_sum += len(line) + 1
    return decoded_indextable


def from_cif_header_cultures1(buffer):  # remaining buffer
    bytes_unknown0 = nexts(buffer, 2)
    bytes_number_of_entries_1 = nexts(buffer, 4)
    bytes_number_of_entries_2 = nexts(buffer, 4)
    bytes_unknown1 = nexts(buffer, 4)
    bytes_size_of_index_table = nexts(buffer, 4)

    size_of_index_table = int.from_bytes(bytes_size_of_index_table, byteorder="little")

    number_of_entries_1 = int.from_bytes(bytes_number_of_entries_1, byteorder="little")
    number_of_entries_2 = int.from_bytes(bytes_number_of_entries_2, byteorder="little")

    assert number_of_entries_1 == number_of_entries_2 == size_of_index_table / 4

    bytes_encoded_indextable = nexts(buffer, size_of_index_table)
    bytes_unknown2 = nexts(buffer, 2)
    bytes_unknown3 = nexts(buffer, 4)

    assert bytes_unknown0 == bytes_unknown2 == b'\x01\x00'
    assert bytes_unknown1 == bytes_unknown3 == b'\x0a\x00\x00\x00'

    bytes_size_of_text_table = nexts(buffer, 4)

    size_of_text_table = int.from_bytes(bytes_size_of_text_table, byteorder="little")

    bytes_encoded_texttable = nexts(buffer, size_of_text_table)
    return bytes_encoded_indextable, bytes_encoded_texttable


def from_cif_header_cultures2(buffer):  # remaining buffer
    bytes_unknown0 = nexts(buffer, 6)
    bytes_unknown1 = nexts(buffer, 4)
    bytes_number_of_entries_1 = nexts(buffer, 4)
    bytes_number_of_entries_2 = nexts(buffer, 4)
    bytes_number_of_entries_3 = nexts(buffer, 4)
    bytes_size_of_text_table_1 = nexts(buffer, 4)

    bytes_unknown2 = nexts(buffer, 4)
    bytes_unknown3 = nexts(buffer, 4)
    bytes_size_of_index_table = nexts(buffer, 4)

    size_of_index_table = int.from_bytes(bytes_size_of_index_table, byteorder="little")

    bytes_encoded_indextable = nexts(buffer, size_of_index_table)
    bytes_unknown4 = nexts(buffer, 1)
    bytes_unknown5 = nexts(buffer, 4)
    bytes_unknown6 = nexts(buffer, 4)
    bytes_size_of_text_table_2 = nexts(buffer, 4)

    size_of_text_table_1 = int.from_bytes(bytes_size_of_text_table_1, byteorder="little")
    size_of_text_table_2 = int.from_bytes(bytes_size_of_text_table_2, byteorder="little")

    number_of_entries_1 = int.from_bytes(bytes_number_of_entries_1, byteorder="little")
    number_of_entries_2 = int.from_bytes(bytes_number_of_entries_2, byteorder="little")
    number_of_entries_3 = int.from_bytes(bytes_number_of_entries_3, byteorder="little")

    assert number_of_entries_1 == number_of_entries_2 == number_of_entries_3 == size_of_index_table/4
    assert size_of_text_table_1 == size_of_text_table_2

    assert bytes_unknown0 == b'\x00\x00\x00\x00\x00\x00'
    assert bytes_unknown1 == b'\x01\x00\x00\x00'
    assert bytes_unknown2 == bytes_unknown5 == b'\xe9\x03\x00\x00'
    assert bytes_unknown3 == bytes_unknown6 == b'\x00\x00\x00\x00'
    assert bytes_unknown4 == b'\x01'

    bytes_encoded_texttable = nexts(buffer, size_of_text_table_1)

    return bytes_encoded_indextable, bytes_encoded_texttable


def to_cif_header_cultures1(bytes_encoded_indextable, bytes_encoded_texttable, number_of_entries):
    bytes_file_id = b'\x41\x00'
    bytes_unknown0 = bytes_unknown2 = b'\x01\x00'
    bytes_unknown1 = bytes_unknown3 = b'\x0a\x00\x00\x00'

    size_of_index_table = number_of_entries * 4
    bytes_number_of_entries = int.to_bytes(number_of_entries, byteorder="little", length=4)
    bytes_size_of_index_table = int.to_bytes(size_of_index_table, byteorder="little", length=4)
    bytes_size_of_text_table = int.to_bytes(len(bytes_encoded_texttable), byteorder="little", length=4)

    bytes_obj = \
        bytes_file_id + \
        bytes_unknown0 + \
        bytes_number_of_entries + \
        bytes_number_of_entries + \
        bytes_unknown1 + \
        bytes_size_of_index_table + \
        bytes_encoded_indextable + \
        bytes_unknown2 + bytes_unknown3 + \
        bytes_size_of_text_table + \
        bytes_encoded_texttable

    return bytes_obj


def to_cif_header_cultures2(bytes_encoded_indextable, bytes_encoded_texttable, number_of_entries):
    bytes_file_id = b'\xfd\x03'
    bytes_unknown0 = b'\x00\x00\x00\x00\x00\x00'
    bytes_unknown1 = b'\x01\x00\x00\x00'
    bytes_unknown2 = bytes_unknown5 = b'\xe9\x03\x00\x00'
    bytes_unknown3 = bytes_unknown6 = b'\x00\x00\x00\x00'
    bytes_unknown4 = b'\x01'

    size_of_index_table = number_of_entries * 4
    bytes_number_of_entries = int.to_bytes(number_of_entries, byteorder="little", length=4)
    bytes_size_of_index_table = int.to_bytes(size_of_index_table, byteorder="little", length=4)
    bytes_size_of_text_table = int.to_bytes(len(bytes_encoded_texttable), byteorder="little", length=4)

    bytes_obj = \
        bytes_file_id + \
        bytes_unknown0 + \
        bytes_unknown1 + \
        bytes_number_of_entries + \
        bytes_number_of_entries + \
        bytes_number_of_entries + \
        bytes_size_of_text_table + \
        bytes_unknown2 + \
        bytes_unknown3 + \
        bytes_size_of_index_table + \
        bytes_encoded_indextable + \
        bytes_unknown4 + \
        bytes_unknown5 + \
        bytes_unknown6 + \
        bytes_size_of_text_table + \
        bytes_encoded_texttable

    return bytes_obj


def cif2ini_content(bytes_obj: bytes, tab_file: bool) -> bytes:
    buffer = bytes_buffer(bytes_obj)

    bytes_file_id = nexts(buffer, 2)
    if bytes_file_id == b'\x41\x00':  # Cultures 1
        bytes_encoded_indextable, bytes_encoded_texttable = from_cif_header_cultures1(buffer)
    elif bytes_file_id == b'\xfd\x03':  # Cultures 2
        bytes_encoded_indextable, bytes_encoded_texttable = from_cif_header_cultures2(buffer)
    else:
        raise ValueError

    bytes_decoded_indextable = cultures_cif_block_encoder_decoder("decode", bytes_encoded_indextable)
    bytes_decoded_texttable = cultures_cif_block_encoder_decoder("decode", bytes_encoded_texttable)

    decoded_texttable = read_texttable(bytes_decoded_indextable, bytes_decoded_texttable)

    decoded_lines = []
    for line in decoded_texttable:
        line = line.replace(b"\n", newline_representation)
        try:
            first_byte = line[0]

            if first_byte == 1:
                line = b"[" + line[1:] + b"]"
            elif first_byte == 2:
                line = line[1:]
            else:
                raise ValueError

        except ValueError:
            if not tab_file:
                raise ValueError
        except IndexError:
            if not tab_file:
                raise ValueError

        decoded_lines.append(line)

    return b"\n".join(decoded_lines)


def ini2cif_content(bytes_obj: bytes, cultures1: bool, tab_file: bool) -> bytes:
    list_decoded_texttable = texttable_to_list(bytes_obj, tab_file)
    decoded_indextable = write_indextable(list_decoded_texttable)

    number_of_entries = len(decoded_indextable)

    bytes_decoded_indextable = integers_to_bytes(decoded_indextable)
    bytes_decoded_texttable = b"\x00".join(list_decoded_texttable)+b"\x00"

    bytes_encoded_indextable = cultures_cif_block_encoder_decoder("encode", bytes_decoded_indextable)
    bytes_encoded_texttable = cultures_cif_block_encoder_decoder("encode", bytes_decoded_texttable)

    if cultures1:
        bytes_encoded = to_cif_header_cultures1(bytes_encoded_indextable, bytes_encoded_texttable, number_of_entries)
    else:
        bytes_encoded = to_cif_header_cultures2(bytes_encoded_indextable, bytes_encoded_texttable, number_of_entries)

    return bytes_encoded


def cif2ini(filename_input, filename_output, tab_file: bool = False):

    with open(filename_input, "rb") as file:
        bytes_obj = file.read()

    bytes_decoded = cif2ini_content(bytes_obj, tab_file)

    with open(filename_output, "wb") as file:
        file.write(bytes_decoded)


def ini2cif(filename_input, filename_output, tab_file: bool = False, cultures1: bool = True):

    with open(filename_input, "rb") as file:
        bytes_obj = file.read()

    bytes_decoded = ini2cif_content(bytes_obj, cultures1, tab_file)

    with open(filename_output, "wb") as file:
        file.write(bytes_decoded)
