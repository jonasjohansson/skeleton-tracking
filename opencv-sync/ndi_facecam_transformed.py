#!/usr/bin/env python3
"""
NDI sender for transformed FaceCam at native resolution (960x540).
"""

import cv2
import numpy as np
import os

def ndi_facecam_transformed():
    """Send transformed FaceCam over NDI at native resolution."""
    print("NDI FaceCam Transformed (960x540)")
    print("=" * 35)
    print("This creates a transformed FaceCam feed for NDI")
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
    print("INSTRUCTIONS FOR NDI:")
    print("1. Open OBS Studio")
    print("2. Add a 'Window Capture' source")
    print("3. Select this window: 'NDI FaceCam Transformed'")
    print("4. Install OBS NDI plugin if not already installed")
    print("5. Add 'NDI Output' filter to the source")
    print("6. Configure NDI output settings")
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
        
        # Add subtle overlay info (can be removed for clean NDI)
        overlay = transformed.copy()
        cv2.putText(overlay, "Transformed FaceCam for NDI", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(overlay, f"Resolution: {w}x{h}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Display the transformed FaceCam
        cv2.imshow("NDI FaceCam Transformed", overlay)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('s') or key == ord('S'):
            # Save test frame
            test_filename = f"ndi_facecam_transformed_{saved_count:03d}.png"
            cv2.imwrite(test_filename, transformed)
            saved_count += 1
            print(f"Saved test frame: {test_filename}")
    
    cap_facecam.release()
    cv2.destroyAllWindows()
    print("NDI FaceCam Transformed stopped")

if __name__ == "__main__":
    ndi_facecam_transformed()

