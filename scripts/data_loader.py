import os

data_directory = "data"
data_encoding = "cp1252"


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

    for index, element in enumerate(list_):
        if index != 0 and element[0] != "\"":
            list_[index] = int(element)

    return list_


def load_ini_as_dictionary(filepath: str, dual_id=False) -> dict:
    data_dict = dict()

    with open(filepath, encoding=data_encoding) as file:

        adding = False
        name = None

        for line in file.readlines():
            line = line_split(line)

            for num, item in enumerate(line):
                if isinstance(item, str):
                    line[num] = item.replace("\"", "").replace("\n", "")

            if line[0] == "Name" and not dual_id:
                adding = True
                name = line[1].replace("\"", "").replace("\n", "")
                data_dict[name] = dict()

            elif line[0] == "Id" and dual_id:
                adding = False
                name = line[1]
            elif line[0] == "SetId" and dual_id:
                assert not adding and name is not None
                adding = True  # "Id" always should be found before "SetId".
                data_dict[name + line[1] * 256] = {"Id": name}
                name += line[1] * 256

            if line[0][0] == "[":
                adding = False
            elif adding:
                subdict = data_dict[name]  # noqa: Pycharm bug
                subdict[line[0]] = subdict.get(line[0], [])
                subdict[line[0]].append(line[1:])
                data_dict[name] = subdict

    all_keys = set()
    for subdict in data_dict.values():
        all_keys.update(subdict.keys())

    for iteration in range(2):
        unique_keys = set()

        for key in all_keys:
            duped = False
            for value in data_dict.values():
                try:
                    if len(value.get(key, [])) >= 2:
                        duped = True
                        break
                except TypeError:
                    pass
            if duped:
                continue

            unique_keys.add(key)

        for key, value in data_dict.items():
            for subkey, subvalue in data_dict[key].items():
                if subkey in unique_keys:
                    try:
                        data_dict[key][subkey] = subvalue[0]
                    except IndexError:
                        data_dict[key][subkey] = None
                    except TypeError:
                        data_dict[key][subkey] = subvalue

    return data_dict


landscapedefs = load_ini_as_dictionary(os.path.join(data_directory, "landscapedefs.ini"))
patterndefs_normal = load_ini_as_dictionary(os.path.join(data_directory, "patterndefs_normal.ini"), dual_id=True)
