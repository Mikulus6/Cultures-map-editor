import numpy as np
import os

from scripts.array_paste import paste_in_bounds
from scripts.buffer import BufferGiver, BufferTaker
from scripts.const import map_const, section_names
from scripts.flags import sequence_to_flags, flags_to_sequence
from scripts.image import bytes_to_image, shorts_to_image, bits_to_image, rgb_to_image, \
                          image_to_bytes, image_to_shorts, image_to_bits, image_to_rgb
from scripts.report import Report

from sections.biomes import derive_biomes
from sections.pathfinder_blockers import pathfinder_blockers_area_shifted
from sections.continents import load_continents_from_xcot, load_xcot_from_continents
from sections.continents2 import derive_continents
from sections.inland_vertices import inland_vertices_flag
from sections.landscapes import load_landscapes_from_llan, load_llan_from_landscapes
from sections.landscapes_area import landscapes_area_flag
from sections.light import derive_light_map
from sections.mesh_points import combine_mep, split_mep
from sections.pathfinder_blockers import draw_pathfinder_blockers
from sections.run_length import run_length_decryption, run_length_encryption
from sections.sectors import load_sectors_from_xsec, load_xsec_from_sectors
from sections.sectors_flag import sectors_flag
from sections.structures import update_structures, validate_structures_continuity, structures_to_rgb, rgb_to_structures
from sections.summary import update_summary
from sections.walk_sector_points import update_sectors, draw_sectors_connections, sector_width
from supplements.textures import mep_colormap


