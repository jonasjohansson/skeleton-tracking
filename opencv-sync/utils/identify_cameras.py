#!/usr/bin/env python3
"""
Identify your specific cameras by testing each one individually.
"""

import cv2
import time

def test_single_camera(camera_index):
    """Test a single camera and show its feed."""
    print(f"\nTesting Camera {camera_index}")
    print("=" * 25)
    
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"Camera {camera_index}: Failed to open")
        return False
    
    # Get camera properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    backend = cap.getBackendName()
    
    print(f"Camera {camera_index}: {width}x{height} @ {fps}fps ({backend})")
    
    # Test reading frames
    ret, frame = cap.read()
    if not ret or frame is None:
        print(f"Camera {camera_index}: Failed to read frame")
        cap.release()
        return False
    
    print(f"Camera {camera_index}: Successfully reading frames")
    print("Press 'q' to quit this camera test")
    print("Press 's' to save a test image")
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"Camera {camera_index}: Lost connection")
            break
        
        # Add info text
        cv2.putText(frame, f"Camera {camera_index}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"{width}x{height} @ {fps}fps", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
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
    """Test each camera individually."""
    print("Camera Identification Test")
    print("=" * 30)
    print("This will test each camera one by one.")
    print("Look for your Elgato FaceCam and ZED2i camera.")
    print()
    
    # Test cameras 0-5
    for i in range(6):
        print(f"\n{'='*50}")
        print(f"Testing Camera {i}")
        print("Is this your Elgato FaceCam or ZED2i camera?")
        print("Press Enter to test this camera, or 'n' to skip...")
        
        choice = input().lower()
        if choice == 'n':
            print(f"Skipping camera {i}")
            continue
        
        success = test_single_camera(i)
        
        if success:
            print(f"\nCamera {i} test completed.")
            print("Was this your Elgato FaceCam or ZED2i? (y/n)")
            is_target_camera = input().lower() == 'y'
            
            if is_target_camera:
                print(f"✓ Camera {i} identified as target camera")
            else:
                print(f"Camera {i} is not your target camera")
        
        print("\nPress Enter to continue to next camera...")
        input()
    
    print("\nCamera identification complete!")
    print("Note which camera indices correspond to your Elgato FaceCam and ZED2i.")

if __name__ == "__main__":
    main()




