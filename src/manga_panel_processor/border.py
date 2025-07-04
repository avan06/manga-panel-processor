import cv2
import numpy as np

# Ensure the thinning function is available
try:
    # Attempt to import the thinning function from the contrib module
    from cv2.ximgproc import thinning
except ImportError:
    # If opencv-contrib-python is not installed, print a warning and provide a dummy function
    print("Warning: cv2.ximgproc.thinning not found. Border removal might be less effective.")
    print("Please install 'opencv-contrib-python' via 'pip install opencv-contrib-python'")
    def thinning(src, thinningType=None): # Dummy function to prevent crashes
        return src


def _find_best_border_line(roi_mask: np.ndarray, axis: int, scan_range: range) -> int:
    """
    A helper function to find the best border line along a single axis.
    It scans from the inside-out and returns the index of the line with the highest score.

    Parameters:
    - roi_mask: The skeletonized mask of the panel's border area.
    - axis: The axis to scan along (0 for vertical, 1 for horizontal).
    - scan_range: The range of indices to scan (defines direction and search zone).

    Returns:
    - The index of the most likely border line.
    """
    best_index, max_score = scan_range.start, -1
    
    # The total span of the search, used for normalizing the position weight.
    total_span = abs(scan_range.stop - scan_range.start)
    if total_span == 0:
        return best_index

    for i in scan_range:
        # Calculate continuity score based on the scan axis
        if axis == 1: # Horizontal scan (for top/bottom borders)
            continuity_score = np.count_nonzero(roi_mask[i, :])
        else: # Vertical scan (for left/right borders)
            continuity_score = np.count_nonzero(roi_mask[:, i])
            
        # Position weight increases as we move from the start (inner) to the end (outer) of the range.
        # This prioritizes lines closer to the physical edge of the panel.
        progress = abs(i - scan_range.start)
        position_weight = progress / total_span
        
        # Combine scores
        score = continuity_score * (1 + position_weight)
        
        # Update if we found a better candidate
        if score >= max_score:
            max_score, best_index = score, i
            
    return best_index


def remove_border(panel_image: np.ndarray, 
                  search_zone_ratio: float = 0.25, 
                  padding: int = 5) -> np.ndarray:
    """
    Removes borders using skeletonization and weighted projection analysis.
    This definitive version accurately finds the innermost border line by reducing
    all contour lines to a single-pixel width, eliminating thickness bias from
    speech bubble intersections.

    Parameters:
    - panel_image: The input panel image.
    - search_zone_ratio: The percentage of the panel's width/height from the edge
                         to define the search area for a border (e.g., 0.25 = 25%).
    - padding: Pixels to add inside the final detected border to avoid clipping art.

    Returns:
    - The cropped panel image, or the original if processing fails.
    """
    # Return original image if it's invalid or too small to process
    if panel_image is None or panel_image.shape[0] < 30 or panel_image.shape[1] < 30:
        return panel_image

    # --- 1. Preparation ---
    # Add a safe, white border to separate the panel's border from the image edge
    pad_size = 15
    padded_image = cv2.copyMakeBorder(
        panel_image, pad_size, pad_size, pad_size, pad_size,
        cv2.BORDER_CONSTANT, value=[255, 255, 255]
    )
    
    # Convert to grayscale and binarize to highlight non-white areas
    gray = cv2.cvtColor(padded_image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    
    # Find the outermost contour, which should now be the panel itself
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # If no contours are found, there's nothing to process
    if not contours:
        return panel_image

    # The largest contour is almost always the panel we want
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)

    # --- 2. Create Skeletonized Mask ---
    # Create a mask by filling the largest contour
    filled_mask = np.zeros_like(gray)
    cv2.drawContours(filled_mask, [largest_contour], -1, 255, cv2.FILLED)
    
    # Create a hollow version of the contour to provide a clean input for skeletonization.
    # Use a fixed number of erosion iterations to define the thickness of the hollow ring.
    erosion_iterations = 5 
    hollow_contour = cv2.subtract(filled_mask, cv2.erode(filled_mask, np.ones((3,3), np.uint8), iterations=erosion_iterations))
    
    # Perform skeletonization to reduce varied-thickness lines to a single-pixel-wide skeleton
    skeleton = thinning(hollow_contour)
    
    # Crop the skeleton mask to the Region of Interest (ROI) for analysis
    roi_mask = skeleton[y:y+h, x:x+w]

    # --- 3. Find Borders using the Helper Function ---
    # Define search zones and scan ranges for each border
    top_search_end = int(h * search_zone_ratio)
    bottom_search_start = h - top_search_end
    left_search_end = int(w * search_zone_ratio)
    right_search_start = w - left_search_end
    
    # The scan_range determines the direction (inside-out)
    top_range = range(top_search_end, -1, -1)
    bottom_range = range(bottom_search_start, h)
    left_range = range(left_search_end, -1, -1)
    right_range = range(right_search_start, w)
    
    # Call the common function for each border
    
    # --- Find Top Border ---
    best_top_y = _find_best_border_line(roi_mask, axis=1, scan_range=top_range)
    # --- Find Bottom Border ---
    best_bottom_y = _find_best_border_line(roi_mask, axis=1, scan_range=bottom_range)
    # --- Find Left Border ---
    best_left_x = _find_best_border_line(roi_mask, axis=0, scan_range=left_range)
    # --- Find Right Border ---
    best_right_x = _find_best_border_line(roi_mask, axis=0, scan_range=right_range)

    # --- 4. Final Cropping ---
    # Convert relative ROI coordinates back to the global coordinates of the padded image and apply padding
    final_x1 = x + best_left_x + padding
    final_y1 = y + best_top_y + padding
    final_x2 = x + best_right_x - padding
    final_y2 = y + best_bottom_y - padding
    
    # If the calculated coordinates are invalid, return the original image
    if final_x1 >= final_x2 or final_y1 >= final_y2: 
        return panel_image
        
    # Crop the final result from the padded image
    cropped = padded_image[final_y1:final_y2, final_x1:final_x2]
    
    # Perform a final check to ensure the cropped image is not too small
    if cropped.shape[0] < 10 or cropped.shape[1] < 10: 
        return panel_image
        
    return cropped
