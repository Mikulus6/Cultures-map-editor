from supplements.read import read

patterndefs_path   = "data_v\\ve_graphics\\pattern1\\patterndefs_normal.cif"

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

def load_ini_as_sections(filepath: str) -> list:
    data_list = []

    assert filepath.endswith(".ini") or filepath.endswith(".cif")

    ini_string = read(filepath)

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

def load_ini_as_dict(filename, allowed_section_names,
                     entries_duplicated, global_key, merge_duplicates) -> dict:
    """This function works also with *.cif files."""
    data_list = load_ini_as_sections(filename)
    data_list = filter_section_by_name(data_list, allowed_section_names)
    data_list = merge_entries_to_dicts(data_list, entries_duplicated, merge_duplicates)
    return list_to_dict_by_global_key(data_list, global_key)

patterndefs_normal = load_ini_as_dict(patterndefs_path,
                                      allowed_section_names=("PatternDef",),
                                      entries_duplicated=("GroundFlagSet", ),
                                      global_key = lambda x: x["Id"] + x["SetId"] * 256,
                                      merge_duplicates=True)

transitions = load_ini_as_dict(patterndefs_path,
                               allowed_section_names=("Transition",),
                               entries_duplicated=tuple(),
                               global_key = lambda x: (x["SrcGroup"], x["DestGroup"]),
                               merge_duplicates=False)

transition_defs = load_ini_as_dict(patterndefs_path,
                                   allowed_section_names=("TransitionDef",),
                                   entries_duplicated=tuple(),
                                   global_key = lambda x: x["Name"],
                                   merge_duplicates=False)
