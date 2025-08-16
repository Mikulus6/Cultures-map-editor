import copy
import os
import shutil
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from typing import Literal
from scripts.abs_path import abs_path
from scripts.buffer import data_encoding
from supplements.bitmaps import Bitmap
from supplements.initialization import decode, encode
from supplements.library import Library
from supplements.remaptables import RemapTables
from sys import argv as sys_argv, exit as sys_exit, executable as sys_executable

quick_conversions_param_name = "--quick-conversions"

# Some procedures require additional information provided by files included in the game.
game_found = False
fallback_active = not(len(sys_argv) > 1 and sys_argv[1] == quick_conversions_param_name)
default_directory = os.getcwd()

while fallback_active:
    try:
        # Add imports dependent on game files here.
        from supplements.gouraud import Gouraud
        from supplements.save import save_to_map
        from supplements.remaptables import load_remaptable_default

        remaptable_default = load_remaptable_default()

        game_found, fallback_active = True, False
    except (FileNotFoundError, ImportError):
        top = tk.Tk(); top.withdraw(); top.attributes("-topmost", True)
        fallback_active = messagebox.askyesno("File not found",
                                              "Some of game files cannot be found in current directory.\n" + \
                                              "Would you like to specify fallback directory manually?",
                                              icon="warning", parent=top)
        top.quit(); top.destroy()
        if not fallback_active: game_found = False
        else:
            try: os.chdir(filedialog.askdirectory())
            except OSError: sys_exit()
else:
    os.chdir(default_directory)
# Here ends the part with loading additional information from game files.


def select_input():
    global input_path

    option = combobox_options[selected_option.get()]

    if option.input_type == "file":
        input_path = filedialog.askopenfilename(title="Open file", filetypes=option.input_filetypes)
    else:
        input_path = filedialog.askdirectory()

    if input_path == "":
        input_path = None
        input_text.set("...")
        button_out.config(state=tk.DISABLED)
    else:
        input_text.set(input_path)
        button_out.config(state=tk.NORMAL)


def save_output():
    option = combobox_options[selected_option.get()]

    if option.output_type == "file":
        try:               defaultextension = option.output_filetypes[0][1]
        except IndexError: defaultextension = None

        output_path = filedialog.asksaveasfilename(title="Open file", defaultextension=defaultextension,
                                                   filetypes=option.output_filetypes)
    else:
        output_path = filedialog.askdirectory()

    if output_path == "":
        return

    if input_path is None:
        messagebox.showwarning("Warning", f"Invalid input path.")
        return

    option.function(input_path, output_path)


class Conversions:
    @classmethod
    def convert_cif_ini(cls, in_path, out_path):
        if not out_path.lower().endswith(".ini"):
            out_path += ".ini"
        with open(in_path, "rb") as file:
            content = decode(file.read(), sal_tab_file_format=False)
        with open(out_path, "w", encoding=data_encoding) as file:
            file.write(content)

    @classmethod
    def convert_ini_cif(cls, in_path, out_path):
        if not out_path.lower().endswith(".cif"):
            out_path += ".cif"
        with open(in_path, "r", encoding=data_encoding) as file:
            content = file.read()
        with open(out_path, "wb",) as file:
            file.write(encode(content, cultures_1=True, sal_tab_file_format=False))

    @classmethod
    def convert_sal_tab_txt(cls, in_path, out_path):
        if not out_path.lower().endswith(".txt"):
            out_path += ".txt"
        with open(in_path, "rb") as file:
            content = decode(file.read(), sal_tab_file_format=True)
        with open(out_path, "w", encoding=data_encoding) as file:
            file.write(content)

    @classmethod
    def convert_txt_sal_tab(cls, in_path, out_path):
        if not out_path.lower().endswith(".sal") or out_path.lower().endswith(".tab"):
            out_path += ".sal"  # *.sal files are more common than *.tab files.
        with open(in_path, "r", encoding=data_encoding) as file:
            content = file.read()
        with open(out_path, "wb",) as file:
            file.write(encode(content, cultures_1=True, sal_tab_file_format=True))

    @classmethod
    def import_sav_map(cls, in_path, out_path):
        if not out_path.lower().endswith(".map"):
            out_path += ".map"
        save_to_map(in_path, out_path)

    @classmethod
    def extract_lib(cls, in_path, out_path):
        library = Library()
        library.load(filename=in_path, cultures_1=True)
        library.extract(out_path)

    @classmethod
    def pack_lib(cls, in_path, out_path):
        if not out_path.lower().endswith(".lib"):
            out_path += ".lib"
        library = Library()
        library.pack(in_path)
        library.save(out_path, cultures_1=True)

    @classmethod
    def extract_bmd(cls, in_path, out_path):
        bitmap = Bitmap()
        bitmap.load(in_path)
        bitmap.extract_to_raw_data(os.path.join(out_path, os.path.basename(in_path).split(".")[0]))

    @classmethod
    def pack_bmd(cls, in_path, out_path):
        bitmap = Bitmap()
        bitmap.load_from_raw_data(in_path)
        if ((not out_path.lower().endswith(".bmd")) and not bitmap.is_font) or \
           ((not out_path.lower().endswith(".fnt")) and bitmap.is_font):
            out_path += ".fnt" if bitmap.is_font else ".bmd"
        bitmap.save(out_path)

    @classmethod
    def extract_dat(cls, in_path, out_path):
        gouraud = Gouraud()
        gouraud.load(in_path)
        gouraud.extract(out_path, remaptable=remaptable_default, create_subdirectory=True)

    @classmethod
    def pack_dat(cls, in_path, out_path):
        if not out_path.lower().endswith(".dat"):
            out_path += ".dat"
        gouraud = Gouraud()
        gouraud.pack(in_path)
        gouraud.save(out_path)

    @classmethod
    def unpack_remaptables(cls, in_path, out_path):
        remaptables = RemapTables(cif_path=os.path.join(in_path, "remaptables.cif"))
        remaptables.load(cdf_path=os.path.join(in_path, "remaptables.cdf"))
        remaptables.extract(os.path.join(out_path, "remaptables"))
        if in_path != out_path:
            for file_extension in ("ini", "cif"):
                try:
                    shutil.copyfile(os.path.join(in_path, "remaptables."+file_extension),
                                    os.path.join(out_path, "remaptables", "remaptables."+file_extension))
                    break
                except FileNotFoundError:
                    continue
            else:
                raise FileNotFoundError

    @classmethod
    def pack_remaptables(cls, in_path, out_path):
        remaptables = RemapTables(cif_path=os.path.join(in_path, "remaptables.cif"))
        remaptables.pack(os.path.join(in_path))
        remaptables.save(cdf_path=os.path.join(out_path, "remaptables", "remaptables.cdf"))
        if in_path != out_path:
            for file_extension in ("ini", "cif"):
                try:
                    shutil.copyfile(os.path.join(in_path, "remaptables."+file_extension),
                                    os.path.join(out_path, "remaptables", "remaptables."+file_extension))
                    break
                except FileNotFoundError:
                    continue
            else:
                raise FileNotFoundError


