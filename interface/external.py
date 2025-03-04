import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from interface.message import message
from interface.states import landscapes_draw_parameters, height_draw_parameters, height_mode_options
from sections.walk_sector_points import sector_width


def askopenfilename(*args, **kwargs):
    filepath = filedialog.askopenfilename(*args, **kwargs)
    return filepath if filepath != "" else None

def asksaveasfilename(*args, **kwargs):
    filepath = filedialog.asksaveasfilename(*args, **kwargs)
    return filepath if filepath != "" else None

def askdirectory(*args, **kwargs):
    directory = filedialog.askdirectory(*args, **kwargs)
    return directory if directory != "" else None

def ask_enforce_height():
    return messagebox.askyesno("Confirm",
                               "Are you sure you want to enforce horizonless heightmap?\nThis will modify map height.")

def ask_save_changes(on_quit: bool = False):
    return messagebox.askyesno("Unsaved changes",
                               "You have unsaved changes.\nAre you sure you want to " + \
                               ("quit?" if on_quit else "proceed?"), icon='warning')

def warning_too_many_area_marks():
    messagebox.showwarning("Warning", f"Area mark limit reached. Cannot add another mark.")

def ask_new_map():
    def validate_entries():
        try:
            width_val = int(width_entry.get())
            height_val = int(height_entry.get())
            rounded_width = round(width_val // sector_width) * sector_width
            rounded_height = round(height_val // sector_width) * sector_width
            width_entry.delete(0, tk.END)
            width_entry.insert(0, str(rounded_width))
            height_entry.delete(0, tk.END)
            height_entry.insert(0, str(rounded_height))
            ok_button.config(state=tk.NORMAL)
        except ValueError:
            ok_button.config(state=tk.DISABLED)

    def on_ok():
        nonlocal result

        try:
            width_val = int(width_entry.get())
            height_val = int(height_entry.get())
        except ValueError:
            width_val = -1
            height_val = -1
        if width_val % sector_width == 0 and height_val % sector_width == 0 and width_val > 0 and height_val > 0:
            result = (width_val, height_val)
            root.quit()
            root.destroy()
        else:
            messagebox.showwarning(
                "Warning", f"Map dimensions must be positive and divisible by {sector_width}.")

    def on_close():
        root.quit()
        root.destroy()

    result = None
    root = tk.Tk()
    root.title("New map")
    root.geometry("225x125")
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", on_close)

    frame = tk.Frame(root)
    frame.pack(expand=True)

    tk.Label(frame, text="Width:").grid(row=0, column=0, padx=5, pady=5, sticky='ew')
    width_entry = tk.Entry(frame)
    width_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
    width_entry.insert(0, f"{sector_width}")
    width_entry.bind("<FocusOut>", lambda event: validate_entries())

    tk.Label(frame, text="Height:").grid(row=1, column=0, padx=5, pady=5, sticky='ew')
    height_entry = tk.Entry(frame)
    height_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
    height_entry.insert(0, f"{sector_width}")
    height_entry.bind("<FocusOut>", lambda event: validate_entries())

    ok_button = tk.Button(frame, text="OK", state=tk.NORMAL, command=on_ok)
    ok_button.grid(row=2, column=0, columnspan=2, pady=10)

    root.mainloop()
    return result


def ask_resize_map(current_map_width, current_map_height):
    def validate_entries():
        try:
            north_val = int(north_entry.get())
            south_val = int(south_entry.get())
            east_val = int(east_entry.get())
            west_val = int(west_entry.get())

            rounded_north = round(north_val // sector_width) * sector_width
            rounded_south = round(south_val // sector_width) * sector_width
            rounded_east = round(east_val // sector_width) * sector_width
            rounded_west = round(west_val // sector_width) * sector_width

            north_entry.delete(0, tk.END)
            north_entry.insert(0, str(rounded_north))
            south_entry.delete(0, tk.END)
            south_entry.insert(0, str(rounded_south))
            east_entry.delete(0, tk.END)
            east_entry.insert(0, str(rounded_east))
            west_entry.delete(0, tk.END)
            west_entry.insert(0, str(rounded_west))

            ok_button.config(state=tk.NORMAL)
        except ValueError:
            ok_button.config(state=tk.DISABLED)

    def on_ok():
        nonlocal result

        try:
            north_val = int(north_entry.get())
            south_val = int(south_entry.get())
            east_val = int(east_entry.get())
            west_val = int(west_entry.get())
        except ValueError:
            north_val = south_val = east_val = west_val = 0

        if check_var.get():
            north_val *= -1
            south_val *= -1
            east_val *= -1
            west_val *= -1

        try:
            if not all(val % sector_width == 0 for val in (north_val, south_val, east_val, west_val)):
                raise ValueError
            if min(current_map_height + north_val + south_val, current_map_width + east_val + west_val) < sector_width:
                raise IndexError
        except ValueError:
            messagebox.showwarning("Warning", f"All dimensions must be divisible by {sector_width}.")
        except IndexError:
            messagebox.showwarning("Warning", f"Resulting map dimensions must be positive.")
        else:

            result = (north_val, south_val, west_val, east_val), \
                     bool(remove_landscapes_var.get()), bool(remove_structures_var.get())
            root.quit()
            root.destroy()

    def on_close():
        root.quit()
        root.destroy()

    result = None
    root = tk.Tk()
    root.title("Resize")
    root.geometry("225x310")
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", on_close)

    frame = tk.Frame(root)
    frame.pack(expand=True)
    tk.Label(frame, text=f"Current size: {current_map_width} x {current_map_height}", fg="gray").grid(row=0, column=0,
                                                                                                      columnspan=2,
                                                                                                      padx=5, pady=5,
                                                                                                      sticky='w')
    tk.Label(frame, text="Extend north:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
    north_entry = tk.Entry(frame)
    north_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
    north_entry.insert(0, "0")
    north_entry.bind("<FocusOut>", lambda event: validate_entries())

    tk.Label(frame, text="Extend south:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
    south_entry = tk.Entry(frame)
    south_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
    south_entry.insert(0, "0")
    south_entry.bind("<FocusOut>", lambda event: validate_entries())

    tk.Label(frame, text="Extend east:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
    east_entry = tk.Entry(frame)
    east_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
    east_entry.insert(0, "0")
    east_entry.bind("<FocusOut>", lambda event: validate_entries())

    tk.Label(frame, text="Extend west:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
    west_entry = tk.Entry(frame)
    west_entry.grid(row=4, column=1, padx=5, pady=5, sticky='ew')
    west_entry.insert(0, "0")
    west_entry.bind("<FocusOut>", lambda event: validate_entries())

    check_var = tk.BooleanVar(value=False)
    check_button = tk.Checkbutton(frame, text="Invert extend and indent", variable=check_var)
    check_button.grid(row=5, column=0, columnspan=2, pady=5, sticky="w")

    remove_landscapes_var = tk.BooleanVar(value=True)
    remove_landscapes_button = tk.Checkbutton(frame, text="Remove landscapes from margin",
                                              variable=remove_landscapes_var)
    remove_landscapes_button.grid(row=6, column=0, columnspan=2, pady=5, sticky="w")

    remove_structures_var = tk.BooleanVar(value=True)
    remove_structures_button = tk.Checkbutton(frame, text="Remove structures from margin",
                                              variable=remove_structures_var)
    remove_structures_button.grid(row=7, column=0, columnspan=2, pady=5, sticky="w")

    ok_button = tk.Button(frame, text="OK", state=tk.NORMAL, command=on_ok)
    ok_button.grid(row=8, column=0, columnspan=2, pady=10)

    root.mainloop()
    return result


def ask_brush_parameters():
    def validate_entries():
        try:
            density_val = float(density_entry.get())
            tickrate_landscapes_val = float(tickrate_landscapes_entry.get())
            tickrate_height_val = float(tickrate_height_entry.get())
            absoulte_val = round(float(value_absolute_entry.get()))
            delta_val = round(float(value_delta_entry.get()))
            random_val = round(float(value_random_entry.get()))
            smoothing_val = round(float(value_smoothing_entry.get()))

            density_val = min(max((density_val, 0)), 1)
            tickrate_landscapes_val = 1 if tickrate_landscapes_val <= 0 else tickrate_landscapes_val
            tickrate_height_val = 1 if tickrate_height_val <= 0 else tickrate_height_val
            absoulte_val = 0 if absoulte_val < 0 else 255 if absoulte_val > 255 else int(absoulte_val)
            delta_val = 0 if delta_val < 0 else 255 if delta_val > 255 else int(delta_val)
            random_val = 0 if random_val < 0 else 255 if random_val > 255 else int(random_val)
            smoothing_val = 0 if smoothing_val < 0 else 255 if smoothing_val > 255 else int(smoothing_val)

            density_entry.delete(0, tk.END)
            density_entry.insert(0, str(density_val))
            tickrate_landscapes_entry.delete(0, tk.END)
            tickrate_landscapes_entry.insert(0, str(tickrate_landscapes_val))
            tickrate_height_entry.delete(0, tk.END)
            tickrate_height_entry.insert(0, str(tickrate_height_val))
            value_absolute_entry.delete(0, tk.END)
            value_absolute_entry.insert(0, str(absoulte_val))
            value_delta_entry.delete(0, tk.END)
            value_delta_entry.insert(0, str(delta_val))
            value_random_entry.delete(0, tk.END)
            value_random_entry.insert(0, str(random_val))
            value_smoothing_entry.delete(0, tk.END)
            value_smoothing_entry.insert(0, str(smoothing_val))

            if height_mode_entry.get() not in height_mode_options:
                height_mode_entry.delete(0, tk.END)
                height_mode_entry.insert(0, str(height_mode_options[0]))

            ok_button.config(state=tk.NORMAL)
        except ValueError:
            ok_button.config(state=tk.DISABLED)

    def on_update():

        try:
            density_val = float(density_entry.get())
            tickrate_landscapes_val = float(tickrate_landscapes_entry.get())
            tickrate_height_val = float(tickrate_height_entry.get())
            absoulte_val = round(float(value_absolute_entry.get()))
            delta_val = round(float(value_delta_entry.get()))
            random_val = round(float(value_random_entry.get()))
            smoothing_val = round(float(value_smoothing_entry.get()))
        except ValueError:
            messagebox.showwarning("Warning", f"Given values must be numbers.")
            return

        height_mode = str(height_mode_entry.get())
        if height_mode not in height_mode_options:
            messagebox.showwarning("Warning", f"Invalid height edit mode.")
            return

        if min(absoulte_val, delta_val, random_val, smoothing_val) < 0 or\
           max(absoulte_val, delta_val, random_val, smoothing_val) > 255:
            messagebox.showwarning("Warning", f"Height brushes parameters must be between 0 and 255.")
            return
        if not (0 <= density_val <= 1):
            messagebox.showwarning("Warning", f"Density must be between 0 and 1.")
            return
        elif min(tickrate_landscapes_val, tickrate_height_val) <= 0:
            messagebox.showwarning("Warning", f"Tickrate must be greater than 0.")
            return

        landscapes_draw_parameters.density = density_val
        landscapes_draw_parameters.tickrate = tickrate_landscapes_val
        landscapes_draw_parameters.legacy_randomness = legacy_randomness_var.get()
        height_draw_parameters.mode = height_mode
        height_draw_parameters.value_absolute = absoulte_val
        height_draw_parameters.value_delta = delta_val
        height_draw_parameters.value_random = random_val
        height_draw_parameters.threshold_smoothing = smoothing_val
        height_draw_parameters.tickrate = tickrate_height_val
        height_draw_parameters.total_smoothing = total_smoothing_var.get()

        root.quit()
        root.destroy()

        message.set_message(f"Brush parameters have been changed.")

    def on_close():
        root.quit()
        root.destroy()

    root = tk.Tk()
    root.title("Brush")
    root.geometry("225x480")
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", on_close)

    frame = tk.Frame(root)
    frame.pack(expand=True)
    frame.grid_columnconfigure(1, weight=1)

    separator_height = tk.Frame(frame)
    separator_height.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")
    ttk.Separator(separator_height, orient="horizontal").pack(side="left", expand=True, fill="x", padx=5)
    tk.Label(separator_height, text="Height").pack(side="left", padx=5)
    ttk.Separator(separator_height, orient="horizontal").pack(side="left", expand=True, fill="x", padx=5)

    tk.Label(frame, text="Active mode:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
    height_mode_value = tk.StringVar()
    height_mode_value.set(f"{height_draw_parameters.mode}")
    height_mode_entry = ttk.Combobox(frame, textvariable=height_mode_value, values=height_mode_options,
                                     width=0, height=0)
    height_mode_entry.grid(row=1, column=1, padx=5, pady=5, sticky='new')
    height_mode_entry.bind("<FocusOut>", lambda event: validate_entries())

    tk.Label(frame, text="Absolute value:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
    value_absolute_entry = tk.Entry(frame)
    value_absolute_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
    value_absolute_entry.insert(0, f"{height_draw_parameters.value_absolute}")
    value_absolute_entry.bind("<FocusOut>", lambda event: validate_entries())

    tk.Label(frame, text="Delta value:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
    value_delta_entry = tk.Entry(frame)
    value_delta_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
    value_delta_entry.insert(0, f"{height_draw_parameters.value_delta}")
    value_delta_entry.bind("<FocusOut>", lambda event: validate_entries())

    tk.Label(frame, text="Random value:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
    value_random_entry = tk.Entry(frame)
    value_random_entry.grid(row=4, column=1, padx=5, pady=5, sticky='ew')
    value_random_entry.insert(0, f"{height_draw_parameters.value_random}")
    value_random_entry.bind("<FocusOut>", lambda event: validate_entries())

    tk.Label(frame, text="Smoothing treshold:").grid(row=5, column=0, padx=5, pady=5, sticky='w')
    value_smoothing_entry = tk.Entry(frame)
    value_smoothing_entry.grid(row=5, column=1, padx=5, pady=5, sticky='ew')
    value_smoothing_entry.insert(0, f"{height_draw_parameters.threshold_smoothing}")
    value_smoothing_entry.bind("<FocusOut>", lambda event: validate_entries())

    total_smoothing_var = tk.BooleanVar(value=height_draw_parameters.total_smoothing)
    total_smoothing_button = tk.Checkbutton(frame, text="Use total average for smoothing",
                                            variable=total_smoothing_var)
    total_smoothing_button.grid(row=6, column=0, columnspan=2, pady=5)

    tk.Label(frame, text="Tickrate [Hz]:").grid(row=7, column=0, padx=5, pady=5, sticky='w')
    tickrate_height_entry = tk.Entry(frame)
    tickrate_height_entry.grid(row=7, column=1, padx=5, pady=5, sticky='ew')
    tickrate_height_entry.insert(0, f"{height_draw_parameters.tickrate}")
    tickrate_height_entry.bind("<FocusOut>", lambda event: validate_entries())

    separator_landscapes = tk.Frame(frame)
    separator_landscapes.grid(row=8, column=0, columnspan=2, pady=10, sticky="ew")
    ttk.Separator(separator_landscapes, orient="horizontal").pack(side="left", expand=True, fill="x", padx=5)
    tk.Label(separator_landscapes, text="Landscapes").pack(side="left", padx=5)
    ttk.Separator(separator_landscapes, orient="horizontal").pack(side="left", expand=True, fill="x", padx=5)

    tk.Label(frame, text="Density:").grid(row=9, column=0, padx=5, pady=5, sticky='w')
    density_entry = tk.Entry(frame)
    density_entry.grid(row=9, column=1, padx=5, pady=5, sticky='ew')
    density_entry.insert(0, f"{landscapes_draw_parameters.density}")
    density_entry.bind("<FocusOut>", lambda event: validate_entries())

    tk.Label(frame, text="Tickrate [Hz]:").grid(row=10, column=0, padx=5, pady=5, sticky='w')
    tickrate_landscapes_entry = tk.Entry(frame)
    tickrate_landscapes_entry.grid(row=10, column=1, padx=5, pady=5, sticky='ew')
    tickrate_landscapes_entry.insert(0, f"{landscapes_draw_parameters.tickrate}")
    tickrate_landscapes_entry.bind("<FocusOut>", lambda event: validate_entries())

    legacy_randomness_var = tk.BooleanVar(value=landscapes_draw_parameters.legacy_randomness)
    legacy_randomness_button = tk.Checkbutton(frame, text="Use legacy randomness",
                                            variable=legacy_randomness_var)
    legacy_randomness_button.grid(row=11, column=0, columnspan=2, pady=5)

    separator_end = tk.Frame(frame)
    separator_end.grid(row=12, column=0, columnspan=2, pady=10, sticky="ew")
    ttk.Separator(separator_end, orient="horizontal").pack(side="left", expand=True, fill="x", padx=5)

    ok_button = tk.Button(frame, text="Update", state=tk.NORMAL, command=on_update)
    ok_button.grid(row=13, column=0, columnspan=2, pady=10)

    root.mainloop()


def ask_area_mark() -> None | str | tuple[int, int, int]:
    def validate_entries():
        try:
            int(x_entry.get())
            int(y_entry.get())
            radius = int(radius_entry.get())

            if radius < 0: radius = 0

            radius_entry.delete(0, tk.END)
            radius_entry.insert(0, str(radius))

            ok_button.config(state=tk.NORMAL)
        except ValueError:
            ok_button.config(state=tk.DISABLED)

    def on_add():
        nonlocal result

        try:
            x = int(x_entry.get())
            y = int(y_entry.get())
            radius = int(radius_entry.get())
        except ValueError:
            messagebox.showwarning("Warning", f"Given values must be integers.")
            return
        if radius < 0:
            messagebox.showwarning("Warning", f"Radius cannot be negative.")
            return

        result = (x, y, radius)
        root.quit()
        root.destroy()

    def on_remove_all():
        nonlocal result

        result = "remove"
        root.quit()
        root.destroy()


    def on_close():
        root.quit()
        root.destroy()

    result = None
    root = tk.Tk()
    root.title("Hexagon")
    root.geometry("225x160")
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", on_close)

    frame = tk.Frame(root)
    frame.pack(expand=True)

    tk.Label(frame, text="X:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
    x_entry = tk.Entry(frame)
    x_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
    x_entry.insert(0, "0")
    x_entry.bind("<FocusOut>", lambda event: validate_entries())

    tk.Label(frame, text="Y:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
    y_entry = tk.Entry(frame)
    y_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
    y_entry.insert(0, "0")
    y_entry.bind("<FocusOut>", lambda event: validate_entries())

    tk.Label(frame, text="Radius:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
    radius_entry = tk.Entry(frame)
    radius_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
    radius_entry.insert(0, "0")
    radius_entry.bind("<FocusOut>", lambda event: validate_entries())

    ok_button = tk.Button(frame, text="Add", state=tk.NORMAL, command=on_add)
    ok_button.grid(row=5, column=0, columnspan=1, pady=10)

    remove_button = tk.Button(frame, text="Remove all", state=tk.NORMAL, command=on_remove_all)
    remove_button.grid(row=5, column=1, columnspan=1, pady=10)

    root.mainloop()
    return result
