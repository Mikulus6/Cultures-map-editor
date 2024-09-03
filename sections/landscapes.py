from buffer import BufferGiver, BufferTaker


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
