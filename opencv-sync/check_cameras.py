#!/usr/bin/env python3
"""
Check camera availability and backends
"""

import cv2
import sys

def check_cameras():
    """Check which cameras are available and working"""
    print("Camera Diagnostic")
    print("=" * 30)
    
    # Test different camera indices
    for i in range(5):
        print(f"\nTesting Camera {i}:")
        
        # Try different backends
        backends = [
            (cv2.CAP_DSHOW, "DirectShow"),
            (cv2.CAP_MSMF, "Media Foundation"),
            (cv2.CAP_ANY, "Any")
        ]
        
        for backend, name in backends:
            cap = cv2.VideoCapture(i, backend)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    h, w = frame.shape[:2]
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    print(f"  {name}: OK - {w}x{h} @ {fps:.1f}fps")
                    cap.release()
                    break
                else:
                    print(f"  {name}: Opened but can't read frames")
                    cap.release()
            else:
                print(f"  {name}: Failed to open")
        else:
            print(f"  Camera {i}: Not available")
    
    print("\nRecommendations:")
    print("- Make sure no other applications are using the cameras")
    print("- Restart OBS Virtual Camera if using Camera 3")
    print("- Check camera permissions in Windows Settings")

if __name__ == "__main__":
    check_cameras()
