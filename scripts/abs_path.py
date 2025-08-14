import os
from scripts.fallback import load_with_fallback

@load_with_fallback
def abs_path(path):
    # This function is important when it comes to loading assets from directories hidden in *.exe file.
    if not os.path.exists(abs_path_result := os.path.abspath(path)):
        raise FileNotFoundError
    return abs_path_result
