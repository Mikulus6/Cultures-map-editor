import os
import numpy as np
from PIL import Image
from scripts.buffer import BufferGiver, BufferTaker, data_encoding
from scripts.colormap import ColorMap
from scripts.data_loader import load_ini_as_dict

remaptables_cdf_path = "data_v\\ve_graphics\\remaptables\\remaptables.cdf"
remaptables_cif_path = "data_v\\ve_graphics\\remaptables\\remaptables.cif"

class RemapTable:
    bitmap_shape = (16, 16)

    def __init__(self):
        self.bitmap = np.zeros(shape=self.__class__.bitmap_shape, dtype=np.ubyte)
        self.palette = ColorMap(dict())

    def load(self, bytes_obj):
        buffer = BufferGiver(bytes_obj)

        assert buffer.unsigned(length=4) == 55
        self.bitmap = np.array(buffer.iterable(length=256), dtype=np.ubyte).reshape(self.__class__.bitmap_shape)
        assert buffer.unsigned(length=4) == 50

        palette_buffer = BufferGiver(buffer.bytes(length=1024))
        self.palette = ColorMap(dict())
        for palette_index in range(256):
            value = palette_buffer.iterable(length=4)
            self.palette[palette_index] = tuple(value[:3][::-1])  # Channels: blue, green, red
            assert value[3] == 0

    def save(self) -> bytes:
        buffer_taker = BufferTaker()
        buffer_taker.unsigned(55, length=4)
        buffer_taker.bytes(self.bitmap.tobytes())
        buffer_taker.unsigned(50, length=4)
        for palette_index in range(256):
            buffer_taker.iterable((*self.palette[palette_index][2::-1], 0))  # Channels: blue, green, red
        return bytes(buffer_taker)

    def pack(self, filepath):
        with Image.open(filepath) as img:
            assert img.mode == 'P'
            self.bitmap = np.array(img, dtype=np.ubyte).reshape(self.__class__.bitmap_shape)
            self.palette = {np.ubyte(key): tuple(img.getpalette()[key*3: (key+1)*3]) for key in range(256)}

    def extract(self, filepath):
        pil_image = Image.fromarray(self.bitmap, mode='P')
        palette_list = [0] * 768
        for key, (r, g, b) in self.palette.items():
            palette_list[key*3: (key+1)*3] = [r, g, b]
        pil_image.putpalette(palette_list)

        if os.path.dirname(filepath) != "":
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

        pil_image.save(filepath, format='pcx')

    def __bytes__(self):
        return self.save()

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return np.all(self.bitmap == other.bitmap) and self.palette == other.palette

    def __getitem__(self, item):
        return self.palette[item]

    def __setitem__(self, key, value):
        assert key in range(256)
        assert isinstance(value, tuple) and all(map(lambda x: x in range(256), value))
        self.palette[key] = value


class RemapTables:

    def __init__(self, cif_path: str = remaptables_cif_path):

        self.remaptables_data = dict()  # key: Name, values: (FileName, RemapTable)
        self.remaptables_meta = load_ini_as_dict(cif_path, allowed_section_names=("RemapTable",),
                                                 entries_duplicated=tuple(), global_key=lambda x: x["Name"],
                                                 merge_duplicates=False)

        self.remaptables16_meta = load_ini_as_dict(cif_path, allowed_section_names=("RemapTable16",),
                                                   entries_duplicated=tuple(), global_key=lambda x: x["Name"],
                                                   merge_duplicates=False)

    def load(self, cdf_path: str = remaptables_cdf_path):
        with open(cdf_path, "rb") as file:
            buffer = BufferGiver(file.read())

        for _ in range(buffer.unsigned(4)):
            name_raw = buffer.bytes(length=30)
            name_length = name_raw.find(0)

            if name_length == -1:
                name_length = 30

            name = str(name_raw[:name_length], encoding=data_encoding)
            filename = self.remaptables_meta[name]["FileName"]

            remaptable = RemapTable()
            remaptable.load(buffer.bytes(length=1288))
            self.remaptables_data[name.lower()] = {"FileName": filename, "RemapTable": remaptable}

        # RemapTable16 data stored in *.cdf file is redundant to RemapTable data stored in same file and additional
        # metadata stored in *.cif file. It is suggested to not keep this data separately in memory.

    def save(self, cdf_path: str = remaptables_cdf_path):
        with open(cdf_path, "wb") as file:
            file.write(bytes(self))

    def pack(self, directory: str = os.path.dirname(remaptables_cdf_path)):
        for name, meta in self.remaptables_meta.items():
            filename = meta["FileName"]
            remaptable = RemapTable()
            remaptable.pack(os.path.join(directory, filename))
            self.remaptables_data[name.lower()] = {"FileName": filename, "RemapTable": remaptable}

    def extract(self, directory: str = os.path.dirname(remaptables_cdf_path)):
        for data in self.remaptables_data.values():
            data["RemapTable"].extract(os.path.join(directory, data["FileName"]))

    def clear(self):
        self.remaptables_data.clear()

    def __bytes__(self):
        buffer_taker = BufferTaker()
        buffer_taker.unsigned(len(self.remaptables_meta), length=4)

        sorted_remaptable_names = []
        for name, meta in self.remaptables_meta.items():

            assert len(name) <= 30
            buffer_taker.string(name)
            buffer_taker.iterable([0] * (30 - len(name)))
            sorted_remaptable_names.append(name)

            remaptable = self.remaptables_data[name.lower()]["RemapTable"]
            buffer_taker.bytes(remaptable.save())

        buffer_taker.unsigned(len(self.remaptables16_meta), length=4)

        for name, meta in self.remaptables16_meta.items():
            assert len(name) <= 30
            buffer_taker.string(name)
            buffer_taker.iterable([0] * (30 - len(name)))

            remaptable16_meta = meta["RemapTable"]
            buffer_taker.unsigned(sorted_remaptable_names.index(remaptable16_meta[0]), length=2)
            buffer_taker.unsigned(remaptable16_meta[1], length=2)

        return bytes(buffer_taker)

    def __getitem__(self, item):
        return self.remaptables_data[item.lower()]["RemapTable"]


remaptables = RemapTables()
remaptables.load()
