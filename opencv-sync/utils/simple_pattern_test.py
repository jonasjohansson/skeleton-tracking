#!/usr/bin/env python3
"""
Simple pattern detection test that works with all OpenCV versions.
"""

import cv2
import numpy as np
from board_def import DICT, BOARD

def test_camera_pattern(camera_index):
    """Test pattern detection on live camera feed."""
    print(f"Testing pattern detection on camera {camera_index}")
    
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Failed to open camera {camera_index}")
        return False
    
    # Create ArUco detector
    det = cv2.aruco.ArucoDetector(DICT, cv2.aruco.DetectorParameters())
    
    print("Position your ChArUco pattern in front of the camera")
    print("Press 's' to save test image, 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect markers
        corners, ids, _ = det.detectMarkers(gray)
        
        # Create visualization
        vis = frame.copy()
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(vis, corners, ids)
        
        # Add status text
        marker_count = len(ids) if ids is not None else 0
        cv2.putText(vis, f"Markers: {marker_count}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        if ids is not None and len(ids) >= 4:
            cv2.putText(vis, "GOOD - Enough markers detected!", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(vis, "NEED MORE MARKERS", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        cv2.imshow("Pattern Detection Test", vis)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = f"test_pattern_{camera_index}.png"
            cv2.imwrite(filename, gray)
            print(f"Saved test image: {filename}")
            
            # Test the saved image
            test_saved_image(filename)
    
    cap.release()
    cv2.destroyAllWindows()

def test_saved_image(image_path):
    """Test pattern detection on a saved image."""
    print(f"Testing pattern detection on: {image_path}")
    
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to read image: {image_path}")
        return False
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Create ArUco detector
    det = cv2.aruco.ArucoDetector(DICT, cv2.aruco.DetectorParameters())
    
    # Detect markers
    corners, ids, _ = det.detectMarkers(gray)
    
    print(f"Image size: {gray.shape}")
    print(f"Markers detected: {len(ids) if ids is not None else 0}")
    
    if ids is not None:
        print(f"Marker IDs: {ids.flatten()}")
        print(f"Number of markers: {len(ids)}")
        
        # Check if enough markers for calibration
        if len(ids) >= 4:
            print("✓ SUCCESS: Enough markers detected for calibration!")
            return True
        else:
            print("✗ FAILED: Not enough markers detected")
            return False
    else:
        print("✗ FAILED: No markers detected")
        return False

def main():
    """Main function."""
    print("Simple ChArUco Pattern Test")
    print("=" * 30)
    print()
    print("This tests if your ChArUco pattern is detected correctly.")
    print()
    print("Choose test method:")
    print("1. Test live camera feed")
    print("2. Test saved image")
    print()
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        camera_index = int(input("Enter camera index (0 for FaceCam, 2 for ZED2i): "))
        test_camera_pattern(camera_index)
    
    elif choice == "2":
        image_path = input("Enter path to test image: ").strip()
        test_saved_image(image_path)
    
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()




