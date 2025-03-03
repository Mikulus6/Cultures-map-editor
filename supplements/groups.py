from random import randint
from scripts.data_loader import load_ini_as_dict

rand_max = 2147483647

landscapes_edit_group_path = "data_v\\ve_edit\\landscapeeditgroups.cif"
landscapes_edit_group = load_ini_as_dict(landscapes_edit_group_path,
                                         allowed_section_names=("landscapegroup",),
                                         entries_duplicated=("Landscape",),
                                         global_key=lambda x: x["Name"],
                                         merge_duplicates=False)

def get_random_landscape(group_landscapes, *, legacy_randomness: bool = False):
    values_sum = sum(entry[1] for entry in group_landscapes)

    if values_sum == 0:
        raise ZeroDivisionError

    random_value = randint(0, rand_max) % values_sum if legacy_randomness else randint(1, values_sum)
    # Legacy randomness algorithm contains a mistake. However, because it is implemented in this way in the editor for
    # the game "Cultures - Northland", it is likely that the same mistake was present in the original editor for
    # "Cultures: Discovery of Vinland", which gives parameters in landscape groups historically accurate
    # interpretation, even though we can clearly see that the intended and actual implementations were not the same.

    for entry in group_landscapes:
        random_value -= entry[1]
        if random_value <= 0:
            return entry[0]
    else:
        raise ValueError
