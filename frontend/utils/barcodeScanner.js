/**
 * Barcode Scanner
 * Camera-based barcode/QR code scanner for patient ID integration
 */

// Check browser support
export function isScannerSupported() {
  return 'BarcodeDetector' in window || 
         ('mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices);
}

// Check if BarcodeDetector API is available
export function isBarcodeDetectorSupported() {
  return 'BarcodeDetector' in window;
}

// Get supported barcode formats
export async function getSupportedFormats() {
  if (!isBarcodeDetectorSupported()) {
    // Fallback formats that can be detected with libraries
    return ['qr_code', 'code_128', 'code_39', 'ean_13', 'upc_a'];
  }
  
  try {
    const formats = await window.BarcodeDetector.getSupportedFormats();
    return formats;
  } catch (error) {
    console.error('[Scanner] Failed to get supported formats:', error);
    return [];
  }
}

// Create barcode detector
export async function createBarcodeDetector(formats = ['qr_code', 'code_128', 'ean_13']) {
  if (!isBarcodeDetectorSupported()) {
    console.warn('[Scanner] BarcodeDetector API not supported');
    return null;
  }
  
  try {
    const detector = new window.BarcodeDetector({ formats });
    return detector;
  } catch (error) {
    console.error('[Scanner] Failed to create detector:', error);
    return null;
  }
}

// Request camera permission
export async function requestCameraPermission() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ 
      video: { facingMode: 'environment' } 
    });
    stream.getTracks().forEach(track => track.stop());
    return { granted: true };
  } catch (error) {
    console.error('[Scanner] Camera permission denied:', error);
    return {
      granted: false,
      error: error.name,
      message: getCameraErrorMessage(error.name)
    };
  }
}

// Get camera error message
function getCameraErrorMessage(errorName) {
  const messages = {
    'NotAllowedError': 'Camera permission denied. Please allow access in settings.',
    'NotFoundError': 'No camera found on this device.',
    'NotReadableError': 'Camera is already in use by another application.',
    'OverconstrainedError': 'No camera matches the requested constraints.',
    'SecurityError': 'Camera access blocked due to security settings.'
  };
  
  return messages[errorName] || 'Failed to access camera.';
}

// Get available cameras
export async function getAvailableCameras() {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    return devices.filter(device => device.kind === 'videoinput');
  } catch (error) {
    console.error('[Scanner] Failed to enumerate devices:', error);
    return [];
  }
}

// Start camera stream
export async function startCameraStream(videoElement, options = {}) {
  try {
    const constraints = {
      video: {
        facingMode: options.facingMode || 'environment',
        width: options.width || { ideal: 1280 },
        height: options.height || { ideal: 720 }
      }
    };
    
    if (options.deviceId) {
      constraints.video.deviceId = { exact: options.deviceId };
    }
    
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    videoElement.srcObject = stream;
    await videoElement.play();
    
    return { success: true, stream };
  } catch (error) {
    console.error('[Scanner] Failed to start camera:', error);
    return {
      success: false,
      error: error.name,
      message: getCameraErrorMessage(error.name)
    };
  }
}

// Stop camera stream
export function stopCameraStream(videoElement) {
  if (videoElement && videoElement.srcObject) {
    videoElement.srcObject.getTracks().forEach(track => track.stop());
    videoElement.srcObject = null;
  }
}

// Scan barcode from video stream
export async function scanFromVideo(detector, videoElement) {
  if (!detector || !videoElement) {
    return { success: false, error: 'Invalid detector or video element' };
  }
  
  try {
    const barcodes = await detector.detect(videoElement);
    
    if (barcodes.length === 0) {
      return { success: false, found: false };
    }
    
    return {
      success: true,
      found: true,
      barcodes: barcodes.map(barcode => ({
        rawValue: barcode.rawValue,
        format: barcode.format,
        boundingBox: barcode.boundingBox,
        cornerPoints: barcode.cornerPoints
      }))
    };
  } catch (error) {
    console.error('[Scanner] Detection error:', error);
    return { success: false, error: error.message };
  }
}

// Scan barcode from image file
export async function scanFromImage(detector, imageFile) {
  if (!detector) {
    return { success: false, error: 'Invalid detector' };
  }
  
  try {
    const image = await createImageBitmap(imageFile);
    const barcodes = await detector.detect(image);
    
    if (barcodes.length === 0) {
      return { success: false, found: false };
    }
    
    return {
      success: true,
      found: true,
      barcodes: barcodes.map(barcode => ({
        rawValue: barcode.rawValue,
        format: barcode.format
      }))
    };
  } catch (error) {
    console.error('[Scanner] Image scan error:', error);
    return { success: false, error: error.message };
  }
}

