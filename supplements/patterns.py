from scripts.data_loader import load_ini_as_dict


patterndefs_path = "data_v\\ve_graphics\\pattern1\\patterndefs_normal.cif"
triangles_path   = "data_v\\ve_edit\\triangletransition.cif"
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
                        global_key = lambda x: x["name"],
                        merge_duplicates=False)

corner_types = load_ini_as_dict(triangles_path,
                                allowed_section_names=("corner_type",),
                                entries_duplicated=tuple(),
                                global_key = lambda x: x["name"],
                                merge_duplicates=False)

triangle_transitions = load_ini_as_dict(triangles_path,
                                        allowed_section_names=("triangle_transition",),
                                        entries_duplicated=tuple(),
                                        global_key = lambda x: x["name"],
                                        merge_duplicates=False)

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
