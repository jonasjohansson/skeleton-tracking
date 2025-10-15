#!/usr/bin/env python3
"""
Test the transform with matched resolutions.
"""

import cv2
import numpy as np
import os

def test_transform_matched():
    """Test the perspective transform with matched resolutions."""
    print("Testing FaceCam to ZED Transform (Matched Resolution)")
    print("=" * 55)
    
    # Load transform
    try:
        transform_matrix = np.load("data/facecam_to_zed_transform.npy")
        print(f"Loaded transform matrix: {transform_matrix.shape}")
    except FileNotFoundError:
        print("Transform not found! Run match_facecam_to_zed_simple.py first.")
        return
    
    # Open cameras
    cap_facecam = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # FaceCam
    cap_zed = cv2.VideoCapture(3, cv2.CAP_DSHOW)      # ZED via OBS
    
    if not cap_facecam.isOpened():
        print("Failed to open FaceCam (Camera 1)")
        return
    
    if not cap_zed.isOpened():
        print("Failed to open ZED camera (Camera 3)")
        cap_facecam.release()
        return
    
    # Set both cameras to the same resolution (ZED resolution)
    target_width, target_height = 1920, 1080
    
    cap_facecam.set(cv2.CAP_PROP_FRAME_WIDTH, target_width)
    cap_facecam.set(cv2.CAP_PROP_FRAME_HEIGHT, target_height)
    cap_zed.set(cv2.CAP_PROP_FRAME_WIDTH, target_width)
    cap_zed.set(cv2.CAP_PROP_FRAME_HEIGHT, target_height)
    
    # Get actual resolutions
    w_f, h_f = int(cap_facecam.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap_facecam.get(cv2.CAP_PROP_FRAME_HEIGHT))
    w_z, h_z = int(cap_zed.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap_zed.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"FaceCam resolution: {w_f}x{h_f}")
    print(f"ZED resolution: {w_z}x{h_z}")
    
    if w_f != w_z or h_f != h_z:
        print("WARNING: Resolutions don't match! This may cause alignment issues.")
        print("The transform was computed with different resolutions.")
    
    print("Press 'Q' to quit, 'S' to save frames")
    
    saved_count = 0
    
    while True:
        ret_facecam, frame_facecam = cap_facecam.read()
        ret_zed, frame_zed = cap_zed.read()
        
        if not ret_facecam or not ret_zed:
            print("Failed to read from cameras")
            break
        
        # Apply perspective transform to FaceCam
        transformed_facecam = cv2.warpPerspective(
            frame_facecam, transform_matrix, (w_z, h_z)
        )
        
        # Add labels
        cv2.putText(transformed_facecam, "FaceCam (Transformed)", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame_zed, "ZED (Original)", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Show both images
        cv2.imshow("FaceCam (Transformed)", transformed_facecam)
        cv2.imshow("ZED (Original)", frame_zed)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('s') or key == ord('S'):
            # Save frames
            cv2.imwrite(f"transformed_facecam_{saved_count:03d}.png", transformed_facecam)
            cv2.imwrite(f"original_zed_{saved_count:03d}.png", frame_zed)
            saved_count += 1
            print(f"Saved frames: {saved_count}")
    
    cap_facecam.release()
    cap_zed.release()
    cv2.destroyAllWindows()
    print("Transform test completed!")

if __name__ == "__main__":
    test_transform_matched()

