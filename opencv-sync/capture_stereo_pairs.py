#!/usr/bin/env python3
"""
Capture synchronized stereo pairs from FaceCam and ZED (via OBS).
"""

import cv2
import numpy as np
import time
import os
from board_def import DICT

def capture_stereo_pairs():
    """Capture synchronized stereo pairs."""
    print("Stereo Pair Capture")
    print("=" * 25)
    print("Capturing synchronized pairs from both cameras")
    print()
    
    # Create ArUco detector
    det = cv2.aruco.ArucoDetector(DICT, cv2.aruco.DetectorParameters())
    
    # Open both cameras
    cap_facecam = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # FaceCam
    cap_zed = cv2.VideoCapture(3, cv2.CAP_DSHOW)      # ZED via OBS
    
    if not cap_facecam.isOpened():
        print("Failed to open FaceCam (Camera 1)")
        return
    
    if not cap_zed.isOpened():
        print("Failed to open ZED camera (Camera 3)")
        cap_facecam.release()
        return
    
    # Set ZED to higher resolution
    cap_zed.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap_zed.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    # Get camera properties
    w_f, h_f = int(cap_facecam.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap_facecam.get(cv2.CAP_PROP_FRAME_HEIGHT))
    w_z, h_z = int(cap_zed.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap_zed.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"FaceCam: {w_f}x{h_f}")
    print(f"ZED: {w_z}x{h_z}")
    
    # Prepare scans directory
    scans_dir = "scans"
    os.makedirs(scans_dir, exist_ok=True)
    
    saved_count = 0
    
    print("\nInstructions:")
    print("- Position ChArUco pattern so BOTH cameras can see it")
    print("- Move pattern to different positions and angles")
    print("- Press 'S' to save synchronized pair")
    print("- Capture 15-25 pairs")
    print("- Press 'Q' to quit")
    print()
    
    while True:
        # Read from both cameras
        ret_f, frame_f = cap_facecam.read()
        ret_z, frame_z = cap_zed.read()
        
        if not ret_f or not ret_z:
            print("Failed to read from cameras")
            break
        
        # Convert to grayscale
        gray_f = cv2.cvtColor(frame_f, cv2.COLOR_BGR2GRAY)
        gray_z = cv2.cvtColor(frame_z, cv2.COLOR_BGR2GRAY)
        
        # Detect markers in both
        corners_f, ids_f, _ = det.detectMarkers(gray_f)
        corners_z, ids_z, _ = det.detectMarkers(gray_z)
        
        # Create visualization
        vis_f = frame_f.copy()
        vis_z = frame_z.copy()
        
        if ids_f is not None:
            cv2.aruco.drawDetectedMarkers(vis_f, corners_f, ids_f)
        if ids_z is not None:
            cv2.aruco.drawDetectedMarkers(vis_z, corners_z, ids_z)
        
        # Add status text
        markers_f = len(ids_f) if ids_f is not None else 0
        markers_z = len(ids_z) if ids_z is not None else 0
        
        cv2.putText(vis_f, f"FaceCam - Markers: {markers_f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(vis_z, f"ZED - Markers: {markers_z}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.putText(vis_f, f"Saved: {saved_count}", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(vis_z, f"Saved: {saved_count}", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Check if both have enough markers
        if markers_f >= 4 and markers_z >= 4:
            cv2.putText(vis_f, "GOOD - Press 'S' to save!", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(vis_z, "GOOD - Press 'S' to save!", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(vis_f, "Need more markers", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.putText(vis_z, "Need more markers", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        cv2.putText(vis_f, "Press 'S' to save, 'Q' to quit", (10, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(vis_z, "Press 'S' to save, 'Q' to quit", (10, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Display both windows
        cv2.imshow("FaceCam", vis_f)
        cv2.imshow("ZED Camera", vis_z)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s') or key == ord('S'):
            if markers_f >= 4 and markers_z >= 4:
                # Save both images
                filename_f = os.path.join(scans_dir, f"pair0_{saved_count:03d}.png")
                filename_z = os.path.join(scans_dir, f"pair1_{saved_count:03d}.png")
                
                cv2.imwrite(filename_f, gray_f)
                cv2.imwrite(filename_z, gray_z)
                
                saved_count += 1
                print(f"Saved pair {saved_count}: {filename_f}, {filename_z}")
                time.sleep(0.2)
            else:
                print("Not enough markers in both cameras")
        
        elif key == ord('q') or key == ord('Q'):
            break
    
    cap_facecam.release()
    cap_zed.release()
    cv2.destroyAllWindows()
    print(f"Captured {saved_count} stereo pairs")

if __name__ == "__main__":
    capture_stereo_pairs()

