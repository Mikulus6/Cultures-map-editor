from scripts.buffer import BufferGiver, data_encoding
from scripts.data_loader import load_ini_as_dict
from supplements.read import read


patterndefs_cdf_path = "data_v\\ve_graphics\\pattern1\\patterndefs_normal.cdf"
patterndefs_cif_path = "data_v\\ve_graphics\\pattern1\\patterndefs_normal.cif"
triangles_path   = "data_v\\ve_edit\\triangletransition.cif"
road_path        = "data_v\\ve_graphics\\roads\\road.cif"


class PatternDefs(dict):
    def __init__(self, cif_path: str = patterndefs_cif_path, *, load_cdf: bool = False):

        super().__init__(
            load_ini_as_dict(cif_path,
                             allowed_section_names=("PatternDef",),
                             entries_duplicated=("GroundFlagSet", ),
                             global_key = lambda x: x["Id"] + x["SetId"] * 256,
                             merge_duplicates=True))

        self.transitions = \
            load_ini_as_dict(patterndefs_cif_path,
                             allowed_section_names=("Transition",),
                             entries_duplicated=tuple(),
                             global_key = lambda x: (x["SrcGroup"], x["DestGroup"]),
                             merge_duplicates=False)

        self.transition_defs = \
            load_ini_as_dict(patterndefs_cif_path,
                             allowed_section_names=("TransitionDef",),
                             entries_duplicated=tuple(),
                             global_key=lambda x: x["Name"],
                             merge_duplicates=False)

        # Following fields are meant for storing info which present in *.cdf file is not redundant to *.cif file
        # content. This is most likely a result of unused leftover data with no deeper meaning.
        # It is not necessary to read *.cdf file at all.
        self.meta_ids = dict()
        self.meta_dump = dict()

        if load_cdf:
            self.load_cdf()

    def load_cdf(self, cdf_path: str = patterndefs_cdf_path):
        buffer = BufferGiver(read(cdf_path, mode="rb"))

        assert buffer.unsigned(length=4) == len(self)

        used_mep_ids = list()
        used_transitions = list()
        used_transition_defs = list()

        for _ in range(len(self)):

            set_id_ = buffer.unsigned(length=2)
            id_ = buffer.unsigned(length=2)
            mep_id_ = set_id_ * 256 + id_

            patterndef = self[mep_id_]
            if mep_id_ in used_mep_ids:
                raise KeyError
            used_mep_ids.append(mep_id_)

            names = []
            for _ in range(3):
                name_raw = buffer.bytes(length=36)
                name_length = name_raw.find(0)
                names.append(str(name_raw[:name_length], encoding=data_encoding).lower())

            assert names == list(map(lambda name: patterndef[name].lower(), ("Name", "MainGroup", "Group")))  # noqa
            assert sum(patterndef.get("GroundFlagSet", (0, ))) == buffer.unsigned(length=2)
            assert patterndef.get("Resistance", 3) == buffer.unsigned(length=2)

            pixel_coords = []
            for _ in range(12):
                pixel_coords.append(buffer.unsigned(4))

            assert (*patterndef["APixelCoords"],) == (*pixel_coords[:6],)
            assert (*patterndef["BPixelCoords"],) == (*pixel_coords[6:],)

            assert patterndef.get("MapColor", 0)       == buffer.unsigned(2)
            assert patterndef.get("GouraudEnable", 1)  == buffer.unsigned(2)
            assert patterndef.get("MaxWater", 0)       == buffer.unsigned(1)
            assert patterndef.get("MaxNutritional", 0) == buffer.unsigned(1)
            assert buffer.unsigned(2) == 0

        assert buffer.unsigned(length=4) == len(self.transitions)

        for _ in range(len(self.transitions)):

            names = []
            for _ in range(2):
                name_raw = buffer.bytes(length=36)
                name_length = name_raw.find(0)
                names.append(str(name_raw[:name_length], encoding=data_encoding))
            transition_key = tuple(names)

            transition = self.transitions[transition_key]
            if transition_key in used_transitions:
                raise KeyError
            used_transitions.append(transition_key)

            assert transition["Type"] == buffer.unsigned(length=2)

            name_raw = buffer.bytes(length=36)
            name_length = name_raw.find(0)
            assert transition["Name"] == str(name_raw[:name_length], encoding=data_encoding)

        assert buffer.unsigned(length=4) == len(self.transition_defs)

        for _ in range(len(self.transition_defs)):
            name_raw = buffer.bytes(length=36)
            name_length = name_raw.find(0)
            name = str(name_raw[:name_length], encoding=data_encoding)

            transition_def = self.transition_defs[name]
            if transition_def in used_transition_defs:
                raise KeyError
            used_transition_defs.append(name)

            assert transition_def["SetId"] == buffer.unsigned(length=4)

            for key_ in ("aa", "ab", "ac", "ba", "bb", "bc"):
                for index_value in range(6):
                    if "TPixelCoords" in transition_def.keys():
                        assert transition_def["TPixelCoords"][index_value] == buffer.unsigned(length=4)
                    else:
                        assert transition_def[f"T{key_.upper()}PixelCoords"][index_value] == buffer.unsigned(length=4)

            assert transition_def["GouraudEnable"] == buffer.unsigned(length=4)

        self.meta_ids = dict()

        for counter in range(len(self)):
            meta_group_identifier = buffer.unsigned(length=4)
            assert meta_group_identifier % len(self) == 0
            self.meta_ids[used_mep_ids[counter]] = meta_group_identifier // len(self)
            # Note that if, instead of iterating patterndefs in order of appearance in *.cdf file, one uses the order
            # present in *.cif file, it might give some other results with roughly the same probability of correctness
            # of interpretation. This is due to the fact that in "Cultures: Discovery of Vinland", in such an
            # alternative case, pattern definition with the name "fog 1" (which defines a rather special pattern for
            # in-game functionality) has unique value from the meta_ids field. However, this may be purely coincidental.

        remaining_bytes_length = buffer.unsigned(length=4)
        assert len(buffer) == remaining_bytes_length == len(self) * 26

        self.meta_dump = dict()

        for counter in range(len(self)):
            self.meta_dump[used_mep_ids[counter]] = buffer.bytes(length=26)


