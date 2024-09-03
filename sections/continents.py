from buffer import BufferGiver, BufferTaker


def load_continents_from_xcot(sequence: bytes) -> list:
    buffer = BufferGiver(sequence)

    continents = list()

    assert buffer.unsigned(4) == 1
    number_of_continents = buffer.unsigned(4)

    for _ in range(number_of_continents):
        continent_type = buffer.signed(1)
        assert buffer.unsigned(3) == 0

        if continent_type == -1:
            buffer.skip(12)
            continue

        elif continent_type in (0, 1):
            corner_start_x = buffer.unsigned(2)
            corner_start_y = buffer.unsigned(2)
            continent_size = buffer.unsigned(8)

            continents.append((continent_type, (corner_start_x, corner_start_y), continent_size))

    return continents


def load_xcot_from_continents(continents: list) -> bytes:
    buffer = BufferTaker()
    buffer.unsigned(1, length=4)
    buffer.unsigned(len(continents), length=4)

    for continent in continents:
        continent_type, continent_coordinates, continent_size = continent
        buffer.signed(continent_type, length=1)
        buffer.unsigned(0, length=3)

        if continent_type == -1:
            buffer.unsigned(0, length=12)

        elif continent_type in (0, 1):
            buffer.unsigned(continent_coordinates[0], length=2)
            buffer.unsigned(continent_coordinates[1], length=2)
            buffer.unsigned(continent_size, length=8)

        else:
            raise ValueError

    return bytes(buffer)