// Continuous scanning with callback
export function startContinuousScanning(detector, videoElement, callback, options = {}) {
  const interval = options.interval || 300; // ms between scans
  let isScanning = true;
  let scanCount = 0;
  let lastResult = null;
  
  const scan = async () => {
    if (!isScanning) return;
    
    const result = await scanFromVideo(detector, videoElement);
    
    if (result.success && result.found) {
      const newResult = result.barcodes[0].rawValue;
      
      // Only callback if different from last result (debounce)
      if (newResult !== lastResult) {
        lastResult = newResult;
        scanCount++;
        callback({
          ...result,
          scanCount
        });
      }
    }
    
    setTimeout(scan, interval);
  };
  
  scan();
  
  return {
    stop: () => {
      isScanning = false;
    },
    getScanCount: () => scanCount
  };
}

// Parse patient ID from barcode
export function parsePatientID(barcodeValue, format) {
  // Remove common prefixes
  let patientId = barcodeValue.trim();
  
  // Remove 'P' or 'PT' prefix if present
  patientId = patientId.replace(/^(P|PT)[-:]?/i, '');
  
  // For QR codes, try to extract from JSON
  if (format === 'qr_code') {
    try {
      const data = JSON.parse(barcodeValue);
      return {
        patientId: data.patientId || data.id || data.mrn || barcodeValue,
        additionalData: data
      };
    } catch (error) {
      // Not JSON, use as-is
    }
  }
  
  return {
    patientId,
    format,
    raw: barcodeValue
  };
}

// Validate patient ID format
export function validatePatientID(patientId) {
  // Basic validation - adjust based on your ID format
  const cleaned = patientId.trim();
  
  if (cleaned.length === 0) {
    return { valid: false, error: 'Patient ID cannot be empty' };
  }
  
  if (cleaned.length < 3) {
    return { valid: false, error: 'Patient ID too short' };
  }
  
  if (cleaned.length > 20) {
    return { valid: false, error: 'Patient ID too long' };
  }
  
  // Check for invalid characters (alphanumeric and hyphens only)
  if (!/^[A-Za-z0-9-]+$/.test(cleaned)) {
    return { valid: false, error: 'Patient ID contains invalid characters' };
  }
  
  return { valid: true, patientId: cleaned };
}

// Generate QR code for patient ID (for testing)
export async function generatePatientQRCode(patientId, additionalData = {}) {
  const data = {
    patientId,
    ...additionalData,
    timestamp: Date.now(),
    source: 'RealDiag'
  };
  
  return JSON.stringify(data);
}

// Draw detection overlay on canvas
export function drawDetectionOverlay(canvas, barcode) {
  const ctx = canvas.getContext('2d');
  
  // Draw bounding box
  if (barcode.boundingBox) {
    ctx.strokeStyle = '#00ff00';
    ctx.lineWidth = 3;
    ctx.strokeRect(
      barcode.boundingBox.x,
      barcode.boundingBox.y,
      barcode.boundingBox.width,
      barcode.boundingBox.height
    );
  }
  
  // Draw corner points
  if (barcode.cornerPoints && barcode.cornerPoints.length === 4) {
    ctx.fillStyle = '#00ff00';
    barcode.cornerPoints.forEach(point => {
      ctx.beginPath();
      ctx.arc(point.x, point.y, 5, 0, 2 * Math.PI);
      ctx.fill();
    });
    
    // Draw connecting lines
    ctx.strokeStyle = '#00ff00';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(barcode.cornerPoints[0].x, barcode.cornerPoints[0].y);
    for (let i = 1; i < barcode.cornerPoints.length; i++) {
      ctx.lineTo(barcode.cornerPoints[i].x, barcode.cornerPoints[i].y);
    }
    ctx.closePath();
    ctx.stroke();
  }
  
  // Draw label
  if (barcode.rawValue) {
    ctx.fillStyle = '#00ff00';
    ctx.font = '16px Arial';
    const textY = barcode.boundingBox ? 
      barcode.boundingBox.y - 10 : 
      canvas.height / 2;
    ctx.fillText(barcode.rawValue, 10, textY);
  }
}

export default {
  isScannerSupported,
  isBarcodeDetectorSupported,
  getSupportedFormats,
  createBarcodeDetector,
  requestCameraPermission,
  getAvailableCameras,
  startCameraStream,
  stopCameraStream,
  scanFromVideo,
  scanFromImage,
  startContinuousScanning,
  parsePatientID,
  validatePatientID,
  generatePatientQRCode,
  drawDetectionOverlay
};
