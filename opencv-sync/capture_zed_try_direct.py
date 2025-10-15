#!/usr/bin/env python3
"""
Try to capture ZED camera directly with different backends and settings.
"""

import cv2
import numpy as np
import time
import os
from board_def import DICT

def capture_zed_try_direct():
    """Try to capture ZED camera directly with different approaches."""
    print("ZED Camera Direct Capture (Multiple Attempts)")
    print("=" * 45)
    print("Trying different approaches to access ZED camera...")
    print()
    
    # Create ArUco detector
    det = cv2.aruco.ArucoDetector(DICT, cv2.aruco.DetectorParameters())
    
    # Try different camera indices and backends
    attempts = [
        (2, cv2.CAP_MSMF, "Camera 2 - Media Foundation"),
        (2, cv2.CAP_DSHOW, "Camera 2 - DirectShow"),
        (2, cv2.CAP_ANY, "Camera 2 - Any Backend"),
        (0, cv2.CAP_MSMF, "Camera 0 - Media Foundation"),
        (0, cv2.CAP_DSHOW, "Camera 0 - DirectShow"),
        (1, cv2.CAP_MSMF, "Camera 1 - Media Foundation"),
    ]
    
    cap = None
    camera_info = None
    
    for camera_index, backend, description in attempts:
        print(f"Trying {description}...")
        cap = cv2.VideoCapture(camera_index, backend)
        
        if cap.isOpened():
            # Try to read a frame
            ret, frame = cap.read()
            if ret and frame is not None:
                h, w = frame.shape[:2]
                fps = cap.get(cv2.CAP_PROP_FPS)
                print(f"SUCCESS: {description} - {w}x{h} @ {fps:.1f}fps")
                camera_info = (camera_index, backend, description, w, h, fps)
                break
            else:
                print(f"Opened but can't read frames")
                cap.release()
        else:
            print(f"Failed to open")
            if cap:
                cap.release()
    
    if not camera_info:
        print("\nCould not access ZED camera with any method")
        print("Make sure:")
        print("- No other applications are using the ZED camera")
        print("- ZED SDK is properly installed")
        print("- Camera permissions are granted")
        return
    
    camera_index, backend, description, width, height, fps = camera_info
    print(f"\nUsing: {description}")
    print(f"Resolution: {width}x{height} @ {fps:.1f}fps")
    
    # Try to set higher resolution if possible
    print("Attempting to set higher resolution...")
    
    # Try different resolution settings
    resolutions = [
        (1920, 1080),  # Full HD
        (1280, 720),   # HD
        (1024, 768),   # XGA
        (800, 600),    # SVGA
    ]
    
    actual_width, actual_height = width, height
    best_resolution = (actual_width, actual_height)
    
    for target_w, target_h in resolutions:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, target_w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, target_h)
        
        # Test if the resolution actually changed
        test_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        test_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        if test_w > actual_width and test_h > actual_height:
            print(f"  Successfully set to {test_w}x{test_h}")
            best_resolution = (test_w, test_h)
            actual_width, actual_height = test_w, test_h
        else:
            print(f"  Could not set to {target_w}x{target_h}")
    
    # Get final resolution
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"Final resolution: {actual_width}x{actual_height} @ {actual_fps:.1f}fps")
    
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
        
        # Crop to left half of stereo feed (assuming split view)
        h, w = frame.shape[:2]
        left_half = frame[:, :w//2]  # Take left half of the frame
        
        # Convert to grayscale
        gray = cv2.cvtColor(left_half, cv2.COLOR_BGR2GRAY)
        
        # Detect ArUco markers
        corners, ids, _ = det.detectMarkers(gray)
        
        # Create visualization (show cropped view)
        vis = left_half.copy()
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(vis, corners, ids)
        
        # Add status text
        marker_count = len(ids) if ids is not None else 0
        cv2.putText(vis, f"ZED Camera (Left Eye) - {actual_width//2}x{actual_height}", (10, 30), 
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
    capture_zed_try_direct()
