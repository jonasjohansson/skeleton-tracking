#!/usr/bin/env python3
"""
NDI FaceCam Only Sender
Sends only the transformed FaceCam over NDI (no side-by-side view).
This creates a clean virtual camera feed for NDI output.
"""

import cv2
import numpy as np
import os
import sys
from board_def import DICT, BOARD

def create_ndi_facecam_only():
    """Create NDI sender for transformed FaceCam only"""
    
    print("NDI FaceCam Only Sender")
    print("=" * 30)
    print("This creates a clean transformed FaceCam feed for NDI")
    print()
    
    # Load the transform matrix
    transform_file = "data/facecam_to_zed_transform.npy"
    if not os.path.exists(transform_file):
        print(f"ERROR: Transform file not found: {transform_file}")
        print("Please run match_facecam_to_zed_simple.py first to generate the transform")
        return False
    
    M = np.load(transform_file)
    print(f"Loaded transform matrix: {M.shape}")
    
    # Initialize FaceCam
    cap_facecam = cv2.VideoCapture(0)  # FaceCam
    
    if not cap_facecam.isOpened():
        print("ERROR: Could not open FaceCam (Camera 0)")
        return False
    
    # Set camera properties for 1080p
    cap_facecam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap_facecam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap_facecam.set(cv2.CAP_PROP_FPS, 30)
    
    print("FaceCam initialized: 1920x1080 @ 30fps")
    print()
    print("INSTRUCTIONS FOR NDI:")
    print("1. Open OBS Studio")
    print("2. Add a 'Window Capture' source")
    print("3. Select this window: 'NDI FaceCam Only'")
    print("4. Install OBS NDI plugin if not already installed")
    print("5. Add 'NDI Output' filter to the source")
    print("6. Configure NDI output settings")
    print()
    print("Press 'Q' to quit, 'S' to save a test frame")
    
    # Create output window
    cv2.namedWindow("NDI FaceCam Only", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("NDI FaceCam Only", 1920, 1080)
    
    frame_count = 0
    
    while True:
        # Read frame
        ret_facecam, frame_facecam = cap_facecam.read()
        
        if not ret_facecam:
            print("Failed to read from FaceCam")
            break
        
        # Apply perspective transform to FaceCam
        h, w = frame_facecam.shape[:2]
        transformed_facecam = cv2.warpPerspective(frame_facecam, M, (w, h))
        
        # Add subtle overlay info (can be removed for clean NDI)
        overlay = transformed_facecam.copy()
        cv2.putText(overlay, "Transformed FaceCam for NDI", (20, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(overlay, f"Frame: {frame_count}", (20, 1030), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Display the transformed FaceCam
        cv2.imshow("NDI FaceCam Only", overlay)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('s') or key == ord('S'):
            # Save test frame
            test_filename = f"ndi_facecam_test_{frame_count:03d}.png"
            cv2.imwrite(test_filename, transformed_facecam)
            print(f"Saved test frame: {test_filename}")
        
        frame_count += 1
    
    # Cleanup
    cap_facecam.release()
    cv2.destroyAllWindows()
    
    print("NDI FaceCam Only Sender stopped")
    return True

if __name__ == "__main__":
    try:
        create_ndi_facecam_only()
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
