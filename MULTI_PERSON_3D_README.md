# Multi-Person 3D Tracking with Body Segmentation

This HTML file provides advanced multi-person pose tracking with body segmentation and 3D objects that appear between tracked people.

## Features

### 🎯 Multi-Person Tracking
- Tracks up to 6 people simultaneously
- Real-time pose detection using MediaPipe
- Individual person identification and tracking
- Confidence-based filtering

### 🎨 Body Segmentation
- Real-time body segmentation for each person
- Color-coded segmentation masks
- Toggle segmentation on/off
- Overlay visualization

### 🎪 3D Objects Between People
- **Individual 3D Objects**: Spheres, cubes, pyramids, torus, icosahedrons
- **Connection Types**:
  - Simple lines
  - Energy beams
  - Animated particles
  - Holographic connections
  - Energy fields
- Dynamic positioning based on person locations
- Animated effects and color changes

### 🎛️ Interactive Controls
- **Detection Settings**: Max people, confidence thresholds
- **Visual Options**: Skeleton overlay, 3D objects, segmentation
- **3D Object Customization**: Type, size, connection type
- **Real-time Stats**: FPS, person count, individual confidence

## How to Use

1. **Open the HTML file** in a modern web browser
2. **Allow camera access** when prompted
3. **Click "Start Detection"** to begin tracking
4. **Adjust settings** using the control panel
5. **Experiment with different connection types** and 3D objects

## Technical Requirements

- Modern web browser with WebGL support
- Camera access permissions
- MediaPipe pose landmarker models (included in `/pose/` directory)
- Three.js library (included in `/build/` directory)

## Performance Tips

- Lower the max people count for better performance
- Disable segmentation if not needed
- Use simpler connection types for better FPS
- Adjust confidence thresholds to balance accuracy vs performance

## Connection Types Explained

1. **Line**: Simple colored lines between people
2. **Energy Beam**: Cylindrical beams with dynamic lighting
3. **Particles**: Animated particle streams with rainbow effects
4. **Holographic**: Multi-layered beams with color shifting
5. **Energy Field**: Single field encompassing all people
6. **None**: No connections (individual objects only)

## Troubleshooting

- **Camera not working**: Check browser permissions
- **Low FPS**: Reduce max people or disable some effects
- **Model loading errors**: Ensure pose models are in the correct directory
- **WebGL errors**: Try a different browser or update graphics drivers

## Browser Compatibility

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

Requires WebGL 2.0 support for optimal performance.
