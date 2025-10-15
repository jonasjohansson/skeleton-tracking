#!/usr/bin/env python3
"""
Capture calibration images specifically for Elgato FaceCam (Camera 0).
"""

import cv2
import time
import os
import argparse

# Ensure we can import board_def when running from the calibration folder
try:
    from board_def import DICT
except ImportError:
    import sys
    ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
    if ROOT_DIR not in sys.path:
        sys.path.append(ROOT_DIR)
    from board_def import DICT

def capture_facecam(camera_index: int = 0):
    """Capture calibration images for Elgato FaceCam."""
    print("Elgato FaceCam Calibration Capture")
    print("=" * 40)
    print(f"Camera: Elgato FaceCam (Camera {camera_index})")
    print("Resolution: 960x540 @ 60fps")
    print()
    
    # Create ArUco detector
    det = cv2.aruco.ArucoDetector(DICT, cv2.aruco.DetectorParameters())
    
    # Open FaceCam with backend fallback (prefer DirectShow on Windows)
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap.release()
        cap = cv2.VideoCapture(camera_index, cv2.CAP_MSMF)
    
    if not cap.isOpened():
        print(f"Failed to open Elgato FaceCam (Camera {camera_index})")
        return
    
    # Set camera properties for higher resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Try to set higher resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    # Get actual resolution
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Camera resolution: {actual_width}x{actual_height}")
    
    if actual_width < 1280:
        print("WARNING: Low resolution may affect pattern detection")
        print("Try moving the iPad closer to the camera")
    
    print("Instructions:")
    print("- Position the ChArUco pattern in front of the Elgato FaceCam")
    print("- Move the pattern to different positions and angles")
    print("- Press 'S' to save frame when pattern is clearly visible")
    print("- Capture 20-30 images")
    print("- Press 'Q' to quit")
    print()
    
    # Prepare scans output directory at repo root
    root_dir = os.path.dirname(os.path.dirname(__file__))
    scans_dir = os.path.join(root_dir, "scans")
    os.makedirs(scans_dir, exist_ok=True)

    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read from Elgato FaceCam")
            break
        
        # Convert to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect ArUco markers
        corners, ids, _ = det.detectMarkers(gray)
        
        # Create visualization
        vis = frame.copy()
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(vis, corners, ids)
        
        # Add status text
        cv2.putText(vis, f"Elgato FaceCam (Camera 0) - Saved: {saved_count}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(vis, "Press 'S' to save, 'Q' to quit", 
                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.imshow("Elgato FaceCam Calibration", vis)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s') or key == ord('S'):
            if ids is not None and len(ids) >= 4:  # Require at least 4 markers
                filename = os.path.join(scans_dir, f"cal_facecam_{saved_count:03d}.png")
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
    print(f"Captured {saved_count} images for Elgato FaceCam")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capture calibration images for Elgato FaceCam")
    parser.add_argument("--camera", type=int, default=0, help="Camera index for FaceCam (default: 0)")
    args = parser.parse_args()
    capture_facecam(camera_index=args.camera)
