import numpy as np
from scripts.buffer import BufferGiver, BufferTaker
_bits_per_byte = 8


def sequence_to_flags(sequence: bytes, *, bytes_per_entry=1) -> list[str]:
    assert len(sequence) % bytes_per_entry == 0
    buffer = BufferGiver(sequence)
    flags_list = [""] * (_bits_per_byte * bytes_per_entry)
    for _ in range(len(sequence)//bytes_per_entry):
        for counter, bit_value in enumerate(buffer.binary(bytes_per_entry)):
            flags_list[counter] += bit_value
    return flags_list


def flags_to_sequence(flags: list[str], *, bytes_per_entry=1) -> bytes:
    buffer = BufferTaker()

    for counter in range(len(flags[0])):
        buffer.binary(''.join([flags[x][counter] for x in range(_bits_per_byte * bytes_per_entry)]))

    return bytes(buffer)


def bool_ndarray_to_flag(bool_ndarray: np.ndarray):
    assert bool_ndarray.dtype == np.bool_
    flat_bool_array = bool_ndarray.flatten()
    return "".join(['1' if val else '0' for val in flat_bool_array])


def flag_to_bool_ndarray(flag, *, map_width):
    return np.array([x == "1" for x in flag], dtype=np.bool_).reshape((len(flag) // map_width, map_width))
