import random
from itertools import product
from PIL import Image
import numpy as np
from interface.triangle_transitions import update_triangles
from scripts.colormap import template_editgroups_palette, find_closest_color
from supplements.patterns import patterndefs_normal, patterndefs_normal_by_name
from supplements.textures import patterndefs_textures
from supplements.groups import pattern_edit_group, get_random_group_entry

def get_patternedit_color_data():
    pattern_edit_groups_by_mep_id = dict()
    for name, group in pattern_edit_group.items():
        pattern_edit_groups_by_mep_id[name] = list()
        for entry in group["Pattern"]:
            entry_def = patterndefs_normal_by_name[entry[0].lower()]
            pattern_edit_groups_by_mep_id[name].append(entry_def["Id"] + entry_def["SetId"] * 256)
    pattern_edit_textures = {name: [patterndefs_textures[mep_id] for mep_id in entry]
                             for name, entry in pattern_edit_groups_by_mep_id.items()}
    color_per_editgroup = dict()  # noqa
    for name, textures in pattern_edit_textures.items():
        average_color_result = [0, 0, 0]
        for texture in textures:
            average_color_a, average_color_b = texture["a"].average_color, texture["b"].average_color
            try:
                average_color = tuple(map(lambda avg: int(avg[0] + avg[1]) // 2, zip(average_color_a, average_color_b)))
            except TypeError:
                average_color = (0, 0, 0)
            average_color_result = [sum(x) for x in zip(average_color, average_color_result)]
        average_color_result = [x // len(textures) for x in average_color_result]
        if tuple(average_color_result) in color_per_editgroup.values():
            average_color_result = find_closest_color(average_color_result,
                                                      excluded_colors=color_per_editgroup.values())
        color_per_editgroup[name] = tuple(average_color_result)
    assert len(color_per_editgroup.values()) == len(set(color_per_editgroup.values()))  # There are no duplicates.
    editgroup_per_color = {color: name for name, color in color_per_editgroup.items()}  # noqa
    return color_per_editgroup, editgroup_per_color

def get_patterndefs_color_data():
    patterndefs_normal_by_group = dict()
    for patterndef in patterndefs_normal.values():
        key = patterndef["Group"].lower()
        if patterndef["Name"] in ("0", "1", "2", "x0", "x1", "x2"):
            continue

        if key not in patterndefs_normal_by_group.keys():
            patterndefs_normal_by_group[key] = [patterndef]
        else:
            patterndefs_normal_by_group[key].append(patterndef)

    patterndefs_textures_by_group = dict()  # noqa
    color_per_group = dict()                # noqa

    for patterndef in patterndefs_normal.values():
        if patterndef["Name"] in ("0", "1", "2", "x0", "x1", "x2") or\
           patterndef["Group"].lower() in ("transparent", "fog", "road", "river", "river2") or\
           patterndef["Group"].lower() == "unterwasser" and patterndef["Name"] != "Water 01":
            continue  # This data is not important in case of rendering map from template.

        texture = patterndefs_textures[patterndef["Id"] + patterndef["SetId"] * 256]
        average_color_a, average_color_b = texture["a"].average_color, texture["b"].average_color
        try:
            average_color = tuple(map(lambda avg: int(avg[0] + avg[1]) // 2, zip(average_color_a, average_color_b)))
        except TypeError:
            average_color = (0, 0, 0)

        if patterndef["Group"].lower() in patterndefs_textures_by_group.keys():
            patterndefs_textures_by_group[patterndef["Group"].lower()].append(patterndef)
            color_per_group[patterndef["Group"].lower()] = [sum(x) for x in
                                                            zip(color_per_group[patterndef["Group"].lower()],
                                                                average_color)]
        else:
            patterndefs_textures_by_group[patterndef["Group"].lower()] = [patterndef]
            color_per_group[patterndef["Group"].lower()] = list(average_color)

    for name, color in color_per_group.items():
        num_of_entries = len(patterndefs_textures_by_group[name])
        color_per_group[name] = (round(color_per_group[name][0] / num_of_entries),
                                 round(color_per_group[name][1] / num_of_entries),
                                 round(color_per_group[name][2] / num_of_entries),)
    return patterndefs_textures_by_group, color_per_group

patterndefs_textures_by_group, color_per_group = get_patterndefs_color_data()
color_per_editgroup, editgroup_by_color = get_patternedit_color_data()

def find_closest_by_color(rgb_value, color_per_entry: dict):
    min_colorspace_distance_squared = float("inf")
    found_group_name = None
    for group_name, group_avg_color in color_per_entry.items():
        distance_squared = (group_avg_color[0] - int(rgb_value[0]))**2 +\
                           (group_avg_color[1] - int(rgb_value[1]))**2 +\
                           (group_avg_color[2] - int(rgb_value[2]))**2

        if distance_squared < min_colorspace_distance_squared:
            min_colorspace_distance_squared = distance_squared
            found_group_name = group_name
    return found_group_name

template_editgroups_palette_inverse = {value: key for key, value in template_editgroups_palette.items()}


def render_map_template(editor, template_filepath: str):
    image = Image.open(template_filepath).convert("RGB").resize((editor.map.map_width, editor.map.map_height // 2),
                                                                Image.NEAREST)  # noqa
    array = np.array(image)
    for y in range(editor.map.map_height // 2):
        for x in range(editor.map.map_width // 2):
            for triangle_type in ("a", "b"):
                color = tuple(map(int, array[y, 2 * x + (1 if triangle_type == "b" else 0)]))

                if color in template_editgroups_palette.values():
                    pattern = patterndefs_normal_by_name[get_random_group_entry(pattern_edit_group[template_editgroups_palette_inverse[color]]["Pattern"]).lower()]
                elif color in color_per_editgroup.values():
                    pattern = patterndefs_normal_by_name[get_random_group_entry(pattern_edit_group[editgroup_by_color[color]]["Pattern"]).lower()]
                else:
                    pattern = random.choice(patterndefs_textures_by_group[find_closest_by_color(color,
                                                                                                color_per_group)])

                mep_id = pattern["Id"] + pattern["SetId"] * 256
                index_bytes = y * editor.map.map_width + x * 2
                match triangle_type:
                    case "a": editor.map.mepa[index_bytes: index_bytes + 2] = int.to_bytes(mep_id, length=2,
                                                                                           byteorder="little")
                    case "b": editor.map.mepb[index_bytes: index_bytes + 2] = int.to_bytes(mep_id, length=2,
                                                                                           byteorder="little")
    update_triangles(editor,
                     product(product(range(editor.map.map_width//2), range(editor.map.map_height//2)), ("a", "b")))
