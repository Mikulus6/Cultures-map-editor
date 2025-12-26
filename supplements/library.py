import os
from scripts.buffer import BufferGiver, BufferTaker

separator = "\\"


class Library(dict):
    def __init__(self):
        super().__init__()

    def load(self, filename: str, *, cultures_1: bool):
        assert filename.endswith(".lib") or (filename.endswith(".c2m") and not cultures_1)

        with open(filename, "rb") as file:
            bytes_obj = file.read()

        if cultures_1: self._extract_content_cultures_1(bytes_obj)
        else:          self._extract_content_cultures_2(bytes_obj)

    def save(self, filename: str, *, cultures_1: bool):
        assert filename.endswith(".lib") or (filename.endswith(".c2m") and not cultures_1)

        if cultures_1: bytes_obj = self._pack_content_cultures_1()
        else:          bytes_obj = self._pack_content_cultures_2()

        with open(filename, "wb") as file:
            file.write(bytes_obj)

    def pack(self, directory: str):
        for root, _, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                with open(filepath, "rb") as file:
                    self[filepath[len(os.path.abspath(os.path.join(directory, os.pardir))) + 1:].replace(os.sep,
                                                                                                 separator)] =\
                                                                                                 file.read()

    def extract(self, directory: str):
        for filepath, content in self.items():
            filename_new = os.path.join(directory, filepath)
            directory_new = os.path.dirname(filename_new)
            os.makedirs(directory_new, exist_ok=True)
            with open(filename_new, "wb") as file:
                file.write(content)

    def _extract_content_cultures_1(self, bytes_obj):
        buffer = BufferGiver(bytes_obj)
        assert buffer.unsigned(4) == 1

        for _ in range(buffer.unsigned(4)):
            filepath = buffer.string(buffer.unsigned(2))
            offset = buffer.unsigned(4)
            size = buffer.unsigned(4)
            self[filepath] = bytes_obj[offset:][:size]

    def _extract_content_cultures_2(self, bytes_obj):
        buffer = BufferGiver(bytes_obj)

        assert buffer.unsigned(4) == 1

        number_of_directories = buffer.unsigned(4)
        number_of_files = buffer.unsigned(4)

        assert buffer.unsigned(4) == 1
        assert buffer.unsigned(4) == 92
        assert buffer.unsigned(1) == 0

        for _ in range(number_of_directories - 1):
            path_length = buffer.unsigned(4)
            filepath = buffer.string(path_length)
            scope = buffer.unsigned(4)
            assert filepath.count(separator) == scope

        for _ in range(number_of_files):
            path_length = buffer.unsigned(4)
            filepath = buffer.string(path_length)
            offset = buffer.unsigned(4)
            size = buffer.unsigned(4)

            self[filepath] = bytes_obj[offset:][:size]

    def _pack_content_cultures_1(self) -> bytes:
        taker_head = BufferTaker()
        taker_body = BufferTaker()

        taker_head.unsigned(1, length=4)
        taker_head.unsigned(len(self), length=4)

        header_length = sum(map(len, self.keys())) + 10 * len(self) + 8

        for filepath, content in self.items():

            taker_head.unsigned(len(filepath), length=2)
            taker_head.string(filepath)
            taker_head.unsigned(header_length + len(taker_body), length=4)
            taker_head.unsigned(len(content), length=4)
            taker_body.bytes(content)

        return bytes(taker_head) + bytes(taker_body)

    def _pack_content_cultures_2(self) -> bytes:
        taker_head = BufferTaker()
        taker_body = BufferTaker()

        directories = set()
        for filepath in self.keys():
            current_path = os.path.dirname(filepath)
            while len(current_path) > 0:
                directories.add(current_path.replace(os.sep, separator) + separator)
                current_path = os.path.dirname(current_path)
        directories = sorted(directories, key=lambda path: path.count(separator))

        header_length = sum(map(len, list(self.keys()) + directories)) + len(directories) * 8 + len(self) * 12 + 21

        taker_head.unsigned(1, length=4)
        taker_head.unsigned(len(directories) + 1, length=4)
        taker_head.unsigned(len(self), length=4)
        taker_head.unsigned(1, length=4)
        taker_head.unsigned(92, length=4)
        taker_head.unsigned(0, length=1)

        for directory_name in directories:
            taker_head.unsigned(len(directory_name), length=4)
            taker_head.string(directory_name)
            taker_head.unsigned(directory_name.count(separator), length=4)

        for filepath, content in self.items():
            taker_head.unsigned(len(filepath), length=4)
            taker_head.string(filepath)
            taker_head.unsigned(header_length + len(taker_body), length=4)
            taker_head.unsigned(len(content), length=4)
            taker_body.bytes(content)

        return bytes(taker_head) + bytes(taker_body)
