"""
Step 2 of the preprocessing pipeline: classical CV skull-stripping heuristic.

Explicitly documented as an unvalidated heuristic, not clinical-grade (not
equivalent to BET/HD-BET). The documented upgrade path if classification
accuracy suffers is swapping in a trained 2D brain-extraction model as a
drop-in replacement for this one function - no other pipeline code would
need to change.
"""
import cv2
import numpy as np


def skull_strip(rgb_array: np.ndarray) -> np.ndarray:
    """
    Otsu thresholding (works reasonably in MRI because, unlike CT, skull
    bone is typically LOW signal, not high, in T1/T2 MRI - so background
    air and skull both tend toward the dark end, making a bright/dark
    split a usable - if crude - starting point), morphological closing,
    largest-contour extraction, an erosion step to shed the skull rim
    itself, and hole-filling.
    """
    gray = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2GRAY)

    _, thresholded = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Morphological closing to bridge small gaps.
    kernel = np.ones((5, 5), np.uint8)
    closed = cv2.morphologyEx(thresholded, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        # Degenerate input (no foreground detected at all) - return the
        # original array unchanged rather than silently zeroing everything out.
        return rgb_array

    # Take the single largest connected contour as "the head," discard
    # everything else (removes small bright artifacts).
    largest_contour = max(contours, key=cv2.contourArea)
    if cv2.contourArea(largest_contour) == 0:
        return rgb_array

    mask = np.zeros_like(gray)
    cv2.drawContours(mask, [largest_contour], -1, 255, thickness=cv2.FILLED)

    # Erosion step to shed the skull rim itself - an improvement to more
    # directly acknowledge that Otsu alone segments "the head" (skull
    # included), not "the brain" specifically.
    erosion_kernel = np.ones((9, 9), np.uint8)
    eroded_mask = cv2.erode(mask, erosion_kernel, iterations=1)

    # Hole-filling on the final mask.
    filled_mask = _fill_holes(eroded_mask)

    if filled_mask.sum() == 0:
        # Erosion ate everything - fall back to the un-eroded mask rather
        # than returning a fully black image.
        filled_mask = _fill_holes(mask)

    result = rgb_array.copy()
    result[filled_mask == 0] = 0
    return result


def _fill_holes(mask: np.ndarray) -> np.ndarray:
    filled = mask.copy()
    h, w = mask.shape
    flood_mask = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(filled, flood_mask, (0, 0), 255)
    filled_inv = cv2.bitwise_not(filled)
    return mask | filled_inv
