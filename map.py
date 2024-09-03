import os
from buffer import BufferGiver, BufferTaker
from const import map_const, section_names

from sections.run_length import run_length_decryption, run_length_encryption
from sections.landscapes import load_landscapes_from_llan, load_llan_from_landscapes
from sections.continents import load_continents_from_xcot, load_xcot_from_continents
from sections.continents2 import derive_continents
from sections.sectors import load_sectors_from_xsec, load_xsec_from_sectors
from sections.light import derive_light_map
from sections.inland_vertices import inland_vertices_flag
from sections.landscapes_area import landscapes_area_flag
from sections.sectors_flag import sectors_flag
from sections.buildability import buildability_area_shifted
from sections.mesh_points import combine_mep, split_mep

from flags import sequence_to_flags, flags_to_sequence
from image import bytes_to_image, shorts_to_image, bits_to_image
from image import image_to_bytes, image_to_shorts, image_to_bits


class Map:
    _number_of_sections = 12
    _xsec_additional_length = 20

    def __init__(self):
        self.map_version = 0  # noqa: E221
        self.map_width   = 0  # noqa: E221
        self.map_height  = 0  # noqa: E221

        self.mhei = b""
        self.mlig = b""
        self.mepa = b""
        self.mepb = b""
        self.mgfs = b""
        self.mstr = b""
        self.mbio = b""
        self.mco2 = b""
        self.mexp = b""

        self.llan = dict()
        self.xcot = list()
        self.xsec = list()
        self.smmw = list()

    # ==================================== updaters ====================================

    def update_all(self):
        self.update_continents()
        self.update_exploration()
        self.update_light()
        self.update_ground_set_flags()
        # TODO: add later derivable sections

    def update_continents(self):
        self.mco2, self.xcot = derive_continents(self.mepa, self.mepb, self.map_width, self.map_height)

    def update_exploration(self):
        self.mexp = b"\x00" * (self.map_width*self.map_height//2)

    def update_light(self):
        self.mlig = derive_light_map(self.mhei, self.mepa, self.mepb, self.map_width, self.map_height)

    def update_ground_set_flags(self, *, update_buildability=True):

        mgfs_flags = sequence_to_flags(self.mgfs)

        mgfs_flags[3] = sectors_flag(self.xsec, self.map_width, self.map_height)
        mgfs_flags[4] = "0" * (self.map_width * self.map_height)
        mgfs_flags[5] = landscapes_area_flag(self.llan, self.map_width, self.map_height, area_type="Extended")  # noqa: E501
        mgfs_flags[6] = inland_vertices_flag(self.mepa, self.mepb, self.map_width, self.map_height)
        mgfs_flags[7] = landscapes_area_flag(self.llan, self.map_width, self.map_height, area_type="Base")

        if update_buildability:
            mgfs_flags[0] = buildability_area_shifted(mgfs_flags[7], self.mepa, self.mepb,
                                                      self.map_width, self.map_height,
                                                      shift_vector=(1, -1), use_coastline_fix=True)

            mgfs_flags[1] = buildability_area_shifted(mgfs_flags[7], self.mepa, self.mepb,
                                                      self.map_width, self.map_height,
                                                      shift_vector=(0, -1), use_coastline_fix=True)

            mgfs_flags[2] = buildability_area_shifted(mgfs_flags[7], self.mepa, self.mepb,
                                                      self.map_width, self.map_height,
                                                      shift_vector=(-1, 0), use_coastline_fix=True)

        self.mgfs = flags_to_sequence(mgfs_flags)

    # ====================================  testers  ====================================

    def test_all(self):
        try:
            assert self.test_continents()
            assert self.test_exploration()
            assert self.test_light()
            assert self.test_ground_set_flags()
            # TODO: add later derivable sections
        except AssertionError:
            # print("test error!")
            raise AssertionError

    def test_continents(self):
        return (self.mco2, self.xcot) == derive_continents(self.mepa, self.mepb, self.map_width, self.map_height)

    def test_exploration(self):
        return self.mexp == b"\x00" * (self.map_width*self.map_height//2)

    def test_light(self):
        return self.mlig == derive_light_map(self.mhei, self.mepa, self.mepb, self.map_width, self.map_height)

    def test_ground_set_flags(self):

        # Maps created before 22nd August 2000 might not pass this test due to different landscapes' shapes.

        mgfs_flags = sequence_to_flags(self.mgfs)

        try:

            # TODO: test layers 0, 1, 2.
            assert mgfs_flags[3] == sectors_flag(self.xsec, self.map_width, self.map_height)
            assert mgfs_flags[4] == "0" * (self.map_width * self.map_height)
            assert mgfs_flags[5] == landscapes_area_flag(self.llan, self.map_width, self.map_height, area_type="Extended")  # noqa: E501
            assert mgfs_flags[6] == inland_vertices_flag(self.mepa, self.mepb, self.map_width, self.map_height)
            assert mgfs_flags[7] == landscapes_area_flag(self.llan, self.map_width, self.map_height, area_type="Base")

        except AssertionError:
            return False
        else:
            return True

    # =================================== load & save ===================================

    def load_from_file(self, sequence: bytes):
        buffer = BufferGiver(sequence)

        self.map_version = buffer.unsigned(2)  # noqa: E221
        self.map_width   = buffer.unsigned(2)  # noqa: E221
        self.map_height  = buffer.unsigned(2)  # noqa: E221

        for _ in range(self.__class__._number_of_sections):
            section_name   = buffer.string(4)[::-1]  # noqa: E221
            section_length = buffer.unsigned(4)      # noqa: E221

            if section_name == "xsec":
                section_length += self.__class__._xsec_additional_length

            section_data = buffer.bytes(section_length)

            if section_name in map_const.keys():
                vars(self)[section_name] = run_length_decryption(section_data,
                                                                 bytes_per_entry=map_const[section_name][0])
            else:
                match section_name:
                    case "llan": self.llan = load_landscapes_from_llan(section_data)
                    case "xcot": self.xcot = load_continents_from_xcot(section_data)
                    case "xsec": self.xsec, self.smmw = load_sectors_from_xsec(section_data)
                    case _: raise NotImplementedError

        assert buffer.string(3)[::-1] == "end"
        assert buffer.unsigned(5) == 0
        assert len(buffer) == 0

    def save_to_file(self, filename: str):
        buffer = BufferTaker()

        buffer.unsigned(self.map_version, length=2)
        buffer.unsigned(self.map_width,   length=2)
        buffer.unsigned(self.map_height,  length=2)

        for section_name in section_names:

            section_buffer = BufferTaker()

            if section_name in map_const.keys():
                section_buffer.bytes(run_length_encryption(vars(self)[section_name],
                                                           bytes_per_entry=map_const[section_name][0],
                                                           header_digit=map_const[section_name][2]))

            else:
                match section_name:
                    case "llan": section_buffer.bytes(load_llan_from_landscapes(self.llan))
                    case "xcot": section_buffer.bytes(load_xcot_from_continents(self.xcot))
                    case "xsec": section_buffer.bytes(load_xsec_from_sectors(self.xsec,
                                                                             self.smmw,
                                                                             self.mco2,
                                                                             self.map_width))
                    case _: raise NotImplementedError

            section_length = len(section_buffer)

            if section_name == "xsec":
                section_length -= self.__class__._xsec_additional_length

            buffer.string(section_name[::-1])
            buffer.unsigned(section_length, length=4)
            buffer.bytes(bytes(section_buffer))

        buffer.string("end"[::-1])
        buffer.unsigned(0, length=5)

        with open(filename, "wb") as file:
            file.write(bytes(buffer))

    def load_from_data(self, directory: str):
        self.mhei = image_to_bytes(os.path.join(directory, "mhei.png"))
        self.mlig = image_to_bytes(os.path.join(directory, "mlig.png"))
        self.mepa, self.mepb = split_mep(image_to_shorts(os.path.join(directory, "mep.png")))

        flags = []
        for counter in range(8):
            flags.append(image_to_bits(os.path.join(directory, f"mgfs_{counter}.png")))

        self.mstr = image_to_shorts(os.path.join(directory, "mstr.png"))

        self.mbio = flags_to_sequence([*sequence_to_flags(image_to_bytes(os.path.join(directory, "mbio_1.png")))[:4],
                                       *sequence_to_flags(image_to_bytes(os.path.join(directory, "mbio_2.png")))[:4]])

        self.mco2 = image_to_bytes(os.path.join(directory, "mco2.png"))

        self.llan = dict()
        with open(os.path.join(directory, "llan.csv"), "r") as file:
            for line in file.readlines():
                entries = line.rstrip("\n").split(",")
                key = (int(entries[0]), int(entries[1]))
                assert key not in self.llan.keys()
                self.llan[key] = entries[2].strip("\"")

        self.xcot = list()
        with open(os.path.join(directory, "xcot.csv"), "r") as file:
            for line in file.readlines():
                entries = line.rstrip("\n").split(",")
                self.xcot.append((int(entries[0]), (int(entries[1]), int(entries[2])), int(entries[3])))

        self.xsec = list()
        with open(os.path.join(directory, "xsec.csv"), "r") as file:
            for line in file.readlines():
                entries = line.rstrip("\n").split(",")
                self.xsec.append((int(entries[0]), int(entries[1]), (int(entries[2]), int(entries[3]))))

        self.smmw = list()
        with open(os.path.join(directory, "smmw.csv"), "r") as file:
            for line in file.readlines():
                self.smmw.append(int(line.rstrip("\n")))

    def save_to_data(self, directory: str):

        os.makedirs(directory, exist_ok=True)

        bytes_to_image(self.mhei, os.path.join(directory, "mhei.png"), width=self.map_width//2)
        bytes_to_image(self.mlig, os.path.join(directory, "mlig.png"), width=self.map_width//2)
        shorts_to_image(combine_mep(self.mepa, self.mepb), os.path.join(directory, "mep.png"), width=self.map_width)

        for counter, flag in enumerate(sequence_to_flags(self.mgfs)):
            bits_to_image(flag, os.path.join(directory, f"mgfs_{counter}.png"), width=self.map_width)  # noqa

        shorts_to_image(self.mstr, os.path.join(directory, "mstr.png"), width=self.map_width)

        mbio_flags = sequence_to_flags(self.mbio)
        mbio_1 = [*mbio_flags[0:4], *(4*["0" * len(mbio_flags[0])])]
        mbio_2 = [*mbio_flags[4:8], *(4*["0" * len(mbio_flags[0])])]

        bytes_to_image(flags_to_sequence(mbio_1), os.path.join(directory, "mbio_1.png"),
                       width=self.map_width//2)
        bytes_to_image(flags_to_sequence(mbio_2), os.path.join(directory, "mbio_2.png"),
                       width=self.map_width//2)

        bytes_to_image(self.mco2, os.path.join(directory, "mco2.png"), width=self.map_width)
        shorts_to_image(self.mexp, os.path.join(directory, "mexp.png"), width=self.map_width//2)

        with open(os.path.join(directory, "llan.csv"), "w") as file:
            for coordinates, landscape in self.llan.items():
                file.write(f"{coordinates[0]},{coordinates[1]},\"{landscape}\"\n")

        with open(os.path.join(directory, "xcot.csv"), "w") as file:
            for continent_data in self.xcot:
                file.write(f"{continent_data[0]},{continent_data[1][0]},"
                           f"{continent_data[1][1]},{continent_data[2]}\n")

        with open(os.path.join(directory, "xsec.csv"), "w") as file:
            for sector_data in self.xsec:
                file.write(f"{sector_data[0]},{sector_data[1]},{sector_data[2][0]},{sector_data[2][1]}\n")

        with open(os.path.join(directory, "smmw.csv"), "w") as file:
            file.write("\n".join(map(str, self.smmw)))
