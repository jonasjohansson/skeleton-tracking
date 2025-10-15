#!/usr/bin/env python3
"""
ChArUco board definition with consistent parameters.
Use the same sizes everywhere for proper calibration.
"""

import cv2

# ArUco dictionary - using DICT_5X5_1000 for better marker detection
DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_1000)

# Board dimensions in meters
SQUARE = 0.035  # Square size in meters
MARKER = 0.028  # Marker size in meters

# Create ChArUco board (7x5 squares)
BOARD = cv2.aruco.CharucoBoard((7, 5), SQUARE, MARKER, DICT)

def generate_printable_board(output_path="charuco_A4.png", dpi=300):
    """
    Generate a printable ChArUco board for A4 paper at specified DPI.
    
    Args:
        output_path: Path to save the board image
        dpi: DPI for the output image
    """
    # A4 size at specified DPI
    width_px = int(2480)  # A4 width at ~300 DPI
    height_px = int(1754)  # A4 height at ~300 DPI
    
    # Generate board image
    img = BOARD.generateImage((width_px, height_px))
    cv2.imwrite(output_path, img)
    
    print(f"ChArUco board saved to: {output_path}")
    print(f"Board size: {width_px}x{height_px} pixels")
    print(f"Square size: {SQUARE}m, Marker size: {MARKER}m")
    print("Print this on A4 paper for calibration")

if __name__ == "__main__":
    generate_printable_board()






