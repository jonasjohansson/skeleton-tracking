#!/usr/bin/env python3
"""
Detect OBS virtual camera and other available cameras.
"""

import cv2
import numpy as np

def detect_all_cameras():
    """Detect all available cameras including OBS virtual camera."""
    print("Detecting All Available Cameras")
    print("=" * 35)
    
    available_cameras = []
    
    # Test camera indices 0-10
    for i in range(11):
        print(f"Testing camera {i}...")
        cap = cv2.VideoCapture(i)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                height, width = frame.shape[:2]
                fps = cap.get(cv2.CAP_PROP_FPS)
                backend = cap.getBackendName()
                
                camera_info = {
                    'index': i,
                    'resolution': f"{width}x{height}",
                    'fps': fps,
                    'backend': backend
                }
                available_cameras.append(camera_info)
                print(f"  ✓ Camera {i}: {width}x{height} @ {fps}fps ({backend})")
            else:
                print(f"  ✗ Camera {i}: Failed to read frame")
        else:
            print(f"  ✗ Camera {i}: Failed to open")
        
        cap.release()
    
    print(f"\nFound {len(available_cameras)} working cameras:")
    for cam in available_cameras:
        print(f"  Camera {cam['index']}: {cam['resolution']} @ {cam['fps']}fps ({cam['backend']})")
    
    return available_cameras

def test_camera_feed(camera_index):
    """Test a specific camera feed."""
    print(f"\nTesting camera {camera_index} feed...")
    
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Failed to open camera {camera_index}")
        return False
    
    # Get camera properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    backend = cap.getBackendName()
    
    print(f"Camera {camera_index}: {width}x{height} @ {fps}fps ({backend})")
    
    print("Press 'q' to quit, 's' to save test image")
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"Failed to read from camera {camera_index}")
            break
        
        # Add info text
        cv2.putText(frame, f"Camera {camera_index} - {width}x{height}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Backend: {backend}", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'q' to quit, 's' to save", (10, 110), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.imshow(f"Camera {camera_index}", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = f"test_camera_{camera_index}_{frame_count}.png"
            cv2.imwrite(filename, frame)
            print(f"Saved: {filename}")
            frame_count += 1
    
    cap.release()
    cv2.destroyAllWindows()
    return True

def main():
    """Main function."""
    print("OBS Virtual Camera Detection")
    print("=" * 35)
    print("This will help you find the OBS virtual camera index.")
    print()
    
    # Detect all cameras
    cameras = detect_all_cameras()
    
    if not cameras:
        print("No cameras detected!")
        return
    
    print("\n" + "="*50)
    print("CAMERA DETECTION COMPLETE")
    print("="*50)
    
    # Ask user to identify cameras
    print("\nPlease identify your cameras:")
    print("1. Which camera is your Elgato FaceCam?")
    print("2. Which camera is the OBS virtual camera (ZED2i)?")
    print("3. Are there any other cameras you want to use?")
    
    # Test specific cameras
    while True:
        try:
            camera_index = int(input("\nEnter camera index to test (or -1 to quit): "))
            if camera_index == -1:
                break
            
            if any(cam['index'] == camera_index for cam in cameras):
                test_camera_feed(camera_index)
            else:
                print(f"Camera {camera_index} not found in available cameras.")
        except ValueError:
            print("Please enter a valid camera index.")
        except KeyboardInterrupt:
            break
    
    print("\nCamera detection complete!")
    print("Note the camera indices for your calibration scripts.")

if __name__ == "__main__":
    main()




