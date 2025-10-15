#!/usr/bin/env python3
"""
Debug visualization showing how the FaceCam image is warped to match ZED.
Shows original image underneath the transformed one.
"""

import cv2
import numpy as np
import os

def show_warp_visualization():
    """Show how the image is warped with original underneath."""
    print("Warp Visualization Debug")
    print("=" * 25)
    
    # Load transform
    try:
        transform_matrix = np.load("data/facecam_to_zed_transform.npy")
        print(f"Transform matrix loaded successfully")
        print(f"Scale X: {transform_matrix[0, 0]:.4f}")
        print(f"Scale Y: {transform_matrix[1, 1]:.4f}")
        print(f"Translation: ({transform_matrix[0, 2]:.1f}, {transform_matrix[1, 2]:.1f})")
    except FileNotFoundError:
        print("Transform not found! Run match_facecam_to_zed_simple.py first.")
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
    
    print("Showing warp visualization...")
    print("Press 'Q' to quit")
    print("Press 'S' to save debug images")
    print("Press 'T' to toggle transparency")
    
    saved_count = 0
    transparency = 0.7  # How transparent the transformed image is
    
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
        
        # Create overlay visualization
        # Start with original FaceCam as base
        overlay = frame_facecam.copy()
        
        # Create a mask for the transformed area
        mask = np.ones((1080, 1920), dtype=np.uint8) * 255
        
        # Blend the transformed image with transparency
        cv2.addWeighted(overlay, 1.0, transformed_facecam, transparency, 0, overlay)
        
        # Add border to show the transformed area
        cv2.rectangle(overlay, (0, 0), (1919, 1079), (0, 255, 0), 3)
        
        # Create side-by-side comparison
        # Resize for display
        h, w = 400, 600
        original_small = cv2.resize(frame_facecam, (w, h))
        transformed_small = cv2.resize(transformed_facecam, (w, h))
        overlay_small = cv2.resize(overlay, (w, h))
        zed_small = cv2.resize(frame_zed, (w, h))
        
        # Create 2x2 grid
        top_row = np.hstack((original_small, transformed_small))
        bottom_row = np.hstack((overlay_small, zed_small))
        combined = np.vstack((top_row, bottom_row))
        
        # Add labels
        cv2.putText(combined, "Original FaceCam", (10, 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(combined, "Transformed FaceCam", (w + 10, 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(combined, f"Overlay (alpha={transparency:.1f})", (10, h + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(combined, "Target ZED", (w + 10, h + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Add transform info
        cv2.putText(combined, f"Scale: {transform_matrix[0, 0]:.3f}, {transform_matrix[1, 1]:.3f}", 
                   (10, h + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        cv2.putText(combined, f"Translation: {transform_matrix[0, 2]:.1f}, {transform_matrix[1, 2]:.1f}", 
                   (10, h + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        cv2.putText(combined, "Press T to toggle transparency", 
                   (10, h + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        cv2.imshow("Warp Visualization Debug", combined)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('s') or key == ord('S'):
            # Save debug images
            cv2.imwrite(f"scans/warp_original_facecam_{saved_count:03d}.png", frame_facecam)
            cv2.imwrite(f"scans/warp_transformed_facecam_{saved_count:03d}.png", transformed_facecam)
            cv2.imwrite(f"scans/warp_overlay_{saved_count:03d}.png", overlay)
            cv2.imwrite(f"scans/warp_target_zed_{saved_count:03d}.png", frame_zed)
            saved_count += 1
            print(f"Saved warp debug images: {saved_count}")
        elif key == ord('t') or key == ord('T'):
            # Toggle transparency
            transparency = 1.0 - transparency
            print(f"Transparency changed to: {transparency:.1f}")
    
    cap_facecam.release()
    cap_zed.release()
    cv2.destroyAllWindows()

def show_corner_analysis():
    """Show how specific corners are transformed."""
    print("\nCorner Analysis")
    print("=" * 15)
    
    # Load transform
    try:
        transform_matrix = np.load("data/facecam_to_zed_transform.npy")
    except FileNotFoundError:
        print("Transform not found!")
        return
    
    # Test corners of the image
    corners = np.array([
        [[0, 0]],           # Top-left
        [[1919, 0]],        # Top-right
        [[0, 1079]],        # Bottom-left
        [[1919, 1079]],     # Bottom-right
        [[960, 540]]        # Center
    ], dtype=np.float32)
    
    # Transform corners
    transformed_corners = cv2.perspectiveTransform(corners, transform_matrix)
    
    print("Corner transformations:")
    corner_names = ["Top-left", "Top-right", "Bottom-left", "Bottom-right", "Center"]
    
    for i, (original, transformed) in enumerate(zip(corners, transformed_corners)):
        print(f"{corner_names[i]}: ({original[0][0]:.1f}, {original[0][1]:.1f}) -> "
              f"({transformed[0][0]:.1f}, {transformed[0][1]:.1f})")
    
    # Calculate displacement
    displacement = transformed_corners - corners
    print(f"\nDisplacement analysis:")
    for i, disp in enumerate(displacement):
        print(f"{corner_names[i]}: ({disp[0][0]:.1f}, {disp[0][1]:.1f}) pixels")

def main():
    """Main function."""
    print("Warp Visualization Debug")
    print("=" * 25)
    
    # Show corner analysis first
    show_corner_analysis()
    
    # Show live warp visualization
    show_warp_visualization()

if __name__ == "__main__":
    main()

