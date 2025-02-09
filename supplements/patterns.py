from scripts.data_loader import load_ini_as_dict


patterndefs_path = "data_v\\ve_graphics\\pattern1\\patterndefs_normal.cif"
road_path        = "data_v\\ve_graphics\\roads\\road.cif"


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

road = load_ini_as_dict(road_path,
                        allowed_section_names=("road",),
                        entries_duplicated=tuple(),
                        global_key= lambda x: x["name"],
                        merge_duplicates=False)
