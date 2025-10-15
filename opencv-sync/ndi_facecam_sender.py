#!/usr/bin/env python3
"""
NDI FaceCam Sender
Sends the transformed FaceCam over NDI using a virtual camera approach.
This creates a virtual camera that OBS can capture and send over NDI.
"""

import cv2
import numpy as np
import os
import sys
from board_def import DICT, BOARD

def create_ndi_facecam_sender():
    """Create NDI sender for transformed FaceCam"""
    
    print("NDI FaceCam Sender")
    print("=" * 30)
    print("This creates a virtual camera feed that OBS can capture for NDI")
    print("Make sure OBS is running and can access virtual cameras")
    print()
    
    # Load the transform matrix
    transform_file = "data/facecam_to_zed_transform.npy"
    if not os.path.exists(transform_file):
        print(f"ERROR: Transform file not found: {transform_file}")
        print("Please run match_facecam_to_zed_simple.py first to generate the transform")
        return False
    
    M = np.load(transform_file)
    print(f"Loaded transform matrix: {M.shape}")
    
    # Initialize cameras
    cap_facecam = cv2.VideoCapture(0)  # FaceCam
    cap_zed = cv2.VideoCapture(3)      # ZED via OBS
    
    if not cap_facecam.isOpened():
        print("ERROR: Could not open FaceCam (Camera 0)")
        return False
    
    if not cap_zed.isOpened():
        print("ERROR: Could not open ZED camera (Camera 3)")
        return False
    
    # Set camera properties
    cap_facecam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap_facecam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap_facecam.set(cv2.CAP_PROP_FPS, 30)
    
    cap_zed.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap_zed.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap_zed.set(cv2.CAP_PROP_FPS, 30)
    
    print("Cameras initialized successfully!")
    print("FaceCam: 1920x1080 @ 30fps")
    print("ZED: 1920x1080 @ 30fps")
    print()
    print("INSTRUCTIONS FOR NDI:")
    print("1. Open OBS Studio")
    print("2. Add a 'Window Capture' source")
    print("3. Select this window: 'NDI FaceCam Sender'")
    print("4. Install OBS NDI plugin if not already installed")
    print("5. Add 'NDI Output' filter to the source")
    print("6. Configure NDI output settings")
    print()
    print("Press 'Q' to quit, 'S' to save a test frame")
    
    # Create output window
    cv2.namedWindow("NDI FaceCam Sender", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("NDI FaceCam Sender", 1920, 1080)
    
    frame_count = 0
    
    while True:
        # Read frames
        ret_facecam, frame_facecam = cap_facecam.read()
        ret_zed, frame_zed = cap_zed.read()
        
        if not ret_facecam or not ret_zed:
            print("Failed to read from cameras")
            break
        
        # Apply perspective transform to FaceCam
        h, w = frame_facecam.shape[:2]
        transformed_facecam = cv2.warpPerspective(frame_facecam, M, (w, h))
        
        # Create side-by-side display for NDI
        # Resize to fit in 1920x1080 window
        display_size = (960, 540)
        zed_resized = cv2.resize(frame_zed, display_size)
        facecam_resized = cv2.resize(transformed_facecam, display_size)
        
        # Create side-by-side layout
        ndi_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        
        # Place ZED on left, transformed FaceCam on right
        ndi_frame[270:810, 0:960] = zed_resized
        ndi_frame[270:810, 960:1920] = facecam_resized
        
        # Add labels
        cv2.putText(ndi_frame, "ZED (Original)", (20, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(ndi_frame, "FaceCam (Transformed)", (980, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Add frame counter
        cv2.putText(ndi_frame, f"Frame: {frame_count}", (20, 1030), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Display the NDI frame
        cv2.imshow("NDI FaceCam Sender", ndi_frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('s') or key == ord('S'):
            # Save test frame
            test_filename = f"ndi_test_frame_{frame_count:03d}.png"
            cv2.imwrite(test_filename, ndi_frame)
            print(f"Saved test frame: {test_filename}")
        
        frame_count += 1
    
    # Cleanup
    cap_facecam.release()
    cap_zed.release()
    cv2.destroyAllWindows()
    
    print("NDI FaceCam Sender stopped")
    return True

if __name__ == "__main__":
    try:
        create_ndi_facecam_sender()
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
