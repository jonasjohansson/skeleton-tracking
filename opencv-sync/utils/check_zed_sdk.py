#!/usr/bin/env python3
"""
Check ZED SDK installation and Python API availability.
"""

import sys
import os

def check_zed_sdk():
    """Check if ZED SDK is properly installed."""
    print("Checking ZED SDK Installation")
    print("=" * 35)
    
    # Check if pyzed module is available
    try:
        import pyzed.sl as sl
        print("✓ pyzed module is available")
        
        # Test basic ZED functionality
        zed = sl.Camera()
        print("✓ ZED Camera class is accessible")
        
        # Check available resolutions
        print("\nAvailable ZED resolutions:")
        resolutions = [
            (sl.RESOLUTION.VGA, "VGA"),
            (sl.RESOLUTION.HD720, "HD720"),
            (sl.RESOLUTION.HD1080, "HD1080"),
            (sl.RESOLUTION.HD2K, "HD2K"),
            (sl.RESOLUTION.HD4K, "HD4K")
        ]
        
        for res, name in resolutions:
            print(f"  {name}: {res}")
        
        return True
        
    except ImportError as e:
        print(f"✗ pyzed module not available: {e}")
        print("\nTrying to find ZED SDK installation...")
        
        # Check common ZED SDK installation paths
        zed_paths = [
            r"C:\Program Files (x86)\ZED SDK",
            r"C:\Program Files\ZED SDK",
            r"C:\ZED SDK",
            os.path.expanduser(r"~\ZED SDK")
        ]
        
        for path in zed_paths:
            if os.path.exists(path):
                print(f"✓ Found ZED SDK at: {path}")
                
                # Check for Python API
                python_path = os.path.join(path, "python")
                if os.path.exists(python_path):
                    print(f"✓ Found Python API at: {python_path}")
                    print(f"  Try installing: pip install {python_path}")
                else:
                    print(f"✗ Python API not found at: {python_path}")
            else:
                print(f"✗ ZED SDK not found at: {path}")
        
        return False
    
    except Exception as e:
        print(f"✗ Error with ZED SDK: {e}")
        return False

def check_zed_explorer():
    """Check if ZED Explorer is available."""
    print("\nChecking ZED Explorer...")
    
    # Check if ZED Explorer executable exists
    explorer_paths = [
        r"C:\Program Files (x86)\ZED SDK\bin\ZED Explorer.exe",
        r"C:\Program Files\ZED SDK\bin\ZED Explorer.exe",
        r"C:\ZED SDK\bin\ZED Explorer.exe"
    ]
    
    for path in explorer_paths:
        if os.path.exists(path):
            print(f"✓ ZED Explorer found at: {path}")
            return True
    
    print("✗ ZED Explorer not found in common locations")
    return False

def main():
    """Main function."""
    print("ZED SDK Installation Check")
    print("=" * 30)
    print()
    
    zed_sdk_ok = check_zed_sdk()
    zed_explorer_ok = check_zed_explorer()
    
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    
    if zed_sdk_ok:
        print("✓ ZED SDK is properly installed and accessible")
        print("✓ You can use the ZED SDK scripts")
    else:
        print("✗ ZED SDK Python API is not available")
        print("  You have ZED Explorer but not the Python API")
        print("  Try installing: pip install pyzed")
    
    if zed_explorer_ok:
        print("✓ ZED Explorer is available")
    else:
        print("✗ ZED Explorer not found")
    
    print("\nRECOMMENDATIONS:")
    if zed_sdk_ok:
        print("1. Use ZED SDK scripts for better resolution")
        print("2. Run: python capture_zed_force_resolution.py")
    else:
        print("1. Install Python API: pip install pyzed")
        print("2. Or use OpenCV scripts with current resolution")
        print("3. Run: python capture_zed_low_res.py")

if __name__ == "__main__":
    main()




