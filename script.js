// Import Three.js for balloon rendering
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

// Import MediaPipe Tasks Vision
import {
  FilesetResolver,
  PoseLandmarker,
} from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.22-rc.20250304/vision_bundle.mjs";

class MultiPersonPoseTracker {
  constructor() {
    this.video = document.getElementById("video");
    this.canvas = document.getElementById("canvas");
    this.ctx = this.canvas.getContext("2d");
    this.threeCanvas = document.getElementById("three-canvas");

    // Set canvas size to fullscreen
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;

    // Ensure video element is ready
    if (!this.video) {
      console.error("Video element not found!");
      return;
    }

    // Pose detection properties
    this.poseLandmarker = null;
    this.isRunning = false;
    this.people = new Map();
    this.nextPersonId = 0;

    // 3D scene properties
    this.scene = null;
    this.camera3D = null;
    this.renderer = null;
    this.balloonMesh = null;
    this.balloonTarget = new THREE.Vector3();
    this.balloonPosition = new THREE.Vector3();
    this.balloonVelocity = new THREE.Vector3();

    // Balloon properties
    this.balloonSmoothing = 0.05; // Smoothing factor for balloon movement
    this.lastUpdateTime = 0;

    // Initialize control values first
    this.behindDistance = 2.5;
    this.heightOffset = 1.7; // Higher default height
    this.minScale = 0.1; // Much smaller minimum scale
    this.maxScale = 3.8;
    this.isTracking = false;

    // Smoothing and quality settings
    this.landmarkSmoothing = 0.8;
    this.positionSmoothing = 0.1;
    this.scaleSmoothing = 0.15;
    this.orientationSmoothing = 0.2;
    this.smoothedLandmarks = null;
    this.smoothedPosition = { x: 0, y: 0, z: 0 };
    this.smoothedScale = 1.0;
    this.smoothedOrientation = 0;

    // MediaPipe quality settings
    this.minDetectionConfidence = 0.5;
    this.minTrackingConfidence = 0.5;
    this.minPosePresence = 0.5;
    this.smoothLandmarks = true;
    this.enableSegmentation = false; // Enable segmentation for body mask
    this.selfieMode = false;

    // Camera settings
    this.cameraWidth = 1920;
    this.cameraHeight = 1080;
    this.cameraFPS = 30;

    // FPS tracking
    this.fps = 0;
    this.frameCount = 0;
    this.lastFpsTime = 0;

    // Segmentation disabled
    this.maskEnabled = false;
    this.showSkeletonDebug = true;

    // Red light controls
    this.redLightIntensity = 20.0;
    this.redLight2Intensity = 15.0;
    this.redLight3Intensity = 10.0;

    // LUT (Look-Up Table) controls
    this.lutEnabled = false;
    this.lutIntensity = 1.0;
    this.lutType = "vintage";
    this.lutCanvas = null;
    this.lutCtx = null;
    this.videoTexture = null;
    this.videoMaterial = null;
    this.videoMesh = null;
  }

  initLUT() {
    // Create LUT canvas for color grading
    this.lutCanvas = document.createElement("canvas");
    this.lutCanvas.width = this.canvas.width;
    this.lutCanvas.height = this.canvas.height;
    this.lutCtx = this.lutCanvas.getContext("2d");

    // Create Three.js video texture
    this.videoTexture = new THREE.VideoTexture(this.video);
    this.videoTexture.minFilter = THREE.LinearFilter;
    this.videoTexture.magFilter = THREE.LinearFilter;
    this.videoTexture.format = THREE.RGBAFormat;

    // Create material with video texture
    this.videoMaterial = new THREE.MeshBasicMaterial({
      map: this.videoTexture,
      transparent: true,
      opacity: 1.0,
    });

    // Create plane geometry for video (will be resized to match video aspect ratio)
    const videoGeometry = new THREE.PlaneGeometry(2, 2);
    this.videoMesh = new THREE.Mesh(videoGeometry, this.videoMaterial);
    this.videoMesh.position.z = -1; // Behind everything else
    this.videoMesh.visible = false; // Start hidden
    this.scene.add(this.videoMesh);

    // Update video mesh size to match video aspect ratio
    this.updateVideoMeshSize();

    console.log("LUT initialized with Three.js video texture");
  }

