#!/usr/bin/env python3
"""
Diagnose camera availability and test FaceCam access.
"""

import cv2
import time

def diagnose_cameras():
    """Diagnose all available cameras."""
    print("Camera Diagnosis")
    print("=" * 20)
    
    # Test all camera indices
    available_cameras = []
    
    for i in range(10):
        print(f"Testing camera {i}...")
        
        # Try different backends
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        
        for backend in backends:
            try:
                cap = cv2.VideoCapture(i, backend)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        height, width = frame.shape[:2]
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        backend_name = cap.getBackendName()
                        
                        print(f"  ✓ Camera {i}: {width}x{height} @ {fps}fps ({backend_name})")
                        available_cameras.append({
                            'index': i,
                            'width': width,
                            'height': height,
                            'fps': fps,
                            'backend': backend_name
                        })
                        cap.release()
                        break
                    cap.release()
            except Exception as e:
                continue
    
    print(f"\nFound {len(available_cameras)} working cameras:")
    for cam in available_cameras:
        print(f"  Camera {cam['index']}: {cam['width']}x{cam['height']} @ {cam['fps']}fps ({cam['backend']})")
    
    if not available_cameras:
        print("No cameras found!")
        return
    
    # Test the first available camera (likely FaceCam)
    print(f"\nTesting camera {available_cameras[0]['index']} (likely FaceCam)...")
    
    # Try different backends for FaceCam
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
    
    for backend in backends:
        print(f"Testing backend: {backend}")
        try:
            cap = cv2.VideoCapture(available_cameras[0]['index'], backend)
            if cap.isOpened():
                print(f"  ✓ Camera {available_cameras[0]['index']} opened with backend: {backend}")
                
                # Try to set higher resolution
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                cap.set(cv2.CAP_PROP_FPS, 30)
                
                # Get actual resolution
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                
                print(f"  Resolution: {width}x{height} @ {fps}fps")
                
                # Test frame capture
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"  ✓ Frame capture successful: {frame.shape}")
                    
                    # Show live feed for 3 seconds
                    print("  Showing live feed for 3 seconds...")
                    start_time = time.time()
                    while time.time() - start_time < 3:
                        ret, frame = cap.read()
                        if ret:
                            cv2.imshow(f"Camera {available_cameras[0]['index']} - {backend}", frame)
                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                break
                        else:
                            print("  Failed to read frame")
                            break
                    
                    cv2.destroyAllWindows()
                    print("  ✓ Live feed test successful")
                else:
                    print("  ✗ Frame capture failed")
                
                cap.release()
                break
            else:
                print(f"  ✗ Failed to open camera {available_cameras[0]['index']} with backend: {backend}")
        except Exception as e:
            print(f"  ✗ Error with backend {backend}: {e}")
    
    print(f"\nRecommendation:")
    if available_cameras:
        print(f"Use camera {available_cameras[0]['index']} for FaceCam in your scripts")
        print(f"Use camera 3 for ZED via OBS virtual camera")
    else:
        print("No cameras found. Check your camera connections.")

if __name__ == "__main__":
    diagnose_cameras()

