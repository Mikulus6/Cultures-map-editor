import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from sections.walk_sector_points import sector_width

def askopenfilename(*args, **kwargs):
    filepath = filedialog.askopenfilename(*args, **kwargs)
    return filepath if filepath != "" else None

def asksaveasfilename(*args, **kwargs):
    filepath = filedialog.asksaveasfilename(*args, **kwargs)
    return filepath if filepath != "" else None


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

            rounded_width = round(north_val // sector_width) * sector_width
            rounded_height = round(south_val // sector_width) * sector_width
            rounded_length = round(east_val // sector_width) * sector_width
            rounded_depth = round(west_val // sector_width) * sector_width

            north_entry.delete(0, tk.END)
            north_entry.insert(0, str(rounded_width))
            south_entry.delete(0, tk.END)
            south_entry.insert(0, str(rounded_height))
            east_entry.delete(0, tk.END)
            east_entry.insert(0, str(rounded_length))
            west_entry.delete(0, tk.END)
            west_entry.insert(0, str(rounded_depth))

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
            if min(current_map_width + north_val + south_val, current_map_height + east_val + west_val) < sector_width:
                raise IndexError
        except ValueError:
            messagebox.showwarning("Warning", f"All dimensions must be divisible by {sector_width}.")
        except IndexError:
            messagebox.showwarning("Warning", f"Resulting map dimensions must be positive.")
        else:

            result = (north_val, south_val, east_val, west_val)
            root.quit()
            root.destroy()

    def on_close():
        root.quit()
        root.destroy()

    result = None
    root = tk.Tk()
    root.title("Resize")
    root.geometry("225x200")
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", on_close)

    frame = tk.Frame(root)
    frame.pack(expand=True)

    tk.Label(frame, text="Extend north:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
    north_entry = tk.Entry(frame)
    north_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
    north_entry.insert(0, "0")
    north_entry.bind("<FocusOut>", lambda event: validate_entries())

    tk.Label(frame, text="Extend south:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
    south_entry = tk.Entry(frame)
    south_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
    south_entry.insert(0, "0")
    south_entry.bind("<FocusOut>", lambda event: validate_entries())

    tk.Label(frame, text="Extend east:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
    east_entry = tk.Entry(frame)
    east_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
    east_entry.insert(0, "0")
    east_entry.bind("<FocusOut>", lambda event: validate_entries())

    tk.Label(frame, text="Extend west:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
    west_entry = tk.Entry(frame)
    west_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
    west_entry.insert(0, "0")
    west_entry.bind("<FocusOut>", lambda event: validate_entries())

    check_var = tk.BooleanVar(value=False)
    check_button = tk.Checkbutton(frame, text="Invert extend and indent", variable=check_var)
    check_button.grid(row=4, column=0, columnspan=2, pady=5)

    ok_button = tk.Button(frame, text="OK", state=tk.NORMAL, command=on_ok)
    ok_button.grid(row=5, column=0, columnspan=2, pady=10)

    root.mainloop()
    return result