import itertools
from map import Map
from scripts.buffer import BufferGiver, data_encoding
from scripts.const import map_const, save_section_names
from sections.continents import load_continents_from_xcot
from sections.landscapes import load_landscapes_from_mobj
from sections.run_length import run_length_decryption
from sections.sectors import load_sectors_from_xsec

section_name_length = 4
save_section_names_bytes = tuple(map(lambda name: bytes(name[::-1], encoding=data_encoding) +\
                                                  (b"\x00" * (section_name_length - len(name))), save_section_names))


def save_to_map(save_filepath: str, new_map_filepath: str):
    # Refines bigger *.sav file to the form of smaller clean *.map file.

    with open(save_filepath, "rb") as file:
        bytes_obj = file.read()

    search_indices  = [[] for _ in save_section_names]

    for index_value, name_bytes in enumerate(save_section_names_bytes):
        current_index = 0 if index_value == 0 else search_indices[index_value-1][0] + section_name_length
        while (index_found := bytes_obj.find(name_bytes, current_index)) != -1:
            search_indices[index_value].append(index_found)
            current_index = index_found + section_name_length
        assert len(search_indices[index_value]) != 0

    assert (min(map(len, search_indices))) == 1

    for permutation in itertools.product(*search_indices):
        try:
            if not all((permutation[x] < permutation[x+1] for x in range(len(save_section_names) - 1))):
                continue

            sections_indices = dict(zip(save_section_names, permutation))  # Warning: Duplicates are being removed here.
            assert sections_indices["sgin"] == 0

            buffer = BufferGiver(bytes_obj)
            buffer.skip(sections_indices["mppa"] - 4)

            map_object = Map()
            map_object.map_version = 12

            map_object.map_width  = buffer.unsigned(length=2)
            map_object.map_height = buffer.unsigned(length=2)

            # All sections from the section "mppa" to the first section "end" resemble inner structure of *.map files.
            for _ in range(save_section_names.index("end") - save_section_names.index("mppa") + 1):
                section_name = buffer.string(4)[::-1]
                section_length = buffer.unsigned(4)

                if section_name == "xsec":
                    section_length += Map._xsec_additional_length  # noqa

                section_data = buffer.bytes(section_length)

                if section_name == "\x00end":
                    break

                if section_name in map_const.keys():
                    vars(map_object)[section_name] = run_length_decryption(section_data,
                                                                           bytes_per_entry=map_const[section_name][0],
                                                                           from_save_file=True)
                else:
                    match section_name:
                        case "mobj": map_object.llan = load_landscapes_from_mobj(section_data, map_object.map_width)
                        case "xcot": map_object.xcot = load_continents_from_xcot(section_data)
                        case "xsec": map_object.xsec, map_object.smmw = load_sectors_from_xsec(section_data)
                        case _: assert section_name in save_section_names

        # If there is some unexpected error in clause above, check if adding another error type here fixes it.
        # Such numerous count of error types is added due to the unpredictability when wrong permutation is selected.
        except (AssertionError, ValueError, IndexError, KeyError,
                OverflowError, ZeroDivisionError, UnicodeDecodeError):
            continue
        break
    else:
        raise ValueError("Save file is corrupted.")

    map_object.save(new_map_filepath)
