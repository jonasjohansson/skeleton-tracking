#!/usr/bin/env python3
"""
Diagnostic tool to check if your ChArUco pattern is working correctly.
"""

import cv2
import numpy as np
from board_def import DICT, BOARD

def test_pattern_detection(image_path):
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
        
        # Interpolate ChArUco corners
        try:
            ret, charuco_corners, charuco_ids = cv2.aruco.interpolateCornersCharuco(
                corners, ids, gray, BOARD
            )
        except AttributeError:
            # Fallback for newer OpenCV versions
            ret, charuco_corners, charuco_ids = cv2.aruco.interpolateCornersCharuco(
                corners, ids, gray, BOARD
            )
        
        print(f"ChArUco corners: {ret}")
        if charuco_ids is not None:
            print(f"ChArUco corner IDs: {charuco_ids.flatten()}")
    
    # Create visualization
    vis = image.copy()
    if ids is not None:
        cv2.aruco.drawDetectedMarkers(vis, corners, ids)
        if charuco_corners is not None:
            cv2.aruco.drawDetectedCornersCharuco(vis, charuco_corners, charuco_ids)
    
    # Show result
    cv2.imshow("Pattern Detection Test", vis)
    print("Press any key to continue...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return ids is not None and len(ids) >= 4

def test_live_camera(camera_index):
    """Test pattern detection on live camera feed."""
    print(f"Testing live camera {camera_index}")
    
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
            
            # Interpolate ChArUco corners
            ret, charuco_corners, charuco_ids = cv2.aruco.interpolateCornersCharuco(
                corners, ids, gray, BOARD
            )
            
            if charuco_corners is not None:
                cv2.aruco.drawDetectedCornersCharuco(vis, charuco_corners, charuco_ids)
        
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
            test_pattern_detection(filename)
    
    cap.release()
    cv2.destroyAllWindows()

def main():
    """Main diagnostic function."""
    print("ChArUco Pattern Diagnostic Tool")
    print("=" * 35)
    print()
    print("This tool helps diagnose pattern detection issues.")
    print()
    print("Choose diagnostic method:")
    print("1. Test live camera feed")
    print("2. Test saved image")
    print("3. Generate new pattern")
    print()
    
    choice = input("Enter choice (1, 2, or 3): ").strip()
    
    if choice == "1":
        camera_index = int(input("Enter camera index (0 for FaceCam, 2 for ZED2i): "))
        test_live_camera(camera_index)
    
    elif choice == "2":
        image_path = input("Enter path to test image: ").strip()
        test_pattern_detection(image_path)
    
    elif choice == "3":
        print("Generating new ChArUco pattern...")
        from board_def import generate_printable_board
        generate_printable_board()
        print("New pattern generated: charuco_A4.png")
        print("Print this new pattern and try again.")
    
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
