#!/usr/bin/env python3
"""
Compare different rectification options for skeleton tracking.
"""

import cv2
import numpy as np
import os

def compare_rectification_options():
    """Compare different rectification approaches."""
    print("Rectification Options Comparison")
    print("=" * 35)
    
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
    
    # Load transforms
    perspective_transform = None
    dual_maps = None
    
    try:
        perspective_transform = np.load("data/facecam_to_zed_transform.npy")
        print("Loaded perspective transform (Option 1)")
    except FileNotFoundError:
        print("Perspective transform not found")
    
    try:
        map1x = np.load("data/dual_map1x.npy")
        map1y = np.load("data/dual_map1y.npy")
        map2x = np.load("data/dual_map2x.npy")
        map2y = np.load("data/dual_map2y.npy")
        dual_maps = (map1x, map1y, map2x, map2y)
        print("Loaded dual rectification maps (Option 2)")
    except FileNotFoundError:
        print("Dual rectification maps not found")
    
    print("\nShowing comparison...")
    print("Press 'Q' to quit")
    print("Press 'S' to save comparison images")
    print("Press '1' for Option 1 (FaceCam->ZED), '2' for Option 2 (Dual), '3' for Option 3 (None)")
    
    saved_count = 0
    current_option = 1  # Start with Option 1
    
    while True:
        ret_facecam, frame_facecam = cap_facecam.read()
        ret_zed, frame_zed = cap_zed.read()
        
        if not ret_facecam or not ret_zed:
            print("Failed to read from cameras")
            break
        
        # Apply different rectification options
        if current_option == 1 and perspective_transform is not None:
            # Option 1: FaceCam transformed to match ZED
            rectified_facecam = cv2.warpPerspective(frame_facecam, perspective_transform, (1920, 1080))
            rectified_zed = frame_zed  # ZED stays original
            title = "Option 1: FaceCam->ZED (ZED original for tracking)"
            
        elif current_option == 2 and dual_maps is not None:
            # Option 2: Both cameras rectified to common reference
            map1x, map1y, map2x, map2y = dual_maps
            rectified_facecam = cv2.remap(frame_facecam, map1x, map1y, cv2.INTER_LINEAR)
            rectified_zed = cv2.remap(frame_zed, map2x, map2y, cv2.INTER_LINEAR)
            title = "Option 2: Both cameras rectified (affects ZED tracking)"
            
        else:
            # Option 3: No rectification
            rectified_facecam = frame_facecam
            rectified_zed = frame_zed
            title = "Option 3: No rectification (original cameras)"
        
        # Add labels
        cv2.putText(rectified_facecam, "FaceCam", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(rectified_zed, "ZED", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Show both images side by side
        combined = np.hstack((rectified_facecam, rectified_zed))
        
        # Add title
        cv2.putText(combined, title, (10, combined.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Add instructions
        cv2.putText(combined, "Press 1/2/3 to switch options, Q to quit, S to save", 
                   (10, combined.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        cv2.imshow("Rectification Options Comparison", combined)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('s') or key == ord('S'):
            # Save comparison images
            cv2.imwrite(f"scans/comparison_facecam_{current_option}_{saved_count:03d}.png", rectified_facecam)
            cv2.imwrite(f"scans/comparison_zed_{current_option}_{saved_count:03d}.png", rectified_zed)
            saved_count += 1
            print(f"Saved comparison images for option {current_option}: {saved_count}")
        elif key == ord('1'):
            current_option = 1
            print("Switched to Option 1: FaceCam->ZED (recommended for skeleton tracking)")
        elif key == ord('2'):
            current_option = 2
            print("Switched to Option 2: Dual rectification (affects ZED tracking)")
        elif key == ord('3'):
            current_option = 3
            print("Switched to Option 3: No rectification (original cameras)")
    
    cap_facecam.release()
    cap_zed.release()
    cv2.destroyAllWindows()

def show_recommendations():
    """Show recommendations for skeleton tracking."""
    print("\nRecommendations for Skeleton Tracking:")
    print("=" * 40)
    print()
    print("Option 1 (FaceCam->ZED): RECOMMENDED")
    print("  ✓ ZED keeps original calibration (best for tracking)")
    print("  ✓ FaceCam provides aligned reference")
    print("  ✓ Minimal impact on tracking accuracy")
    print("  ✓ Good for visual confirmation/overlay")
    print()
    print("Option 2 (Dual rectification): NOT RECOMMENDED")
    print("  ✗ ZED loses original calibration")
    print("  ✗ May affect skeleton tracking accuracy")
    print("  ✗ Depth measurements might be affected")
    print("  ✓ Both cameras have same perspective")
    print()
    print("Option 3 (No rectification): ALTERNATIVE")
    print("  ✓ Maximum accuracy for both cameras")
    print("  ✓ No processing overhead")
    print("  ✗ Cameras might not be well-aligned")
    print("  ✗ Harder to compare views")
    print()
    print("For skeleton tracking, use Option 1 to keep ZED accuracy!")

def main():
    """Main function."""
    print("Rectification Options for Skeleton Tracking")
    print("=" * 45)
    
    # Show recommendations
    show_recommendations()
    
    # Show live comparison
    compare_rectification_options()

if __name__ == "__main__":
    main()

