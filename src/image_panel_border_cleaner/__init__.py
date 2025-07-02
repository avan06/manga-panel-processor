# Define the package version so users can check it.
__version__ = "0.1.1"

# --- Proactive dependency check ---
try:
    # Attempt to import the function we absolutely need.
    from cv2.ximgproc import thinning
except (ImportError, AttributeError):
    # If it fails, raise a custom, user-friendly error message.
    raise ImportError(
        "Could not import the 'thinning' function from 'cv2.ximgproc'. "
        "This is likely because the wrong OpenCV package is installed. "
        "Please uninstall other opencv packages and install the correct one:\n\n"
        "pip uninstall opencv-python opencv-python-headless opencv-contrib-python-headless\n"
        "pip install opencv-contrib-python"
    )

# --- Export the main function ---
# This line will only be reached if the check above passes.
from .border import remove_border