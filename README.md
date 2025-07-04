# Manga Panel Processor

A Python utility toolkit for processing comic or manga panels.

This package provides two main features:

1. **Panel Border Cleaner** – Removes borders from individual comic panels using image skeletonization.
2. **Panel Sorter** – Automatically sorts multiple panels on a full comic page based on natural reading order (top-to-bottom, then left-to-right or right-to-left).

---

## Features

- **Remove Borders**: Cleanly removes borders from individual comic panels using OpenCV and thinning algorithms.
- **Sort Panels**: Automatically reorders multiple comic panels from a full page scan into the correct reading sequence.
- Supports both **left-to-right (LTR)** and **right-to-left (RTL)** reading directions.
- Robust vertical grouping logic with dynamic tolerance for complex layouts, including asymmetric and spanning panels.

---

## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/avan06/manga-panel-processor.git
```

Dependencies such as `numpy` and `opencv-contrib-python` will be installed automatically.

---

## Usage

### Remove Border from a Single Panel

```python
import cv2
from manga_panel_processor import remove_border

panel_image = cv2.imread("path/to/panel.png")
cleaned = remove_border(panel_image)
cv2.imwrite("cleaned.png", cleaned)
```

---

### Sort Panels on a Full Page

```python
import cv2
from manga_panel_processor import sort_panels_by_column_then_row

# Assume 'contours' is a list of bounding contours (from cv2.findContours)
# or bounding boxes (x, y, w, h) for each panel
contours = [...]  # extracted from page layout

# Sort panels in right-to-left reading order (typical for Japanese manga)
sorted_panels = sort_panels_by_column_then_row(contours, rtl_order=True)

# Now 'sorted_panels' is ordered for reading: top-to-bottom, right-to-left
```

The sorting algorithm first splits panels into left and right columns based on horizontal gaps, sorts each column by top-to-bottom, and merges them according to the specified reading direction. Spanning panels (e.g. wide bottom panels) are inserted according to their vertical position.

---

## License

This project is licensed under the [Apache License 2.0](LICENSE).
