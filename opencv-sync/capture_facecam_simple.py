#!/usr/bin/env python3
"""
Simple FaceCam capture with error handling.
"""

import cv2
import numpy as np
import time
import os
from board_def import DICT

def capture_facecam_simple():
    """Simple FaceCam capture."""
    print("FaceCam Simple Capture")
    print("=" * 25)
    
    # Create ArUco detector
    det = cv2.aruco.ArucoDetector(DICT, cv2.aruco.DetectorParameters())
    
    # Open FaceCam with retry logic
    cap = None
    for attempt in range(3):
        print(f"Attempt {attempt + 1} to open FaceCam...")
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print("FaceCam opened successfully!")
                break
            else:
                print("FaceCam opened but can't read frames")
                cap.release()
                cap = None
        else:
            print("Failed to open FaceCam")
            if cap:
                cap.release()
                cap = None
        
        time.sleep(1)
    
    if cap is None:
        print("Could not open FaceCam after 3 attempts")
        return
    
    # Set to HD resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    # Get actual resolution
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"FaceCam resolution: {width}x{height}")
    
    print("\nInstructions:")
    print("- Position ChArUco pattern in front of FaceCam")
    print("- Press 'S' to save, 'Q' to quit")
    print()
    
    # Prepare scans directory
    scans_dir = "scans"
    os.makedirs(scans_dir, exist_ok=True)
    
    saved_count = 0
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print(f"Failed to read frame {frame_count}")
            frame_count += 1
            if frame_count > 10:
                print("Too many failed reads, stopping")
                break
            time.sleep(0.1)
            continue
        
        frame_count = 0  # Reset on successful read
        
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
        cv2.putText(vis, f"FaceCam - {width}x{height}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(vis, f"Markers: {marker_count} - Saved: {saved_count}", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        if ids is not None and len(ids) >= 4:
            cv2.putText(vis, "GOOD - Press 'S' to save!", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(vis, "Need more markers", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        cv2.putText(vis, "Press 'S' to save, 'Q' to quit", (10, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.imshow("FaceCam Simple Capture", vis)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s') or key == ord('S'):
            if ids is not None and len(ids) >= 4:
                filename = os.path.join(scans_dir, f"cal_facecam_hd_{saved_count:03d}.png")
                cv2.imwrite(filename, gray)
                saved_count += 1
                print(f"Saved: {filename} ({saved_count} images)")
                time.sleep(0.2)
            else:
                print("Not enough markers detected")
        
        elif key == ord('q') or key == ord('Q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"Captured {saved_count} FaceCam images")

if __name__ == "__main__":
    capture_facecam_simple()

