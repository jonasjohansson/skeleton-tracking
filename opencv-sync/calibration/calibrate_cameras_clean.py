#!/usr/bin/env python3
"""
Clean camera calibration for FaceCam (camera 0) and ZED (camera 2).
Uses images from scans folder and creates proper calibration files.
"""

import glob
import cv2
import numpy as np
import os
from board_def import BOARD, DICT

def calibrate_camera(prefix, camera_id):
    """
    Calibrate a single camera from captured images.
    
    Args:
        prefix: Camera prefix (e.g., "facecam", "zed")
        camera_id: Camera ID (0 for FaceCam, 2 for ZED)
    """
    # Find all calibration images for this camera in scans folder
    image_files = sorted(glob.glob(f"scans/cal_{prefix}_*.png"))
    
    if len(image_files) == 0:
        print(f"No calibration images found for {prefix} in scans folder")
        return False, None, None, float('inf')
    
    print(f"Processing {len(image_files)} images for {prefix} (Camera {camera_id})...")
    
    # Create ArUco detector and Charuco detector
    det = cv2.aruco.ArucoDetector(DICT, cv2.aruco.DetectorParameters())
    charuco_detector = cv2.aruco.CharucoDetector(BOARD)
    
    # Termination criteria for corner refinement
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    
    # Arrays to store object points and image points from all the images
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane
    image_size = None
    
    valid_images = 0
    
    for img_path in image_files:
        # Read grayscale image
        gray = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if gray is None:
            print(f"Failed to read {img_path}")
            continue
        
        if image_size is None:
            image_size = gray.shape[::-1]  # (width, height)
        
        # Detect ChArUco board
        charuco_corners, charuco_ids, marker_corners, marker_ids = charuco_detector.detectBoard(gray)
        
        if charuco_corners is not None and len(charuco_corners) >= 8:
            # Get the board's 3D points (it's a tuple of arrays)
            board_points = BOARD.getObjPoints()
            
            # Create corresponding 3D and 2D points
            obj_pts = []
            img_pts = []
            
            for i, corner_id in enumerate(charuco_ids.ravel()):
                if corner_id < len(board_points):
                    # board_points[corner_id] is an array of 4 corners for that marker
                    # We need to find which corner of the marker corresponds to the detected corner
                    marker_corners_for_id = board_points[corner_id]
                    # For simplicity, use the first corner of each marker
                    obj_pts.append(marker_corners_for_id[0])
                    img_pts.append(charuco_corners[i])
            
            if len(obj_pts) >= 8:
                # Convert to numpy arrays with correct format
                obj_pts_array = np.array(obj_pts, dtype=np.float32)
                img_pts_array = np.array(img_pts, dtype=np.float32)
                
                # Refine corner positions
                refined_corners = cv2.cornerSubPix(gray, img_pts_array, (11,11), (-1,-1), criteria)
                
                # Add to calibration data - ensure correct format
                objpoints.append(obj_pts_array)
                imgpoints.append(refined_corners)
                
                valid_images += 1
                print(f"  {os.path.basename(img_path)}: {len(charuco_corners)} corners detected")
            else:
                print(f"  {os.path.basename(img_path)}: Not enough valid correspondences")
        else:
            print(f"  {os.path.basename(img_path)}: Not enough corners ({len(charuco_corners) if charuco_corners is not None else 0})")
    
    if len(objpoints) < 5:
        print(f"Not enough valid images for {prefix}. Found {len(objpoints)} valid images.")
        return False, None, None, float('inf')
    
    print(f"Calibrating {prefix} (Camera {camera_id}) with {len(objpoints)} valid images...")
    
    # Perform camera calibration using standard OpenCV approach
    try:
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            objpoints, imgpoints, image_size, None, None
        )
        
        if ret and mtx is not None and dist is not None:
            # Save calibration parameters with camera ID
            np.save(f"K_{prefix}.npy", mtx)
            np.save(f"dist_{prefix}.npy", dist)
            
            print(f"\n{prefix} (Camera {camera_id}) calibration successful!")
            print(f"RMS reprojection error: {ret:.4f} pixels")
            print(f"Camera matrix (K):")
            print(mtx)
            print(f"Distortion coefficients:")
            print(dist.ravel())
            print(f"Saved K_{prefix}.npy and dist_{prefix}.npy")
            
            return True, mtx, dist, ret
        else:
            print(f"{prefix} calibration failed!")
            return False, None, None, float('inf')
            
    except Exception as e:
        print(f"Calibration failed with error: {e}")
        return False, None, None, float('inf')

def main():
    """Main function to calibrate both cameras."""
    print("Clean Camera Calibration")
    print("=" * 25)
    print("FaceCam: Camera 0")
    print("ZED: Camera 2")
    print()
    
    # Calibrate FaceCam (Camera 0)
    print("="*50)
    print("Calibrating FaceCam (Camera 0)...")
    facecam_success, K_facecam, dist_facecam, error_facecam = calibrate_camera("facecam", 0)
    
    # Calibrate ZED (Camera 2)
    print("\n" + "="*50)
    print("Calibrating ZED (Camera 2)...")
    zed_success, K_zed, dist_zed, error_zed = calibrate_camera("zed", 2)
    
    # Summary
    print(f"\n{'='*50}")
    print("CALIBRATION SUMMARY")
    print("=" * 50)
    
    if facecam_success:
        print(f"OK FaceCam (Camera 0): RMS error = {error_facecam:.4f} pixels")
    else:
        print(f"FAILED FaceCam (Camera 0): Calibration failed")
    
    if zed_success:
        print(f"OK ZED (Camera 2): RMS error = {error_zed:.4f} pixels")
    else:
        print(f"FAILED ZED (Camera 2): Calibration failed")
    
    if facecam_success and zed_success:
        print(f"\nBoth cameras calibrated successfully!")
        print("Ready for stereo calibration and rectification.")
    elif facecam_success or zed_success:
        successful_cameras = []
        if facecam_success:
            successful_cameras.append("FaceCam (Camera 0)")
        if zed_success:
            successful_cameras.append("ZED (Camera 2)")
        print(f"\nOnly {', '.join(successful_cameras)} calibrated successfully.")
    else:
        print("\nNo cameras calibrated successfully.")

if __name__ == "__main__":
    main()
