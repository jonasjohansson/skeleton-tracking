# ZED2i + Elgato FaceCam ChArUco Calibration System

This system provides a complete pipeline for calibrating and synchronizing your ZED2i camera with your Elgato FaceCam using ChArUco patterns.

## Overview

The system follows a streamlined 5-step process:
1. **Generate ChArUco Pattern** - Create a printable calibration board
2. **Capture Intrinsics** - Collect calibration images from each camera
3. **Calibrate Intrinsics** - Compute individual camera parameters
4. **Capture Stereo Pairs** - Collect synchronized image pairs
5. **Compute Stereo Extrinsics** - Calculate camera relationship

## Requirements

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install ZED SDK (Optional)
For ZED2i camera support, follow the detailed guide in `ZED_INSTALLATION.md`:

**Quick ZED SDK Installation:**
1. Download ZED SDK from [Stereolabs](https://www.stereolabs.com/developers/release/)
2. Install the SDK
3. Install Python API: `pip install pyzed`

**Alternative: Use OpenCV Cameras Only**
If ZED SDK installation fails, you can still use the system with:
- Elgato FaceCam + any other USB camera
- Two webcams
- Any combination of OpenCV-compatible cameras

### 3. Test Your Setup
```bash
python simple_camera_test.py
```
This will detect and test your available cameras.

## Quick Start

### Step 1: Generate ChArUco Pattern
```bash
python board_def.py
```
This creates `charuco_A4.png` - print this on A4 paper for calibration.

### Step 2: Capture Individual Camera Calibration Images
```bash
python capture_intrinsics.py
```
- Press 'S' to save frames when the ChArUco pattern is visible
- Move the pattern to different positions and angles
- Capture 20-30 images per camera
- Press 'Q' to quit

### Step 3: Calibrate Individual Cameras
```bash
python calibrate_intrinsics.py
```
This computes intrinsic parameters for each camera and saves:
- `K_facecam.npy` - FaceCam camera matrix
- `dist_facecam.npy` - FaceCam distortion coefficients
- `K_zed.npy` - ZED camera matrix
- `dist_zed.npy` - ZED distortion coefficients

### Step 4: Capture Stereo Pairs
```bash
python capture_pairs.py
```
- Press '1' to capture from FaceCam
- Press '2' to capture from ZED
- Press 'S' to save the synchronized pair
- Capture 10-15 different poses
- Press 'Q' to quit

### Step 5: Compute Stereo Extrinsics
```bash
python stereo_extrinsics.py
```
This computes the relationship between cameras and saves:
- `R.npy` - Rotation matrix between cameras
- `t.npy` - Translation vector between cameras
- `E.npy` - Essential matrix
- `F.npy` - Fundamental matrix

### Step 6: Run Synchronized Stream
```bash
python camera_sync.py
```
- View synchronized, undistorted feeds from both cameras
- Press 'S' to save synchronized frames
- Press 'V' to toggle epipolar line visualization
- Press 'Q' to quit

## File Structure

```
opencv-sync/
├── board_def.py              # ChArUco board definition
├── capture_intrinsics.py     # Capture calibration images
├── calibrate_intrinsics.py   # Calibrate individual cameras
├── capture_pairs.py          # Capture stereo pairs
├── stereo_extrinsics.py      # Compute stereo extrinsics
├── camera_sync.py            # Synchronized camera stream
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Calibration Parameters

The system uses consistent ChArUco board parameters:
- **Dictionary**: DICT_5X5_1000 (better marker detection)
- **Board Size**: 7x5 squares
- **Square Size**: 35mm
- **Marker Size**: 28mm

## Troubleshooting

### Camera Detection Issues
- Ensure cameras are connected and recognized by Windows
- Try different camera indices in the scripts
- Check that no other applications are using the cameras

### ZED2i Issues
- Install the latest ZED SDK
- Ensure ZED camera is properly connected via USB 3.0
- Check ZED camera firmware is up to date

### Calibration Quality
- Use good lighting conditions
- Ensure ChArUco pattern is flat and well-printed
- Capture images from various angles and distances
- Avoid motion blur in captured images

### Synchronization Issues
- Ensure both cameras are running at the same frame rate
- Check that system can handle the data throughput
- Consider using hardware synchronization if available

## Advanced Usage

### Custom Board Parameters
Edit `board_def.py` to modify:
- Board dimensions (squares_x, squares_y)
- Square and marker sizes
- ArUco dictionary type

### Camera Properties
Modify camera settings in the scripts:
- Resolution (default: 1920x1080)
- Frame rate (default: 30 FPS)
- Exposure settings

### Integration with Other Applications
The saved `.npy` files can be loaded in other applications:
```python
import numpy as np

# Load calibration data
K_facecam = np.load("K_facecam.npy")
dist_facecam = np.load("dist_facecam.npy")
R = np.load("R.npy")
t = np.load("t.npy")
```

## Performance Tips

1. **Use SSD storage** for faster image saving during calibration
2. **Close other applications** to free up system resources
3. **Use USB 3.0 ports** for both cameras
4. **Ensure adequate lighting** for better pattern detection
5. **Print ChArUco pattern at high quality** (300 DPI recommended)

## Support

For issues with:
- **ZED2i camera**: Check [Stereolabs documentation](https://www.stereolabs.com/docs/)
- **Elgato FaceCam**: Check [Elgato support](https://help.elgato.com/)
- **OpenCV/ChArUco**: Check [OpenCV documentation](https://docs.opencv.org/)

## License

This project is provided as-is for educational and research purposes.
