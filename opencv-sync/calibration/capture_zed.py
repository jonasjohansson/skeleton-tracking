#!/usr/bin/env python3
"""
Capture calibration images specifically for ZED2i (Camera 2).
"""

import cv2
import time
from board_def import DICT

def capture_zed():
    """Capture calibration images for ZED2i."""
    print("ZED2i Calibration Capture")
    print("=" * 30)
    print("Camera: ZED2i (Camera 2)")
    print("Resolution: 1344x376 @ 30fps")
    print()
    
    # Create ArUco detector
    det = cv2.aruco.ArucoDetector(DICT, cv2.aruco.DetectorParameters())
    
    # Open ZED2i (Camera 2)
    cap = cv2.VideoCapture(2)
    
    if not cap.isOpened():
        print("Failed to open ZED2i (Camera 2)")
        return
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print("Instructions:")
    print("- Position the ChArUco pattern in front of the ZED2i camera")
    print("- Move the pattern to different positions and angles")
    print("- Press 'S' to save frame when pattern is clearly visible")
    print("- Capture 20-30 images")
    print("- Press 'Q' to quit")
    print()
    
    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read from ZED2i")
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
        cv2.putText(vis, f"ZED2i (Camera 2) - Saved: {saved_count}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(vis, "Press 'S' to save, 'Q' to quit", 
                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.imshow("ZED2i Calibration", vis)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s') or key == ord('S'):
            if ids is not None and len(ids) >= 4:  # Require at least 4 markers
                filename = f"cal_zed_{saved_count:03d}.png"
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
    print(f"Captured {saved_count} images for ZED2i")

if __name__ == "__main__":
    capture_zed()




