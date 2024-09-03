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
 ["mhei", "mlig", "mepa", "mepb",
  "mgfs", "mstr", "mbio", "mco2",
  "mexp", "llan", "xcot", "xsec"]
