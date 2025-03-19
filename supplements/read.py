import os
from typing import Literal
from scripts.buffer import data_encoding
from supplements.library import Library
from supplements.initialization import decode

game_basepath = "."  # Put relative path to game's main directory here.

libraries_directory = "data_l"
libraries_directory = os.path.join(game_basepath, libraries_directory)
loaded_libraries = dict()

def read(filepath: str, mode: Literal["r", "rb"] = "r", *,
         skip_file = False, skip_library = False, skip_cif_check = False,
         cultures_1 = True, recursive = False) -> bytes | str:
    """
    This function is supposed to work as combination of built-in open() and file.read() functions, but with the addition
    of backup libraries and cif <-> ini files equivalence similarly to how games from Cultures series load files.

    Warnings:
     - Parameter 'mode' will be ignored if file extension is *.ini, *.cif, *.tab or *.sal.
     - File *.cif will check for backup *.ini file, but it does not work the other way around.
     - Skips-related parameter should be left as False and modified only in recursive cases.
    """
    global loaded_libraries

    if not recursive:
        filepath = os.path.join(game_basepath, filepath)
    filepath = filepath.lower()

    assert not skip_cif_check or filepath.endswith(".cif")

    if not (skip_file or skip_library or skip_cif_check):
        if filepath.endswith(".cif"):

            filepaths = filepath[:-4]+".ini", filepath[:-4]+".cif"

            for skip_lib in (False, True):
                for is_decoded, sub_filepath in zip((True, False), filepaths):
                    try:
                        content = read(sub_filepath, mode= "r" if is_decoded else "rb",
                                       skip_file=not skip_lib, skip_library=skip_lib, recursive=True)
                        return content if isinstance(content, str) else decode(content, tab_sal_file_format=False)
                    except FileNotFoundError:
                        pass

        if (filepath.endswith(".tab") or filepath.endswith(".sal")) and mode == "r":
            return decode(read(filepath, "rb", skip_file=False, skip_library=False, recursive=True),
                          tab_sal_file_format=True)

    if not skip_file:
        try:
            match mode:
                case "r":
                    with open(filepath, mode, encoding=data_encoding) as file:
                        return file.read()
                case "rb":
                    with open(filepath, mode) as file:
                        return file.read()
                case _:
                    raise ValueError

        except FileNotFoundError:
            pass

    if not skip_cif_check and filepath.endswith(".ini"):
        try:                      return decode(read(filepath[:-4]+".cif", mode="rb", skip_cif_check=True,
                                                     recursive=True), tab_sal_file_format=False)
        except FileNotFoundError: pass

    if not skip_library:
        parent_directory = os.path.normpath(filepath).split(os.sep)[0]
        library_path = libraries_directory + os.sep + parent_directory.lower() + ".lib"
        if library_path not in loaded_libraries.keys():

            try:
                library = Library()
                library.load(library_path, cultures_1=cultures_1)
                loaded_libraries[library_path] = library
            except FileNotFoundError:
                raise FileNotFoundError

        try:
            return loaded_libraries[library_path][filepath]
        except KeyError:
            pass

    raise FileNotFoundError
