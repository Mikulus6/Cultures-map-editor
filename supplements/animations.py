import os
from math import ceil, log2
from tkinter import messagebox
from scripts.animation import Animation
from scripts.buffer import BufferGiver, BufferTaker
from scripts.report import Report
from supplements.bitmaps import Bitmap
from supplements.landscapedefs import landscapedefs, name_max_length
from supplements.remaptables import remaptables


default_shading_factor = 128

animations_directory = "data_v\\ve_graphics\\bobmanager"


def load_animation(landscape_name) -> Animation:
    landscape = landscapedefs[landscape_name]
    boblibs = landscape.get("BobLibs", ("", ""))
    remapname = landscape.get("RemapName", None)

    # Note that remaptables are not responsible for landscapes display in-game, yet they are a good visual approximation
    # for all landscapes.

    if remapname is not None: remaptable = remaptables[remapname]
    else:                     remaptable = None

    if boblibs[0] == "":
        return Animation.empty()

    first_bob = landscape["FirstBob"]
    elements = landscape["Elements"]
    shading_factor = landscape.get("ShadingFactor", default_shading_factor)
    high_color_shading_mode = landscape.get("HighColorShadingMode", 0)

    path_packed = os.path.join(animations_directory, boblibs[0]+".bmd")
    path_masked = os.path.join(animations_directory, boblibs[1]+".bmd")

    bitmap_packed = Bitmap()
    bitmap_masked = Bitmap()
    bitmap_packed.load(path_packed)
    bitmap_masked.load(path_masked)
    animation_packed = bitmap_packed.to_animation(remaptable, 255, first_bob, elements,
                                                  high_color_shading_mode, masked_file=False)
    animation_masked = bitmap_masked.to_animation(remaptable, shading_factor, first_bob, elements,
                                                  high_color_shading_mode, masked_file=True)

    animation_masked.paste(animation_packed)
    return animation_masked


class Animations(dict):
    """Dictionary with animations of landscapes"""
    initialized = False
    cache_filepath = "cache.bin"
    name_max_bytes = ceil(log2(name_max_length))
    pygame_converted = False

    def __init__(self, *, report=False):
        super().__init__(dict())
        if self.__class__.initialized:
            raise ValueError(f"{self.__class__.__name__} is a singleton.")
        self.__class__.initialized = True
        self.__class__.pygame_converted = False

        # On device where this part of code was tested, loading all animations directly from *.bmd files and applying
        # palettes takes around 15 minutes, while loading it from cache file takes around 3 seconds. Loading time is
        # therefore improved by around 27500% by cache usage.

        try:
            self.load_cache()
        except FileNotFoundError:
            if messagebox.askyesno("File not found",
                                   "Cache file not found. Do you want to extract bitmaps?\n\n"+\
                                   "This may take a few minutes. There will be no visual progress indicator until "+\
                                   "everything is loaded up. If this is your first time using the editor, note that "+\
                                   "this loading process will not happen again as long as cache file remains in your "+\
                                   "files. Alternatively you can try to find pre-generated cache online.",
                                   icon="warning"):
                print("Warning: cache file not found. Animations will be extracted from game files.")
                self.load_all_animations(report=report)
                self.save_cache()
            else:
                exit()

    def load_all_animations(self, *, report=False) -> dict:
        report = Report(muted=not report)
        self.clear()
        for name in landscapedefs.keys():
            self[name] = load_animation(name)
            report.report(f"Loaded landscape \"{name}\".")

    def export_all_animations(self, directory: str, *, report=False) -> dict:

        if self.__class__.pygame_converted:
            raise ValueError("Animations cannot be saved after conversion to pygame.")

        os.makedirs(directory, exist_ok=True)
        report = Report(muted=not report)
        for name in self.keys():
            self[name].save(os.path.join(directory, name+".webp"))
            report.report(f"Saved landscape \"{name}\".")

    # Following two methods do not correspond to any binary data present in game files. This is merely a project
    # convention for storing animations as bytes.

    def save_cache(self):

        if self.__class__.pygame_converted:
            raise ValueError("Cache cannot be saved after conversion to pygame.")

        buffer_taker = BufferTaker()
        buffer_taker.unsigned(len(self), length=4)
        for name, animation in self.items():
            buffer_taker.unsigned(len(name), length=self.__class__.name_max_bytes)
            buffer_taker.string(name)
            buffer_taker.unsigned(len(bytes(animation)), length=4)
            buffer_taker.bytes(bytes(animation))

        with open(self.__class__.cache_filepath, "wb") as file:
            file.write(bytes(buffer_taker))

    def load_cache(self):
        self.clear()
        with open(self.__class__.cache_filepath, "rb") as file:
            buffer = BufferGiver(file.read())
        for _ in range(buffer.unsigned(length=4)):
            name = buffer.string(length=buffer.unsigned(length=self.__class__.name_max_bytes))
            animation = Animation.from_bytes(buffer.bytes(buffer.unsigned(length=4)))
            self[name] = animation
        self.__class__.pygame_converted = False

    def pygame_convert(self):
        # Note that this process is currently irreversible. It also requires pygame display to be present.
        if self.__class__.pygame_converted:
            return
        for name, animation in self.items():
            animation.convert_pygame()
        self.__class__.pygame_converted = True


animations = Animations(report=True)
