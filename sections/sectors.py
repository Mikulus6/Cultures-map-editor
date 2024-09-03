from buffer import BufferGiver, BufferTaker
from sections.summary import load_summary_from_bytes, load_summary_to_bytes


def load_sectors_from_xsec(sequence: bytes) -> (list, list):
    buffer = BufferGiver(sequence)

    sectors = []

    smmw_data = load_summary_from_bytes(buffer.bytes(28))

    assert buffer.unsigned(16) == 0

    for _ in range(smmw_data[2]):
        sector_type = buffer.unsigned(2)

        assert sector_type in (0, 1)

        sector_value = buffer.unsigned(1)  # TODO: purpose unknown
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
        buffer.unsigned(sector_value, length=1)
        buffer.unsigned(mco2_array[coordintes[0] + map_width * coordintes[1]], length=1)
        buffer.unsigned(coordintes[0], length=2)
        buffer.unsigned(coordintes[1], length=2)

    return bytes(buffer)
