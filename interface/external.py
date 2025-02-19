import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from sections.walk_sector_points import sector_width

def askopenfilename(*args, **kwargs):
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(*args, **kwargs)
    return filepath if filepath != "" else None

def asksaveasfilename(*args, **kwargs):
    root = tk.Tk()
    root.withdraw()
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
        if width_val % 20 == 0 and height_val % 20 == 0 and width_val > 0 and height_val > 0:
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
    root.protocol("WM_DELETE_WINDOW", on_close)  # Handle 'X' button press

    frame = tk.Frame(root)
    frame.pack(expand=True)

    tk.Label(frame, text="Width:").grid(row=0, column=0, padx=5, pady=5, sticky='ew')
    width_entry = tk.Entry(frame)
    width_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
    width_entry.insert(0, "20")
    width_entry.bind("<FocusOut>", lambda event: validate_entries())

    tk.Label(frame, text="Height:").grid(row=1, column=0, padx=5, pady=5, sticky='ew')
    height_entry = tk.Entry(frame)
    height_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
    height_entry.insert(0, "20")
    height_entry.bind("<FocusOut>", lambda event: validate_entries())

    ok_button = tk.Button(frame, text="OK", state=tk.NORMAL, command=on_ok)
    ok_button.grid(row=2, column=0, columnspan=2, pady=10)

    root.mainloop()
    return result
