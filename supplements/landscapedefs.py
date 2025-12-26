from math import ceil
from scripts.buffer import BufferGiver, data_encoding
from scripts.data_loader import load_ini_as_dict, load_ini_as_sections, filter_section_by_name, merge_entries_to_dicts
from supplements.read import read

sum_nested = lambda x: sum(sum_nested(i) if isinstance(i, list) else i for i in x)

dummy_seedling_value = 0
chars_per_byte = 4

landscapedefs_cdf_path = "data_v\\ve_graphics\\landscape\\landscapedefs.cdf"
landscapedefs_cif_path = "data_v\\ve_graphics\\landscape\\landscapedefs.cif"


class LandscapeDefs(dict):
    def __init__(self, cif_path: str = landscapedefs_cif_path, *, load_cdf: bool = False):

        super().__init__(load_ini_as_dict(cif_path, allowed_section_names=("LandscapeElement",),
                         entries_duplicated=("BaseArea", "ExtendedArea", "SpecialArea", "AddNextLandscape", "FlagSet"),
                         global_key=lambda x: x["Name"].lower(), merge_duplicates=False))

        # Following fields are meant for storing info which present in *.cdf file is not redundant to *.cif file
        # content. This is most likely a result of unused leftover data with no deeper meaning. Remember that *.cdf file
        # cannot be fully interpreted alone without *.cif file, because there is no distinction between the beginning of
        # "AddNextLandscape" parameter and new "Name" parameter. It is also not necessary to read *.cdf file at all.
        self.data_add_next_duplicates = dict()
        self.data_groups = dict()

        self.name_max_length = ceil((max(map(len, self.keys())) + 1) / chars_per_byte) * chars_per_byte
        # length of names is padded to multiple of four bytes containing at least one additional byte for termination.

        if load_cdf:
            self.load_cdf()

    def load_cdf(self, cdf_path: str = landscapedefs_cdf_path):
        buffer = BufferGiver(read(cdf_path, mode="rb"))

        landscapes = list()
        landscapes_add_next_data = dict()

        group_names = dict()
        remaptables_names = dict()
        shadow_remaptables_names = dict()
        sound_names = dict()

        for num_landscape in range(buffer.unsigned(4)):
            name_raw = buffer.bytes(length=self.name_max_length)
            name_length = name_raw.find(0)

            if name_length == -1:
                name_length = self.name_max_length

            name = str(name_raw[:name_length], encoding=data_encoding).lower()

            # Meanings of following entries of constant size up to "Energy" value were obtained and provided by
            # Benedikt Magnus on 01.10.2025.

            assert buffer.unsigned(4) == 0
            group_id = buffer.unsigned(2)
            assert buffer.unsigned(2) == num_landscape
            assert buffer.unsigned(1) == self[name].get("Mode", 0)
            assert buffer.unsigned(1) == sum_nested(self[name].get("FlagSet", [0]))
            assert buffer.signed(2) % (2 ** 16) == self[name].get("FirstBob", -1) % (2 ** 16)
            assert (buffer.unsigned(2) == self[name].get("FirstShadowBob")) or\
                   (self[name].get("FirstShadowBob", None) is None)
            assert buffer.unsigned(2) == self[name].get("Elements", 0)
            assert buffer.unsigned(1) == self[name].get("RemapDisable", 0)
            assert buffer.unsigned(1) == 0
            remaptable_id = buffer.signed(2)
            shadow_remaptable_id = buffer.signed(2)
            assert buffer.unsigned(2) == self[name].get("ShadingFactor", 128)
            assert buffer.unsigned(1) == self[name].get("HighColorShadingMode", 0)
            assert buffer.unsigned(5) == 0
            sound_name_id = buffer.signed(2)

            for value_id, names_dict, field_name in \
                    ((group_id, group_names, "GroupName"),
                     (remaptable_id, remaptables_names, "RemapName"),
                     (shadow_remaptable_id, shadow_remaptables_names, "ShadowRemapName"),
                     (sound_name_id, sound_names, "SoundName")):

                if value_id == -1: continue
                elif value_id in names_dict.keys(): assert names_dict[value_id] == self[name][field_name].lower()
                else: names_dict[value_id] = self[name][field_name].lower()

            assert buffer.unsigned(2) == len(self[name].get("AddNextLandscape", []))

            for value_name in ("MotivateReligion",     "MotivateCulture",
                               "WaterNecessity",       "WaterLimit",
                               "NutritionalNecessity", "NutritionalLimit"):
                assert buffer.unsigned(1) == (self[name].get(value_name, 0) if value_name != "MotivateCulture" else 0)

            match buffer.unsigned(1) % 2:
                case 0: assert self[name].get("Seedling", dummy_seedling_value) == dummy_seedling_value
                case 1: assert self[name].get("Seedling", dummy_seedling_value) is None
                case _: raise ArithmeticError

            assert [buffer.unsigned(1) for _ in range(3)] == self[name].get("ReproduceData", [0, 0, 0])
            assert buffer.unsigned(2) == self[name].get("Energy", 0)
            assert buffer.unsigned(2) == 0
            assert buffer.signed(4) == -1

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
            name_raw = buffer.bytes(length=self.name_max_length)
            name_length = name_raw.find(0)

            if name_length == -1:
                name_length = self.name_max_length

            name = str(name_raw[:name_length], encoding=data_encoding)
            assert buffer.unsigned(4) == 0

            values = []
            for _ in range(buffer.unsigned(2)):
                values.append(value := landscapes[buffer.unsigned(2)])
                assert self[value]["GroupName"] == name

            self.data_groups[name] = values


landscapedefs = LandscapeDefs(load_cdf=False)

landscapes_sorted = tuple(map(lambda x: x["Name"], merge_entries_to_dicts(filter_section_by_name(
                                                   load_ini_as_sections(landscapedefs_cif_path),
                                                   allowed_section_names=("LandscapeElement",)),
                                                   entries_duplicated=("BaseArea", "ExtendedArea", "SpecialArea",
                                                                       "AddNextLandscape", "FlagSet"),
                                                   merge_duplicates=False)))

landscapes_sorted_lowercase = tuple(map(lambda x: x.lower(), landscapes_sorted))

revert_landscape_capitalization = lambda name: landscapes_sorted[landscapes_sorted_lowercase.index(name.lower())]
