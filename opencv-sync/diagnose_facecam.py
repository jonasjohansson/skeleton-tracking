#!/usr/bin/env python3
"""
Diagnose FaceCam issues.
"""

import cv2
import time

def diagnose_facecam():
    """Diagnose FaceCam camera issues."""
    print("FaceCam Diagnostic")
    print("=" * 20)
    
    # Test different camera indices
    for i in range(5):
        print(f"\nTesting Camera {i}:")
        
        # Try DirectShow
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        
        if cap.isOpened():
            print(f"  DirectShow: Opened")
            
            # Try to read a frame
            ret, frame = cap.read()
            if ret and frame is not None:
                h, w = frame.shape[:2]
                print(f"  Frame read: OK - {w}x{h}")
                
                # Test different resolutions
                resolutions = [
                    (960, 540),   # Original
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
                print(f"  Frame read: FAILED")
                cap.release()
        else:
            print(f"  DirectShow: Failed to open")
    
    print("\nFaceCam not found! Check:")
    print("- FaceCam is connected and powered on")
    print("- No other applications are using the camera")
    print("- Camera permissions are granted")
    return None

def test_facecam_simple(camera_index):
    """Test FaceCam with simple setup."""
    print(f"\nTesting FaceCam (Camera {camera_index})")
    print("Press 'Q' to quit")
    
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print("Failed to open FaceCam")
        return
    
    # Try original resolution first
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
    
    # Get actual resolution
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"FaceCam resolution: {w}x{h}")
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"Failed to read frame {frame_count}")
            frame_count += 1
            if frame_count > 10:
                break
            time.sleep(0.1)
            continue
        
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
    camera_index = diagnose_facecam()
    if camera_index is not None:
        test_facecam_simple(camera_index)

