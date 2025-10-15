#!/usr/bin/env python3
"""
Test the transform with FaceCam at native resolution (960x540).
"""

import cv2
import numpy as np
import os

def test_transform_native():
    """Test the perspective transform with FaceCam at native resolution."""
    print("FaceCam Transform at Native Resolution (960x540)")
    print("=" * 50)
    
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
    
    # Don't try to set resolution - use native
    # Get actual resolution
    w, h = int(cap_facecam.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap_facecam.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"FaceCam native resolution: {w}x{h}")
    
    print("Press 'Q' to quit, 'S' to save frames")
    
    saved_count = 0
    
    while True:
        ret, frame = cap_facecam.read()
        
        if not ret:
            print("Failed to read from FaceCam")
            break
        
        # Apply perspective transform at native resolution
        transformed = cv2.warpPerspective(
            frame, transform_matrix, (w, h)
        )
        
        # Add labels
        cv2.putText(frame, "FaceCam (Original)", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(transformed, "FaceCam (Transformed)", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Show side by side
        combined = np.hstack((frame, transformed))
        cv2.imshow("FaceCam: Original vs Transformed (960x540)", combined)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('s') or key == ord('S'):
            # Save frames
            cv2.imwrite(f"facecam_original_{saved_count:03d}.png", frame)
            cv2.imwrite(f"facecam_transformed_{saved_count:03d}.png", transformed)
            saved_count += 1
            print(f"Saved frames: {saved_count}")
    
    cap_facecam.release()
    cv2.destroyAllWindows()
    print("Transform test completed!")

if __name__ == "__main__":
    test_transform_native()

