import cv2
import numpy as np

def sort_panels_by_column_then_row(items, rtl_order: bool) -> list:
    """
    Core logic:
    1. Compute x_center, y_top, width, and full page width.
    2. Identify spanning panels whose width >= 60% of full width.
    3. Use remaining panels to find largest horizontal gap => split_x.
    4. Assign remaining panels to left or right by x_center < or >= split_x.
    5. Determine column order based on rtl_order.
    6. Sort panels within each column by y_top ascending => non_spanning Ordered.
    7. Sort spanning panels by y_top ascending.
    8. Merge non_spanning and spanning lists by y_top so spanning panels appear in correct vertical position.
    """
    if not items:
        return []

    # Step 1: gather panel data and measure full width
    data = []  # List of tuples: (item, x_center, y_top, x, y, w, h)
    max_x2 = 0
    for item in items:
        if isinstance(item, np.ndarray):
            x, y, w, h = cv2.boundingRect(item)
        else:
            x, y, w, h = item
        max_x2 = max(max_x2, x + w)
        data.append((item, x + w/2, y, x, y, w, h))
    full_width = max_x2

    # Step 2: separate spanning panels (width >= 60% of full page)
    spanning = [d for d in data if d[5] >= full_width * 0.6]
    remaining = [d for d in data if d not in spanning]
    
    # if too few non-spanning, treat all as non-spanning
    if len(remaining) < 2:
        remaining = data
        spanning = []

    # Step 3: find split_x using remaining panels
    remaining.sort(key=lambda d: d[1])
    x_centers = [d[1] for d in remaining]
    gaps = [(x_centers[i+1] - x_centers[i], i) for i in range(len(x_centers)-1)]
    split_idx = max(gaps, key=lambda g: g[0])[1] if gaps else 0
    split_x = (x_centers[split_idx] + x_centers[split_idx+1]) / 2

    # Step 4: divide remaining into left/right
    left_group = [d for d in remaining if d[1] < split_x]
    right_group = [d for d in remaining if d[1] >= split_x]

    # Step 5: set column order
    columns = [left_group, right_group] if not rtl_order else [right_group, left_group]

    # Step 6: sort non-spanning by column then y_top
    non_spanning = []
    for col in columns:
        non_spanning.extend(sorted(col, key=lambda d: d[2]))

    # Step 7: sort spanning by y_top
    spanning_sorted = sorted(spanning, key=lambda d: d[2])

    # Step 8: merge lists by y_top
    merged = []
    i = j = 0
    while i < len(non_spanning) and j < len(spanning_sorted):
        if spanning_sorted[j][2] < non_spanning[i][2]:
            merged.append(spanning_sorted[j][0]); j += 1
        else:
            merged.append(non_spanning[i][0]); i += 1
    # append leftovers
    merged.extend([d[0] for d in non_spanning[i:]])
    merged.extend([d[0] for d in spanning_sorted[j:]])

    return merged