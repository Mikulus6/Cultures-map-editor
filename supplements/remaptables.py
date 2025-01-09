from scripts.colormap import ColorMap
from scripts.data_loader import data_encoding
from scripts.buffer import BufferGiver
from supplements.library import Library

remaptables_path = "data_v\\ve_graphics\\remaptables\\remaptables.cdf"

def get_remaptables_bytes():
    try:
        with open(remaptables_path, "rb") as file:
            return file.read()
    except FileNotFoundError:
        # Loading library might not be necessary if different part of code already did it.
        # This code can be further optimized for reduction of initialization time .
        library = Library().load("data_l\\data_v.lib", cultures_1=True)
        return library[remaptables_path]

def load_remaptables():
    remaptables_dict = dict()
    buffer = BufferGiver(get_remaptables_bytes())

    for _ in range(buffer.unsigned(4)):
        name_raw = buffer.bytes(length=30)
        name = str(name_raw[:name_raw.find(0)], encoding=data_encoding)
        assert buffer.unsigned(length=4) == 55
        buffer.skip(256)
        assert buffer.unsigned(length=4) == 50

        palette_buffer = BufferGiver(buffer.bytes(length=1024))
        colormap = ColorMap(dict())
        for palette_index in range(256):
            value = palette_buffer.iterable(length=4)
            colormap[palette_index] = tuple(value[:3][::-1])  # Channels order is switched.
            assert value[3] == 0 # unused channel

        remaptables_dict[name] = colormap

    return remaptables_dict

remaptables = load_remaptables()
