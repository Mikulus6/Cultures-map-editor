import numpy as np
import os
from PIL import Image
from scripts.buffer import BufferGiver, BufferTaker
from supplements.read import read
from supplements.remaptables import RemapTable, remaptable_default

filepath_default = "data_v\\ve_graphics\\gouraud\\gouraud.dat"
entry_size = 256

directory_name = "gouraud"
metadata_filename = "metadata.csv"
bitmap_filename = "bitmap.pcx"


uint32_to_float32 = lambda x: float(np.frombuffer(np.uint32(x).tobytes(), dtype=np.float32)[0])
float32_to_uint32 = lambda x: int(np.frombuffer(np.float32(x).tobytes(), dtype=np.uint32)[0])

class Gouraud:
    # Class meant for storing pre-rendered shades of colors used in game for Gouraud shading of terrain and landscapes.
    # For mor information about Gouraud shading check this article: https://en.wikipedia.org/wiki/Gouraud_shading

    def __init__(self):
        self.value1 = 0.0
        self.value2 = 0.0
        self.array = np.zeros(shape=(1, 256), dtype=np.uint8)

    def load(self, filepath: str = filepath_default):
        buffer = BufferGiver(read(filepath, mode="rb"))

        number_of_entries= 2 * buffer.unsigned(2) + 1

        self.value1 = uint32_to_float32(buffer.unsigned(4))
        self.value2 = uint32_to_float32(buffer.unsigned(4))
        self.array = np.zeros(shape=(number_of_entries, 256), dtype=np.uint8)

        for x in range(number_of_entries):
            for y, item in enumerate(buffer.iterable(entry_size)):
                self.array[x, y] = item

        assert len(buffer) == 0

    def save(self, filepath: str = filepath_default):
        buffer_taker = BufferTaker()
        assert self.array.shape[0] % 2 == 1  # There must be odd number of rows (middle row must exist).
        buffer_taker.unsigned(self.array.shape[0] // 2, length=2)
        buffer_taker.unsigned(float32_to_uint32(self.value1), length=4)
        buffer_taker.unsigned(float32_to_uint32(self.value2), length=4)

        for x in range(self.array.shape[0]):
            for y in range(entry_size):
                buffer_taker.unsigned(int(self.array[x, y]), length=1)

        with open(filepath, "wb") as file:
            file.write(bytes(buffer_taker))

    def pack(self, directory: str):
        directory_full = os.path.join(directory, directory_name)
        with open(os.path.join(directory_full, metadata_filename), "r") as file:
            self.value1, self.value2 = map(float, file.read().strip("\n").split(","))
        self.array = np.array(Image.open(os.path.join(directory_full, bitmap_filename)))

    def extract(self, directory: str, *, remaptable: RemapTable = remaptable_default):
        directory_full = os.path.join(directory, directory_name)
        os.makedirs(directory_full, exist_ok=True)
        with open(os.path.join(directory_full, metadata_filename), "w") as file:
            file.write(f"{self.value1},{self.value2}")
        image = Image.fromarray(self.array)
        image.putpalette([value for rgb in [remaptable[i] for i in range(256)] for value in rgb])
        image.save(os.path.join(directory_full, bitmap_filename))
        # In created bitmap, horizontal axis represents palette index and vertical axis represents brightness.
        # Values present there are responsible for displaying palette colors corrected by in-game light.

gouraud = Gouraud()
gouraud.load()
