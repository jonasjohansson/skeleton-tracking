#!/usr/bin/env python3
"""
Test both cameras simultaneously.
"""

import cv2
import time

def test_both_cameras():
    """Test both cameras simultaneously."""
    print("Testing Both Cameras")
    print("=" * 25)
    
    # Initialize cameras
    cap0 = None  # FaceCam
    cap3 = None  # ZED via OBS
    
    # Try different backends for FaceCam (camera 0)
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
    
    for backend in backends:
        try:
            cap0 = cv2.VideoCapture(0, backend)
            if cap0.isOpened():
                print(f"✓ Camera 0 (FaceCam) opened with backend: {backend}")
                break
        except:
            continue
    
    if cap0 is None or not cap0.isOpened():
        print("✗ Failed to open camera 0 (FaceCam)")
        return
    
    # Try different backends for ZED via OBS (camera 3)
    for backend in backends:
        try:
            cap3 = cv2.VideoCapture(3, backend)
            if cap3.isOpened():
                print(f"✓ Camera 3 (ZED via OBS) opened with backend: {backend}")
                break
        except:
            continue
    
    if cap3 is None or not cap3.isOpened():
        print("✗ Failed to open camera 3 (ZED via OBS)")
        cap0.release()
        return
    
    # Set camera properties
    cap0.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap0.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap0.set(cv2.CAP_PROP_FPS, 30)
    
    cap3.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap3.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap3.set(cv2.CAP_PROP_FPS, 30)
    
    print("\nBoth cameras initialized successfully!")
    print("Press 'Q' to quit")
    print("Press 'S' to save frames")
    
    save_count = 0
    
    while True:
        # Read frames from both cameras
        ret0, frame0 = cap0.read()
        ret3, frame3 = cap3.read()
        
        if not ret0:
            print("Failed to read from camera 0 (FaceCam)")
            break
        
        if not ret3:
            print("Failed to read from camera 3 (ZED via OBS)")
            break
        
        # Add status text
        cv2.putText(frame0, f"Camera 0 (FaceCam) - {frame0.shape}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame0, "Press 'Q' to quit, 'S' to save", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.putText(frame3, f"Camera 3 (ZED via OBS) - {frame3.shape}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame3, "Press 'Q' to quit, 'S' to save", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Display frames
        cv2.imshow("Camera 0 (FaceCam)", frame0)
        cv2.imshow("Camera 3 (ZED via OBS)", frame3)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('s') or key == ord('S'):
            # Save frames
            filename0 = f"test_frame0_{save_count:03d}.png"
            filename3 = f"test_frame3_{save_count:03d}.png"
            cv2.imwrite(filename0, frame0)
            cv2.imwrite(filename3, frame3)
            print(f"Saved: {filename0}, {filename3}")
            save_count += 1
    
    # Cleanup
    cap0.release()
    cap3.release()
    cv2.destroyAllWindows()
    
    print("Test completed!")

if __name__ == "__main__":
    test_both_cameras()


