#!/usr/bin/env python3
"""
Test the transform with corrected scaling for native resolution.
"""

import cv2
import numpy as np
import os

def test_transform_corrected():
    """Test the perspective transform with corrected scaling."""
    print("FaceCam Transform with Corrected Scaling")
    print("=" * 40)
    
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
    print(f"FaceCam native resolution: {w}x{h}")
    
    # The transform was computed to map from FaceCam (960x540) to ZED (1920x1080)
    # We need to scale it down to map from FaceCam (960x540) to FaceCam (960x540)
    # This means we need to scale the transform matrix
    
    # Create a scaling matrix to adjust the transform
    # Scale factor: 960/1920 = 0.5, 540/1080 = 0.5
    scale_x = w / 1920.0  # 960/1920 = 0.5
    scale_y = h / 1080.0  # 540/1080 = 0.5
    
    print(f"Scale factors: x={scale_x:.2f}, y={scale_y:.2f}")
    
    # Create scaling matrix
    scale_matrix = np.array([
        [scale_x, 0, 0],
        [0, scale_y, 0],
        [0, 0, 1]
    ], dtype=np.float32)
    
    # Apply scaling to the transform matrix
    corrected_transform = scale_matrix @ transform_matrix
    
    print("Press 'Q' to quit, 'S' to save frames")
    
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
        
        # Add labels
        cv2.putText(frame, "FaceCam (Original)", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(transformed, "FaceCam (Transformed)", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Show side by side
        combined = np.hstack((frame, transformed))
        cv2.imshow("FaceCam: Original vs Transformed (Corrected)", combined)
        
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
    test_transform_corrected()

