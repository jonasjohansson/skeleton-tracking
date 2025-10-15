#!/usr/bin/env python3
"""
Debug stereo pairs to see what's happening with correspondences.
"""

import cv2
import numpy as np
import glob
import os
from board_def import DICT, BOARD

def debug_stereo_pairs():
    """Debug stereo pairs to understand correspondence issues."""
    print("Debug Stereo Pairs")
    print("=" * 20)
    
    # Create ArUco detector
    det = cv2.aruco.ArucoDetector(DICT, cv2.aruco.DetectorParameters())
    
    # Find stereo pairs
    pair0_files = sorted(glob.glob("scans/pair0_*.png"))
    pair1_files = sorted(glob.glob("scans/pair1_*.png"))
    
    print(f"Found {len(pair0_files)} FaceCam images")
    print(f"Found {len(pair1_files)} ZED images")
    
    if len(pair0_files) == 0 or len(pair1_files) == 0:
        print("No stereo pairs found!")
        return
    
    # Check first few pairs
    for i in range(min(5, len(pair0_files))):
        print(f"\nChecking pair {i}:")
        
        # Load images
        img0 = cv2.imread(pair0_files[i])
        img1 = cv2.imread(pair1_files[i])
        
        if img0 is None or img1 is None:
            print(f"  Failed to load images")
            continue
        
        # Detect markers
        corners0, ids0, _ = det.detectMarkers(img0)
        corners1, ids1, _ = det.detectMarkers(img1)
        
        print(f"  FaceCam: {len(ids0) if ids0 is not None else 0} markers")
        print(f"  ZED: {len(ids1) if ids1 is not None else 0} markers")
        
        if ids0 is not None and ids1 is not None:
            print(f"  FaceCam IDs: {ids0.flatten()[:10]}...")  # Show first 10 IDs
            print(f"  ZED IDs: {ids1.flatten()[:10]}...")      # Show first 10 IDs
            
            # Find common IDs
            common_ids = np.intersect1d(ids0.flatten(), ids1.flatten())
            print(f"  Common IDs: {len(common_ids)} ({common_ids[:10]}...)")
        else:
            print("  No markers detected in one or both images")
    
    print("\nRecommendations:")
    print("- Make sure both cameras can see the same ChArUco pattern")
    print("- Check that the pattern is clearly visible in both views")
    print("- Ensure the cameras are synchronized (captured at the same time)")

if __name__ == "__main__":
    debug_stereo_pairs()