class Option:
    names = []

    def __init__(self, name: str, cli_name: str,
                 input_type: Literal["directory", "file"], output_type: Literal["directory", "file"],
                 input_filetypes = (("all files", "*.*"),), output_filetypes = (("all files", "*.*"),),
                 function = lambda in_path, out_path: None, requires_game_files: bool = False):
        self.name = name
        self.cli_name = cli_name
        self.input_type = input_type
        self.output_type = output_type
        self.input_filetypes = input_filetypes if input_type == "file" else None
        self.output_filetypes = output_filetypes if output_type == "file" else None
        self.function = function
        self.requires_game_files = requires_game_files

        assert self.name not in self.__class__.names
        self.__class__.names.append(self.name)

options = [Option("Convert *.cif -> *.ini", "cif-ini",
                  input_type="file", output_type="file",
                  input_filetypes=(("cif files", "*.cif"), ("all files", "*.*")),
                  output_filetypes=(("ini files", "*.ini"), ("all files", "*.*")),
                  function=Conversions.convert_cif_ini,
                  requires_game_files=False),

           Option("Convert *.ini -> *.cif", "ini-cif",
                  input_type="file", output_type="file",
                  input_filetypes=(("ini files", "*.ini"), ("all files", "*.*")),
                  output_filetypes=(("cif files", "*.cif"), ("all files", "*.*")),
                  function=Conversions.convert_ini_cif,
                  requires_game_files=False),

           Option("Convert *.sal/*.tab -> *.txt", "sal-txt",
                  input_type="file", output_type="file",
                  input_filetypes=(("sal/tab files", "*.sal;*.tab"), ("all files", "*.*")),
                  output_filetypes=(("txt files", "*.txt"), ("all files", "*.*")),
                  function=Conversions.convert_sal_tab_txt,
                  requires_game_files=False),

           Option("Convert *.txt -> *.sal/*.tab", "txt-sal",
                  input_type="file", output_type="file",
                  input_filetypes=(("txt files", "*.txt"), ("all files", "*.*")),
                  output_filetypes=(("sal/tab files", "*.sal;*.tab"), ("all files", "*.*")),
                  function=Conversions.convert_txt_sal_tab,
                  requires_game_files=False),

           Option("Import *.sav -> *.map", "sav-map",
                  input_type="file", output_type="file",
                  input_filetypes=(("sav files", "*.sav"), ("all files", "*.*")),
                  output_filetypes=(("map files", "*.map"), ("all files", "*.*")),
                  function=Conversions.import_sav_map,
                  requires_game_files=True),

           Option("Extract *.lib", "lib-dir",
                  input_type="file", output_type="directory",
                  input_filetypes=(("lib files", "*.lib"), ("all files", "*.*")),
                  function=Conversions.extract_lib,
                  requires_game_files=False),

           Option("Create *.lib", "dir-lib",
                  input_type="directory", output_type="file",
                  output_filetypes=(("lib files", "*.lib"), ("all files", "*.*")),
                  function=Conversions.pack_lib,
                  requires_game_files=False),

           Option("Extract *.bmd/*.fnt to raw data", "bmd-dir",
                  input_type="file", output_type="directory",
                  input_filetypes=(("bmd/fnt files", "*.bmd;*.fnt"), ("all files", "*.*")),
                  function=Conversions.extract_bmd,
                  requires_game_files=False),

           Option("Create *.bmd/*.fnt from raw data", "dir-bmd",
                  input_type="directory", output_type="file",
                  output_filetypes=(("bmd/fnt files", "*.bmd;*.fnt"), ("all files", "*.*")),
                  function=Conversions.pack_bmd,
                  requires_game_files=False),

           Option("Extract gouraud.dat to raw data", "dat-dir",
                  input_type="file", output_type="directory",
                  input_filetypes=(("dat files", "*.dat"), ("all files", "*.*")),
                  function=Conversions.extract_dat,
                  requires_game_files=True),

           Option("Create gouraud.dat from raw data", "dir-dat",
                  input_type="directory", output_type="file",
                  output_filetypes=(("dat files", "*.dat"), ("all files", "*.*")),
                  function=Conversions.pack_dat,
                  requires_game_files=True),

           Option("Unpack remaptables directory", "cdf-dir",
                  input_type="directory", output_type="directory",
                  function=Conversions.unpack_remaptables,
                  requires_game_files=False),

           Option("Pack remaptables directory", "dir-cdf",
                  input_type="directory", output_type="directory",
                  function=Conversions.pack_remaptables,
                  requires_game_files=False)]