class Map:
    _number_of_sections = 13
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

    def update_all(self, *, exclude_continents=False, report: Report = None):
        if report is None: report = Report(muted=True)
        elif report: report = Report(muted=False)
        if not exclude_continents:
            report.report("Updating continents.")
            self.update_continents()

        report.report("Updating summary.")
        self.update_summary()

        report.report("Updating exploration.")
        self.update_exploration()

        report.report("Updating light.")
        self.update_light()

        report.report("Updating structures.")
        self.update_structures()

        report.report("Updating biomes.")
        self.update_biomes()

        report.report("Updating ground set flags.")
        self.update_ground_set_flags(pre_sectors_update=True, report=report)

        report.report("Updating sectors.")
        self.update_sectors()

        self.update_ground_set_flags(post_sectors_update=True, report=report)

        report.report("Map updates are finished.")

    def update_summary(self):
        self.smmw = update_summary(self.map_width, self.map_height)

    def update_continents(self):
        self.mco2, self.xcot = derive_continents(self.mepa, self.mepb, self.map_width, self.map_height)

    def update_exploration(self):
        self.mexp = b"\x00" * (self.map_width*self.map_height//2)

    def update_light(self):
        self.mlig = derive_light_map(self.mhei, self.mepa, self.mepb, self.map_width, self.map_height)

    def update_structures(self):
        self.mstr = update_structures(self.mstr, self.mco2, self.xcot, self.map_width, self.map_height)

    def update_biomes(self):
        self.mbio = derive_biomes(self.mepa, self.mepb, self.mstr, self.map_width, self.map_height)

    def update_ground_set_flags(self, post_sectors_update=False, pre_sectors_update=False, report: Report = None):
        if report is None: report = Report(muted=True)

        if post_sectors_update:
            report.report("Updating ground set flag sectors data.")
            mgfs_flags = sequence_to_flags(self.mgfs)
            mgfs_flags[3] = sectors_flag(self.xsec, self.map_width, self.map_height)
            self.mgfs = flags_to_sequence(mgfs_flags)

        else:

            if pre_sectors_update:
                report.report("Updating ground set flag sectors data.")
                mgfs_flags_3 = sectors_flag([], self.map_width, self.map_height)
            else:
                mgfs_flags_3 = sequence_to_flags(self.mgfs)[3]

            report.report("Updating ground set flag unused data.")
            mgfs_flags_4 = "0" * (self.map_width * self.map_height)

            report.report("Updating ground set flag landscapes' ExtendedArea.")
            mgfs_flags_5 = landscapes_area_flag(self.llan, self.map_width, self.map_height, area_type="Extended")

            report.report("Updating ground set flag in-land vertices.")
            mgfs_flags_6 = inland_vertices_flag(self.mepa, self.mepb, self.map_width, self.map_height)

            report.report("Updating ground set flag landscapes' BaseArea.")
            mgfs_flags_7 = landscapes_area_flag(self.llan, self.map_width, self.map_height, area_type="Base")

            report.report("Updating ground set flag connections (backslash direction).")
            mgfs_flags_0 = pathfinder_blockers_area_shifted(mgfs_flags_7, self.mepa, self.mepb, self.mhei,
                                                            self.map_width, self.map_height, flag_index=0)

            report.report("Updating ground set flag connections (forward slash direction).")
            mgfs_flags_1 = pathfinder_blockers_area_shifted(mgfs_flags_7, self.mepa, self.mepb, self.mhei,
                                                            self.map_width, self.map_height, flag_index=1)

            report.report("Updating ground set flag connections (horizontal direction).")
            mgfs_flags_2 = pathfinder_blockers_area_shifted(mgfs_flags_7, self.mepa, self.mepb, self.mhei,
                                                            self.map_width, self.map_height, flag_index=2)

            self.mgfs = flags_to_sequence([mgfs_flags_0, mgfs_flags_1, mgfs_flags_2, mgfs_flags_3,
                                           mgfs_flags_4, mgfs_flags_5, mgfs_flags_6, mgfs_flags_7])

    def update_sectors(self):
        self.xsec = update_sectors(self.mgfs, self.mco2, self.xcot, self.map_width, self.map_height)

    # ====================================  testers  ====================================

    def test_all(self):
        try:
            assert self.test_continents()
            assert self.test_summary()
            assert self.test_exploration()
            assert self.test_light()
            assert self.test_biomes()
            assert self.test_structures()
            assert self.test_sectors()
            assert self.test_ground_set_flags()
        except AssertionError:
            return False
        else:
            return True

    def test_summary(self):

        # Some maps with incorrectly set flag might not pass this test.
        # For details look into comments in module where function called below is defined.

        return self.smmw == self.update_summary()

    def test_continents(self):
        return (self.mco2, self.xcot) == derive_continents(self.mepa, self.mepb, self.map_width, self.map_height)

    def test_exploration(self):
        return self.mexp == b"\x00" * (self.map_width*self.map_height//2)

    def test_light(self):
        return self.mlig == derive_light_map(self.mhei, self.mepa, self.mepb, self.map_width, self.map_height)

    def test_structures(self):
        return self.mstr == update_structures(self.mstr, self.mco2, self.xcot, self.map_width, self.map_height) and \
               validate_structures_continuity(self.mstr, self.map_width, self.map_height)

    def test_biomes(self):
        return self.mbio == derive_biomes(self.mepa, self.mepb, self.mstr, self.map_width, self.map_height)

    def test_ground_set_flags(self):
        # Maps created before 18th August 2000 might not pass this test due to different landscapes' shapes.

        mgfs_flags_3 = sectors_flag(self.xsec, self.map_width, self.map_height)
        mgfs_flags_4 = "0" * (self.map_width * self.map_height)
        mgfs_flags_5 = landscapes_area_flag(self.llan, self.map_width, self.map_height, area_type="Extended")
        mgfs_flags_6 = inland_vertices_flag(self.mepa, self.mepb, self.map_width, self.map_height)
        mgfs_flags_7 = landscapes_area_flag(self.llan, self.map_width, self.map_height, area_type="Base")

        mgfs_flags_0 = pathfinder_blockers_area_shifted(mgfs_flags_7, self.mepa, self.mepb, self.mhei,
                                                        self.map_width, self.map_height, flag_index=0)

        mgfs_flags_1 = pathfinder_blockers_area_shifted(mgfs_flags_7, self.mepa, self.mepb, self.mhei,
                                                        self.map_width, self.map_height, flag_index=1)

        mgfs_flags_2 = pathfinder_blockers_area_shifted(mgfs_flags_7, self.mepa, self.mepb, self.mhei,
                                                        self.map_width, self.map_height, flag_index=2)

        mgfs_new = flags_to_sequence([mgfs_flags_0, mgfs_flags_1, mgfs_flags_2, mgfs_flags_3,
                                      mgfs_flags_4, mgfs_flags_5, mgfs_flags_6, mgfs_flags_7])

        return mgfs_new == self.mgfs

    def test_sectors(self):
        # return check_sectors_coherency(self.mco2, self.xsec, self.map_width, self.map_height)
        return self.xsec == update_sectors(self.mgfs, self.mco2, self.xcot, self.map_width, self.map_height)

    # =================================== load & save ===================================

    def load(self, filename: str):

        self.__init__()

        with open(filename, 'rb') as file:
            buffer = BufferGiver(file.read())

        self.map_version = buffer.unsigned(2)  # noqa: E221
        self.map_width   = buffer.unsigned(2)  # noqa: E221
        self.map_height  = buffer.unsigned(2)  # noqa: E221

        match self.map_version:
            case 6:
                self.__class__ = MapVersion6
                self.__init__()
                self.load(filename)
                return

            case 11 | 12:
                for _ in range(self.__class__._number_of_sections):
                    section_name = buffer.string(4)[::-1]  # noqa: E221
                    section_length = buffer.unsigned(4)    # noqa: E221

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
                            case _: pass

                    if section_name == "\x00end":
                        break
                assert len(buffer) == 0

            case _: raise NotImplementedError


    def save(self, filename: str):

        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
        except FileNotFoundError:
            pass

        buffer = BufferTaker()

        buffer.unsigned(self.map_version if self.map_version != 6 else 12, length=2)
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

    def pack(self, directory: str, report: bool = False):

        report = Report(muted=not report)

        report.report("Reading input files.")
        self.mhei, width = image_to_bytes(os.path.join(directory, "heightmap.png"), get_width=True)
        self.mepa, self.mepb = split_mep(image_to_shorts(os.path.join(directory, "terrain.png"), colormap=mep_colormap))

        self.map_version = 12
        self.map_width = width * 2
        self.map_height = (len(self.mhei)//width) * 2

        self.llan = dict()
        with open(os.path.join(directory, "landscapes.csv"), "r") as file:
            for line in file.readlines():
                entries = line.rstrip("\n").split(",")
                key = (int(entries[0]), int(entries[1]))
                assert key not in self.llan.keys()
                self.llan[key] = entries[2].strip("\"")

        report.report("Updating continents.")
        self.update_continents()

        self.mstr = rgb_to_structures(image_to_rgb(os.path.join(directory, "structures.png")),
                                      self.mco2, self.xcot, self.map_width, self.map_height)

        self.update_all(exclude_continents=True, report=report)

    def extract(self, directory: str, expand=False):

        # Setting 'expand' to True makes this conversion one-directional.

        os.makedirs(directory, exist_ok=True)

        bytes_to_image(self.mhei, os.path.join(directory, "heightmap.png"), width=self.map_width//2,
                       expansion_mode="hexagon" if expand else None)

        shorts_to_image(combine_mep(self.mepa, self.mepb), os.path.join(directory, "terrain.png"), width=self.map_width,
                        expansion_mode="triangle" if expand else None, colormap=mep_colormap)

        with open(os.path.join(directory, "landscapes.csv"), "w") as file:
            for coordinates, landscape in self.llan.items():
                file.write(f"{coordinates[0]},{coordinates[1]},\"{landscape}\"\n")

        rgb_to_image(structures_to_rgb(self.mstr, self.map_width, self.map_height),
                     os.path.join(directory, "structures.png"), width=self.map_width,
                     expansion_mode="hexagon" if expand else None)

    # ============================= debug load & debug save =============================

    def _load_from_raw_data(self, directory: str, interprete_structures=False):

        with open(os.path.join(directory, "header.csv"), "r") as file:
            self.map_version, self.map_width, self.map_height = map(int, file.read().strip("\n").split(","))

        self.mhei = image_to_bytes(os.path.join(directory, "mhei.png"))
        self.mlig = image_to_bytes(os.path.join(directory, "mlig.png"))
        self.mepa, self.mepb = split_mep(image_to_shorts(os.path.join(directory, "mep.png")))

        flags = []
        for counter in range(8):
            flags.append(image_to_bits(os.path.join(directory, f"mgfs_{counter}.png")))

        if interprete_structures:
            self.mstr = rgb_to_structures(image_to_rgb(os.path.join(directory, "mstr.png")),
                                          self.mco2, self.xcot, self.map_width, self.map_height)
        else:
            self.mstr = flags_to_sequence([*sequence_to_flags(image_to_bytes(
                                           os.path.join(directory, "mstr_1.png")))[:8],
                                           *(7*["0" * (self.map_width * self.map_height)]),
                                           image_to_bits(os.path.join(directory, "mstr_2.png"))], bytes_per_entry=2)

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
                self.xsec.append([int(entries[0]), entries[1].strip("\""), (int(entries[2]), int(entries[3]))])

        self.smmw = list()
        with open(os.path.join(directory, "smmw.csv"), "r") as file:
            for line in file.readlines():
                self.smmw.append(int(line.rstrip("\n")))

    def _extract_to_raw_data(self, directory: str, interprete_structures=False, interprete_sectors=False, expand=False):

        # Setting 'expand' to True makes this conversion one-directional.

        os.makedirs(directory, exist_ok=True)

        with open(os.path.join(directory, "header.csv"), "w") as file:
            file.write(f"{self.map_version},{self.map_width},{self.map_height}\n")

        os.makedirs(directory, exist_ok=True)

        bytes_to_image(self.mhei, os.path.join(directory, "mhei.png"), width=self.map_width//2,
                       expansion_mode="hexagon" if expand else None)
        bytes_to_image(self.mlig, os.path.join(directory, "mlig.png"), width=self.map_width//2,
                       expansion_mode="hexagon" if expand else None)
        shorts_to_image(combine_mep(self.mepa, self.mepb), os.path.join(directory, "mep.png"), width=self.map_width,
                        expansion_mode="triangle" if expand else None)

        if expand:
            draw_pathfinder_blockers(self.mgfs, self.map_width, self.map_height).save(os.path.join(directory,
                                                                                                   "mgfs_0_1_2.png"))
        for counter, flag in enumerate(sequence_to_flags(self.mgfs)):
            if expand and counter < 3:
                continue
            bits_to_image(flag, os.path.join(directory, f"mgfs_{counter}.png"), width=self.map_width,
                          expansion_mode="hexagon" if expand else None)  # noqa

        mstr_flags = sequence_to_flags(self.mstr, bytes_per_entry=2)

        if interprete_structures:
            rgb_to_image(structures_to_rgb(self.mstr, self.map_width, self.map_height),
                         os.path.join(directory, "mstr.png"), width=self.map_width,
                         expansion_mode="hexagon" if expand else None)
        else:
            mstr_1 = mstr_flags[0:8]
            mstr_2 = mstr_flags[15]

            bytes_to_image(flags_to_sequence(mstr_1), os.path.join(directory, "mstr_1.png"), width=self.map_width,
                           expansion_mode="parallelogram" if expand else None)
            bits_to_image(mstr_2, os.path.join(directory, "mstr_2.png"), width=self.map_width,
                          expansion_mode="parallelogram" if expand else None)
            del mstr_1, mstr_2

        mbio_flags = sequence_to_flags(self.mbio)
        mbio_1 = [*mbio_flags[0:4], *(4*["0" * len(mbio_flags[0])])]
        mbio_2 = [*mbio_flags[4:8], *(4*["0" * len(mbio_flags[0])])]

        bytes_to_image(flags_to_sequence(mbio_1), os.path.join(directory, "mbio_1.png"),
                       width=self.map_width//2, expansion_mode="hexagon" if expand else None)
        bytes_to_image(flags_to_sequence(mbio_2), os.path.join(directory, "mbio_2.png"),
                       width=self.map_width//2, expansion_mode="hexagon" if expand else None)

        bytes_to_image(self.mco2, os.path.join(directory, "mco2.png"), width=self.map_width,
                       expansion_mode="hexagon" if expand else None)
        shorts_to_image(self.mexp, os.path.join(directory, "mexp.png"), width=self.map_width//2,
                        expansion_mode="hexagon" if expand else None)

        with open(os.path.join(directory, "llan.csv"), "w") as file:
            for coordinates, landscape in self.llan.items():
                file.write(f"{coordinates[0]},{coordinates[1]},\"{landscape}\"\n")

        with open(os.path.join(directory, "xcot.csv"), "w") as file:
            for continent_data in self.xcot:
                file.write(f"{continent_data[0]},{continent_data[1][0]},"
                           f"{continent_data[1][1]},{continent_data[2]}\n")

        with open(os.path.join(directory, "xsec.csv"), "w") as file:
            for sector_data in self.xsec:
                file.write(f"{sector_data[0]},\"{sector_data[1]}\",{sector_data[2][0]},{sector_data[2][1]}\n")

        with open(os.path.join(directory, "smmw.csv"), "w") as file:
            file.write("\n".join(map(str, self.smmw)))

        if interprete_sectors:
            draw_sectors_connections(self.mco2, self.xsec, self.map_width, self.map_height,
                                     expansion_mode="hexagon" if expand else None).save(os.path.join(directory,
                                                                                                     "xsec.png"))

    def to_bytearrays(self):
        for section_name in map_const.keys():
            vars(self)[section_name] = bytearray(vars(self)[section_name])

    def from_bytearrays(self):
        for section_name in map_const.keys():
            vars(self)[section_name] = bytes(vars(self)[section_name])

    # ============================ editor-related functions =============================

    # Following functions operate only on primary sections. All secondary sections should be updated after using those
    # functions if they are meant to be used outside regular editor.

    new_map_default_mep_id = 126

    def empty(self, size):

        assert size[0] % 20 == size[1] % 20 == 0

        self.map_version = 12
        self.map_width = size[0]
        self.map_height = size[1]

        self.mhei = b"\x00" * (size[0] * size[1] // 4)
        self.mepa = int.to_bytes(Map.new_map_default_mep_id, length=2, byteorder="little") * (size[0] * size[1] // 4)
        self.mepb = int.to_bytes(Map.new_map_default_mep_id, length=2, byteorder="little") * (size[0] * size[1] // 4)
        self.mstr = b"\x00" * (size[0] * size[1] * 2)
        self.llan = dict()

        self.update_light()

    def resize_visible(self, deltas: (int, int, int, int)):
        # deltas = (top, bottom, left, right)
        are_arrays = isinstance(self.mhei, bytearray)

        mhei_ndarray = np.frombuffer(self.mhei, dtype=np.ubyte).reshape((self.map_height // 2, self.map_width // 2))
        mlig_ndarray = np.frombuffer(self.mlig, dtype=np.ubyte).reshape((self.map_height // 2, self.map_width // 2))
        mepa_ndarray = np.frombuffer(self.mepa, dtype=np.ushort).reshape((self.map_height // 2, self.map_width // 2))
        mepb_ndarray = np.frombuffer(self.mepb, dtype=np.ushort).reshape((self.map_height // 2, self.map_width // 2))
        mstr_ndarray = np.frombuffer(self.mstr, dtype=np.ushort).reshape((self.map_height, self.map_width))

        self.map_width += deltas[2] + deltas[3]
        self.map_height += deltas[0] + deltas[1]

        self.llan = {(key[0] + deltas[2], key[1] + deltas[0]): value for key, value in self.llan.items()
                     if 0 <= key[0] + deltas[2] < self.map_width and 0 <= key[1] + deltas[0] < self.map_height}

        mhei_ndarray_new = np.zeros((self.map_height // 2, self.map_width // 2), dtype=np.ubyte)
        mlig_ndarray_new = np.ones((self.map_height // 2, self.map_width // 2), dtype=np.ubyte) * 127
        mepa_ndarray_new = np.ones((self.map_height // 2, self.map_width // 2), dtype=np.ushort) * \
                                                                                              Map.new_map_default_mep_id
        mepb_ndarray_new = np.ones((self.map_height // 2, self.map_width // 2), dtype=np.ushort) * \
                                                                                              Map.new_map_default_mep_id
        mstr_ndarray_new = np.zeros((self.map_height, self.map_width), dtype=np.ushort)

        paste_in_bounds(mhei_ndarray_new, mhei_ndarray, deltas[0] // 2, deltas[2] // 2)
        paste_in_bounds(mlig_ndarray_new, mlig_ndarray, deltas[0] // 2, deltas[2] // 2)
        paste_in_bounds(mepa_ndarray_new, mepa_ndarray, deltas[0] // 2, deltas[2] // 2)
        paste_in_bounds(mepb_ndarray_new, mepb_ndarray, deltas[0] // 2, deltas[2] // 2)
        paste_in_bounds(mstr_ndarray_new, mstr_ndarray, deltas[0], deltas[2])

        self.mhei = mhei_ndarray_new.tobytes()
        self.mlig = mlig_ndarray_new.tobytes()
        self.mepa = mepa_ndarray_new.tobytes()
        self.mepb = mepb_ndarray_new.tobytes()
        self.mstr = mstr_ndarray_new.tobytes()

        self.update_light()
        self.xsec = [[0, "00000000", (0, 0)]] * (self.map_width * self.map_height // sector_width**2)

        if are_arrays:
            self.to_bytearrays()


class MapVersion6(Map):
    _version_number = 6

    def __init__(self):
        super().__init__()
        self.map_version = self.__class__._version_number
        self.m_unknown = b""

    def load(self, filename: str):
        self.__init__()

        with open(filename, 'rb') as file:
            buffer = BufferGiver(file.read())

        self.map_version = buffer.unsigned(2)      # noqa: E221
        self.map_width   = buffer.unsigned(2) * 2  # noqa: E221
        self.map_height  = buffer.unsigned(2) * 2  # noqa: E221

        if self.map_version != self.__class__._version_number:
            del self.m_unknown
            self.__class__ = Map
            self.__init__()
            self.load(filename)
            return

        self.mhei =  buffer.bytes(self.map_width * self.map_height // 4)
        self.mlig =  buffer.bytes(self.map_width * self.map_height // 4)
        self.mepa = buffer.bytes(self.map_width * self.map_height // 2)
        self.mepb = buffer.bytes(self.map_width * self.map_height // 2)

        self.m_unknown = buffer.bytes(self.map_width * self.map_height * 3 // 4)  # Purpose of this section is unknown.
        assert self.m_unknown == len(self.m_unknown) * b"\x00"
        assert buffer.signed(2) == -1
        assert len(buffer) == 0

        # Structures must be declared, because this is both a primary section and something dependent on map size.
        self.mstr = b"\x00" * (self.map_width * self.map_height * 2)

    def save(self, filename: str, *, use_original_format: bool = False):

        if use_original_format:

            assert self.map_version == self.__class__._version_number

            buffer_taker = BufferTaker()
            buffer_taker.unsigned(self.map_version,    length=2)
            buffer_taker.unsigned(self.map_width // 2,  length=2)
            buffer_taker.unsigned(self.map_height // 2, length=2)
            buffer_taker.bytes(self.mhei)
            buffer_taker.bytes(self.mlig)
            buffer_taker.bytes(self.mepa)
            buffer_taker.bytes(self.mepb)
            buffer_taker.bytes(b"\x00" * (self.map_width * self.map_height * 3 // 4))
            buffer_taker.signed(-1, length=2)

            with open(filename, 'wb') as file:
                file.write(bytes(buffer_taker))

        else:
            super().save(filename)

    def pack(self, directory: str, report: bool = False):

        super().pack(directory, report)
        self.map_version = self.__class__._version_number
        self.m_unknown = b"\x00" * (self.map_width * self.map_height * 3 // 4)

    def _load_from_raw_data(self, directory: str, interprete_structures=False):
        if interprete_structures:
            raise AttributeError(f"Maps from version {self.__class__._version_number} do not contain structures")

        with open(os.path.join(directory, "header.csv"), "r") as file:
            self.map_version, self.map_width, self.map_height = map(int, file.read().strip("\n").split(","))
            print(self.map_width, self.map_height)
            self.map_width *= 2
            self.map_height *= 2

        self.mhei = image_to_bytes(os.path.join(directory, "mhei.png"))
        self.mlig = image_to_bytes(os.path.join(directory, "mlig.png"))
        self.mepa, self.mepb = split_mep(image_to_shorts(os.path.join(directory, "mep.png")))
        self.m_unknown = bytes([value for rgb in image_to_rgb(os.path.join(directory, "unknown.png")) for value in rgb])

    def _extract_to_raw_data(self,directory: str, interprete_structures=False, interprete_sectors=False, expand=False):

        # Setting 'expand' to True makes this conversion one-directional.

        if interprete_structures or interprete_sectors:
            raise AttributeError(f"Maps from version {self.__class__._version_number} " + \
                                  "do not contain structures or sectors")

        os.makedirs(directory, exist_ok=True)

        with open(os.path.join(directory, "header.csv"), "w") as file:
            file.write(f"{self.map_version},{self.map_width // 2},{self.map_height // 2}\n")

        os.makedirs(directory, exist_ok=True)

        bytes_to_image(self.mhei, os.path.join(directory, "mhei.png"), width=self.map_width // 2,
                       expansion_mode="hexagon" if expand else None)
        bytes_to_image(self.mlig, os.path.join(directory, "mlig.png"), width=self.map_width // 2,
                       expansion_mode="hexagon" if expand else None)
        shorts_to_image(combine_mep(self.mepa, self.mepb), os.path.join(directory, "mep.png"), width=self.map_width,
                        expansion_mode="triangle" if expand else None)
        rgb_to_image([tuple(self.m_unknown[i:i+3]) for i in range(0, len(self.m_unknown), 3)],
                     os.path.join(directory, "unknown.png"), width=self.map_width // 2,
                     expansion_mode="hexagon" if expand else None)


if __name__ == "__main__":  # This part of code is responsible for testing correctness of derivations.

    # Following directories should be created manually
    directory_input = "maps"  # put all *.map files there
    directory_output = "edit"  # all extracted maps will be here

    for item in os.listdir(directory_input):

        if os.path.splitext(item)[1] != ".map":
            continue

        path = os.path.join(directory_input, item)
        directory_path = os.path.join(directory_output, os.path.splitext(item)[0])
        print(item)

        try:
            map_object = Map()
            map_object.load(path)
            map_object.extract(directory_path)
            map_object._extract_to_raw_data(os.path.join(directory_path, "raw"))  # noqa

            map_object_new = MapVersion6() if isinstance(map_object, MapVersion6) else Map()
            map_object_new.pack(directory_path)
            map_object_new._extract_to_raw_data(os.path.join(directory_path, "raw2"))  # noqa

            del map_object, map_object_new

            # Compare 'raw' and 'raw2' folders to verify the correctness of derivations.

        except NotImplementedError:
            print("*not implemented*")
