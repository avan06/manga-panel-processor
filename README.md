# Image Panel Border Cleaner

A simple Python utility designed to automatically detect and remove the borders of comic book panels.

This tool uses OpenCV's contour detection and image skeletonization (thinning) to accurately find the innermost border line, which is effective even when borders intersect with other elements like speech bubbles.

## Features

-   Automatically removes the border from a single comic panel image.
-   Uses image skeletonization to accurately locate the innermost border line.
-   Allows customization of the border search zone and internal padding.

## Installation

You can install this package directly from GitHub using pip:

```bash
pip install git+https://github.com/avan06/image-panel-border-cleaner.git
```

This package depends on `numpy` and `opencv-contrib-python`, which will be installed automatically by pip.

## Usage

After installation, you can use it in your Python scripts as follows:

```python
import cv2
from image_panel_border_cleaner import remove_border

# Load your panel image
panel_image = cv2.imread("path/to/your/panel.png")

# Remove the border
cleaned_panel = remove_border(panel_image)

# Save or display the result
cv2.imwrite("path/to/cleaned_panel.png", cleaned_panel)
```

## License

This project is licensed under the [Apache License 2.0](LICENSE).