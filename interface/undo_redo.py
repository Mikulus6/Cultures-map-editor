from typing import Literal

class MemorySnapshot(dict):
    def __init__(self):
        super().__init__(dict())

    def add_entry(self, section_name: Literal["mepa", "mepb", "mhei", "mstr", "llan"],
                  coordinates, value_before, value_after):
        if value_before == value_after:
            return
        key = (section_name, coordinates)
        if key in self.keys():
            self[key] = [self[key][0], value_after]
        else:
            self[key] = [value_before, value_after]

    def enforce_snapshot(self, editor, direction: Literal["before", "after"]):
        mstr_postdata = list()
        list_of_coordinates = list()
        for key, value in self.items():
            section_name, coordinates = key
            value_sub = value[0] if direction=="before" else value[1]

            match section_name:
                case "mepa":
                    editor.update_triange(coordinates, "a", value_sub, ignore_undo=True)
                    list_of_coordinates.append(coordinates)
                case "mepb":
                    editor.update_triange(coordinates, "b", value_sub, ignore_undo=True)
                    list_of_coordinates.append(coordinates)
                case "mhei":
                    editor.update_height(coordinates, value_sub, as_delta=False, ignore_undo=True)
                    list_of_coordinates.append(coordinates)
                case "mstr":
                    editor.update_structures(coordinates, None, ignore_undo=True)
                    mstr_postdata.append((coordinates, value_sub))
                    list_of_coordinates.append(coordinates)
                case "llan":
                    editor.update_landscape(coordinates, value_sub, ignore_undo=True)
                    list_of_coordinates.append(coordinates)
        for coordinates, value_sub in mstr_postdata:
            editor.update_structures(coordinates, value_sub, ignore_undo=True)
        editor.update_local_secondary_data_multiple_points(list_of_coordinates, margin=5)


class UndoRedoMemory:
    initialized = False
    def __init__(self):
        if self.__class__.initialized:
            raise ValueError(f"{self.__class__.__name__} is a singleton.")
        self.__class__.initialized = True

        self.snapshots = [MemorySnapshot(), MemorySnapshot()]
        self.current_index = 1
        self.undo_wait = False  # Is state after doing undo stuff with unbroken redo chain of actions still active.

    def undo(self, editor):
        if self.current_index == 0:
            return
        elif self.current_index == len(self.snapshots) - 1 and len(self.current_snapshot) == 0:
            self.current_index -= 1
        self.current_snapshot.enforce_snapshot(editor, direction="before")
        self.current_index -= 1
        self.current_index = max(0, self.current_index)
        self.undo_wait = True

    def redo(self, editor):
        if self.current_index == len(self.snapshots) - 1:
            return
        self.current_index += 1
        self.current_snapshot.enforce_snapshot(editor, direction="after")

    def add_entry(self, section_name, coordinates, value_before, value_after):
        if self.undo_wait:
            self.undo_wait = False
            self.current_index += 1
            for i in range(self.current_index, len(self.snapshots)):
                self.snapshots[i] = MemorySnapshot()
            if self.current_index == len(self.snapshots) and len(self.snapshots[-1]) != 0:
                self.snapshots.append(MemorySnapshot())
        if self.current_index >= len(self.snapshots):
            self.current_index = len(self.snapshots) - 1
        self.current_snapshot.add_entry(section_name, coordinates, value_before, value_after)

    def update(self):
        if len(self.current_snapshot) == 0 and self.current_index != 0:
            return
        self.snapshots.append(MemorySnapshot())
        self.undo_wait = True

        for i in range(len(self.snapshots) - 1, -1, -1):
            if len(self.snapshots[i]) == 0 and i > 0:
                del self.snapshots[i]
            else:
                break
        self.current_index = min(self.current_index, len(self.snapshots) - 1)
        if len(self.snapshots) < 2:
            self.snapshots = [MemorySnapshot(), MemorySnapshot()]

    def reset(self):
        self.snapshots = [MemorySnapshot(), MemorySnapshot()]
        self.current_index = 1
        self.undo_wait = False

    @property
    def current_snapshot(self):
        return self.snapshots[self.current_index]


undo_redo_memory = UndoRedoMemory()
