from PIL import Image
from scripts.colormap import apply_colormap_to_shorts, remove_colormap_from_shorts, ColorMap
from scripts.expansions import expand_image


def get_rgb_hue_tuple(value):
    value %= 1
    kr, kg, kb = (5 + value * 6) % 6, (3 + value * 6) % 6, (1 + value * 6) % 6
    color = (1-max((min((kr, 4 - kr, 1)), 0)),
             1-max((min((kg, 4 - kg, 1)), 0)),
             1-max((min((kb, 4 - kb, 1)), 0)))
    return tuple(map(lambda x: max(min(round(x * 255), 255), 0), color))


def bytes_to_image(sequence: bytes, filename: str, width: int, expansion_mode=None):
    image = Image.new('L', (width, len(sequence)//width))
    image.putdata(sequence)
    image = expand_image(image, expansion_mode=expansion_mode)
    image.save(filename)


def shorts_to_image(sequence: bytes, filename: str, width: int, expansion_mode=None, colormap: ColorMap = None):
    image = Image.new('RGB', (width, len(sequence)//(2*width)))

    if colormap is not None: image.putdata(apply_colormap_to_shorts(sequence, colormap))
    else: image.putdata([(byte1, byte2, 0) for byte1, byte2 in zip(sequence[::2], sequence[1::2])])

    image = expand_image(image, expansion_mode=expansion_mode)
    image.save(filename)


def bits_to_image(sequence: str, filename: str, width: int, expansion_mode=None):
    to_color = lambda x: (255, 255, 255) if x == 1 else (0, 0, 0)  # noqa: E731
    image = Image.new('RGB', (width, len(sequence)//width))
    image.putdata([to_color(int(x)) for x in sequence])  # noqa
    image = expand_image(image, expansion_mode=expansion_mode)
    image.save(filename)


def bits_difference_to_image(sequence_1, sequence_2, filename: str, width: int, expansion_mode=None):
    assert len(sequence_1) == len(sequence_2)

    image = Image.new('RGB', (width, len(sequence_1)//width))

    for index, values in list(enumerate(zip(sequence_1, sequence_2))):
        match int(values[0]), int(values[1]):
            case 0, 0: color = (0, 192, 0)  # true negative
            case 0, 1: color = (192, 0, 0)  # false negative
            case 1, 0: color = (255, 0, 0)  # false positive
            case 1, 1: color = (0, 255, 0)  # true positive
            case _: raise ValueError

        image.putpixel((index % width, index // width), color)

    image = expand_image(image, expansion_mode=expansion_mode)
    image.save(filename)


def rgb_to_image(rgb_iterable: list | tuple, filename: str, width, expansion_mode=None):
    image = Image.new('RGB', (width, len(rgb_iterable)//width))
    image.putdata(rgb_iterable)  # noqa
    image = expand_image(image, expansion_mode=expansion_mode)
    image.save(filename)


def image_to_bytes(filename: str, get_width=False):
    image = Image.open(filename)
    pixels = list(image.getdata())
    if isinstance(pixels[0], tuple):
        pixels = [x[0] for x in pixels]
    return (bytes(pixels), image.width) if get_width else bytes(pixels)


def image_to_shorts(filename: str, colormap: ColorMap = None) -> bytes:
    if colormap is not None:
        return remove_colormap_from_shorts(list(Image.open(filename).getdata()), colormap)

    shorts = []
    for r, g, b in [x[:3] for x in Image.open(filename).getdata()]:
        shorts += [r, g]
    return bytes(shorts)



def image_to_bits(filename: str):
    return ''.join(['1' if r == g == b == 255 else '0' for r, g, b in Image.open(filename).getdata()])


def image_to_rgb(filename: str) -> tuple:
    return tuple([x[:3] for x in Image.open(filename).getdata()])
