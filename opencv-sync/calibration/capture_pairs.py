#!/usr/bin/env python3
"""
Capture stereo pairs for stereo calibration.
Press 1 to save Facecam, 2 to save ZED, then S when both updated.
Repeat 10–15 poses.
"""

import cv2
import time
import sys

def capture_stereo_pairs():
    """Capture synchronized stereo image pairs."""
    print("Stereo Pair Capture")
    print("=" * 30)
    print("Instructions:")
    print("- Press '1' to capture from camera 0 (FaceCam)")
    print("- Press '2' to capture from camera 3 (ZED via OBS)")
    print("- Press 'S' to save the pair when both are updated")
    print("- Press 'Q' to quit")
    print("- Capture 10-15 different poses")
    
    # Initialize cameras
    cap0 = None
    cap1 = None
    
    # Try different backends for better camera access
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
    
    for backend in backends:
        try:
            cap0 = cv2.VideoCapture(0, backend)
            if cap0.isOpened():
                print(f"Camera 0 (FaceCam) opened with backend: {backend}")
                break
        except:
            continue
    
    for backend in backends:
        try:
            cap1 = cv2.VideoCapture(3, backend)  # Camera 3 for OBS virtual camera
            if cap1.isOpened():
                print(f"Camera 3 (ZED via OBS) opened with backend: {backend}")
                break
        except:
            continue
    
    if cap0 is None or not cap0.isOpened():
        print("Failed to open camera 0 (FaceCam)")
        return
    
    if cap1 is None or not cap1.isOpened():
        print("Failed to open camera 3 (ZED via OBS)")
        return
    
    # Set camera properties
    cap0.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap0.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap0.set(cv2.CAP_PROP_FPS, 30)
    
    cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap1.set(cv2.CAP_PROP_FPS, 30)
    
    pair_count = 0
    frame0 = None
    frame1 = None
    
    print("\nStarting stereo pair capture...")
    
    while True:
        # Read frames from both cameras
        ret0, img0 = cap0.read()
        ret1, img1 = cap1.read()
        
        if not ret0 or not ret1:
            print("Failed to read from one or both cameras")
            break
        
        # Create visualization windows
        vis0 = img0.copy()
        vis1 = img1.copy()
        
        # Add status text
        cv2.putText(vis0, f"Camera 0 (FaceCam) - Pair: {pair_count}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(vis0, "Press '1' to capture", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(vis0, "Press 'S' to save pair", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.putText(vis1, f"Camera 3 (ZED via OBS) - Pair: {pair_count}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(vis1, "Press '2' to capture", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(vis1, "Press 'S' to save pair", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Show captured status
        if frame0 is not None:
            cv2.putText(vis0, "CAPTURED", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        if frame1 is not None:
            cv2.putText(vis1, "CAPTURED", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # Display frames
        cv2.imshow("Camera 0 (FaceCam)", vis0)
        cv2.imshow("Camera 3 (ZED via OBS)", vis1)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('1'):
            frame0 = img0.copy()
            cv2.imwrite("_tmp0.png", frame0)
            print("Captured from camera 0")
        
        elif key == ord('2'):
            frame1 = img1.copy()
            cv2.imwrite("_tmp1.png", frame1)
            print("Captured from camera 1")
        
        elif key == ord('s') or key == ord('S'):
            if frame0 is not None and frame1 is not None:
                # Save the stereo pair
                filename0 = f"pair0_{pair_count:03d}.png"
                filename1 = f"pair1_{pair_count:03d}.png"
                
                cv2.imwrite(filename0, frame0)
                cv2.imwrite(filename1, frame1)
                
                print(f"Saved stereo pair {pair_count}: {filename0}, {filename1}")
                pair_count += 1
                time.sleep(0.1)  # Small delay
                
                # Reset for next pair
                frame0 = None
                frame1 = None
            else:
                print("Both frames must be captured before saving pair!")
        
        elif key == ord('q') or key == ord('Q'):
            break
    
    # Cleanup
    cap0.release()
    cap1.release()
    cv2.destroyAllWindows()
    
    print(f"\nCaptured {pair_count} stereo pairs")
    print("Files saved as pair0_XXX.png and pair1_XXX.png")

def main():
    """Main function."""
    try:
        capture_stereo_pairs()
    except KeyboardInterrupt:
        print("\nCapture interrupted by user")
    except Exception as e:
        print(f"Error during capture: {str(e)}")

if __name__ == "__main__":
    main()



