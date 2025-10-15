# ZED SDK Installation Guide

The ZED SDK needs to be installed separately from the Python packages. Here's how to set it up:

## Option 1: Official ZED SDK (Recommended)

1. **Download ZED SDK**
   - Go to [Stereolabs ZED SDK Downloads](https://www.stereolabs.com/developers/release/)
   - Download the latest ZED SDK for Windows
   - Choose the version that matches your Python version

2. **Install ZED SDK**
   - Run the downloaded installer
   - Follow the installation wizard
   - The SDK will install to `C:\Program Files (x86)\ZED SDK\`

3. **Install Python API**
   - Open Command Prompt as Administrator
   - Navigate to the ZED SDK Python folder:
     ```cmd
     cd "C:\Program Files (x86)\ZED SDK\python"
     ```
   - Install the Python API:
     ```cmd
     pip install pyzed
     ```

## Option 2: Alternative Installation

If the above doesn't work, try:

1. **Download ZED SDK Python API directly**
   - Go to [ZED SDK Python API](https://pypi.org/project/pyzed/)
   - Download the wheel file for your Python version
   - Install manually:
     ```cmd
     pip install path/to/downloaded/wheel.whl
     ```

## Option 3: Without ZED SDK (Limited Functionality)

If you can't install the ZED SDK, the system will still work with your Elgato FaceCam and any other OpenCV-compatible camera. The ZED-specific features will be disabled.

## Verification

Test your installation:

```python
try:
    import pyzed.sl as sl
    print("ZED SDK installed successfully!")
except ImportError:
    print("ZED SDK not available - using OpenCV cameras only")
```

## Troubleshooting

### Common Issues:

1. **"No module named 'pyzed'"**
   - Ensure ZED SDK is installed first
   - Check Python version compatibility
   - Try reinstalling the Python API

2. **"ZED camera not detected"**
   - Ensure ZED camera is connected via USB 3.0
   - Check ZED camera firmware is up to date
   - Try different USB ports

3. **Permission errors**
   - Run Command Prompt as Administrator
   - Check antivirus software isn't blocking installation

## Alternative: Use OpenCV Only

If ZED SDK installation fails, you can still use the system with:
- Elgato FaceCam (camera 0)
- Any other USB camera (camera 1)
- Webcam or other OpenCV-compatible camera

The calibration and synchronization will work the same way, just without ZED-specific features like depth sensing.






