#!/usr/bin/env python3
"""
Simple camera test without ZED SDK dependency.
Tests basic camera functionality for calibration setup.
"""

import cv2
import numpy as np
import time

def test_cameras():
    """Test available cameras without ZED SDK."""
    print("Simple Camera Test")
    print("=" * 20)
    
    available_cameras = []
    
    # Test camera indices 0-5
    for i in range(6):
        print(f"Testing camera {i}...")
        cap = cv2.VideoCapture(i)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                height, width = frame.shape[:2]
                fps = cap.get(cv2.CAP_PROP_FPS)
                
                camera_info = {
                    'index': i,
                    'resolution': f"{width}x{height}",
                    'fps': fps,
                    'backend': cap.getBackendName()
                }
                available_cameras.append(camera_info)
                print(f"  ✓ Camera {i}: {width}x{height} @ {fps}fps ({cap.getBackendName()})")
            else:
                print(f"  ✗ Camera {i}: Failed to read frame")
        else:
            print(f"  ✗ Camera {i}: Failed to open")
        
        cap.release()
    
    if not available_cameras:
        print("\nNo cameras detected!")
        return
    
    print(f"\nFound {len(available_cameras)} working cameras:")
    for cam in available_cameras:
        print(f"  Camera {cam['index']}: {cam['resolution']} @ {cam['fps']}fps")
    
    # Test camera feeds
    if len(available_cameras) >= 2:
        print("\nTesting camera feeds...")
        print("Press 'q' to quit, 's' to save frame")
        
        # Open first two cameras
        cap0 = cv2.VideoCapture(available_cameras[0]['index'])
        cap1 = cv2.VideoCapture(available_cameras[1]['index'])
        
        if cap0.isOpened() and cap1.isOpened():
            frame_count = 0
            
            while True:
                ret0, frame0 = cap0.read()
                ret1, frame1 = cap1.read()
                
                if not ret0 or not ret1:
                    print("Failed to read from cameras")
                    break
                
                # Add timestamp and camera info
                timestamp = time.time()
                cam0_info = f"Camera {available_cameras[0]['index']} - {timestamp:.3f}"
                cam1_info = f"Camera {available_cameras[1]['index']} - {timestamp:.3f}"
                
                cv2.putText(frame0, cam0_info, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame1, cam1_info, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow(f"Camera {available_cameras[0]['index']}", frame0)
                cv2.imshow(f"Camera {available_cameras[1]['index']}", frame1)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    cv2.imwrite(f"test_frame0_{frame_count}.png", frame0)
                    cv2.imshow("Camera 1", frame1)
                    print(f"Saved test frames: test_frame0_{frame_count}.png, test_frame1_{frame_count}.png")
                    frame_count += 1
            
            cap0.release()
            cap1.release()
            cv2.destroyAllWindows()
            
            print("\nCamera test completed!")
            print("You can now proceed with calibration using these camera indices.")
        else:
            print("Failed to open cameras for testing")
    else:
        print("Need at least 2 cameras for stereo calibration")

def main():
    """Main function."""
    try:
        test_cameras()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error during camera test: {str(e)}")

if __name__ == "__main__":
    main()
