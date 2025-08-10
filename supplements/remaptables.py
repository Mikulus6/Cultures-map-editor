from io import BytesIO
import os
import numpy as np
from PIL import Image
from scripts.buffer import BufferGiver, BufferTaker, data_encoding
from scripts.colormap import ColorMap
from scripts.data_loader import load_ini_as_dict
from supplements.read import read

name_max_length = 30

remaptable_defalut_path = "data_v\\gg_system\\palette.pcx"
remaptables_cdf_path = "data_v\\ve_graphics\\remaptables\\remaptables.cdf"
remaptables_cif_path = "data_v\\ve_graphics\\remaptables\\remaptables.cif"

class RemapTable:
    bitmap_shape_default = (16, 16)

    def __init__(self):
        self.bitmap = np.zeros(shape=self.__class__.bitmap_shape_default, dtype=np.ubyte)
        self.palette = ColorMap()

    def load(self, bytes_obj):
        buffer = BufferGiver(bytes_obj)

        assert buffer.unsigned(length=4) == 55
        self.bitmap = np.array(buffer.iterable(length=256), dtype=np.ubyte).reshape(self.__class__.bitmap_shape_default)
        assert buffer.unsigned(length=4) == 50

        palette_buffer = BufferGiver(buffer.bytes(length=1024))
        self.palette = ColorMap()
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

    def pack(self, filepath, *, bitmap_shape=None):
        with Image.open(BytesIO(read(filepath, mode="rb"))) as img:
            assert img.mode == 'P'
            self.bitmap = np.array(img, dtype=np.ubyte).reshape(self.__class__.bitmap_shape_default
                                                                if bitmap_shape is None else bitmap_shape)
            self.palette = {np.ubyte(key): tuple(img.getpalette()[key*3: (key+1)*3]) for key in range(256)}

    def extract(self, filepath):
        pil_image = Image.fromarray(self.bitmap).convert("P")
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

        self.data = dict()  # key: Name, values: (FileName, RemapTable)
        self.meta = load_ini_as_dict(cif_path, allowed_section_names=("RemapTable",), entries_duplicated=tuple(),
                                     global_key=lambda x: x["Name"], merge_duplicates=False)

        self.meta_16 = load_ini_as_dict(cif_path, allowed_section_names=("RemapTable16",), entries_duplicated=tuple(),
                                        global_key=lambda x: x["Name"], merge_duplicates=False)

    def load(self, cdf_path: str = remaptables_cdf_path):

        if os.path.isfile(cdf_path):

            buffer = BufferGiver(read(cdf_path, mode="rb"))

            for _ in range(buffer.unsigned(4)):
                name_raw = buffer.bytes(length=name_max_length)
                name_length = name_raw.find(0)

                if name_length == -1:
                    name_length = name_max_length

                name = str(name_raw[:name_length], encoding=data_encoding)

                try:
                    filename = self.meta[name]["FileName"]
                except KeyError:
                    buffer.bytes(length=1288)
                    continue

                remaptable = RemapTable()
                remaptable.load(buffer.bytes(length=1288))
                self.data[name.lower()] = {"FileName": filename, "RemapTable": remaptable}

                # RemapTable16 data stored in *.cdf file is redundant to RemapTable data stored in the same file and
                # additional metadata stored in *.cif file. It is suggested to not keep this data separately in memory.

        if not self.is_loaded:
            # This is backup loading procedure in case not all remaptables are in *.cdf file.

            base_directory = os.path.dirname(cdf_path)

            for meta_key, meta_values in self.meta.items():
                if meta_key.lower() in self.data.keys():
                    continue

                name = meta_values["Name"]
                filename = meta_values["FileName"]

                remaptable = RemapTable()
                remaptable.pack(os.path.join(base_directory, filename))
                self.data[name.lower()] = {"FileName": filename, "RemapTable": remaptable}

        if not self.is_loaded:
            raise FileNotFoundError

    def reload_fix(self):
        if not self.is_loaded:
            self.load()
        if not self.is_loaded:
            raise FileNotFoundError

    def save(self, cdf_path: str = remaptables_cdf_path):
        os.makedirs(os.path.dirname(cdf_path), exist_ok=True)
        with open(cdf_path, "wb") as file:
            file.write(bytes(self))

    def pack(self, directory: str = os.path.dirname(remaptables_cdf_path)):
        for name, meta in self.meta.items():
            filename = meta["FileName"]
            remaptable = RemapTable()
            remaptable.pack(os.path.join(directory, filename))
            self.data[name.lower()] = {"FileName": filename, "RemapTable": remaptable}

    def extract(self, directory: str = os.path.dirname(remaptables_cdf_path)):
        for data in self.data.values():
            data["RemapTable"].extract(os.path.join(directory, data["FileName"]))

    def clear(self):
        self.data.clear()

    @property
    def is_loaded(self):
        return len(self.data) == len(self.meta)

    def __bytes__(self):
        buffer_taker = BufferTaker()
        buffer_taker.unsigned(len(self.meta), length=4)

        sorted_remaptable_names = []
        for name, meta in self.meta.items():

            assert len(name) <= name_max_length
            buffer_taker.string(name)
            buffer_taker.iterable([0] * (name_max_length - len(name)))
            sorted_remaptable_names.append(name)

            remaptable = self.data[name.lower()]["RemapTable"]
            buffer_taker.bytes(remaptable.save())

        buffer_taker.unsigned(len(self.meta_16), length=4)

        for name, meta in self.meta_16.items():
            assert len(name) <= name_max_length
            buffer_taker.string(name)
            buffer_taker.iterable([0] * (name_max_length - len(name)))

            remaptable16_meta = meta["RemapTable"]
            buffer_taker.unsigned(sorted_remaptable_names.index(remaptable16_meta[0]), length=2)
            buffer_taker.unsigned(remaptable16_meta[1], length=2)

        return bytes(buffer_taker)

    def __getitem__(self, item):
        return self.data[item.lower()]["RemapTable"]

    def __setitem__(self, key, value):
        if isinstance(value, RemapTable):
            self.data[key.lower()]["RemapTable"] = value
        elif isinstance(value, np.ndarray):
            assert value.shape == RemapTable.bitmap_shape_default and value.dtype == np.ubyte
            self.data[key.lower()]["RemapTable"].bitmap = value
        elif isinstance(value, ColorMap):
            self.data[key.lower()]["RemapTable"].palette = value
        else:
            raise TypeError

    def __iter__(self):
        yield from [value["RemapTable"] for value in self.data.values()]

    def __len__(self):
        assert (length := len(self.meta)) == len(self.data)
        return length


def load_remaptable_default(path: str = remaptable_defalut_path):
    remaptable_default_local = RemapTable()
    remaptable_default_local.pack(path, bitmap_shape=(4, 4))
    return remaptable_default_local

remaptable_default = RemapTable()

try:
    remaptable_default = load_remaptable_default()

    remaptables = RemapTables()
    remaptables.load()

except FileNotFoundError:
    pass  # This will yield further errors if editor is being launched, but for other compilable scripts it removes
          # dependency from game files while also making it possible to use remaptables. Hence, making it more portable.

remaptable_direct = RemapTable()
remaptable_direct.palette = ColorMap({x : (x, x, x) for x in range(256)})
