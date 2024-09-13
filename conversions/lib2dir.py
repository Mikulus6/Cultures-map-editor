import itertools
import os

separator = "\\"

nexts = lambda iterable, var: bytes(list(itertools.islice(iterable, var)))  # noqa


def bytes_buffer(bytes_obj):
    for byte in bytes_obj:
        yield byte


def subcontent_generator(directory, basepath=None):

    directory = str(os.path.normpath(directory))

    if basepath is None:
        basepath = len(directory[:directory.rfind(separator)+1])

    dirname = directory[basepath:]+separator
    yield directory[basepath:]+separator, dirname.count(separator)

    for item in os.listdir(directory):
        content = directory + separator + item
        if os.path.isdir(content):
            content += separator
            yield from subcontent_generator(content, basepath=basepath)
        else:  # isfile
            filename = content[basepath:]
            with open(content, "rb") as file:
                file_data = file.read()
            yield filename, file_data


def lib_extract_content_cultures1(bytes_obj: bytes) -> dict:
    buffer = bytes_buffer(bytes_obj)

    dict_obj = dict()

    bytes_unknown0 = nexts(buffer, 4)
    assert bytes_unknown0 == b"\x01\x00\x00\x00"

    bytes_number_of_entries = nexts(buffer, 4)

    number_of_entries = int.from_bytes(bytes_number_of_entries, byteorder="little")

    for _ in range(number_of_entries):
        bytes_path_length = nexts(buffer, 2)

        path_length = int.from_bytes(bytes_path_length, byteorder="little")

        bytes_filepath = nexts(buffer, path_length)
        bytes_offset = nexts(buffer, 4)
        bytes_size = nexts(buffer, 4)

        filepath = str(bytes_filepath, encoding="cp1250")
        offset = int.from_bytes(bytes_offset, byteorder="little")
        size = int.from_bytes(bytes_size, byteorder="little")

        dict_obj[filepath] = (offset, size)
    del buffer

    for filepath, data_tuple in dict_obj.items():
        offset, size = data_tuple
        dict_obj[filepath] = bytes_obj[offset:][:size]

    return dict_obj


def lib_extract_content_cultures2(bytes_obj: bytes) -> dict:
    buffer = bytes_buffer(bytes_obj)

    dict_obj = dict()

    bytes_unknown0 = nexts(buffer, 4)
    bytes_first_file_index = nexts(buffer, 4)
    bytes_number_of_files = nexts(buffer, 4)
    bytes_unknown1 = nexts(buffer, 4)
    bytes_unknown2 = nexts(buffer, 4)
    bytes_unknown3 = nexts(buffer, 1)

    assert bytes_unknown0 == b"\x01\x00\x00\x00"
    assert bytes_unknown1 == b"\x01\x00\x00\x00"
    assert bytes_unknown2 == b"\x5c\x00\x00\x00"
    assert bytes_unknown3 == b"\x00"

    first_file_index = int.from_bytes(bytes_first_file_index, byteorder="little")
    number_of_files = int.from_bytes(bytes_number_of_files, byteorder="little")

    for _ in range(first_file_index-1):
        bytes_path_length = nexts(buffer, 4)

        path_length = int.from_bytes(bytes_path_length, byteorder="little")

        bytes_filepath = nexts(buffer, path_length)
        bytes_scope = nexts(buffer, 4)

        filepath = str(bytes_filepath, encoding="cp1250")
        scope = int.from_bytes(bytes_scope, byteorder="little")

        assert filepath.count(separator) == scope

        dict_obj[filepath] = scope

    for _ in range(number_of_files):
        bytes_path_length = nexts(buffer, 4)

        path_length = int.from_bytes(bytes_path_length, byteorder="little")

        bytes_filepath = nexts(buffer, path_length)
        bytes_offset = nexts(buffer, 4)
        bytes_size = nexts(buffer, 4)

        filepath = str(bytes_filepath, encoding="cp1250")
        offset = int.from_bytes(bytes_offset, byteorder="little")
        size = int.from_bytes(bytes_size, byteorder="little")

        dict_obj[filepath] = (offset, size)

    del buffer

    for filepath, data_tuple in dict_obj.items():
        if isinstance(data_tuple, tuple):
            offset, size = data_tuple
            dict_obj[filepath] = bytes_obj[offset:][:size]

    return dict_obj


