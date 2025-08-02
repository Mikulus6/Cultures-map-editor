import os
from math import ceil, log2
from sys import exit as sys_exit
import tkinter as tk
from tkinter import Tk, ttk, messagebox
import time
from scripts.animation import Animation
from scripts.buffer import BufferGiver, BufferTaker
from scripts.fallback import fallback_directories, load_with_fallback
from scripts.report import Report
from supplements.bitmaps import Bitmap
from supplements.landscapedefs import landscapedefs, name_max_length
from supplements.remaptables import remaptables


class LoadingVisuals:
    def __init__(self):
        self.root = None
        self.progress = None
        self.loading_text = None
        self.estimate_text = None
        self.closed = False
        self.start_time = 0

    def start(self):
        def on_close():
            self.root.quit()
            self.root.destroy()
            self.closed = True

        self.root = Tk()
        self.root.title("Loading bitmaps")
        self.root.geometry("300x70")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", on_close)
        self.root.attributes("-topmost", True)
        self.loading_text = tk.StringVar()
        self.estimate_text = tk.StringVar()
        self.closed = False

        self.loading_text.set("...")
        self.estimate_text.set("...")
        tk.Label(self.root, textvariable=self.loading_text).grid(row=0, column=0, sticky="w")
        tk.Label(self.root, textvariable=self.estimate_text).grid(row=2, column=0, sticky="w")
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress.grid(row=1, column=0)
        self.start_time = time.time()

    def step(self, value, landscape_name):
        self.loading_text.set(f"Loaded landscape \"{landscape_name}\".")

        estimate = round((time.time() - self.start_time) * ((1 -  value) / value))
        estimate_text_value = "%02d:%02d:%02d" % (estimate // 3600, (estimate % 3600) // 60, estimate % 60)

        self.estimate_text.set(f"Estimated time remaining {estimate_text_value}")
        if not self.closed:
            self.progress['value'] = value * 100
            self.root.update()

    def stop(self):
        self.root.quit()
        self.root.destroy()

loading_visuals = LoadingVisuals()

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
    high_color_shading_mode = landscape.get("HighColorShadingMode", 0)

    path_packed = os.path.join(animations_directory, boblibs[0]+".bmd")
    path_masked = os.path.join(animations_directory, boblibs[1]+".bmd")

    bitmap_packed = Bitmap()
    bitmap_masked = Bitmap()
    bitmap_packed.load(path_packed)
    bitmap_masked.load(path_masked)
    animation_packed = bitmap_packed.to_animation(remaptable, 255, first_bob, elements,
                                                  high_color_shading_mode, masked_file=False)
    animation_masked = bitmap_masked.to_animation(remaptable, 200, first_bob, elements,
                                                  high_color_shading_mode, masked_file=True)

    animation_masked.paste(animation_packed)
    return animation_masked


class Animations(dict):
    """Dictionary with animations of landscapes"""
    initialized = False
    cache_filepath = "cache.bin"
    name_max_bytes = ceil(log2(name_max_length))
    pygame_converted = False

    @load_with_fallback
    def __init__(self, *, report=False):

        remaptables.reload_fix()

        super().__init__(dict())
        if self.__class__.initialized:
            raise ValueError(f"{self.__class__.__name__} is a singleton.")
        self.__class__.initialized = True
        self.__class__.pygame_converted = False

        # On device where this part of code was tested, loading all animations directly from *.bmd files and applying
        # palettes takes around 15 minutes, while loading it from cache file takes around 3 seconds. Loading time is
        # therefore improved by around 27500% by cache usage.

        os.chdir(fallback_directories[-1])  # We want cache file to be loaded from fallback directory. It is recommended
                                            # to do it like that due to possible confusion of cache file from multiple
                                            # different versions of the game, which can result in further errors.

        try:
            self.load_cache()
        except FileNotFoundError:

            top = tk.Tk()
            top.withdraw()
            top.attributes("-topmost", True)

            if messagebox.askyesno("File not found",
                                   "Cache file not found. Do you want to extract bitmaps?\n\n"+\
                                   "This may take a few minutes. If this is your first time using the editor, note "+\
                                   "that this loading process will not happen again as long as cache file remains in "+\
                                   "your files. Alternatively you can try to find pre-generated cache file online.",
                                   icon="warning", parent=top):
                top.quit()
                top.destroy()
                loading_visuals.start()
                self.load_all_animations(report=report)
                self.save_cache()
                loading_visuals.stop()
            else:
                top.quit()
                top.destroy()
                sys_exit()

        os.chdir(fallback_directories[0])

    def load_all_animations(self, *, report=False) -> dict:
        report = Report(muted=not report)
        self.clear()
        loaded_num = 0
        for name in landscapedefs.keys():
            self[name] = load_animation(name)
            report.report(f"Loaded landscape \"{name}\".")
            loaded_num += 1
            loading_visuals.step(loaded_num/len(landscapedefs), name)

            if loading_visuals.closed:
                sys_exit()

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
