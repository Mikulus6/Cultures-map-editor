from scripts.buffer import BufferGiver, BufferTaker
from typing import Literal


def run_length_decryption(sequence: bytes, *, bytes_per_entry: int) -> bytes:
    buffer_input = BufferGiver(sequence)
    buffer_output = BufferTaker()

    assert buffer_input.unsigned(1)     == 1            # noqa: E221
    assert buffer_input.string(4)[::-1] == "Xpck"       # noqa: E221
    assert int(buffer_input.string(1)) in (8, 6)        # noqa: E221
    assert buffer_input.string(3)[::-1] == "rle"        # noqa: E221
    assert buffer_input.unsigned(2)     == 0            # noqa: E221
    assert buffer_input.bytes(2)        == b"\xee\xee"  # noqa: E221

    number_of_tiles   = buffer_input.unsigned(4)  # noqa: E221
    number_of_entries = buffer_input.unsigned(4)  # noqa: E221

    assert number_of_entries + 1 == len(sequence)

    while number_of_tiles > len(buffer_output):
        bits = buffer_input.binary(1)
        flag = int(bits[0]) == 1
        head = int(bits[1:], 2)

        if flag:
            buffer_output.bytes(buffer_input.bytes(bytes_per_entry) * head)
        else:
            buffer_output.bytes(buffer_input.bytes(bytes_per_entry * head))

    assert number_of_tiles == len(buffer_output)

    return bytes(buffer_output)


def run_length_encryption(sequence: bytes, *, bytes_per_entry: int, header_digit: Literal[6, 8]) -> bytes:

    buffer_input = BufferGiver(sequence)
    buffer_output = BufferTaker()
    buffer_output_data = BufferTaker()

    buffer_output.unsigned(1, length=1)
    buffer_output.string("Xpck"[::-1])
    buffer_output.string(str(header_digit))
    buffer_output.string("rle"[::-1])
    buffer_output.unsigned(0, length=2)
    buffer_output.bytes(b"\xee\xee")
    buffer_output.unsigned(len(sequence), length=4)

    assert len(sequence) % bytes_per_entry == 0

    pre_compressed_data = []
    current_count = 1
    current_entry = buffer_input.bytes(bytes_per_entry)

    while len(buffer_input) > 0:
        new_entry = buffer_input.bytes(bytes_per_entry)
        if new_entry == current_entry and current_count < 127:
            current_count += 1
        else:
            if current_count == 1:
                if len(pre_compressed_data) != 0 and isinstance(pre_compressed_data[-1], bytes) and\
                   len(pre_compressed_data[-1]) < 127:
                    pre_compressed_data[-1] += current_entry
                else:
                    pre_compressed_data.append(current_entry)
            else:
                pre_compressed_data.append([current_count, current_entry])
            current_entry = new_entry
            current_count = 1

    pre_compressed_data.append([current_count, current_entry])

    for item in pre_compressed_data:
        if isinstance(item, bytes):
            buffer_output_data.unsigned(len(item)//bytes_per_entry, length=1)
            buffer_output_data.bytes(item)
        else:
            item_temp = bin(item[0])[2:]
            item_temp = "1" + "0" * (7 - len(item_temp)) + item_temp
            buffer_output_data.binary(item_temp)
            buffer_output_data.bytes(item[1])

    buffer_output.unsigned(len(buffer_output_data)+len(buffer_output)+3, length=4)
    buffer_output.bytes(bytes(buffer_output_data))
    return bytes(buffer_output)
