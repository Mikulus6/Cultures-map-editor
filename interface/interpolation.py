
def get_data_interpolated(coordinates, map_size: [int, int], map_section_bytes: bytes):
    x, y = coordinates

    x %= map_size[0]
    y %= map_size[1]

    if (x % 2 == 0 and y % 4 == 0) or (x % 2 == 1 and y % 4 == 2):
        return map_section_bytes[y * map_size[0] // 4 + x // 2]  # do not interpolate

    elif (x % 2 == 1 and y % 4 == 0) or (x % 2 == 0 and y % 4 == 2):
        vertices = [x - 1, y], [x + 1, y]
    elif (x % 2 == 0 and y % 4 == 1) or (x % 2 == 1 and y % 4 == 3):
        vertices = [x, y - 1], [x + 1, y + 1]
    elif (x % 2 == 1 and y % 4 == 1) or (x % 2 == 0 and y % 4 == 3):
        vertices = [x + 1, y - 1], [x, y + 1]

    else:
        raise IndexError  # this case should be unobtainable

    vertices = [[value // 2 % bound for value, bound in zip(vertex, (map_size[0]  // 2, map_size[1] // 2))]
                for vertex in vertices]

    return (map_section_bytes[vertices[0][1] * map_size[0] // 2 + vertices[0][0]] +
            map_section_bytes[vertices[1][1] * map_size[1] // 2 + vertices[1][0]]) // 2
