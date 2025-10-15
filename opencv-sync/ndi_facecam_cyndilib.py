#!/usr/bin/env python3
"""
NDI sender for transformed FaceCam using cyndilib.
"""

import cv2
import numpy as np
import time
from cyndilib.sender import Sender
from cyndilib.video_frame import VideoSendFrame
from cyndilib.wrapper.ndi_structs import FourCC

def ndi_facecam_cyndilib():
    """Send transformed FaceCam over NDI using cyndilib."""
    print("NDI FaceCam Transformed (cyndilib)")
    print("=" * 40)
    print("This creates a direct NDI stream of the transformed FaceCam")
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
    
    # Create NDI sender
    sender_name = "FaceCam_Transformed"
    sender = Sender(sender_name)
    
    # Create video frame for NDI
    vf = VideoSendFrame()
    vf.set_resolution(w, h)
    vf.set_frame_rate(30)  # 30 FPS
    vf.set_fourcc(FourCC.BGRA)  # Use BGRA format
    
    # Add video frame to sender
    sender.set_video_frame(vf)
    
    print(f"NDI Sender: '{sender_name}'")
    print("Press 'Q' to quit, 'S' to save frames")
    print()
    print("INSTRUCTIONS FOR RESOLUME:")
    print("1. In Resolume, add an 'NDI' source")
    print(f"2. Select '{sender_name}' from the NDI sources list")
    print("3. The transformed FaceCam will appear directly in Resolume")
    print()
    
    saved_count = 0
    frame_count = 0
    
    try:
        with sender:
            while True:
                ret, frame = cap_facecam.read()
                
                if not ret:
                    print("Failed to read from FaceCam")
                    break
                
                # Apply corrected perspective transform
                transformed = cv2.warpPerspective(
                    frame, corrected_transform, (w, h),
                    flags=cv2.INTER_LINEAR,
                    borderMode=cv2.BORDER_CONSTANT,
                    borderValue=(0, 0, 0)
                )
                
                # Convert BGR to BGRA for NDI
                bgra_frame = cv2.cvtColor(transformed, cv2.COLOR_BGR2BGRA)
                
                # Flatten the frame to 1D array for NDI
                frame_data = bgra_frame.flatten()
                
                # Send frame over NDI
                sender.write_video_async(frame_data)
                
                # Display for debugging
                cv2.imshow("NDI_FaceCam_Transformed", transformed)
                
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q') or key == ord('Q'):
                    break
                elif key == ord('s') or key == ord('S'):
                    # Save test frame
                    test_filename = f"ndi_facecam_cyndilib_{saved_count:03d}.png"
                    cv2.imwrite(test_filename, transformed)
                    saved_count += 1
                    print(f"Saved test frame: {test_filename}")
                
                frame_count += 1
                if frame_count % 100 == 0:
                    print(f"Sent {frame_count} frames over NDI")
    
    except KeyboardInterrupt:
        print("\nStopping NDI sender...")
    
    finally:
        cap_facecam.release()
        cv2.destroyAllWindows()
        print("NDI FaceCam Transformed (cyndilib) stopped")

if __name__ == "__main__":
    ndi_facecam_cyndilib()