def quick_conversions():

    if __name__ == "__main__":
        # This print statement is an integrated part of documentation due to pyinstaller ignoring print statements when
        # compiling Python code to executable file with command-line explicitly turned off. This statement provides
        # information about conversion names in command line mode.
        print("\n".join(f"{option.cli_name} ({option.name})" for option in options
                        if not option.requires_game_files or game_found))

    remove_quotation = lambda string: string[1:-1] if string.startswith("\"") and string.endswith("\"") else string

    sys_argv_copy = copy.copy(sys_argv)
    sys_argv_copy.pop(0)

    if len(sys_argv_copy) > 0 and sys_argv_copy[0] == quick_conversions_param_name:
        sys_argv_copy.pop(0)
        sys_argv_copy_len = len(sys_argv_copy)
        sys_argv_copy = iter(sys_argv_copy)

        for _ in range(sys_argv_copy_len // 3):

            conv_cli_name = remove_quotation(next(sys_argv_copy))
            conv_in_path  = os.path.join(os.path.dirname(sys_executable), remove_quotation(next(sys_argv_copy)))
            conv_out_path = os.path.join(os.path.dirname(sys_executable), remove_quotation(next(sys_argv_copy)))

            for opiton in options:
                if opiton.cli_name.lower() == conv_cli_name.lower():
                    if not opiton.requires_game_files or game_found:
                        opiton.function(conv_in_path, conv_out_path)
                    break
            else:
                raise NameError

        sys_exit()


quick_conversions()

root = tk.Tk()
root.title("Converters")
root.geometry("235x160")
root.resizable(False, False)
root.iconbitmap(abs_path("assets/icon_converters.ico"))

input_path = None

button_in = tk.Button(root, command=select_input)
button_in.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
button_out = tk.Button(root, command=save_output)
button_out.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

input_text = tk.StringVar()
selected_option = tk.StringVar()
selected_input = tk.Label(root, textvariable=input_text, width=30, anchor="e")
selected_input.grid(row=2, column=0, sticky="w", padx=10, pady=5)

def update_by_combobox(event=None):  # noqa - parameter unused
    global input_path
    option = combobox_options[selected_option.get()]
    button_in.config(text=f"Select input {option.input_type}")
    button_out.config(text=f"Save to {option.output_type}")
    input_path = None
    input_text.set("...")
    button_out.config(state=tk.DISABLED)

label = tk.Label(root, text="Select action:")
label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
combobox_options = {option_obj.name: option_obj for option_obj in options
                    if not option_obj.requires_game_files or game_found}
combobox = ttk.Combobox(root, textvariable=selected_option, values=tuple(combobox_options.keys()), width=32)
combobox.current(0)
update_by_combobox()
combobox.grid(row=1, column=0, sticky="ew", padx=10)
combobox.bind("<<ComboboxSelected>>", update_by_combobox)

root.mainloop()
