#!/usr/bin/env python3
"""
Spout sender for transformed FaceCam.
"""

import cv2
import numpy as np
import os

def spout_facecam_transformed():
    """Send transformed FaceCam via Spout."""
    print("Spout FaceCam Transformed")
    print("=" * 30)
    print("This creates a transformed FaceCam feed for Spout")
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
    print("INSTRUCTIONS FOR SPOUT:")
    print("1. Install Spout for Python: pip install spout")
    print("2. In Resolume, add a 'Spout Receiver' source")
    print("3. Select 'FaceCam_Transformed' as the Spout sender")
    print("4. The transformed FaceCam will appear in Resolume")
    print()
    
    # Try to import Spout
    try:
        import spout
        spout_sender = spout.SpoutSender("FaceCam_Transformed", w, h)
        print("Spout sender initialized successfully!")
        spout_available = True
    except ImportError:
        print("Spout not available. Install with: pip install spout")
        print("Showing preview window instead...")
        spout_available = False
    except Exception as e:
        print(f"Spout initialization failed: {e}")
        print("Showing preview window instead...")
        spout_available = False
    
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
        
        if spout_available:
            # Send via Spout
            try:
                spout_sender.send(transformed)
            except Exception as e:
                print(f"Spout send error: {e}")
        else:
            # Show preview window
            overlay = transformed.copy()
            cv2.putText(overlay, "Transformed FaceCam (Spout)", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(overlay, f"Resolution: {w}x{h}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            cv2.imshow("Spout FaceCam Transformed", overlay)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('s') or key == ord('S'):
            # Save test frame
            test_filename = f"spout_facecam_transformed_{saved_count:03d}.png"
            cv2.imwrite(test_filename, transformed)
            saved_count += 1
            print(f"Saved test frame: {test_filename}")
    
    if spout_available:
        spout_sender.close()
    
    cap_facecam.release()
    cv2.destroyAllWindows()
    print("Spout FaceCam Transformed stopped")

if __name__ == "__main__":
    spout_facecam_transformed()

