from scripts.buffer import BufferGiver, data_encoding
from scripts.data_loader import load_ini_as_dict

name_max_length = 84
group_name_max_length = 36

landscapedefs_cdf_path = "data_v\\ve_graphics\\landscape\\landscapedefs.cdf"
landscapedefs_cif_path = "data_v\\ve_graphics\\landscape\\landscapedefs.cif"


class LandscapeDefs(dict):
    def __init__(self, cif_path: str = landscapedefs_cif_path):

        super().__init__(load_ini_as_dict(cif_path, allowed_section_names=("LandscapeElement",),
                         entries_duplicated=("BaseArea", "ExtendedArea", "SpecialArea", "AddNextLandscape", "FlagSet"),
                         global_key=lambda x: x["Name"], merge_duplicates=False))

        # Following fields are meant for storing info which present in *.cdf file is not redundant to *.cif file
        # content. This is most likely a result of unused leftover data with no deeper meaning. Remember that *.cdf file
        # cannot be fully interpreted alone without *.cif file, because there is no distinction between the beginning of
        # "AddNextLandscape" parameter and new "Name" parameter.
        self.data_add_next_duplicates = dict()
        self.data_groups = dict()

    def load_cdf(self, cdf_path: str = landscapedefs_cdf_path):
        with open(cdf_path, "rb") as file:
            buffer = BufferGiver(file.read())

        landscapes = list()
        landscapes_add_next_data = dict()

        for num_landscape in range(buffer.unsigned(4)):
            name_raw = buffer.bytes(length=name_max_length)
            name_length = name_raw.find(0)

            if name_length == -1:
                name_length = name_max_length

            name = str(name_raw[:name_length], encoding=data_encoding)

            bob_libs_packed = ""
            bob_libs_masked = ""
            base_area = []
            extended_area = []
            special_area = []

            if buffer.unsigned(1):
                bob_libs_packed = buffer.string(buffer.unsigned(1))
                assert buffer.unsigned(1) == 0

            if buffer.unsigned(1):
                bob_libs_masked = buffer.string(buffer.unsigned(1))
                assert buffer.unsigned(1) == 0

            if buffer.unsigned(1):
                for _ in range(buffer.unsigned(2)):
                    base_area.append([buffer.signed(2),
                                      buffer.signed(2),
                                      buffer.signed(2)])

            if buffer.unsigned(1):
                for _ in range(buffer.unsigned(2)):
                    extended_area.append([buffer.signed(2),
                                          buffer.signed(2),
                                          buffer.signed(2)])

            if buffer.unsigned(1):
                for _ in range(buffer.unsigned(2)):
                    special_area.append([buffer.signed(2),
                                         buffer.signed(2),
                                         buffer.signed(2)])

            bob_libs_packed_from_meta, bob_libs_masked_from_meta = tuple(self[name].get("BobLibs", ("", "")))
            assert bob_libs_packed_from_meta.lower() == bob_libs_packed.lower()
            assert bob_libs_masked_from_meta.lower() == bob_libs_masked.lower()
            del bob_libs_packed_from_meta, bob_libs_masked_from_meta

            assert base_area == self[name].get("BaseArea", [])
            assert extended_area == self[name].get("ExtendedArea", [])
            assert special_area == self[name].get("SpecialArea", [])

            if "AddNextLandscape" in self[name].keys():
                for _ in range(len(self[name]["AddNextLandscape"])):

                    landscapes_add_next_data[name] = landscapes_add_next_data.get(name, list()) + \
                                                     [[buffer.unsigned(1), buffer.unsigned(1), buffer.signed(2)]]
                    assert buffer.unsigned(2) == 1

            landscapes.append(name)

        for name, landscape_add_next in landscapes_add_next_data.items():

            preduplicates = []
            duplicates = []
            for entry_index, entry in enumerate(landscape_add_next):

                entry = [entry[0], "remove" if entry[2] == -1 else landscapes[entry[2]].lower(), entry[1]]

                if entry in preduplicates:
                    duplicates.append(entry)
                    continue

                entry_ref = self[name]["AddNextLandscape"][entry_index]
                entry_ref[1] = entry_ref[1].lower()

                assert entry == entry_ref
                preduplicates.append(entry)

            if len(duplicates) > 0:
                self.data_add_next_duplicates[name] = duplicates

        for _ in range(buffer.unsigned(4)):
            name_raw = buffer.bytes(length=group_name_max_length)
            name_length = name_raw.find(0)

            if name_length == -1:
                name_length = group_name_max_length

            name = str(name_raw[:name_length], encoding=data_encoding)
            values = []
            for _ in range(buffer.unsigned(2)):
                values.append(value := landscapes[buffer.unsigned(2)])
                assert self[value]["GroupName"] == name

            self.data_groups[name] = values


landscapedefs = LandscapeDefs()
landscapedefs.load_cdf()
