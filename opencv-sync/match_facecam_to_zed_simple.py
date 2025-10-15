#!/usr/bin/env python3
"""
Simple perspective transform to match FaceCam to ZED camera.
This creates a more natural-looking transformation without heavy distortion.
"""

import cv2
import numpy as np
import glob
import os
from board_def import BOARD, DICT

def find_correspondences():
    """Find corresponding points between FaceCam and ZED images."""
    print("Finding correspondences between FaceCam and ZED...")
    
    # Find stereo pairs
    pair_files = sorted(glob.glob("scans/pair0_*.png"))
    
    if len(pair_files) == 0:
        print("No stereo pairs found!")
        return None, None
    
    print(f"Found {len(pair_files)} stereo pairs")
    
    # Create ArUco detector and Charuco detector
    det = cv2.aruco.ArucoDetector(DICT, cv2.aruco.DetectorParameters())
    charuco_detector = cv2.aruco.CharucoDetector(BOARD)
    
    facecam_points = []
    zed_points = []
    valid_pairs = 0
    
    for pair_file in pair_files:
        # Extract pair number
        basename = os.path.basename(pair_file)
        pair_num = basename.replace("pair0_", "").replace(".png", "")
        pair_file_zed = f"scans/pair1_{pair_num}.png"
        
        if not os.path.exists(pair_file_zed):
            continue
        
        # Read both images
        img_facecam = cv2.imread(pair_file, cv2.IMREAD_GRAYSCALE)
        img_zed = cv2.imread(pair_file_zed, cv2.IMREAD_GRAYSCALE)
        
        if img_facecam is None or img_zed is None:
            continue
        
        # Detect ChArUco board in both images
        charuco_corners_facecam, charuco_ids_facecam, _, _ = charuco_detector.detectBoard(img_facecam)
        charuco_corners_zed, charuco_ids_zed, _, _ = charuco_detector.detectBoard(img_zed)
        
        if (charuco_corners_facecam is None or charuco_corners_zed is None or
            len(charuco_corners_facecam) < 8 or len(charuco_corners_zed) < 8):
            continue
        
        # Find common markers
        charuco_ids_facecam_flat = charuco_ids_facecam.flatten()
        charuco_ids_zed_flat = charuco_ids_zed.flatten()
        common_ids = np.intersect1d(charuco_ids_facecam_flat, charuco_ids_zed_flat)
        
        if len(common_ids) < 8:
            continue
        
        # Create corresponding points
        facecam_pts = []
        zed_pts = []
        
        for common_id in common_ids:
            # Find indices in both images
            idx_facecam = np.where(charuco_ids_facecam_flat == common_id)[0]
            idx_zed = np.where(charuco_ids_zed_flat == common_id)[0]
            
            if len(idx_facecam) > 0 and len(idx_zed) > 0:
                facecam_pts.append(charuco_corners_facecam[idx_facecam[0]])
                zed_pts.append(charuco_corners_zed[idx_zed[0]])
        
        if len(facecam_pts) >= 8:
            facecam_points.extend(facecam_pts)
            zed_points.extend(zed_pts)
            valid_pairs += 1
            print(f"Pair {pair_num}: {len(facecam_pts)} common points")
    
    if valid_pairs < 3:
        print(f"Not enough valid pairs ({valid_pairs}). Need at least 3.")
        return None, None
    
    print(f"Found {len(facecam_points)} corresponding points from {valid_pairs} pairs")
    return np.array(facecam_points, dtype=np.float32), np.array(zed_points, dtype=np.float32)

def compute_perspective_transform():
    """Compute a perspective transform from FaceCam to ZED."""
    print("Computing perspective transform...")
    
    # Find correspondences
    facecam_points, zed_points = find_correspondences()
    
    if facecam_points is None:
        print("Failed to find correspondences!")
        return None
    
    # Compute perspective transform
    try:
        # Use RANSAC for robust estimation
        transform_matrix, mask = cv2.findHomography(
            facecam_points, zed_points, 
            cv2.RANSAC, 
            ransacReprojThreshold=5.0
        )
        
        if transform_matrix is not None:
            print("Perspective transform computed successfully!")
            print(f"Transform matrix shape: {transform_matrix.shape}")
            
            # Save transform
            np.save("data/facecam_to_zed_transform.npy", transform_matrix)
            print("Transform saved to data/facecam_to_zed_transform.npy")
            
            return transform_matrix
        else:
            print("Failed to compute perspective transform!")
            return None
            
    except Exception as e:
        print(f"Transform computation failed: {e}")
        return None

def test_transform():
    """Test the perspective transform with live cameras."""
    print("\nTesting perspective transform with live cameras...")
    
    # Load transform
    try:
        transform_matrix = np.load("data/facecam_to_zed_transform.npy")
    except FileNotFoundError:
        print("Transform not found! Run compute_perspective_transform() first.")
        return
    
    # Open cameras
    cap_facecam = cv2.VideoCapture(0)  # FaceCam
    cap_zed = cv2.VideoCapture(3)      # ZED via OBS
    
    if not cap_facecam.isOpened() or not cap_zed.isOpened():
        print("Failed to open cameras")
        return
    
    # Set camera properties
    cap_facecam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap_facecam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap_zed.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap_zed.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    print("Showing perspective transform...")
    print("Press 'Q' to quit")
    print("Press 'S' to save transformed frames")
    
    saved_count = 0
    
    while True:
        ret_facecam, frame_facecam = cap_facecam.read()
        ret_zed, frame_zed = cap_zed.read()
        
        if not ret_facecam or not ret_zed:
            print("Failed to read from cameras")
            break
        
        # Apply perspective transform to FaceCam
        transformed_facecam = cv2.warpPerspective(
            frame_facecam, transform_matrix, (1920, 1080)
        )
        
        # Add labels
        cv2.putText(transformed_facecam, "FaceCam -> ZED Transform", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame_zed, "Original ZED (Reference)", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Show both images side by side
        combined = np.hstack((transformed_facecam, frame_zed))
        cv2.imshow("FaceCam to ZED Perspective Transform", combined)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('s') or key == ord('S'):
            # Save transformed FaceCam and original ZED
            cv2.imwrite(f"scans/transformed_facecam_{saved_count:03d}.png", transformed_facecam)
            cv2.imwrite(f"scans/original_zed_{saved_count:03d}.png", frame_zed)
            saved_count += 1
            print(f"Saved transformed FaceCam and original ZED: {saved_count}")
    
    cap_facecam.release()
    cap_zed.release()
    cv2.destroyAllWindows()

def main():
    """Main function."""
    print("FaceCam to ZED Perspective Transform")
    print("=" * 35)
    
    # Create data directory
    os.makedirs("data", exist_ok=True)
    
    # Compute perspective transform
    transform_matrix = compute_perspective_transform()
    
    if transform_matrix is not None:
        print("\nPerspective transform computed successfully!")
        print("FaceCam will be transformed to match ZED camera perspective.")
        test_transform()
    else:
        print("\nPerspective transform failed!")
        print("Check your stereo pair images and try again.")

if __name__ == "__main__":
    main()

