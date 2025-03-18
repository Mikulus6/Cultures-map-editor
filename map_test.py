import os
from map import Map

# Following directories should be created manually
directory_input = "maps"  # put all *.map files there
directory_output = "edit"  # all extracted maps will be here

if __name__ == "__main__":
    for item in os.listdir(directory_input):

        if os.path.splitext(item)[1] != ".map":
            continue

        path = os.path.join(directory_input, item)
        directory = os.path.join(directory_output, os.path.splitext(item)[0])
        print(item)

        try:
            map_object = Map()
            map_object.load(path)
            map_object.extract(directory)
            map_object._extract_to_raw_data(os.path.join(directory, "raw"))  # noqa
            del map_object

            map_object_new = Map()
            map_object_new.pack(directory)
            map_object_new._extract_to_raw_data(os.path.join(directory, "raw2"))  # noqa
            del map_object_new

            # Compare 'raw' and 'raw2' folders to verify the correctness of derivations.

        except NotImplementedError:
            print("*not implemented*")
