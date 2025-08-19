import copy
import os
import sys
from sys import argv as sys_argv, exit as sys_exit
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

fallback_directories = [getattr(sys, '_MEIPASS', os.getcwd()),  # This path is relevant only for compiled *.exe file
                        os.path.dirname(os.path.abspath(sys_argv[0]))]

if fallback_directories[0] == fallback_directories[1]:
    fallback_directories.pop(-1)

def quit_fallback():
    top = tk.Tk()
    top.withdraw()
    top.attributes("-topmost", True)
    messagebox.showerror("File not found", "Editor cannot be launched without specified game directory.",
                         icon="error", parent=top)
    top.quit()
    top.destroy()
    sys_exit()


def fallback(function):
    def new_function(*args, **kwargs):
        global fallback_directories

        fallback_active = True
        while fallback_active:
            try:
                value = function(*args, **kwargs)
                fallback_active = False
            except FileNotFoundError:
                top = tk.Tk()
                top.withdraw()
                top.attributes("-topmost", True)

                if messagebox.askyesno("File not found",
                                       "Some of game files cannot be found in current directory.\n" + \
                                       "Would you like to specify fallback directory manually?",
                                       icon="warning", parent=top):
                    top.quit()
                    top.destroy()
                    fallback_directories.append(filedialog.askdirectory())
                else:
                    fallback_active = False
                    quit_fallback()
        return value  # noqa
    return new_function


def load_with_fallback(function):
    def new_function(*args, **kwargs):
        current_working_directory = os.getcwd()

        if current_working_directory in fallback_directories:
            directories_to_search = copy.copy(fallback_directories)
            directories_to_search.remove(current_working_directory)
            directories_to_search = [current_working_directory, *directories_to_search]
        else:
            directories_to_search = [current_working_directory, *fallback_directories]

        for directory in directories_to_search:
            try:
                os.chdir(directory)
            except OSError:
                quit_fallback()

            try:
                value = function(*args, **kwargs)
                break
            except FileNotFoundError:
                continue
        else:
            raise FileNotFoundError
        os.chdir(current_working_directory)
        return value
    return new_function
