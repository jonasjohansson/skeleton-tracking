#!/usr/bin/env python3
"""
Capture FaceCam at its native resolution (960x540).
"""

import cv2
import numpy as np
import time
import os
from board_def import DICT

def capture_facecam_native():
    """Capture FaceCam at native resolution."""
    print("FaceCam Native Resolution Capture")
    print("=" * 35)
    
    # Create ArUco detector
    det = cv2.aruco.ArucoDetector(DICT, cv2.aruco.DetectorParameters())
    
    # Open FaceCam
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print("Failed to open FaceCam (Camera 1)")
        return
    
    # Don't try to set resolution - use native
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
    
    # Get actual resolution
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"FaceCam native resolution: {width}x{height} @ {fps:.1f}fps")
    
    print("\nInstructions:")
    print("- Position the iPad with ChArUco pattern in front of the FaceCam")
    print("- Move the iPad to different positions and angles")
    print("- Press 'S' to save frame when pattern is clearly visible")
    print("- Capture 20-30 images")
    print("- Press 'Q' to quit")
    print()
    
    # Prepare scans directory
    scans_dir = "scans"
    os.makedirs(scans_dir, exist_ok=True)
    
    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read from FaceCam")
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
        cv2.putText(vis, f"FaceCam Native - {width}x{height}", (10, 30), 
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
        
        cv2.imshow("FaceCam Native Capture", vis)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s') or key == ord('S'):
            if ids is not None and len(ids) >= 4:
                filename = os.path.join(scans_dir, f"cal_facecam_native_{saved_count:03d}.png")
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
    print(f"Captured {saved_count} FaceCam images at native resolution")

if __name__ == "__main__":
    capture_facecam_native()

