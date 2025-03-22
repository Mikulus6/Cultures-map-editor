import os
import sys

def abs_path(path):
    # This function is important when it comes to loading assets from directories hidden in *.exe file.
    return os.path.join(getattr(sys, '_MEIPASS', os.getcwd()), path)
