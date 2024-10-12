from PIL import Image
from scripts.expansions import expand_image


def get_rgb_hue_tuple(value):
    value %= 1
    if 0 <= value < 1/3: color = 1, (value / 1/3), 0
    elif 1/3 <= value < 2/3: color = (1 - (value - 1/3) / (1/3)), 1, ((value - 1/3) / (1/3))
    else: color = ((value - (2/3)) / (1/3)), (1 - (value - (2/3)) / (1/3)), 1
    return tuple(map(lambda x: max(min(round(x * 255), 255), 0), color))


def bytes_to_image(sequence: bytes, filename: str, width: int, expansion_mode=None):
    image = Image.new('L', (width, len(sequence)//width))
    image.putdata(sequence)
    image = expand_image(image, expansion_mode=expansion_mode)
    image.save(filename)


def shorts_to_image(sequence: bytes, filename: str, width: int, expansion_mode=None):
    image = Image.new('RGB', (width, len(sequence)//(2*width)))
    image.putdata([(byte1, byte2, 0) for byte1, byte2 in zip(sequence[::2], sequence[1::2])])  # noqa
    image = expand_image(image, expansion_mode=expansion_mode)
    image.save(filename)


def bits_to_image(sequence: str, filename: str, width: int, expansion_mode=None):
    to_color = lambda x: (255, 255, 255) if x == 1 else (0, 0, 0)  # noqa: E731
    image = Image.new('RGB', (width, len(sequence)//width))
    image.putdata([to_color(int(x)) for x in sequence])  # noqa
    image = expand_image(image, expansion_mode=expansion_mode)
    image.save(filename)


def rgb_to_image(rgb_iterable: list | tuple, filename: str, width, expansion_mode=None):
    image = Image.new('RGB', (width, len(rgb_iterable)//width))
    image.putdata(rgb_iterable)  # noqa
    image = expand_image(image, expansion_mode=expansion_mode)
    image.save(filename)


def image_to_bytes(filename: str):
    pixels = list(Image.open(filename).getdata())
    if isinstance(pixels[0], tuple):
        pixels = [x[0] for x in pixels]
    return bytes(pixels)


def image_to_shorts(filename: str) -> bytes:
    shorts = []
    for r, g, b in [x[:3] for x in Image.open(filename).getdata()]:
        shorts += [r, g]
    return bytes(shorts)


def image_to_bits(filename: str):
    return ''.join(['1' if r == g == b == 255 else '0' for r, g, b in Image.open(filename).getdata()])


def image_to_rgb(filename: str) -> tuple:
    return tuple([x[:3] for x in Image.open(filename).getdata()])
