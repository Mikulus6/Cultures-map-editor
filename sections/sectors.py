import numpy as np
from scripts.buffer import BufferGiver, BufferTaker
from sections.summary import load_summary_from_bytes, load_summary_to_bytes


sector_width = 20


def load_sectors_from_xsec(sequence: bytes) -> (list, list):
    buffer = BufferGiver(sequence)

    sectors = []

    smmw_data = load_summary_from_bytes(buffer.bytes(28))

    assert buffer.unsigned(16) == 0

    for _ in range(smmw_data[2]):
        sector_type = buffer.unsigned(2)

        assert sector_type in (0, 1)

        sector_value = buffer.binary(1)
        buffer.skip(1)  # mco2 vertex duplicate

        coordinate_x = buffer.unsigned(2)
        coordinate_y = buffer.unsigned(2)

        sectors.append([sector_type, sector_value, (coordinate_x, coordinate_y)])

    return sectors, smmw_data


def load_xsec_from_sectors(sectors: list, smmw_data: list, mco2_array: bytes, map_width: int) -> bytes:
    buffer = BufferTaker()

    buffer.bytes(load_summary_to_bytes(smmw_data))
    buffer.unsigned(0, length=16)

    for sector in sectors:
        sector_type, sector_value, coordintes = sector

        assert sector_type in (0, 1)

        buffer.unsigned(sector_type, length=2)
        buffer.binary(sector_value)
        buffer.unsigned(mco2_array[coordintes[0] + map_width * coordintes[1]], length=1)
        buffer.unsigned(coordintes[0], length=2)
        buffer.unsigned(coordintes[1], length=2)

    return bytes(buffer)


def check_sectors_coherency(mco2: bytes, sectors: list, map_width: int, map_height: int):

    mco2_ndarray = np.frombuffer(mco2, dtype=np.ubyte).reshape((map_height, map_width))
    sectors_width = map_width // sector_width + (1 if map_width % sector_width != 0 else 0)
    sectors_height = map_height // sector_width + (1 if map_height % sector_width != 0 else 0)

    try:
        for index_value, sector in enumerate(sectors):
            sector_type, sector_value, coordintes = sector

            if sector_type == 0:
                assert sector_value == "00000000"

            sector_x, sector_y = index_value % sectors_width, index_value // sectors_width

            neighbours = [[sector_x + 1, sector_y - 1],
                          [sector_x, sector_y - 1],
                          [sector_x - 1, sector_y - 1],
                          [sector_x - 1, sector_y],
                          [sector_x - 1, sector_y + 1],
                          [sector_x, sector_y + 1],
                          [sector_x + 1, sector_y + 1],
                          [sector_x + 1, sector_y]]

            for neighbour_relative_index, neighbour in enumerate(neighbours):
                neighbour_sector_index = neighbour[1] * sectors_width + neighbour[0]

                if not(0 <= neighbour[0] < sectors_width and 0 <= neighbour[1] < sectors_height):
                    continue

                neighbour_type, neighbour_value, neighbour_coordinates = sectors[neighbour_sector_index]

                if neighbour_type == 0:
                    assert neighbour_value == "00000000"
                assert sector_value[neighbour_relative_index] == neighbour_value[(neighbour_relative_index + 4) % 8]

                if int(sector_value[neighbour_relative_index]) == 1:
                    assert mco2_ndarray[*coordintes[::-1]] == mco2_ndarray[*neighbour_coordinates[::-1]]

    except AssertionError:
        return False
    return True
