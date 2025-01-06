from typing import Literal
from scripts.buffer import BufferGiver, BufferTaker

newline_representation = "\\n"

# Cultures Initialization File (*.cif) format

# Following code written below was initially constructed around years 2009 - 2010 on XeNTaX forum.
# Original discussion was available here: https://forum.xentax.com/viewtopic.php?t=3711

def apply_cipher(bytes_obj: bytes, mode: Literal["decode", "encode"]) -> bytes:
    result = BufferTaker()
    c, d = 71, 126

    for b in bytes_obj:
        match mode:
            case "decode": b = (b - 1) ^ c
            case "encode": b = (b ^ c) + 1
            case _: raise ValueError
        c += d
        d += 33
        result.unsigned(b % 256, length=1)

    return bytes(result)

# cif -> ini
def decode(content: bytes, tab_sal_file_format: bool) -> str:
    buffer = BufferGiver(content)

    match buffer.unsigned(length=2):
        case 65: # cultures 1
            assert buffer.unsigned(length=2) == 1
            entries_num = buffer.unsigned(4)
            assert entries_num == buffer.unsigned(4)
            assert buffer.unsigned(length=4) == 10
            index_table_encoded = buffer.bytes(index_table_size := buffer.unsigned(4))
            assert entries_num == index_table_size // 4
            assert buffer.unsigned(length=2) == 1
            assert buffer.unsigned(length=4) == 10
            text_table_encoded = buffer.bytes(buffer.unsigned(4))

        case 1021: # cultures 2
            assert not tab_sal_file_format
            assert buffer.unsigned(length=6) == 0
            assert buffer.unsigned(length=4) == 1
            entries_num = buffer.unsigned(4)
            assert entries_num == buffer.unsigned(4) == buffer.unsigned(4)
            text_table_size = buffer.unsigned(4)
            assert buffer.unsigned(length=4) == 1001
            assert buffer.unsigned(length=4) == 0
            index_table_encoded = buffer.bytes(buffer.unsigned(4))
            assert buffer.unsigned(length=1) == 1
            assert buffer.unsigned(length=4) == 1001
            assert buffer.unsigned(length=4) == 0
            assert text_table_size == buffer.unsigned(length=4)
            text_table_encoded = buffer.bytes(text_table_size)

        case _: raise ValueError

    index_table_decoded = apply_cipher(index_table_encoded, "decode")
    text_table_decoded  = apply_cipher(text_table_encoded, "decode")

    index_table_decoded_buffer = BufferGiver(index_table_decoded)
    decoded_string = str()

    for _ in range(len(index_table_decoded)//4):
        index_value = index_table_decoded_buffer.unsigned(4)
        text_table_entry_taker = BufferTaker()

        while (char_value := text_table_decoded[index_value]) != 0:
            text_table_entry_taker.unsigned(char_value, length=1)
            index_value += 1

        line_buffer = BufferGiver(bytes(text_table_entry_taker))

        if not tab_sal_file_format:
            match line_buffer.unsigned(length=1):
                case 1: line = "[" + str(line_buffer) + "]"
                case 2: line = str(line_buffer)
                case _: raise ValueError
        else:
            line = str(line_buffer)

        decoded_string += line.replace("\n", newline_representation) + "\n"
    return decoded_string


# ini -> cif
def encode(content: str, *, cultures_1: bool, tab_sal_file_format: bool) -> bytes:
    assert cultures_1 or not tab_sal_file_format

    text_table_taker = BufferTaker()
    index_table_taker = BufferTaker()

    for line in content.split("\n")[:-1]:
        line = line.replace(newline_representation, "\n")
        index_table_taker.unsigned(len(text_table_taker), length=4)
        if not tab_sal_file_format:
            if line.startswith("[") and line.endswith("]"):
                text_table_taker.unsigned(1, length=1)
                text_table_taker.string(line[1:-1])
            else:
                text_table_taker.unsigned(2, length=1)
                text_table_taker.string(line)
        else:
            text_table_taker.string(line)
        text_table_taker.unsigned(0, length=1)

    index_table_encoded = apply_cipher(bytes(index_table_taker), "encode")
    text_table_encoded = apply_cipher(bytes(text_table_taker), "encode")
    entries_num = len(index_table_encoded) // 4

    encoded_buffer = BufferTaker()

    if cultures_1:
        encoded_buffer.unsigned(65, length=2)
        encoded_buffer.unsigned(1, length=2)
        encoded_buffer.unsigned(entries_num, length=4)
        encoded_buffer.unsigned(entries_num, length=4)
        encoded_buffer.unsigned(10, length=4)
        encoded_buffer.unsigned(len(index_table_encoded), length=4)
        encoded_buffer.bytes(index_table_encoded)
        encoded_buffer.unsigned(1, length=2)
        encoded_buffer.unsigned(10, length=4)
        encoded_buffer.unsigned(len(text_table_encoded), length=4)
        encoded_buffer.bytes(text_table_encoded)

    else: # cultures 2
        encoded_buffer.unsigned(1021, length=2)
        encoded_buffer.unsigned(0, length=6)
        encoded_buffer.unsigned(1, length=4)
        encoded_buffer.unsigned(entries_num, length=4)
        encoded_buffer.unsigned(entries_num, length=4)
        encoded_buffer.unsigned(entries_num, length=4)
        encoded_buffer.unsigned(len(text_table_encoded), length=4)
        encoded_buffer.unsigned(1001, length=4)
        encoded_buffer.unsigned(0, length=4)
        encoded_buffer.unsigned(len(index_table_encoded), length=4)
        encoded_buffer.bytes(index_table_encoded)
        encoded_buffer.unsigned(1, length=1)
        encoded_buffer.unsigned(1001, length=4)
        encoded_buffer.unsigned(0, length=4)
        encoded_buffer.unsigned(len(text_table_encoded), length=4)
        encoded_buffer.bytes(text_table_encoded)

    return bytes(encoded_buffer)
