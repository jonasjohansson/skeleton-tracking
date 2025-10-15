#!/usr/bin/env python3
"""
Capture calibration images directly from ZED camera (Camera 2).
"""

import cv2
import numpy as np
import time
import os
from board_def import DICT

def capture_zed_direct():
    """Capture calibration images directly from ZED camera."""
    print("ZED Camera Direct Capture")
    print("=" * 30)
    print("Camera: ZED Camera (Camera 2)")
    print("Resolution: 1280x720 @ 30fps")
    print()
    
    # Create ArUco detector
    det = cv2.aruco.ArucoDetector(DICT, cv2.aruco.DetectorParameters())
    
    # Use camera 2 for ZED (Media Foundation backend)
    camera_index = 2
    
    print(f"Using camera {camera_index} as ZED camera")
    
    # Open the ZED camera with Media Foundation backend
    cap = cv2.VideoCapture(camera_index, cv2.CAP_MSMF)
    
    if not cap.isOpened():
        print(f"Failed to open ZED camera {camera_index}")
        return
    
    # Get camera properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"ZED camera resolution: {width}x{height} @ {fps}fps")
    
    print("\nInstructions:")
    print("- Position the iPad with ChArUco pattern in front of the ZED camera")
    print("- Move the iPad to different positions and angles")
    print("- Press 'S' to save frame when pattern is clearly visible")
    print("- Capture 20-30 images")
    print("- Press 'Q' to quit")
    print()
    
    # Prepare scans output directory
    scans_dir = "scans"
    os.makedirs(scans_dir, exist_ok=True)
    
    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read from ZED camera")
            break
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect ArUco markers
        corners, ids, _ = det.detectMarkers(gray)
        
        # Create visualization
        vis = frame.copy()
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(vis, corners, ids)
        
        # Add status text
        marker_count = len(ids) if ids is not None else 0
        cv2.putText(vis, f"ZED Camera - Resolution: {width}x{height}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(vis, f"Markers: {marker_count} - Saved: {saved_count}", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        if ids is not None and len(ids) >= 4:
            cv2.putText(vis, "GOOD - Press 'S' to save!", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(vis, "NEED MORE MARKERS - Try different position", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        cv2.putText(vis, "Press 'S' to save, 'Q' to quit", (10, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.imshow("ZED Camera Calibration", vis)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s') or key == ord('S'):
            if ids is not None and len(ids) >= 4:  # Require at least 4 markers
                filename = os.path.join(scans_dir, f"cal_zed_{saved_count:03d}.png")
                cv2.imwrite(filename, gray)  # Save grayscale image
                saved_count += 1
                print(f"Saved: {filename} ({saved_count} images)")
                time.sleep(0.15)  # Small delay to prevent rapid saves
            else:
                print("Not enough markers detected. Try different position.")
        
        elif key == ord('q') or key == ord('Q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"Captured {saved_count} images for ZED camera")

if __name__ == "__main__":
    capture_zed_direct()
