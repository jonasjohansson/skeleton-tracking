#!/usr/bin/env python3
"""
Simple ZED camera capture with error handling.
"""

import cv2
import numpy as np
import time
import os
from board_def import DICT

def capture_zed_simple():
    """Simple ZED camera capture."""
    print("ZED Camera Simple Capture")
    print("=" * 30)
    
    # Create ArUco detector
    det = cv2.aruco.ArucoDetector(DICT, cv2.aruco.DetectorParameters())
    
    # Try Camera 0 with Media Foundation
    cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
    
    if not cap.isOpened():
        print("Failed to open ZED camera")
        return
    
    # Get camera properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"ZED camera: {width}x{height} @ {fps:.1f}fps")
    
    # Prepare scans directory
    scans_dir = "scans"
    os.makedirs(scans_dir, exist_ok=True)
    
    saved_count = 0
    frame_count = 0
    
    print("\nInstructions:")
    print("- Position ChArUco pattern in front of ZED camera")
    print("- Press 'S' to save, 'Q' to quit")
    print()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read from camera")
            frame_count += 1
            if frame_count > 10:  # Give up after 10 failed attempts
                break
            time.sleep(0.1)
            continue
        
        # Crop to left half (stereo view)
        h, w = frame.shape[:2]
        left_half = frame[:, :w//2]
        
        # Convert to grayscale
        gray = cv2.cvtColor(left_half, cv2.COLOR_BGR2GRAY)
        
        # Detect markers
        corners, ids, _ = det.detectMarkers(gray)
        
        # Create visualization
        vis = left_half.copy()
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(vis, corners, ids)
        
        # Add status
        marker_count = len(ids) if ids is not None else 0
        cv2.putText(vis, f"ZED (Left Eye) - {w//2}x{h}", (10, 30), 
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
        
        cv2.imshow("ZED Camera Capture", vis)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s') or key == ord('S'):
            if ids is not None and len(ids) >= 4:
                filename = os.path.join(scans_dir, f"cal_zed_{saved_count:03d}.png")
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
    print(f"Captured {saved_count} images")

if __name__ == "__main__":
    capture_zed_simple()

