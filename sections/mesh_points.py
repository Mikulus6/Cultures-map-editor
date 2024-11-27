def combine_mep(mepa, mepb):
    mep = b""
    for index in range(len(mepa)):
        mep += mepa[2 * index: 2 * index + 2]
        mep += mepb[2 * index: 2 * index + 2]
    return mep


def split_mep(mep):
    mepa = b""
    mepb = b""

    for index in range(len(mep) // 2):
        if index % 2 == 0:
            mepa += mep[2 * index: 2 * index + 2]
        else:
            mepb += mep[2 * index: 2 * index + 2]

    return mepa, mepb


def get_adjacent_mep_coordinates(coordinates, *, ignore_minor_vertices=False):
    # 'ignore_minor_vertices' should always be set to False, except for recursive case in function definitnion.
    x, y = coordinates

    if x % 2 == 0 and y % 4 == 0:    # major vertex, even row
        mepa_coordinates = [(x//2, y//2), (x//2 - 1, y//2 - 1), (x//2, y//2 - 1)]
        mepb_coordinates = [(x//2, y//2), (x//2 - 1, y//2 - 1), (x//2 - 1, y//2)]
    elif x % 2 == 1 and y % 4 == 2:  # major vertex, odd row
        mepa_coordinates = [(x//2, y//2), (x//2, y//2 - 1), (x//2 + 1, y//2 - 1)]
        mepb_coordinates = [(x//2, y//2), (x//2, y//2 - 1), (x//2 - 1, y//2)]
    elif not ignore_minor_vertices:  # minor vertex
        if y % 2 == 0: neighbours = [(x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1), (x - 1, y + 1), (x - 1, y - 1)]
        else:          neighbours = [(x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1), (x + 1, y + 1), (x + 1, y - 1)]

        mepa_coordinates_collection = []
        mepb_coordinates_collection = []

        for neighbour in neighbours:
            mepa_coordinates_temp, mepb_coordinates_temp = get_adjacent_mep_coordinates(neighbour,
                                                                                        ignore_minor_vertices=True)
            if len(mepa_coordinates_temp) + len(mepb_coordinates_temp) != 0:  # major vertex
                mepa_coordinates_collection.append(mepa_coordinates_temp)
                mepb_coordinates_collection.append(mepb_coordinates_temp)

        mepa_coordinates = [coordinates for coordinates in mepa_coordinates_collection[0] if
                            coordinates in mepa_coordinates_collection[1]]
        mepb_coordinates = [coordinates for coordinates in mepb_coordinates_collection[0] if
                            coordinates in mepb_coordinates_collection[1]]

        return mepa_coordinates, mepb_coordinates
    else:
        mepa_coordinates, mepb_coordinates = [], []

    return mepa_coordinates, mepb_coordinates