road = \
    load_ini_as_dict(road_path,
                     allowed_section_names=("road",),
                     entries_duplicated=tuple(),
                     global_key = lambda x: x["name"],
                     merge_duplicates=False)

corner_types = \
    load_ini_as_dict(triangles_path,
                     allowed_section_names=("corner_type",),
                     entries_duplicated=tuple(),
                     global_key = lambda x: x["name"],
                     merge_duplicates=False)

triangle_transitions = \
    load_ini_as_dict(triangles_path,
                     allowed_section_names=("triangle_transition",),
                     entries_duplicated=tuple(),
                     global_key = lambda x: x["name"],
                     merge_duplicates=False)

patterndefs_normal = PatternDefs(load_cdf=False)
patterndefs_normal_by_name = {x["Name"].lower(): x for x in patterndefs_normal.values()}

patterndefs_normal_by_groups = dict()
for mep_id, value in patterndefs_normal.items():
    group, maingroup = value["Group"].lower(), value["MainGroup"].lower()
    for group_name in (value["Group"].lower(), value["MainGroup"].lower()):
        patterndefs_normal_by_groups.setdefault(group, set()).update({mep_id})
        patterndefs_normal_by_groups.setdefault(maingroup, set()).update({mep_id})

triangle_transitions_by_corner_types = dict()
for triangle_transition in triangle_transitions.values():
    key = tuple(sorted(triangle_transition["corner_types"]))
    if key not in triangle_transitions_by_corner_types.keys():
        triangle_transitions_by_corner_types[key] = [triangle_transition]
    else:
        triangle_transitions_by_corner_types[key].append(triangle_transition)
