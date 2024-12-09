import os
import conversions  # noqa
from map import Map  # <-- The important file

# Following directories should be created manually
directory_input = "maps"  # put all *.map files there
directory_output = "edit"  # all extracted maps will be here

for item in os.listdir(directory_input):

    if os.path.splitext(item)[1] != ".map":
        continue

    path = os.path.join(directory_input, item)
    directory = os.path.join(directory_output, os.path.splitext(item)[0])
    print(item)

    try:
        map_object = Map()
        map_object.load(directory)
        map_object.extract(directory)
        map_object._extract_to_raw_data(os.path.join(directory, "raw"))
        del map_object

        map_object_new = Map()
        map_object_new.pack(directory)
        map_object_new._extract_to_raw_data(os.path.join(directory, "raw2"))
        del map_object_new

        # compare 'raw' and 'raw2' folders to vertify the correctness of derivations.

    except NotImplementedError:
        print("*not implemented*")
