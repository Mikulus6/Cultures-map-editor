from scripts.buffer import BufferGiver, data_encoding
from scripts.data_loader import load_ini_as_dict
from supplements.read import read

_unassigned_memory_short = b"\xcd\xcd"

animation_descriptions_cdf_path = "data_v\\ve_graphics\\creatures\\z_animation_descriptions.cdf"
animation_descriptions_cif_path = "data_v\\ve_graphics\\creatures\\z_animation_descriptions.cif"

random_remaps_path         = "data_v\\ve_graphics\\creatures\\x_random_remaps.cif"
creature_descriptions_path = "data_v\\ve_graphics\\creatures\\z_creature_descriptions.cif"
walkdata_descriptions_path = "data_v\\ve_graphics\\creatures\\z_walkdata_descriptions.cif"


class AnimationDescriptions(dict):

    def __init__(self, cif_path: str = animation_descriptions_cif_path, *, load_cdf: bool = False):
        super().__init__(load_ini_as_dict(cif_path,
                                          allowed_section_names=("AnimationType",),
                                          entries_duplicated=("Bobs", "Event", "EventSound"),
                                          global_key=lambda x: x["Name"],
                                          merge_duplicates=True))
        if load_cdf:
            # Content stored in z_animation_descriptions.cdf is entirely reduntant to information stored in three other
            # files. These are: remaptables.cif, soundfx.cif, and z_animation_descriptions.cif.
            self.load_cdf()

    def load_cdf(self, cdf_path: str = animation_descriptions_cdf_path):
        buffer = BufferGiver(read(cdf_path, mode="rb"))

        number_of_entries = buffer.unsigned(length=4)
        assert len(self) <= number_of_entries  # There might be duplicates.

        remaptables_16_names = dict()
        event_sounds_names   = dict()

        for _ in range(number_of_entries):

            name_raw = buffer.bytes(length=50)
            name_length = name_raw.find(0)
            name = str(name_raw[:name_length], encoding=data_encoding)

            assert self[name].get("Mode", 1) == buffer.unsigned(2)
            assert self[name]["Speed"] == buffer.unsigned(2)
            assert self[name]["Speed"] * buffer.unsigned(length=2) == 12
            assert self[name]["Frames"] == buffer.unsigned(length=2)
            assert self[name].get("Replays", 0) == buffer.signed(2)
            assert len(self[name].get("Event", [])) // 2 == buffer.signed(2)
            assert self[name].get("StartDirection", 100) == buffer.unsigned(1)
            assert self[name].get("EndDirection", 100) == buffer.unsigned(1)

            assert buffer.unsigned(2) == 0

            remaptable_16_id_1 = buffer.signed(2)
            remaptable_16_id_2 = buffer.signed(2)
            # Identification number of RemapTable16 is counted from zero by order of appearance in remaptables.cif file.

            for remaptable_index, remaptable_id in enumerate((remaptable_16_id_1, remaptable_16_id_2)):
                if remaptable_id == -1:
                    continue
                elif remaptable_id in remaptables_16_names.keys():
                    assert remaptables_16_names[remaptable_id] == self[name]["CarryGoodRemapTables"][remaptable_index]
                else:
                    remaptables_16_names[remaptable_id] = self[name]["CarryGoodRemapTables"][remaptable_index]

            bob_names_1 = list()
            bob_names_2 = list()

            while (flag := buffer.unsigned(length=1)) == 1:  # Always 19 iterations in existing entries.
                bob_names_1.append(buffer.string(buffer.unsigned(1)))
                assert buffer.unsigned(length=1) == 0

            assert flag == 0
            assert buffer.unsigned(length=1) == 0

            while (flag := buffer.unsigned(length=1)) == 1:  # Always 17 iterations in existing entries.
                bob_names_2.append(buffer.string(buffer.unsigned(1)))
                assert buffer.unsigned(length=1) == 0

            assert flag == 0
            assert buffer.unsigned(length=5) == 0

            if buffer.unsigned(length=1) == 1:
                assert self[name]["ShadowBobLibrary"].lower() == buffer.string(buffer.unsigned(1)).lower()
                assert buffer.unsigned(length=1) == 0

            assert bob_names_1[0].lower() == self[name]["BobLibrary"].lower()
            assert bob_names_1[1:] == [f"Overlay_Head_{x:02d}" for x in range(18)]
            assert bob_names_2 == [f"Overlay_Head_{x:02d}" for x in range(20, 27)] + \
                                  [f"Overlay_Cap_{x:02d}" for x in range(10)]

            for bob in self[name]["Bobs"]:
                assert bob + self[name]["BobOffset"] == buffer.unsigned(length=2)

            events = list()
            event_sounds = list()

            for _ in range(len(self[name].get("Event", [])) // 2):
                events.extend([buffer.unsigned(2), buffer.unsigned(2)])

                event_sound = buffer.unsigned(2)
                if  int.to_bytes(event_sound, length=2) != _unassigned_memory_short:
                    event_sounds.append(event_sound)

            assert len(event_sounds) == len(self[name].get("EventSound", []))

            for event_sound_id, event_sound_name in zip(event_sounds, self[name].get("EventSound", [])):

                if event_sound_id in event_sounds_names.keys():
                    assert event_sounds_names[event_sound_id].lower() == event_sound_name.lower()
                else:
                    # Identification number of SoundFX is counted from zero by order of appearance in soundfx.cif file.
                    event_sounds_names[event_sound_id] = event_sound_name.lower()


animation_descriptions = AnimationDescriptions(load_cdf=False)

random_remaps = \
    load_ini_as_dict(random_remaps_path,
                     allowed_section_names=("RemapRandom",),
                     entries_duplicated=("RemapRandom",),
                     global_key=lambda x: x["Name"],
                     merge_duplicates=False)

creature_descriptions = \
    load_ini_as_dict(creature_descriptions_path,
                     allowed_section_names=("CreatureType",),
                     entries_duplicated=("AllowsJobType", "Animation", "AnimationX", "WalkType", "RemapRandom"),
                     global_key=lambda x: x["Name"],
                     merge_duplicates=False)

walkdata_descriptions = \
    load_ini_as_dict(walkdata_descriptions_path,
                     allowed_section_names=("WalkDataType",),
                     entries_duplicated=("WaitAnimation", "WaitAnimationX"),
                     global_key=lambda x: x["Name"],
                     merge_duplicates=True)
