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
    print(item)

    with open(path, "rb") as file:
        try:
            map_object = Map()
            map_object.load_from_file(file.read())
            map_object.save_to_data(os.path.join(directory_output, os.path.splitext(item)[0]))
            # map_object.load_from_data(os.path.join(directory_output, os.path.splitext(item)[0]))
            # map_object.save_to_file(f"{os.path.splitext(item)[0]}_edit.map")
        except NotImplementedError:
            print("*not implemented*")
