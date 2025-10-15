#!/usr/bin/env python3
"""
Optimized NDI sender for transformed FaceCam using efficient OpenCV operations.
"""

import cv2
import numpy as np
import os

def ndi_facecam_optimized():
    """Send transformed FaceCam over NDI with optimizations."""
    print("NDI FaceCam Transformed (Optimized)")
    print("=" * 40)
    print("This creates an optimized transformed FaceCam feed for NDI")
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
    
    # Pre-allocate arrays for better performance
    output_size = (w, h)
    
    print("Press 'Q' to quit, 'S' to save frames")
    print()
    print("INSTRUCTIONS FOR NDI:")
    print("1. Open OBS Studio")
    print("2. Add a 'Window Capture' source")
    print("3. Select this window: 'NDI_FaceCam_Optimized'")
    print("4. Install OBS NDI plugin if not already installed")
    print("5. Add 'NDI Output' filter to the source")
    print("6. Configure NDI output settings")
    print("7. In Resolume, add an 'NDI' source")
    print("8. Select the NDI stream from OBS")
    print()
    
    saved_count = 0
    frame_count = 0
    
    while True:
        ret, frame = cap_facecam.read()
        
        if not ret:
            print("Failed to read from FaceCam")
            break
        
        # Apply corrected perspective transform with optimized parameters
        transformed = cv2.warpPerspective(
            frame, corrected_transform, output_size,
            flags=cv2.INTER_LINEAR,  # Use linear interpolation for speed
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0)  # Black border
        )
        
        # Create a clean window for NDI (no overlays for better performance)
        clean_output = transformed.copy()
        
        # Display the transformed FaceCam
        cv2.imshow("NDI_FaceCam_Optimized", clean_output)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('s') or key == ord('S'):
            # Save test frame
            test_filename = f"ndi_facecam_optimized_{saved_count:03d}.png"
            cv2.imwrite(test_filename, transformed)
            saved_count += 1
            print(f"Saved test frame: {test_filename}")
        
        frame_count += 1
        if frame_count % 100 == 0:
            print(f"Processed {frame_count} frames")
    
    cap_facecam.release()
    cv2.destroyAllWindows()
    print("NDI FaceCam Transformed (Optimized) stopped")

if __name__ == "__main__":
    ndi_facecam_optimized()

