#!/bin/bash

# Create mediapipe directory structure
mkdir -p mediapipe/pose

echo "Downloading MediaPipe Pose files..."

# Download from jsDelivr CDN
echo "Downloading from jsDelivr CDN..."

# Core files
curl -o mediapipe/pose/pose_solution_packed_assets.data "https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.5.1635988164/pose_solution_packed_assets.data"
curl -o mediapipe/pose/pose_solution_packed_assets.js "https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.5.1635988164/pose_solution_packed_assets.js"
curl -o mediapipe/pose/pose_solution_packed_assets.wasm "https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.5.1635988164/pose_solution_packed_assets.wasm"

# SIMD files
curl -o mediapipe/pose/pose_solution_simd_packed_assets.wasm "https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.5.1635988164/pose_solution_simd_packed_assets.wasm"
curl -o mediapipe/pose/pose_solution_simd_wasm_bin.js "https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.5.1635988164/pose_solution_simd_wasm_bin.js"
curl -o mediapipe/pose/pose_solution_simd_wasm_bin.wasm "https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.5.1635988164/pose_solution_simd_wasm_bin.wasm"

# Additional files that might be needed
curl -o mediapipe/pose/pose_solution_packed_assets_loader.js "https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.5.1635988164/pose_solution_packed_assets_loader.js"

echo "Download complete!"
echo "Files downloaded to: mediapipe/pose/"
ls -la mediapipe/pose/