def lib_extract_content(bytes_obj: bytes, cultures1: bool) -> dict:
    if cultures1:
        dict_obj = lib_extract_content_cultures1(bytes_obj)
    else:
        dict_obj = lib_extract_content_cultures2(bytes_obj)
    return dict_obj


def lib_extract(filename_input, directory_output, cultures1: bool = False):

    with open(filename_input, "rb") as file:
        dict_obj = lib_extract_content(file.read(), cultures1)

    for filename, value in dict_obj.items():

        filename = os.path.normpath(filename)
        filename_sub = os.path.join(directory_output, filename)
        directory = os.path.dirname(filename_sub)
        os.makedirs(directory, exist_ok=True)

        if isinstance(value, bytes):
            with open(filename_sub, "wb") as file:
                file.write(value)


def lib_archive_content_cultures1(dict_obj: dict) -> bytes:
    dict_obj = {key: value for key, value in dict_obj.items() if isinstance(value, bytes)}
    bytes_data = b""
    bytes_header_data = b""
    header_length = 0

    for filepath, content in dict_obj.items():
        header_length += len(filepath) + 10
        dict_obj[filepath] = (len(bytes_data), len(content))  # noqa
        bytes_data += content

    number_of_entries = len(dict_obj)
    bytes_number_of_entries = int.to_bytes(number_of_entries, length=4, byteorder="little")

    bytes_header_data += b"\x01\x00\x00\x00" + bytes_number_of_entries
    header_length += 8

    for filepath, header_data in dict_obj.items():
        offset, size = header_data
        offset += header_length
        bytes_header_data += int.to_bytes(len(filepath), length=2, byteorder="little")
        bytes_header_data += bytes(filepath, encoding="cp1250")
        bytes_header_data += int.to_bytes(offset, length=4, byteorder="little")
        bytes_header_data += int.to_bytes(size, length=4, byteorder="little")

    assert len(bytes_header_data) == header_length

    return bytes_header_data + bytes_data


def lib_archive_content_cultures2(dict_obj: dict) -> bytes:
    dict_directories_obj = {key: value for key, value in dict_obj.items() if isinstance(value, int)}
    dict_files_obj = {key: value for key, value in dict_obj.items() if isinstance(value, bytes)}

    first_file_index = len(dict_directories_obj) + 1
    number_of_files = len(dict_files_obj)

    bytes_data = b""
    header_length = 0

    for filepath, content in dict_files_obj.items():
        header_length += len(filepath) + 12
        dict_files_obj[filepath] = (len(bytes_data), len(content))  # noqa
        bytes_data += content

    bytes_header_data = b"\x01\x00\x00\x00" + \
                        int.to_bytes(first_file_index, length=4, byteorder="little") + \
                        int.to_bytes(number_of_files, length=4, byteorder="little") + \
                        b"\x01\x00\x00\x00\x5c\x00\x00\x00\x00"

    for directory_name, scope in dict_directories_obj.items():
        bytes_header_data += int.to_bytes(len(directory_name), length=4, byteorder="little")
        bytes_header_data += bytes(directory_name, encoding="cp1250")
        bytes_header_data += int.to_bytes(scope, length=4, byteorder="little")

    header_length += len(bytes_header_data)

    for filepath, header_data in dict_files_obj.items():
        offset, size = header_data
        offset += header_length
        bytes_header_data += int.to_bytes(len(filepath), length=4, byteorder="little")
        bytes_header_data += bytes(filepath, encoding="cp1250")
        bytes_header_data += int.to_bytes(offset, length=4, byteorder="little")
        bytes_header_data += int.to_bytes(size, length=4, byteorder="little")

    assert len(bytes_header_data) == header_length

    return bytes_header_data + bytes_data


def lib_archive_content(dict_obj: dict, cultures1: bool) -> bytes:
    if cultures1:
        bytes_obj = lib_archive_content_cultures1(dict_obj)
    else:
        bytes_obj = lib_archive_content_cultures2(dict_obj)
    return bytes_obj


def lib_archive(directory_input, filename_output, cultures1: bool = False):

    dict_obj = {key: value for key, value in subcontent_generator(directory_input)}

    bytes_obj = lib_archive_content(dict_obj, cultures1)

    with open(filename_output, "wb") as file:
        file.write(bytes_obj)