  applyLUT() {
    if (!this.lutEnabled || !this.video) return;

    // Apply CSS filters directly to video element
    let filterString = "";

    switch (this.lutType) {
      case "vintage":
        filterString = `sepia(${this.lutIntensity * 0.8}) saturate(${1 + this.lutIntensity * 0.5}) hue-rotate(${
          this.lutIntensity * 20
        }deg) contrast(${1 + this.lutIntensity * 0.2})`;
        break;
      case "dramatic":
        filterString = `contrast(${1 + this.lutIntensity * 0.5}) brightness(${1 + this.lutIntensity * 0.2}) saturate(${
          1 + this.lutIntensity * 0.3
        })`;
        break;
      case "cool":
        filterString = `hue-rotate(${this.lutIntensity * -30}deg) saturate(${1 + this.lutIntensity * 0.3}) brightness(${
          1 + this.lutIntensity * 0.1
        })`;
        break;
      case "warm":
        filterString = `hue-rotate(${this.lutIntensity * 20}deg) saturate(${1 + this.lutIntensity * 0.4}) brightness(${
          1 + this.lutIntensity * 0.15
        })`;
        break;
      case "monochrome":
        filterString = `grayscale(${this.lutIntensity}) contrast(${1 + this.lutIntensity * 0.2})`;
        break;
      case "sepia":
        filterString = `sepia(${this.lutIntensity}) contrast(${1 + this.lutIntensity * 0.1}) brightness(${1 + this.lutIntensity * 0.05})`;
        break;
    }

    // Apply filter to video element
    this.video.style.filter = filterString;
  }

  updateLUTUniforms() {
    // Apply LUT immediately when settings change
    if (this.lutEnabled) {
      this.applyLUT();
    } else {
      // Clear filters when disabled
      this.video.style.filter = "";
    }
  }

  updateVideoMeshSize() {
    if (!this.videoMesh || !this.video || this.video.videoWidth === 0 || this.video.videoHeight === 0) return;

    // Calculate video aspect ratio
    const videoAspect = this.video.videoWidth / this.video.videoHeight;
    const canvasAspect = this.canvas.width / this.canvas.height;

    let scaleX, scaleY;

    if (canvasAspect > videoAspect) {
      // Canvas is wider than video - letterbox
      scaleY = 2; // Full height
      scaleX = 2 * videoAspect; // Scale width to maintain aspect ratio
    } else {
      // Canvas is taller than video - pillarbox
      scaleX = 2; // Full width
      scaleY = 2 / videoAspect; // Scale height to maintain aspect ratio
    }

    // Update the video mesh scale
    this.videoMesh.scale.set(scaleX, scaleY, 1);

    console.log("Video mesh resized:", scaleX, "x", scaleY, "aspect:", videoAspect);
  }

  initGUI() {
    // Check if dat.GUI is available
    if (typeof dat === "undefined") {
      console.error("dat.GUI not loaded");
      return;
    }

    // GUI controls
    this.gui = new dat.GUI();
    this.gui.domElement.style.position = "absolute";
    this.gui.domElement.style.top = "10px";
    this.gui.domElement.style.right = "10px";
    this.gui.domElement.style.zIndex = "1000";

    // Balloon controls
    const balloonFolder = this.gui.addFolder("Balloon");
    balloonFolder.add(this, "balloonSmoothing", 0.01, 0.2).name("Smoothing");
    balloonFolder.add(this, "behindDistance", 0.5, 5.0).name("Behind Distance");
    balloonFolder.add(this, "heightOffset", -2.0, 3.0).name("Height Offset");
    balloonFolder.add(this, "minScale", 0.1, 2.0).name("Min Scale");
    balloonFolder.add(this, "maxScale", 0.5, 5.0).name("Max Scale");
    balloonFolder
      .add(this, "redLightIntensity", 0.0, 30.0)
      .name("Red Light 1")
      .onChange((value) => {
        if (this.redLight) this.redLight.intensity = value;
      });
    balloonFolder
      .add(this, "redLight2Intensity", 0.0, 30.0)
      .name("Red Light 2")
      .onChange((value) => {
        if (this.redLight2) this.redLight2.intensity = value;
      });
    balloonFolder
      .add(this, "redLight3Intensity", 0.0, 30.0)
      .name("Red Light 3")
      .onChange((value) => {
        if (this.redLight3) this.redLight3.intensity = value;
      });
    balloonFolder.open();

    // LUT controls
    const lutFolder = this.gui.addFolder("Color Grading (LUT)");
    lutFolder
      .add(this, "lutEnabled", false)
      .name("Enable LUT")
      .onChange(() => {
        this.updateLUTUniforms();
      });
    lutFolder
      .add(this, "lutType", ["vintage", "dramatic", "cool", "warm", "monochrome", "sepia"])
      .name("LUT Type")
      .onChange(() => {
        this.updateLUTUniforms();
      });
    lutFolder
      .add(this, "lutIntensity", 0.0, 2.0)
      .name("LUT Intensity")
      .onChange(() => {
        this.updateLUTUniforms();
      });
    lutFolder.open();

    // Tracking controls
    const trackingFolder = this.gui.addFolder("Tracking");
    trackingFolder
      .add(this, "isTracking")
      .name("Start/Stop Tracking")
      .onChange((value) => {
        if (value) {
          this.start();
        } else {
          this.stop();
        }
      });
    trackingFolder.add(this, "showSkeletonDebug", true).name("Show Skeleton Debug");
    trackingFolder.open();

    // Smoothing controls
    const smoothingFolder = this.gui.addFolder("Smoothing");
    smoothingFolder.add(this, "landmarkSmoothing", 0.1, 1.0).name("Landmark Smoothing");
    smoothingFolder.add(this, "positionSmoothing", 0.01, 0.5).name("Position Smoothing");
    smoothingFolder.add(this, "scaleSmoothing", 0.01, 0.5).name("Scale Smoothing");
    smoothingFolder.add(this, "orientationSmoothing", 0.01, 0.5).name("Orientation Smoothing");
    smoothingFolder.open();

    // Quality controls
    const qualityFolder = this.gui.addFolder("Quality");
    const detectionConfidenceControl = qualityFolder.add(this, "minDetectionConfidence", 0.1, 1.0).name("Detection Confidence");
    const trackingConfidenceControl = qualityFolder.add(this, "minTrackingConfidence", 0.1, 1.0).name("Tracking Confidence");
    const posePresenceControl = qualityFolder.add(this, "minPosePresence", 0.1, 1.0).name("Pose Presence");
    const smoothLandmarksControl = qualityFolder.add(this, "smoothLandmarks", true).name("Smooth Landmarks");
    const selfieModeControl = qualityFolder.add(this, "selfieMode", false).name("Selfie Mode");

    // Add change listeners to update MediaPipe settings
    detectionConfidenceControl.onChange(() => this.updateMediaPipeSettings());
    trackingConfidenceControl.onChange(() => this.updateMediaPipeSettings());
    posePresenceControl.onChange(() => this.updateMediaPipeSettings());
    smoothLandmarksControl.onChange(() => this.updateMediaPipeSettings());
    selfieModeControl.onChange(() => this.updateMediaPipeSettings());

    qualityFolder.open();

    // Camera controls
    const cameraFolder = this.gui.addFolder("Camera");
    const cameraWidthControl = cameraFolder.add(this, "cameraWidth", 640, 1920).name("Width");
    const cameraHeightControl = cameraFolder.add(this, "cameraHeight", 480, 1080).name("Height");
    const cameraFPSControl = cameraFolder.add(this, "cameraFPS", 15, 60).name("FPS");

    // Note: Camera settings require restart to take effect

    cameraFolder.open();
  }

