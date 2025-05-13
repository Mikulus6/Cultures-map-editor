import os
from scripts.buffer import data_encoding
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from typing import Literal
from supplements.bitmaps import Bitmap
from supplements.initialization import decode, encode
from supplements.library import Library


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
        with open(in_path, "rb") as file:
            content = decode(file.read(), sal_tab_file_format=False)
        with open(out_path, "w", encoding=data_encoding) as file:
            file.write(content)

    @classmethod
    def convert_ini_cif(cls, in_path, out_path):
        with open(in_path, "r", encoding=data_encoding) as file:
            content = file.read()
        with open(out_path, "wb",) as file:
            file.write(encode(content, cultures_1=True, sal_tab_file_format=False))

    @classmethod
    def convert_sal_tab_txt(cls, in_path, out_path):
        with open(in_path, "rb") as file:
            content = decode(file.read(), sal_tab_file_format=True)
        with open(out_path, "w", encoding=data_encoding) as file:
            file.write(content)

    @classmethod
    def convert_txt_sal_tab(cls, in_path, out_path):
        with open(in_path, "r", encoding=data_encoding) as file:
            content = file.read()
        with open(out_path, "wb",) as file:
            file.write(encode(content, cultures_1=True, sal_tab_file_format=True))

    @classmethod
    def extract_fnt(cls, in_path, out_path):
        bitmap = Bitmap()
        bitmap.load(in_path, font_header=True)
        bitmap.extract_to_raw_data(os.path.join(out_path, os.path.basename(in_path).split(".")[0]))

    @classmethod
    def pack_fnt(cls, in_path, out_path):
        bitmap = Bitmap()
        bitmap.load_from_raw_data(in_path)
        bitmap.save(out_path, font_header=True)

    @classmethod
    def extract_lib(cls, in_path, out_path):
        library = Library()
        library.load(filename=in_path, cultures_1=True)
        library.extract(out_path)

    @classmethod
    def pack_lib(cls, in_path, out_path):
        library = Library()
        library.pack(in_path)
        library.save(out_path, cultures_1=True)


class Option:
    names = []

    def __init__(self, name: str, input_type: Literal["directory", "file"], output_type: Literal["directory", "file"],
                 input_filetypes = (("all files", "*.*"),), output_filetypes = (("all files", "*.*"),),
                 function = lambda in_path, out_path: None):
        self.name = name
        self.input_type = input_type
        self.output_type = output_type
        self.input_filetypes = input_filetypes if input_type == "file" else None
        self.output_filetypes = output_filetypes if output_type == "file" else None
        self.function = function

        assert self.name not in self.__class__.names
        self.__class__.names.append(self.name)

options = [Option("Convert *.cif -> *.ini", input_type="file", output_type="file",
                  input_filetypes=(("cif files", "*.cif"), ("all files", "*.*")),
                  output_filetypes=(("ini files", "*.ini"), ("all files", "*.*")),
                  function=Conversions.convert_cif_ini),

           Option("Convert *.ini -> *.cif", input_type="file", output_type="file",
                  input_filetypes=(("ini files", "*.ini"), ("all files", "*.*")),
                  output_filetypes=(("cif files", "*.cif"), ("all files", "*.*")),
                  function=Conversions.convert_ini_cif),

           Option("Convert *.sal/*.tab -> *.txt", input_type="file", output_type="file",
                  input_filetypes=(("sal/tab files", "*.sal;*.tab"), ("all files", "*.*")),
                  output_filetypes=(("txt files", "*.txt"), ("all files", "*.*")),
                  function=Conversions.convert_sal_tab_txt),

           Option("Convert *.txt -> *.sal/*.tab", input_type="file", output_type="file",
                  input_filetypes=(("txt files", "*.txt"), ("all files", "*.*")),
                  output_filetypes=(("sal/tab files", "*.sal;*.tab"), ("all files", "*.*")),
                  function=Conversions.convert_txt_sal_tab),

           Option("Extract *.fnt", input_type="file", output_type="directory",
                  input_filetypes=(("fnt files", "*.fnt"), ("all files", "*.*")),
                  function=Conversions.extract_fnt),

           Option("Create *.fnt", input_type="directory", output_type="file",
                  output_filetypes=(("fnt files", "*.fnt"), ("all files", "*.*")),
                  function=Conversions.pack_fnt),

           Option("Extract *.lib", input_type="file", output_type="directory",
                  input_filetypes=(("lib files", "*.lib"), ("all files", "*.*")),
                  function=Conversions.extract_lib),

           Option("Create *.lib", input_type="directory", output_type="file",
                  output_filetypes=(("lib files", "*.lib"), ("all files", "*.*")),
                  function=Conversions.pack_lib)]

root = tk.Tk()
root.title("Converters")
root.geometry("235x160")
root.resizable(False, False)
root.iconbitmap("assets/icon_converters.ico")

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
combobox_options = {option_obj.name: option_obj for option_obj in options}
combobox = ttk.Combobox(root, textvariable=selected_option, values=tuple(combobox_options.keys()), width=32)
combobox.current(0)
update_by_combobox()
combobox.grid(row=1, column=0, sticky="ew", padx=10)
combobox.bind("<<ComboboxSelected>>", update_by_combobox)

root.mainloop()
