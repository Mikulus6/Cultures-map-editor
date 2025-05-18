from scripts.buffer import BufferGiver, BufferTaker
from sections.walk_sector_points import sector_width


flag_state = 1
# Value above is most likely outside of categories of derivable and visible primary map data. It seems to be a flag of
# inner gameplay state. When it is set to 0, structure of walk sector points will remain unchanged upon initializing a
# pathfinding algorithm. When it is set to 1, recalculation function of walk sector points will be called inside main
# game loop upon first usage of pathfinding algorithm. Obstructing walk sector point with building or landscape will
# cause this value to be changed to 1. Effectively, this value stores the information about walk sector points not being
# up-to-date with currect placament of landscapes and buildings. Moreover, only around 21% of all unique maps found in
# original games have this flag set to 0, which makes setting this value to 1 a statistically better choice in case of
# missing the hidden meaning beneath this boolean value.


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

    flag = buffer.unsigned(4)

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


def update_summary(map_width, map_height):

    grid_width = map_width // sector_width + (1 if map_width % sector_width != 0 else 0)
    grid_height = map_height // sector_width + (1 if map_height % sector_width != 0 else 0)

    return grid_width, grid_height, grid_width * grid_height, flag_state