  initThreeJS() {
    // Create Three.js scene
    this.scene = new THREE.Scene();
    this.scene.background = null; // Transparent background

    // Create camera
    this.camera3D = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    this.camera3D.position.set(0, 0, 5);

    // Create renderer
    this.renderer = new THREE.WebGLRenderer({
      canvas: this.threeCanvas,
      alpha: true,
      antialias: true,
      stencil: true, // Enable stencil buffer for masking
    });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.renderer.setClearColor(0x000000, 0); // Transparent background

    // Create lights
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
    this.scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 10, 5);
    directionalLight.castShadow = true;
    this.scene.add(directionalLight);

    // Add red light specifically for balloon illumination
    this.redLight = new THREE.PointLight(0xff4444, this.redLightIntensity, 30);
    this.redLight.position.set(0, 3, 0);
    this.redLight.castShadow = true;
    this.scene.add(this.redLight);

    // Add another red light from a different angle
    this.redLight2 = new THREE.PointLight(0xff6666, this.redLight2Intensity, 25);
    this.redLight2.position.set(-2, 2, 1);
    this.redLight2.castShadow = true;
    this.scene.add(this.redLight2);

    // Add a third red light for better coverage
    this.redLight3 = new THREE.PointLight(0xff8888, this.redLight3Intensity, 20);
    this.redLight3.position.set(2, 1, -1);
    this.redLight3.castShadow = true;
    this.scene.add(this.redLight3);

    // Load balloon GLB model
    this.loadBalloonModel();

    // String is included in the GLB model, no need to generate one

    // Start animation loop
    this.animate3D();

    // Initialize LUT
    this.initLUT();

