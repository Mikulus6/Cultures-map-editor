from scripts.buffer import BufferGiver, BufferTaker


def load_summary_from_bytes(sequence: bytes) -> tuple:
    buffer = BufferGiver(sequence)

    assert len(sequence) == 28
    assert buffer.string(4)[::-1] == "smmw"
    assert buffer.unsigned(4) == 0
    assert buffer.unsigned(4) == 2

    grid_width = buffer.unsigned(4)   # noqa: E221
    grid_height = buffer.unsigned(4)  # noqa: E221
    grid_size = buffer.unsigned(4)    # noqa: E221

    assert grid_width * grid_height == grid_size

    flag = buffer.unsigned(4)  # TODO: purpose unknown

    assert flag in (0, 1)

    return grid_width, grid_height, grid_size, flag


def load_summary_to_bytes(smmw_data: list | tuple) -> bytes:
    buffer = BufferTaker()

    grid_width, grid_height, grid_size, flag = smmw_data

    assert grid_width * grid_height == grid_size
    assert flag in (0, 1)

    buffer.string("smmw"[::-1])
    buffer.unsigned(0, length=4)
    buffer.unsigned(2, length=4)

    buffer.unsigned(grid_width, length=4)
    buffer.unsigned(grid_height, length=4)
    buffer.unsigned(grid_size, length=4)
    buffer.unsigned(flag, length=4)

    return bytes(buffer)
