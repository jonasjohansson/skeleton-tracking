#!/usr/bin/env python3
"""
Simple Spout-style sender for transformed FaceCam using window capture.
"""

import cv2
import numpy as np
import os

def spout_facecam_simple():
    """Send transformed FaceCam via window capture (Spout-style)."""
    print("FaceCam Transformed (Window Capture)")
    print("=" * 40)
    print("This creates a transformed FaceCam window for capture")
    print()
    
    # Load transform
    try:
        transform_matrix = np.load("data/facecam_to_zed_transform.npy")
        print(f"Loaded transform matrix: {transform_matrix.shape}")
    except FileNotFoundError:
        print("Transform not found! Run match_facecam_to_zed_simple.py first.")
        return
    
    # Open FaceCam at native resolution
    cap_facecam = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # FaceCam
    
    if not cap_facecam.isOpened():
        print("Failed to open FaceCam (Camera 1)")
        return
    
    # Get actual resolution
    w, h = int(cap_facecam.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap_facecam.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"FaceCam resolution: {w}x{h}")
    
    # Create corrected transform for native resolution
    scale_x = w / 1920.0  # 960/1920 = 0.5
    scale_y = h / 1080.0  # 540/1080 = 0.5
    
    scale_matrix = np.array([
        [scale_x, 0, 0],
        [0, scale_y, 0],
        [0, 0, 1]
    ], dtype=np.float32)
    
    corrected_transform = scale_matrix @ transform_matrix
    
    print("Press 'Q' to quit, 'S' to save frames")
    print()
    print("INSTRUCTIONS FOR RESOLUME:")
    print("1. In Resolume, add a 'Window Capture' source")
    print("2. Select this window: 'FaceCam_Transformed_Spout'")
    print("3. The transformed FaceCam will appear in Resolume")
    print("4. This works like Spout but uses window capture")
    print()
    
    saved_count = 0
    
    while True:
        ret, frame = cap_facecam.read()
        
        if not ret:
            print("Failed to read from FaceCam")
            break
        
        # Apply corrected perspective transform
        transformed = cv2.warpPerspective(
            frame, corrected_transform, (w, h)
        )
        
        # Create a clean window for capture (no overlays)
        # This is what Resolume will capture
        clean_output = transformed.copy()
        
        # Display the transformed FaceCam
        cv2.imshow("FaceCam_Transformed_Spout", clean_output)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('s') or key == ord('S'):
            # Save test frame
            test_filename = f"spout_facecam_transformed_{saved_count:03d}.png"
            cv2.imwrite(test_filename, transformed)
            saved_count += 1
            print(f"Saved test frame: {test_filename}")
    
    cap_facecam.release()
    cv2.destroyAllWindows()
    print("FaceCam Transformed Spout stopped")

if __name__ == "__main__":
    spout_facecam_simple()

