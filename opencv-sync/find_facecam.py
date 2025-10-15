#!/usr/bin/env python3
"""
Find the FaceCam camera and test different resolutions.
"""

import cv2
import time

def find_facecam():
    """Find which camera index is the FaceCam."""
    print("Finding FaceCam Camera")
    print("=" * 25)
    
    # Test different camera indices
    for i in range(5):
        print(f"\nTesting Camera {i}:")
        
        # Try DirectShow first (usually works better for FaceCam)
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                h, w = frame.shape[:2]
                print(f"  DirectShow: OK - {w}x{h}")
                
                # Test different resolutions
                resolutions = [
                    (960, 540),   # Original FaceCam resolution
                    (1280, 720),  # HD
                    (1920, 1080), # Full HD
                ]
                
                for target_w, target_h in resolutions:
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, target_w)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, target_h)
                    
                    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    
                    if actual_w == target_w and actual_h == target_h:
                        print(f"    {target_w}x{target_h}: OK")
                    else:
                        print(f"    {target_w}x{target_h}: {actual_w}x{actual_h}")
                
                cap.release()
                return i
            else:
                print(f"  DirectShow: Opened but can't read frames")
                cap.release()
        else:
            print(f"  DirectShow: Failed to open")
    
    print("\nFaceCam not found! Check:")
    print("- FaceCam is connected and powered on")
    print("- No other applications are using the camera")
    print("- Camera permissions are granted")
    return None

def test_facecam_live(camera_index):
    """Test FaceCam with live feed."""
    print(f"\nTesting FaceCam (Camera {camera_index})")
    print("Press 'Q' to quit")
    
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print("Failed to open FaceCam")
        return
    
    # Try to set to 1920x1080
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    # Get actual resolution
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"FaceCam resolution: {w}x{h}")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read from FaceCam")
            break
        
        # Add label
        cv2.putText(frame, f"FaceCam - {w}x{h}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        cv2.imshow("FaceCam Test", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    camera_index = find_facecam()
    if camera_index is not None:
        test_facecam_live(camera_index)