    // Initialize GUI after everything is set up (with delay to ensure dat.GUI is loaded)
    setTimeout(() => this.initGUI(), 100);
  }

  loadBalloonModel() {
    const loader = new GLTFLoader();

    loader.load(
      "./Balloon.glb", // Path to your balloon model
      (gltf) => {
        // Get the balloon mesh from the loaded model
        this.balloonMesh = gltf.scene;

        // Scale the balloon to appropriate size
        this.balloonMesh.scale.setScalar(0.5);

        // Enable shadows
        this.balloonMesh.traverse((child) => {
          if (child.isMesh) {
            child.castShadow = true;
            child.receiveShadow = true;
          }
        });

        // Position and add to scene
        this.balloonMesh.visible = false; // Start hidden
        this.scene.add(this.balloonMesh);
      },
      (progress) => {},
      (error) => {
        console.error("Error loading balloon model:", error);
        // Fallback to sphere if GLB fails to load
        this.createFallbackBalloon();
      }
    );
  }

  createFallbackBalloon() {
    const balloonGeometry = new THREE.SphereGeometry(1.2, 32, 32);
    const balloonMaterial = new THREE.MeshPhongMaterial({
      color: 0xff0000,
      shininess: 100,
      specular: 0xffffff,
    });
    this.balloonMesh = new THREE.Mesh(balloonGeometry, balloonMaterial);
    this.balloonMesh.castShadow = true;
    this.balloonMesh.receiveShadow = true;
    this.balloonMesh.visible = false; // Start hidden
    this.scene.add(this.balloonMesh);
  }

  animate3D() {
    requestAnimationFrame(() => this.animate3D());
    this.renderer.render(this.scene, this.camera3D);
  }

  setupEventListeners() {
    // Manual start/stop control via dat.GUI

    // Handle window resize
    window.addEventListener("resize", () => {
      this.canvas.width = window.innerWidth;
      this.canvas.height = window.innerHeight;
      this.bodyMaskCanvas.width = window.innerWidth;
      this.bodyMaskCanvas.height = window.innerHeight;
      this.lutCanvas.width = window.innerWidth;
      this.lutCanvas.height = window.innerHeight;
      this.renderer.setSize(window.innerWidth, window.innerHeight);
      this.camera3D.aspect = window.innerWidth / window.innerHeight;
      this.camera3D.updateProjectionMatrix();

      // Update video mesh size on resize
      this.updateVideoMeshSize();
    });
  }

  async initializePose() {
    try {
      console.log("Initializing MediaPipe Tasks Vision...");

      // Create the vision tasks resolver
      const vision = await FilesetResolver.forVisionTasks("https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision/wasm");

      // Model configuration - use local model
      const modelType = "heavy"; // Options: "lite", "full", "heavy"
      const modelPath = `./pose/pose_landmarker_${modelType}.task`;

      // Create the pose landmarker
      this.poseLandmarker = await PoseLandmarker.createFromOptions(vision, {
        baseOptions: {
          modelAssetPath: modelPath,
          delegate: "GPU",
        },
        runningMode: "VIDEO",
        numPoses: 2,
        minDetectionConfidence: this.minDetectionConfidence,
        minTrackingConfidence: this.minTrackingConfidence,
        minPosePresence: this.minPosePresence,
        smoothLandmarks: this.smoothLandmarks,
        selfieMode: this.selfieMode,
      });

      // Using default pose options
    } catch (error) {
      console.error("Error initializing pose:", error);
      console.error("Pose initialization error:", error.message);
    }
  }

  // updatePoseOptions method removed - using default values

  async startCamera() {
    try {
      // Starting camera...

      if (!this.video) {
        throw new Error("Video element not found");
      }

      // Get camera access
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: this.cameraWidth },
          height: { ideal: this.cameraHeight },
          frameRate: { ideal: this.cameraFPS },
          facingMode: "user",
        },
      });
      this.video.srcObject = stream;

      // Wait for video to be ready
      await new Promise((resolve) => {
        this.video.onloadeddata = resolve;
      });

      // Verify video has valid dimensions
      if (this.video.videoWidth === 0 || this.video.videoHeight === 0) {
        throw new Error("Video dimensions are invalid");
      }

      // Update video mesh size now that video is ready
      this.updateVideoMeshSize();

      // Camera started
    } catch (error) {
      console.error("Error starting camera:", error);
      throw error;
    }
  }

  async start() {
    if (this.isRunning) return;

    try {
      // Ensure video is ready before starting detection
      if (!this.video || this.video.videoWidth === 0 || this.video.videoHeight === 0) {
        console.error("Video not ready, cannot start detection");
        return;
      }

      // Ensure MediaPipe is initialized
      if (!this.poseLandmarker) {
        console.error("MediaPipe not initialized, cannot start detection");
        return;
      }

      this.isRunning = true;
      this.isTracking = true;

      this.startFPS();
      this.detectPoses();
    } catch (error) {
      console.error("Error starting pose detection:", error);
    }
  }

  stop() {
    this.isRunning = false;
    this.isTracking = false;

    // Stop camera
    if (this.video.srcObject) {
      const tracks = this.video.srcObject.getTracks();
      tracks.forEach((track) => track.stop());
      this.video.srcObject = null;
    }

    this.people.clear();

    // Clear canvas
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // Hide balloon
    if (this.balloonMesh) {
      this.balloonMesh.visible = false;
    }
  }

  startFPS() {
    let lastTime = 0;
    let frameCount = 0;

    const updateFPS = (currentTime) => {
      frameCount++;
      if (currentTime - lastTime >= 1000) {
        const fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
        this.fps = fps;
        frameCount = 0;
        lastTime = currentTime;
      }
      if (this.isRunning) {
        requestAnimationFrame(updateFPS);
      }
    };

    requestAnimationFrame(updateFPS);
  }

  onPoseResults(results) {
    if (results.landmarks) {
      this.updatePeople(results);

      // Apply LUT to video element
      if (this.lutEnabled) {
        this.applyLUT();
      } else {
        // Remove all filters when LUT is disabled
        this.video.style.filter = "";
      }

      // Clear canvas before drawing skeleton
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

      // Draw skeletons on top of LUT background
      this.ctx.strokeStyle = "#00ff00";
      this.ctx.fillStyle = "#ff0000";
      this.ctx.lineWidth = 2;

      if (this.people.size > 0) {
        this.people.forEach((person, id) => {
          this.drawSkeleton(person.landmarks);
          this.updateBalloon(person.landmarks);
        });
      } else {
        if (results.landmarks && results.landmarks.length > 0) {
          this.drawSkeletonFromResults(results.landmarks[0]);
        } else {
          this.drawSkeletons();
        }
      }

      // UI removed - using dat.GUI instead
    }
  }

  updatePeople(results) {
    const minConfidence = 0.01; // Default confidence threshold
    const maxPeople = 4; // Default max people

    // MediaPipe Tasks Vision uses 'landmarks' property
    const landmarks = results.landmarks;

    if (!landmarks || landmarks.length === 0) {
      return;
    }

    // Process each detected pose
    landmarks.forEach((landmarkSet, index) => {
      if (landmarkSet && landmarkSet.length > 0) {
        // Calculate confidence for this pose
        const confidence = this.calculateAverageConfidence(landmarkSet);

        // Only add if confidence is above threshold and we haven't reached max people
        if (confidence >= minConfidence && this.people.size < maxPeople) {
          // Check if this person already exists (simple check)
          let personExists = false;
          this.people.forEach((existingPerson) => {
            if (existingPerson.landmarks && existingPerson.landmarks.length > 0) {
              const distance = Math.sqrt(
                Math.pow(existingPerson.landmarks[0].x - landmarkSet[0].x, 2) +
                  Math.pow(existingPerson.landmarks[0].y - landmarkSet[0].y, 2)
              );
              if (distance < 0.1) {
                // Update existing person
                existingPerson.landmarks = landmarkSet;
                existingPerson.confidence = confidence;
                existingPerson.lastSeen = Date.now();
                personExists = true;
              }
            }
          });

          if (!personExists) {
            // Add new person
            const personId = this.nextPersonId++;
            this.people.set(personId, {
              id: personId,
              landmarks: landmarkSet,
              confidence: confidence,
              lastSeen: Date.now(),
            });
          }
        }
      }
    });

    // Remove old people (not seen for 5 seconds)
    const now = Date.now();
    this.people.forEach((person, id) => {
      if (now - person.lastSeen > 5000) {
        this.people.delete(id);
      }
    });
  }

  calculateAverageConfidence(landmarks) {
    if (!landmarks || landmarks.length === 0) return 0;

    let totalConfidence = 0;
    let validLandmarks = 0;

    landmarks.forEach((landmark, index) => {
      let confidence = 1.0; // Default high confidence

      // Check if we have visibility, presence, or score data
      if (landmark.visibility !== undefined) {
        confidence = landmark.visibility;
      } else if (landmark.presence !== undefined) {
        confidence = landmark.presence;
      } else if (landmark.score !== undefined) {
        confidence = landmark.score;
      } else {
        // If no confidence data, calculate based on position
        // Landmarks closer to center of image are more likely to be accurate
        const centerX = 0.5;
        const centerY = 0.5;
        const distanceFromCenter = Math.sqrt(Math.pow(landmark.x - centerX, 2) + Math.pow(landmark.y - centerY, 2));
        // Closer to center = higher confidence, with some randomness
        confidence = Math.max(0.6, Math.min(0.95, 1.0 - distanceFromCenter + (Math.random() - 0.5) * 0.1));
      }

      totalConfidence += confidence;
      validLandmarks++;
    });

    const averageConfidence = validLandmarks > 0 ? totalConfidence / validLandmarks : 0.8;
    // Add small random variation to prevent identical confidence values
    const finalConfidence = averageConfidence + (Math.random() - 0.5) * 0.02;

    return Math.max(0, Math.min(1, finalConfidence));
  }

  drawSkeletons() {
    // This method can be used to draw all tracked people
    this.people.forEach((person) => {
      this.drawSkeleton(person.landmarks);
    });
  }

  drawSkeletonFromResults(landmarks) {
    this.drawSkeleton(landmarks);
    this.updateBalloon(landmarks);
  }

  drawSkeleton(landmarks) {
    if (!landmarks) return;

    // Skip drawing if skeleton debug is disabled
    if (!this.showSkeletonDebug) return;

    // Calculate video display area within canvas
    const canvasAspect = this.canvas.width / this.canvas.height;
    const videoAspect = this.video.videoWidth / this.video.videoHeight;

    let videoDisplayWidth, videoDisplayHeight, videoOffsetX, videoOffsetY;

    if (canvasAspect > videoAspect) {
      // Canvas is wider than video - letterboxing
      videoDisplayHeight = this.canvas.height;
      videoDisplayWidth = this.canvas.height * videoAspect;
      videoOffsetX = (this.canvas.width - videoDisplayWidth) / 2;
      videoOffsetY = 0;
    } else {
      // Canvas is taller than video - pillarboxing
      videoDisplayWidth = this.canvas.width;
      videoDisplayHeight = this.canvas.width / videoAspect;
      videoOffsetX = 0;
      videoOffsetY = (this.canvas.height - videoDisplayHeight) / 2;
    }

    const connections = [
      [11, 12],
      [11, 13],
      [13, 15],
      [15, 17],
      [15, 19],
      [15, 21],
      [17, 19],
      [12, 14],
      [14, 16],
      [16, 18],
      [16, 20],
      [16, 22],
      [18, 20],
      [11, 23],
      [12, 24],
      [23, 24],
      [23, 25],
      [24, 26],
      [25, 27],
      [26, 28],
      [27, 29],
      [28, 30],
      [29, 31],
      [30, 32],
      [31, 32],
    ];

    // Draw connections
    this.ctx.beginPath();
    let visibleConnections = 0;

    connections.forEach(([startIdx, endIdx]) => {
      const startPoint = landmarks[startIdx];
      const endPoint = landmarks[endIdx];

      if (
        startPoint &&
        endPoint &&
        (startPoint.visibility > 0.1 || startPoint.visibility === undefined) &&
        (endPoint.visibility > 0.1 || endPoint.visibility === undefined)
      ) {
        // Map connection points to video display area
        const startX = videoOffsetX + startPoint.x * videoDisplayWidth;
        const startY = videoOffsetY + startPoint.y * videoDisplayHeight;
        const endX = videoOffsetX + endPoint.x * videoDisplayWidth;
        const endY = videoOffsetY + endPoint.y * videoDisplayHeight;

        this.ctx.moveTo(startX, startY);
        this.ctx.lineTo(endX, endY);
        visibleConnections++;
      }
    });

    this.ctx.stroke();

    // Draw landmarks
    this.ctx.fillStyle = "#ff0000";
    let visibleLandmarks = 0;

    landmarks.forEach((landmark, index) => {
      // Draw ALL landmarks regardless of visibility - just make them smaller if low confidence
      const visibility = landmark.visibility || 1.0; // Default to 1.0 if undefined
      const radius = visibility > 0.5 ? 4 : 2; // Smaller dots for low confidence

      this.ctx.beginPath();
      // Map landmark coordinates to video display area
      const x = videoOffsetX + landmark.x * videoDisplayWidth;
      const y = videoOffsetY + landmark.y * videoDisplayHeight;
      this.ctx.arc(x, y, radius, 0, 2 * Math.PI);
      this.ctx.fill();
      visibleLandmarks++;

      if (index < 5) {
      }
    });
  }

  // updateUI method removed - using dat.GUI instead

  detectPoses() {
    if (!this.isRunning || !this.poseLandmarker) return;

    const detectFrame = async () => {
      if (!this.isRunning) return;

      try {
        const results = this.poseLandmarker.detect(this.video);
        this.onPoseResults(results);
      } catch (error) {
        console.error("Error detecting poses:", error);
      }

      requestAnimationFrame(detectFrame);
    };

    detectFrame();
  }

  updateBalloon(landmarks) {
    if (!landmarks || landmarks.length === 0) return;

    // Find nose landmark (index 0)
    const nose = landmarks[0];
    if (nose && (nose.visibility > 0.1 || nose.visibility === undefined)) {
      const currentTime = performance.now();
      const deltaTime = currentTime - this.lastUpdateTime;
      this.lastUpdateTime = currentTime;

      // Convert 2D video coordinates to 3D world coordinates
      // Use actual video dimensions, not display dimensions
      const videoWidth = this.video.videoWidth;
      const videoHeight = this.video.videoHeight;
      const videoX = nose.x * videoWidth;
      const videoY = nose.y * videoHeight;

      // Convert to 3D coordinates (center origin, scale appropriately)
      const rawHeadX = (videoX - videoWidth / 2) / 100; // Center and scale
      const rawHeadY = -(videoY - videoHeight / 2) / 100; // Flip Y and center
      const rawHeadZ = 0; // Keep on the same Z plane

      // Apply smoothing to position
      const headX = this.smoothedPosition.x + (rawHeadX - this.smoothedPosition.x) * this.positionSmoothing;
      const headY = this.smoothedPosition.y + (rawHeadY - this.smoothedPosition.y) * this.positionSmoothing;
      const headZ = this.smoothedPosition.z + (rawHeadZ - this.smoothedPosition.z) * this.positionSmoothing;

      // Update smoothed position
      this.smoothedPosition.x = headX;
      this.smoothedPosition.y = headY;
      this.smoothedPosition.z = headZ;

      // Calculate body orientation and distance for positioning
      let behindOffsetX = 0;
      let behindOffsetZ = -2.0; // Further back by default
      let balloonScale = 1.0;

      // Use multiple body measurements for better distance estimation
      // Method 1: Head-to-hip distance (more stable than shoulders)
      const leftHip = landmarks[23];
      const rightHip = landmarks[24];

      // Method 2: Overall body size using multiple key points
      const leftEar = landmarks[7];
      const rightEar = landmarks[8];
      const leftShoulder = landmarks[11];
      const rightShoulder = landmarks[12];
      const leftAnkle = landmarks[27];
      const rightAnkle = landmarks[28];

      let bodySize = 0;
      let bodyOrientation = 0;

      // Calculate body size using head-to-hip distance (most stable)
      if (nose && leftHip && rightHip) {
        const hipCenterX = (leftHip.x + rightHip.x) / 2;
        const hipCenterY = (leftHip.y + rightHip.y) / 2;
        bodySize = Math.sqrt(Math.pow(nose.x - hipCenterX, 2) + Math.pow(nose.y - hipCenterY, 2));

        // Calculate orientation from head-to-hip line
        bodyOrientation = Math.atan2(hipCenterY - nose.y, hipCenterX - nose.x);
      }

      // Fallback: Use ear-to-ear distance if available
      if (bodySize === 0 && leftEar && rightEar) {
        bodySize = Math.sqrt(Math.pow(rightEar.x - leftEar.x, 2) + Math.pow(rightEar.y - leftEar.y, 2));
      }

      // Fallback: Use shoulder distance as last resort
      if (bodySize === 0 && leftShoulder && rightShoulder) {
        bodySize = Math.sqrt(Math.pow(rightShoulder.x - leftShoulder.x, 2) + Math.pow(rightShoulder.y - leftShoulder.y, 2));
        bodyOrientation = Math.atan2(rightShoulder.y - leftShoulder.y, rightShoulder.x - leftShoulder.x);
      }

      // Enhanced orientation detection using multiple methods
      let detectedOrientation = bodyOrientation;
      let orientationMethod = "head-to-hip";

      // Method 1: Use shoulder line for orientation (when visible and not overlapping)
      if (
        leftShoulder &&
        rightShoulder &&
        (leftShoulder.visibility > 0.1 || leftShoulder.visibility === undefined) &&
        (rightShoulder.visibility > 0.1 || rightShoulder.visibility === undefined)
      ) {
        const shoulderOrientation = Math.atan2(rightShoulder.y - leftShoulder.y, rightShoulder.x - leftShoulder.x);

        // Check if shoulders are more reliable (not overlapping due to rotation)
        const shoulderDistance = Math.sqrt(Math.pow(rightShoulder.x - leftShoulder.x, 2) + Math.pow(rightShoulder.y - leftShoulder.y, 2));

        // If shoulders are far enough apart, use them for orientation
        if (shoulderDistance > 0.05) {
          detectedOrientation = shoulderOrientation;
          orientationMethod = "shoulders";
        }
      }

      // Method 2: Use ear line for orientation (more stable than shoulders)
      if (leftEar && rightEar && orientationMethod === "head-to-hip") {
        const earOrientation = Math.atan2(rightEar.y - leftEar.y, rightEar.x - leftEar.x);
        detectedOrientation = earOrientation;
        orientationMethod = "ears";
      }

      // Method 3: Use hip line for orientation (very stable)
      if (leftHip && rightHip && orientationMethod === "head-to-hip") {
        const hipOrientation = Math.atan2(rightHip.y - leftHip.y, rightHip.x - leftHip.x);
        detectedOrientation = hipOrientation;
        orientationMethod = "hips";
      }

      // Method 4: Use ankle line for orientation (most stable, but may not always be visible)
      if (leftAnkle && rightAnkle && orientationMethod === "head-to-hip") {
        const ankleOrientation = Math.atan2(rightAnkle.y - leftAnkle.y, rightAnkle.x - leftAnkle.x);
        detectedOrientation = ankleOrientation;
        orientationMethod = "ankles";
      }

      if (bodySize > 0) {
        // Map body size to balloon scale
        // Typical body sizes: 0.1 (far) to 0.4 (close)
        const minSize = 0.08; // Far away
        const maxSize = 0.35; // Close up
        const minScale = this.minScale; // Use GUI control
        const maxScale = this.maxScale; // Use GUI control

        // Linear interpolation between min and max
        const normalizedSize = Math.max(minSize, Math.min(maxSize, bodySize));
        const rawBalloonScale = minScale + (maxScale - minScale) * ((normalizedSize - minSize) / (maxSize - minSize));

        // Apply smoothing to scale
        balloonScale = this.smoothedScale + (rawBalloonScale - this.smoothedScale) * this.scaleSmoothing;
        this.smoothedScale = balloonScale;

        // Apply smoothing to orientation
        const smoothedOrientation = this.smoothedOrientation + (detectedOrientation - this.smoothedOrientation) * this.orientationSmoothing;
        this.smoothedOrientation = smoothedOrientation;

        // Simple approach: position balloon behind based on head position
        // Use a fixed "behind" direction that's more predictable
        // Behind means: opposite of head X position, and further back in Z
        behindOffsetX = -headX * 0.5; // Move opposite to head X, but not as far
        behindOffsetZ = -this.behindDistance - 1.5; // Always move back in Z
      } else {
        // Use a default scale based on head position
        const headDistance = Math.sqrt(headX * headX + headY * headY);
        balloonScale = Math.max(0.5, Math.min(1.5, 1.0 / (headDistance + 0.5)));
      }

      // Set target position (above and behind based on body orientation)
      this.balloonTarget.x = headX + behindOffsetX;
      this.balloonTarget.y = headY + this.heightOffset + 1.0; // Balloon height (not affected by string length)
      this.balloonTarget.z = headZ + behindOffsetZ;

      // Apply balloon scale
      this.balloonMesh.scale.setScalar(balloonScale);

      // Smooth balloon movement with physics
      this.updateBalloonPhysics(deltaTime);

      // Update 3D balloon position and scale
      this.balloonMesh.position.copy(this.balloonPosition);
      this.balloonMesh.visible = true;
    }
  }

  updateBalloonPhysics(deltaTime) {
    // Simple smooth interpolation to target position
    const smoothing = this.balloonSmoothing * (deltaTime / 16.67); // Normalize to 60fps
    this.balloonPosition.x += (this.balloonTarget.x - this.balloonPosition.x) * smoothing;
    this.balloonPosition.y += (this.balloonTarget.y - this.balloonPosition.y) * smoothing;
    this.balloonPosition.z += (this.balloonTarget.z - this.balloonPosition.z) * smoothing;
  }

  // updateUI method removed - using dat.GUI instead

  detectPoses() {
    if (!this.isRunning || !this.poseLandmarker) return;

    let errorCount = 0;
    const maxErrors = 5;

    const detectFrame = async () => {
      if (!this.isRunning) return;

      // Check if video has valid dimensions before processing
      if (!this.video || this.video.videoWidth === 0 || this.video.videoHeight === 0) {
        requestAnimationFrame(detectFrame);
        return;
      }

      try {
        // For VIDEO mode, we need to use detectForVideo with a timestamp
        const timestamp = performance.now();
        const results = this.poseLandmarker.detectForVideo(this.video, timestamp);
        this.onPoseResults(results);
        errorCount = 0; // Reset error count on success
      } catch (error) {
        errorCount++;

        // Stop detection on persistent errors to prevent console spam
        if (error.message.includes("ROI width and height must be > 0") || errorCount >= maxErrors) {
          console.error("Too many errors, stopping detection");
          this.stop();
          return;
        }

        // Add delay before retrying
        setTimeout(() => {
          if (this.isRunning) {
            requestAnimationFrame(detectFrame);
          }
        }, 100);
        return;
      }

      requestAnimationFrame(detectFrame);
    };

    detectFrame();
  }

  updateMediaPipeSettings() {
    if (!this.poseLandmarker) return;

    try {
      // Update MediaPipe settings in real-time
      this.poseLandmarker.setOptions({
        minDetectionConfidence: this.minDetectionConfidence,
        minTrackingConfidence: this.minTrackingConfidence,
        minPosePresence: this.minPosePresence,
        smoothLandmarks: this.smoothLandmarks,
        selfieMode: this.selfieMode,
      });
    } catch (error) {
      console.error("Error updating MediaPipe settings:", error);
    }
  }
}

// Initialize the application
let tracker;

document.addEventListener("DOMContentLoaded", async () => {
  try {
    console.log("Initializing Multi-Person Pose Tracker...");

    tracker = new MultiPersonPoseTracker();
    tracker.setupEventListeners();
    await tracker.startCamera();
    await tracker.initializePose();
    tracker.initThreeJS();

    console.log("Application initialized successfully");
  } catch (error) {
    console.error("Error initializing application:", error);
  }
});
