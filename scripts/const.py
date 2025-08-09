# name : (bytes per entry, size reduction, header digit)
map_const = \
    {"mhei": (1, True,  8),
     "mlig": (1, True,  8),
     "mepa": (2, True,  6),
     "mepb": (2, True,  6),
     "mgfs": (1, False, 8),
     "mstr": (2, False, 6),
     "mbio": (1, True,  8),
     "mco2": (1, False, 8),
     "mexp": (2, True,  6)}

section_names = \
 ("mhei", "mlig", "mepa", "mepb",
  "mgfs", "mstr", "mbio", "mco2",
  "mexp", "llan", "xcot", "xsec")

save_section_names = \
    ("sgin", "sghd", "mtsa", "sgld", "ldms", "pvms", "coom", "mtmv", "daas", "mmcl", "psmr",
     "mppa", "mppb", "mepa", "mepb", "mhei", "mlig", "mobj", "mcre", "mdfs", "mgfs", "mstr",
     "mbio", "mco2", "mexp", "xcot", "xsec", "xsea", "end" , "vlar", "hvat", "avat", "maar",
     "hwac", "cwac", "cmxx", "guar", "merc", "stoc", "gsta", "vamg", "msmn", "cdac", "end", )
    # Multiple sections with common name "vasp" were ignored due to inconsistences in save files.
