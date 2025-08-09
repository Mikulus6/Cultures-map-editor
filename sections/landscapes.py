import numpy as np
from scripts.buffer import BufferGiver, BufferTaker
from sections.run_length import run_length_decryption
from supplements.landscapedefs import landscapes_sorted


def load_landscapes_from_llan(sequence: bytes) -> dict:
    buffer = BufferGiver(sequence)

    text_entries = []
    text_entries_length = buffer.unsigned(4)

    for _ in range(text_entries_length):
        text_entries.append(buffer.string(buffer.unsigned(1)))
        assert buffer.unsigned(1) == 0

    landscapes_dict = {}
    landscapes_entries_length = buffer.unsigned(4)

    for _ in range(landscapes_entries_length):
        vertex_coordinate_x = buffer.unsigned(2)  # noqa: E221
        vertex_coordinate_y = buffer.unsigned(2)  # noqa: E221
        landscape_index     = buffer.unsigned(2)  # noqa: E221

        landscapes_dict[vertex_coordinate_x, vertex_coordinate_y] = text_entries[landscape_index]

    assert len(buffer) == 0

    return landscapes_dict


def load_landscapes_from_mobj(sequence: bytes, map_width: int) -> dict:

    # File landscapedefs.cif is necessary for loading landscapes from "mobj" section.

    map_objects = run_length_decryption(sequence, bytes_per_entry=2, from_save_file=True)
    map_height = len(map_objects) // (2 * map_width)
    map_objects_ndarray = np.frombuffer(map_objects, dtype=np.short).reshape((map_height, map_width))

    landscapes = dict()

    for y in range(map_height):
        for x in range(map_width):
            if (landscape_id := int(map_objects_ndarray[y, x])) != -1:
                try:
                    landscapes[x, y] = landscapes_sorted[landscape_id % 65536]  # Conversion to unsigned short.
                except IndexError:
                    pass  # Section "mobj" is used to store information not only about landscapes.

    return landscapes


def load_llan_from_landscapes(landscapes: dict) -> bytes:
    buffer = BufferTaker()
    buffer2 = BufferTaker()
    text_list = []

    buffer.unsigned(len(set(landscapes.values())), length=4)

    buffer2.unsigned(len(landscapes), length=4)

    for coordinates, landscape_name in landscapes.items():
        if landscape_name in text_list:
            landscape_index = text_list.index(landscape_name)
        else:
            landscape_index = len(text_list)
            text_list.append(landscape_name)

        buffer2.unsigned(coordinates[0], length=2)
        buffer2.unsigned(coordinates[1], length=2)
        buffer2.unsigned(landscape_index, length=2)

    for text_entry in text_list:
        buffer.unsigned(len(text_entry), length=1)
        buffer.string(text_entry)
        buffer.unsigned(0, length=1)

    buffer.bytes(bytes(buffer2))

    return bytes(buffer)
