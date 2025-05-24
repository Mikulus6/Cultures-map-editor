import copy
import os
from sys import exit as sys_exit
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

fallback_directories = [os.getcwd()]

def fallback(function):
    def new_function(*args, **kwargs):
        global fallback_directories
        try:
            value = function(*args, **kwargs)
        except FileNotFoundError:
            top = tk.Tk()
            top.withdraw()
            top.attributes("-topmost", True)

            if messagebox.askyesno("File not found",
                                   "Some of game files cannot be found in working directory.\n" + \
                                   "Would you like to specify fallback directory manually?",
                                   icon="warning", parent=top):
                top.quit()
                top.destroy()
                fallback_directories.append(filedialog.askdirectory())
                value = function(*args, **kwargs)
            else:
                sys_exit()
                value = None  # unreachable code
        return value
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
            os.chdir(directory)
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
