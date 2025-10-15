#!/usr/bin/env python3
"""
Simple camera calibration using ChArUco boards.
"""

import cv2
import numpy as np
import glob
import os
from board_def import BOARD, DICT

def calibrate_camera_simple(camera_name, image_pattern):
    """Calibrate a single camera using a simpler approach."""
    print(f"\nCalibrating {camera_name}...")
    
    # Find calibration images
    image_files = sorted(glob.glob(image_pattern))
    
    if len(image_files) == 0:
        print(f"No {camera_name} images found!")
        return None, None
    
    print(f"Found {len(image_files)} {camera_name} images")
    
    # Create ArUco detector and Charuco detector
    det = cv2.aruco.ArucoDetector(DICT, cv2.aruco.DetectorParameters())
    charuco_detector = cv2.aruco.CharucoDetector(BOARD)
    
    # Prepare calibration data
    all_obj_points = []
    all_img_points = []
    valid_images = 0
    
    for image_file in image_files:
        # Read image
        img = cv2.imread(image_file, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        
        # Detect ChArUco board
        charuco_corners, charuco_ids, marker_corners, marker_ids = charuco_detector.detectBoard(img)
        
        if charuco_corners is not None and len(charuco_corners) > 8:
            # Get board points
            board_points = BOARD.getObjPoints()
            
            # Create object and image points for this image
            obj_pts = []
            img_pts = []
            
            for i, corner_id in enumerate(charuco_ids.flatten()):
                if corner_id < len(board_points):
                    # board_points[corner_id] is 4x3 (4 corners per marker)
                    # We need to use the first corner of each marker
                    obj_pts.append(board_points[corner_id][0])  # First corner
                    img_pts.append(charuco_corners[i])
            
            if len(obj_pts) >= 8:
                # Format for OpenCV calibration: each image needs to be a list of points
                all_obj_points.append(np.array(obj_pts, dtype=np.float32))
                all_img_points.append(np.array(img_pts, dtype=np.float32))
                valid_images += 1
                print(f"  {os.path.basename(image_file)}: {len(obj_pts)} points")
            else:
                print(f"  {os.path.basename(image_file)}: Not enough points ({len(obj_pts)})")
        else:
            print(f"  {os.path.basename(image_file)}: Not enough corners detected")
    
    if valid_images < 10:
        print(f"Not enough valid {camera_name} images ({valid_images}). Need at least 10.")
        return None, None
    
    print(f"Calibrating {camera_name} with {valid_images} valid images...")
    
    # Get image size
    img = cv2.imread(image_files[0], cv2.IMREAD_GRAYSCALE)
    image_size = (img.shape[1], img.shape[0])
    
    # Calibrate camera
    try:
        ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(
            all_obj_points, all_img_points, image_size, None, None
        )
        
        if ret:
            print(f"{camera_name} calibration successful! RMS error: {ret:.4f} pixels")
            return K, dist
        else:
            print(f"{camera_name} calibration failed!")
            return None, None
            
    except Exception as e:
        print(f"{camera_name} calibration failed with error: {e}")
        return None, None

def main():
    """Main calibration function."""
    print("Simple Camera Calibration")
    print("=" * 25)
    
    # Create data directory
    os.makedirs("data", exist_ok=True)
    
    # Calibrate FaceCam
    K_facecam, dist_facecam = calibrate_camera_simple("FaceCam", "scans/cal_facecam_*.png")
    
    # Calibrate ZED
    K_zed, dist_zed = calibrate_camera_simple("ZED", "scans/cal_zed_*.png")
    
    # Save calibration data
    if K_facecam is not None and dist_facecam is not None:
        np.save("data/K_facecam.npy", K_facecam)
        np.save("data/dist_facecam.npy", dist_facecam)
        print(f"\nFaceCam calibration saved:")
        print(f"  Camera matrix: {K_facecam.shape}")
        print(f"  Distortion coefficients: {dist_facecam.shape}")
    
    if K_zed is not None and dist_zed is not None:
        np.save("data/K_zed.npy", K_zed)
        np.save("data/dist_zed.npy", dist_zed)
        print(f"\nZED calibration saved:")
        print(f"  Camera matrix: {K_zed.shape}")
        print(f"  Distortion coefficients: {dist_zed.shape}")
    
    if K_facecam is not None and K_zed is not None:
        print("\nBoth cameras calibrated successfully!")
        print("Ready for stereo calibration and rectification.")
    else:
        print("\nCalibration incomplete. Check your captured images.")

if __name__ == "__main__":
    main()
