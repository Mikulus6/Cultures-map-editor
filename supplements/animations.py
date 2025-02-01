import os
from scripts.animation import Animation
from scripts.report import Report
from supplements.bitmaps import Bitmap
from supplements.landscapedefs import landscapedefs
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
    animation_packed = bitmap_packed.to_animation(remaptable, 255, first_bob, elements, high_color_shading_mode, masked_file=False)
    animation_masked = bitmap_masked.to_animation(remaptable, shading_factor, first_bob, elements, high_color_shading_mode, masked_file=True)

    animation_masked.paste(animation_packed)
    return animation_masked


def load_all_animations(*, report=False) -> dict:
    report = Report(muted=not report)
    animations_dict = dict()
    for name in landscapedefs.keys():
        animations_dict[name] = load_animation(name)
        report.report(f"Loaded landscape \"{name}\".")
    return animations_dict


def load_and_export_all_animations(directory: str, *, report=False) -> dict:
    os.makedirs(directory, exist_ok=True)
    report = Report(muted=not report)
    animations_dict = dict()
    for name in landscapedefs.keys():
        animations_dict[name] = load_animation(name)
        animations_dict[name].save(os.path.join(directory, name+".webp"))
        report.report(f"Saved landscape \"{name}\".")
    return animations_dict
