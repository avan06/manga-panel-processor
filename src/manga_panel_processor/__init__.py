import importlib.metadata

try:
    # This will read the version from the installed package's metadata
    __version__ = importlib.metadata.version("image-panel-border-cleaner")
except importlib.metadata.PackageNotFoundError:
    # Fallback for when the package is not installed (e.g., running from source)
    __version__ = "0.0.0-dev"

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
from .border import remove_border, extract_panel_content
from .layout import sort_panels_by_column_then_row