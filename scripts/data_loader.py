import os

from supplements.library import Library, separator
from supplements.initialization import decode

data_encoding = "cp1252"

backup_library_path_data_v = "data_l/data_v.lib"
landscapedefs_path = "data_v/ve_graphics/landscape/landscapedefs.ini"
patterndefs_path = "data_v/ve_graphics/pattern1/patterndefs_normal.ini"

def line_split(line_: str):
    list_ = [""]
    quoted = False
    for char in line_:
        if char != " " or quoted:
            list_[-1] += char
        else:
            list_.append("")
        if char == "\"":
            quoted = not quoted

    for index in range(len(list_)):
        if index == len(list_) - 1:
            list_[index] = list_[index].rstrip("\n")
        if str.isdigit(list_[index].replace("-", "")):
            list_[index] = int(list_[index])
        else:
            list_[index] = list_[index].strip("\"")

    return list_

def load_ini_as_sections(filepath: str, backup_library_path: str = "") -> list:
    data_list = []

    ini_string = load_ini(filepath, backup_library_path)

    for line in ini_string.split("\n"):
        if len(line) == 0:
            continue
        line = line_split(line)
        if line[0][0] == "[" and line[0][-1] == "]":  # header
            header = line[0][1:-1]
            data_list.append([header, list()])
        else:                                         # entry
            data_list[-1][1].append(line)
    return data_list

def filter_section_by_name(data_list, allowed_section_names=tuple()):
    data_list_new = []
    for element in data_list:
        if element[0] in allowed_section_names:
            data_list_new.append(element[1])
    return data_list_new

def merge_entries_to_dicts(data_list, entries_duplicated, merge_duplicates) -> list:
    data_list_new = []
    for section in data_list:
        section_dict = dict()
        for element in section:
            name, parameters = element[0], element[1:]
            if name in entries_duplicated:
                match merge_duplicates:
                    case True:  section_dict.setdefault(name, []).extend(parameters)
                    case False: section_dict.setdefault(name, []).append(parameters)
            else:
                assert section_dict.get(name, None) is None
                if len(parameters) > 1:
                    section_dict[name] = parameters
                elif len(parameters) == 1:
                    section_dict[name] = parameters[0]
                else:
                    section_dict[name] = None
        data_list_new.append(section_dict)
    return data_list_new

def list_to_dict_by_global_key(data_list, global_key):
    data_dict = dict()
    for section in data_list:
        data_dict[global_key(section)] = section
    return data_dict

def load_ini_as_dict(filename, backup_library_path, allowed_section_names,
                     entries_duplicated, global_key, merge_duplicates) -> dict:
    data_list = load_ini_as_sections(filename, backup_library_path)
    data_list = filter_section_by_name(data_list, allowed_section_names)
    data_list = merge_entries_to_dicts(data_list, entries_duplicated, merge_duplicates)
    return list_to_dict_by_global_key(data_list, global_key)

def load_ini(filepath: str, backup_lib_filepath: str):
    filepath            = filepath.replace("/", separator)
    backup_lib_filepath = backup_lib_filepath.replace("/", separator)

    try:
        with open(filepath, "r", encoding=data_encoding) as file:
            return file.read()
    except FileNotFoundError:
        pass

    try:
        with open(filepath[:-3]+"cif", "rb") as file:
            return decode(file.read(), tab_sal_file_format=False)
    except FileNotFoundError:
        pass

    print((filepath[:-3]+"cif").replace(os.sep, separator))
    library = Library()
    library.load(backup_lib_filepath, cultures_1=True)

    try:
        return str(library[filepath.replace(os.sep, separator)], encoding=data_encoding)
    except KeyError:
        pass

    try:
        return decode(library[(filepath[:-3]+"cif").replace(os.sep, separator)], tab_sal_file_format=False)
    except KeyError:
        raise FileNotFoundError


landscapedefs = load_ini_as_dict(landscapedefs_path,
                                 backup_library_path_data_v,
                                 allowed_section_names=("LandscapeElement",),
                                 entries_duplicated=("BaseArea", "ExtendedArea", "SpecialArea",
                                                     "AddNextLandscape", "FlagSet"),
                                 global_key = lambda x: x.get("Name"),
                                 merge_duplicates=False)

patterndefs_normal = load_ini_as_dict(patterndefs_path,
                                      backup_library_path_data_v,
                                      allowed_section_names=("PatternDef",),
                                      entries_duplicated=("GroundFlagSet", ),
                                      global_key = lambda x: x.get("Id") + x.get("SetId") * 256,
                                      merge_duplicates=True)

transitions = load_ini_as_dict(patterndefs_path,
                               backup_library_path_data_v,
                               allowed_section_names=("Transition",),
                               entries_duplicated=tuple(),
                               global_key = lambda x: x.get("Name"),
                               merge_duplicates=False)

transition_defs = load_ini_as_dict(patterndefs_path,
                                   backup_library_path_data_v,
                                   allowed_section_names=("TransitionDef",),
                                   entries_duplicated=tuple(),
                                   global_key = lambda x: x.get("Name"),
                                   merge_duplicates=False)
