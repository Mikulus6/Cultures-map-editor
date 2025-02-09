from supplements.patterns import patterndefs_normal


border_full_ids = tuple([key for key in patterndefs_normal if
                         patterndefs_normal[key].get("MainGroup", "") == "border"])

void_full_ids = tuple([key for key in patterndefs_normal if
                       1 in patterndefs_normal[key].get("GroundFlagSet", [])])

underwater_full_ids = tuple([key for key in patterndefs_normal if
                             patterndefs_normal[key].get("MainGroup", "") == "unterwasser"])

water_full_ids = tuple([key for key in patterndefs_normal if
                        2 in patterndefs_normal[key].get("GroundFlagSet", []) or
                        patterndefs_normal[key].get("MainGroup", "") in ("river", "river2")])

land_full_ids = tuple([key for key in patterndefs_normal if
                       key not in (*void_full_ids, *water_full_ids)])
