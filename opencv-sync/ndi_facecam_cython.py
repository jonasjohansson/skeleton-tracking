#!/usr/bin/env python3
"""
NDI sender for transformed FaceCam using Cython for performance.
"""

import numpy as np
import os
import sys

def ndi_facecam_cython():
    """Send transformed FaceCam over NDI using Cython."""
    print("NDI FaceCam Transformed (Cython)")
    print("=" * 40)
    print("This creates a high-performance transformed FaceCam feed for NDI")
    print()
    
    # Load transform
    try:
        transform_matrix = np.load("data/facecam_to_zed_transform.npy")
        print(f"Loaded transform matrix: {transform_matrix.shape}")
    except FileNotFoundError:
        print("Transform not found! Run match_facecam_to_zed_simple.py first.")
        return
    
    # Create corrected transform for native resolution
    w, h = 960, 540  # FaceCam native resolution
    scale_x = w / 1920.0  # 960/1920 = 0.5
    scale_y = h / 1080.0  # 540/1080 = 0.5
    
    scale_matrix = np.array([
        [scale_x, 0, 0],
        [0, scale_y, 0],
        [0, 0, 1]
    ], dtype=np.float32)
    
    corrected_transform = scale_matrix @ transform_matrix
    
    print("Press 'Q' to quit, 'S' to save frames")
    print()
    print("INSTRUCTIONS FOR NDI:")
    print("1. Open OBS Studio")
    print("2. Add a 'Window Capture' source")
    print("3. Select this window: 'NDI_FaceCam_Cython'")
    print("4. Install OBS NDI plugin if not already installed")
    print("5. Add 'NDI Output' filter to the source")
    print("6. Configure NDI output settings")
    print("7. In Resolume, add an 'NDI' source")
    print("8. Select the NDI stream from OBS")
    print()
    
    # Try to import Cython module
    try:
        import facecam_transform_cython
        print("Using Cython optimization...")
        facecam_transform_cython.process_facecam_stream(1, corrected_transform, "NDI_FaceCam_Cython")
    except ImportError:
        print("Cython module not found. Building...")
        print("Run: python setup.py build_ext --inplace")
        print("Then run this script again.")
        return
    
    print("NDI FaceCam Transformed (Cython) stopped")

if __name__ == "__main__":
    ndi_facecam_cython()

