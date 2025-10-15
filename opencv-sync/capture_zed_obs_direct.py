#!/usr/bin/env python3
"""
Capture calibration images from OBS Virtual Camera (Camera 3).
"""

import cv2
import numpy as np
import time
import os
from board_def import DICT

def capture_zed_obs_direct():
    """Capture calibration images from OBS Virtual Camera."""
    print("OBS Virtual Camera Capture")
    print("=" * 30)
    print("Camera: OBS Virtual Camera (Camera 3)")
    print("Resolution: 640x480")
    print()
    
    # Create ArUco detector
    det = cv2.aruco.ArucoDetector(DICT, cv2.aruco.DetectorParameters())
    
    # Use camera 3 for OBS Virtual Camera (DirectShow backend)
    camera_index = 3
    
    print(f"Using camera {camera_index} as OBS Virtual Camera")
    
    # Open the OBS Virtual Camera with DirectShow backend
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print(f"Failed to open OBS Virtual Camera {camera_index}")
        return
    
    # Get camera properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"OBS Virtual Camera resolution: {width}x{height} @ {fps}fps")
    
    # Try to set higher resolution
    print("Attempting to set higher resolution...")
    resolutions = [
        (1920, 1080),  # Full HD
        (1280, 720),   # HD
        (1024, 768),   # XGA
    ]
    
    for target_w, target_h in resolutions:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, target_w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, target_h)
        
        # Check if resolution changed
        new_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        new_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        if new_w > width and new_h > height:
            print(f"  Successfully set to {new_w}x{new_h}")
            width, height = new_w, new_h
            break
        else:
            print(f"  Could not set to {target_w}x{target_h}")
    
    print(f"Final resolution: {width}x{height}")
    
    print("\nInstructions:")
    print("- Make sure OBS is running and showing the ZED camera feed")
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
            print("Failed to read from OBS Virtual Camera")
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
        cv2.putText(vis, f"OBS Virtual Camera - Resolution: {width}x{height}", (10, 30), 
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
        
        cv2.imshow("OBS Virtual Camera Calibration", vis)
        
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
    print(f"Captured {saved_count} images for ZED via OBS Virtual Camera")

if __name__ == "__main__":
    capture_zed_obs_direct()
