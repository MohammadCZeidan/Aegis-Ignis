import { useState, useEffect, useRef } from 'react';
import { Camera, Check, X, Loader2, LogOut, Users, MapPin, AlertCircle, CheckCircle, ArrowLeft, ArrowRight, ArrowUp, ArrowDown, ZoomIn, ZoomOut } from 'lucide-react';
import { API_BASE_URL } from '../services/api';

interface FaceRegistrationProps {
  onLogout: () => void;
}

interface FaceDetectionResult {
  success: boolean;
  faces_detected: number;
  faces: Array<{
    bbox: [number, number, number, number];
    confidence: number;
    embedding?: number[];
  }>;
  ideal_head_position?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

const DEPARTMENTS = [
  'Engineering',
  'HR',
  'Sales',
  'Marketing',
  'Finance',
  'Operations',
  'IT',
  'Security'
];

export function FaceRegistration({ onLogout }: FaceRegistrationProps) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [employeeId, setEmployeeId] = useState('');
  const [department, setDepartment] = useState('');
  const [capturedImage, setCapturedImage] = useState<Blob | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [cameraReady, setCameraReady] = useState(false);
  const [positioningMessage, setPositioningMessage] = useState('Position your face in the circle');
  const [positioningStatus, setPositioningStatus] = useState<'good' | 'warning' | 'error'>('warning');
  const [captureEnabled, setCaptureEnabled] = useState(false);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const overlayCanvasRef = useRef<HTMLCanvasElement>(null);
  const detectionIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    initCamera();
    fetchNextEmployeeId();
    return () => {
      stopCamera();
    };
  }, []);

  const fetchNextEmployeeId = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/employees/next-id`);
      if (response.ok) {
        const data = await response.json();
        setEmployeeId(data.next_id);
      }
    } catch (err) {
      console.error('Failed to fetch next employee ID:', err);
      // Default to EMP001 if fetch fails
      setEmployeeId('EMP001');
    }
  };

  const initCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 }
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          if (canvasRef.current && overlayCanvasRef.current && videoRef.current) {
            // Capture canvas matches video stream size
            canvasRef.current.width = videoRef.current.videoWidth;
            canvasRef.current.height = videoRef.current.videoHeight;
            
            // Overlay canvas matches the DISPLAYED size (may be scaled by CSS)
            const updateOverlaySize = () => {
              if (overlayCanvasRef.current && videoRef.current) {
                const rect = videoRef.current.getBoundingClientRect();
                overlayCanvasRef.current.width = rect.width;
                overlayCanvasRef.current.height = rect.height;
                console.log('🎥 Canvas sizes updated:', {
                  videoStream: { w: videoRef.current.videoWidth, h: videoRef.current.videoHeight },
                  displaySize: { w: rect.width, h: rect.height },
                  overlay: { w: overlayCanvasRef.current.width, h: overlayCanvasRef.current.height }
                });
              }
            };
            
            // Wait for layout to settle, then update sizes
            setTimeout(updateOverlaySize, 100);
            window.addEventListener('resize', updateOverlaySize);
            
            startFaceDetection();
          }
        };
      }
      
      setCameraReady(true);
    } catch (err) {
      console.error('Camera error:', err);
      setError('Failed to access camera. Please allow camera permission.');
    }
  };

  const stopCamera = () => {
    if (videoRef.current?.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
    }
    if (detectionIntervalRef.current) {
      clearInterval(detectionIntervalRef.current);
    }
  };

  const startFaceDetection = () => {
    if (detectionIntervalRef.current) {
      clearInterval(detectionIntervalRef.current);
    }

    detectionIntervalRef.current = setInterval(async () => {
      if (!videoRef.current || !canvasRef.current || !overlayCanvasRef.current) return;
      if (videoRef.current.paused || videoRef.current.ended) return;

      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      ctx.drawImage(videoRef.current, 0, 0);

      canvas.toBlob(async (blob) => {
        if (!blob) return;

        try {
          const formData = new FormData();
          formData.append('file', blob);

          const FACE_SERVICE_URL = import.meta.env.VITE_FACE_SERVICE_URL || 'http://localhost:8001';
          const response = await fetch(`${FACE_SERVICE_URL}/detect-faces`, {
            method: 'POST',
            body: formData
          });

          if (response.ok) {
            const result: FaceDetectionResult = await response.json();
            drawFaceDetection(result);
          } else {
            console.error('Face detection failed:', response.status, response.statusText);
          }
        } catch (err) {
          console.error('Face detection error:', err);
        }
      }, 'image/jpeg', 0.7);
    }, 300);
  };

  const drawFaceDetection = (result: FaceDetectionResult) => {
    const canvas = overlayCanvasRef.current;
    const video = videoRef.current;
    if (!canvas || !video) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // DEBUG: Log what we're receiving
    console.log(' Face Detection Result:', {
      faces: result.faces_detected,
      canvasSize: { w: canvas.width, h: canvas.height },
      videoSize: { w: video.videoWidth, h: video.videoHeight },
      displaySize: { w: video.offsetWidth, h: video.offsetHeight },
      bbox: result.faces[0]?.bbox,
      idealHead: result.ideal_head_position
    });

    if (result.faces_detected === 0) {
      setPositioningMessage('No face detected - Move closer');
      setPositioningStatus('error');
      setCaptureEnabled(false);
    } else if (result.faces_detected > 1) {
      setPositioningMessage('Multiple faces detected - Only one person');
      setPositioningStatus('warning');
      setCaptureEnabled(false);
    } else {
      const face = result.faces[0];
      
      // CRITICAL: Scale coordinates from capture canvas to display canvas
      // The capture canvas is videoWidth x videoHeight (e.g., 640x480)
      // But the overlay canvas matches the video element's actual display size
      const scaleX = canvas.width / video.videoWidth;
      const scaleY = canvas.height / video.videoHeight;
      
      console.log(' Scale factors:', { scaleX, scaleY });
      
      const [x1Raw, y1Raw, x2Raw, y2Raw] = face.bbox;
      const x1 = x1Raw * scaleX;
      const y1 = y1Raw * scaleY;
      const x2 = x2Raw * scaleX;
      const y2 = y2Raw * scaleY;
      
      console.log(' Coordinates:', { 
        raw: [x1Raw, y1Raw, x2Raw, y2Raw],
        scaled: [x1, y1, x2, y2]
      });

      // Calculate face position relative to center
      const faceCenterX = (x1 + x2) / 2;
      const faceCenterY = (y1 + y2) / 2;
      const videoCenterX = canvas.width / 2;
      const videoCenterY = canvas.height / 2;

      const offsetX = faceCenterX - videoCenterX;
      const offsetY = faceCenterY - videoCenterY;
      const faceWidth = x2 - x1;

      // Draw the ideal head guide box (larger box that follows the head)
      if (result.ideal_head_position) {
        const headBox = result.ideal_head_position;
        const headX = headBox.x * scaleX;
        const headY = headBox.y * scaleY;
        const headWidth = headBox.width * scaleX;
        const headHeight = headBox.height * scaleY;
        
        console.log('Drawing guide box:', { headX, headY, headWidth, headHeight, scaleX, scaleY });
        
        // Draw guide box in bright cyan (thicker, more visible)
        ctx.strokeStyle = '#00ffff';
        ctx.lineWidth = 4;
        ctx.setLineDash([15, 8]);
        ctx.strokeRect(headX, headY, headWidth, headHeight);
        ctx.setLineDash([]);
        
        // Also draw a semi-transparent fill for better visibility
        ctx.fillStyle = 'rgba(0, 255, 255, 0.1)';
        ctx.fillRect(headX, headY, headWidth, headHeight);
      } else {
        console.warn('No ideal_head_position in response:', result);
      }

      // Draw ONE green box around detected face
      ctx.strokeStyle = '#00ff00';
      ctx.lineWidth = 4;
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

      // Provide positioning guidance
      if (Math.abs(offsetX) > 100) {
        if (offsetX > 0) {
          setPositioningMessage('Move LEFT');
        } else {
          setPositioningMessage('Move RIGHT');
        }
        setPositioningStatus('warning');
        setCaptureEnabled(false);
      } else if (Math.abs(offsetY) > 80) {
        if (offsetY > 0) {
          setPositioningMessage('Move UP');
        } else {
          setPositioningMessage('Move DOWN');
        }
        setPositioningStatus('warning');
        setCaptureEnabled(false);
      } else if (faceWidth < 150) {
        setPositioningMessage('Move CLOSER');
        setPositioningStatus('warning');
        setCaptureEnabled(false);
      } else if (faceWidth > 400) {
        setPositioningMessage('Move BACK');
        setPositioningStatus('warning');
        setCaptureEnabled(false);
      } else {
        setPositioningMessage('Perfect! Click Capture');
        setPositioningStatus('good');
        setCaptureEnabled(true);
      }
    }
  };

  const handleCapture = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    // Stop face detection
    if (detectionIntervalRef.current) {
      clearInterval(detectionIntervalRef.current);
      detectionIntervalRef.current = null;
    }

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.drawImage(videoRef.current, 0, 0);

    setLoading(true);
    setError('');
    setPositioningMessage('Checking for duplicates...');

    canvas.toBlob(async (blob) => {
      if (!blob) {
        setLoading(false);
        return;
      }

      // CHECK DUPLICATE IMMEDIATELY ON CAPTURE - Call Python service directly for speed
      try {
        const formData = new FormData();
        formData.append('file', blob, 'face.jpg');
        
        const FACE_SERVICE_URL = import.meta.env.VITE_FACE_SERVICE_URL || 'http://localhost:8001';
        const response = await fetch(`${FACE_SERVICE_URL}/check-face-duplicate`, {
          method: 'POST',
          body: formData
        });

        if (response.status === 400) {
          const errorData = await response.json();
          setError(errorData.detail);
          setLoading(false);
          startFaceDetection();
          return;
        }

        if (response.status === 503) {
          setError('Face Recognition Service Unavailable');
          setLoading(false);
          startFaceDetection();
          return;
        }

        if (!response.ok) {
          const errorData = await response.json();
          setError('Face Check Failed\n' + (errorData.detail || ''));
          setLoading(false);
          startFaceDetection();
          return;
        }

        const result = await response.json();
        
        // IF DUPLICATE FOUND - SHOW MESSAGE AND STOP
        if (result.is_duplicate) {
          const employeeName = result.matched_employee?.name || 'there';
          const employeeId = result.matched_employee?.employee_number || result.matched_employee?.id;
          const dept = result.matched_employee?.department || 'N/A';
          
          setError(
            `Already Registered!\n\n` +
            `Hi ${employeeName}! You're in the system.\n\n` +
            `Employee ID: ${employeeId}\n` +
            `Department: ${dept}\n\n` +
            `No need to register again!`
          );
          setLoading(false);
          startFaceDetection();
          return;
        }

        // NO DUPLICATE - PROCEED WITH CAPTURE
        setCapturedImage(blob);
        setPreviewUrl(URL.createObjectURL(blob));
        setPositioningMessage('Face verified - Fill the form');
        
        // Clear overlay
        const overlayCtx = overlayCanvasRef.current?.getContext('2d');
        if (overlayCtx && overlayCanvasRef.current) {
          overlayCtx.clearRect(0, 0, overlayCanvasRef.current.width, overlayCanvasRef.current.height);
        }
        
      } catch (err: any) {
        setError('Cannot check duplicates: ' + err.message);
        startFaceDetection();
      } finally {
        setLoading(false);
      }
    }, 'image/jpeg', 0.95);
  };

  const handleClear = () => {
    setCapturedImage(null);
    setPreviewUrl(null);
    setName('');
    setEmail('');
    setPassword('');
    setDepartment('');
    setError('');
    setSuccess('');
    fetchNextEmployeeId(); // Fetch next ID after clearing
    startFaceDetection();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    if (!capturedImage) {
      setError('Please capture a face first!');
      setLoading(false);
      return;
    }

    try {
      // Duplicate already checked on capture - proceed with employee creation
      const employeeData = {
        name,
        employee_number: employeeId,
        department,
        email: email || employeeId.toLowerCase() + '@company.com',
        password: password || 'password123',
        role: 'employee'
      };

      const createResponse = await fetch(`${API_BASE_URL}/employees/create-with-face`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(employeeData)
      });

      if (!createResponse.ok) {
        const errorData = await createResponse.json();
        
        // Handle validation errors (422)
        if (createResponse.status === 422 && errorData.errors) {
          const errorMessages = Object.entries(errorData.errors)
            .map(([field, messages]: [string, any]) => {
              const fieldName = field.charAt(0).toUpperCase() + field.slice(1);
              return `${fieldName}: ${Array.isArray(messages) ? messages.join(', ') : messages}`;
            })
            .join('\n');
          throw new Error(`Validation Failed:\n${errorMessages}`);
        }
        
        throw new Error(errorData.detail || errorData.message || 'Failed to create employee');
      }

      const employeeResult = await createResponse.json();
      const createdEmployeeId = employeeResult.id || employeeResult.employee_id;

      // Now register face with Python service
      const formData = new FormData();
      formData.append('file', capturedImage, 'face.jpg');
      formData.append('employee_id', createdEmployeeId.toString());
      formData.append('floor_id', '1');
      formData.append('room_location', 'Office');

      const FACE_SERVICE_URL = import.meta.env.VITE_FACE_SERVICE_URL || 'http://localhost:8001';
      const faceResponse = await fetch(`${FACE_SERVICE_URL}/register-face`, {
        method: 'POST',
        body: formData
      });

      if (!faceResponse.ok) {
        const errorData = await faceResponse.json();
        const errorMessage = errorData.detail || 'Face registration failed';
        
        // Check if it's a friendly duplicate message (contains "Hi")
        if (errorMessage.includes('Hi') || errorMessage.includes('already registered')) {
          // Show the friendly greeting message
          throw new Error(errorMessage);
        }
        
        throw new Error(errorMessage);
      }

      // CRITICAL: Verify that the face was actually registered with embedding
      const faceResult = await faceResponse.json();
      console.log('Face registration result:', faceResult);
      
      if (!faceResult.has_embedding) {
        throw new Error(' Face was detected but embedding was not saved! This means duplicate detection won\'t work. Please contact support.');
      }
      
      if (!faceResult.success) {
        throw new Error('Face registration failed: ' + (faceResult.message || 'Unknown error'));
      }

      setSuccess(`Success! ${name} has been registered with face ID and biometric data.`);
      
      setTimeout(() => {
        handleClear();
        startFaceDetection();
      }, 3000);

    } catch (err: any) {
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const getPositioningColor = () => {
    switch (positioningStatus) {
      case 'good': return 'bg-green-600';
      case 'warning': return 'bg-orange-500';
      case 'error': return 'bg-red-600';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-lg border-b border-slate-200 px-6 py-5 shadow-sm">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-4">
            <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br from-blue-600 to-cyan-600 rounded-xl shadow-lg">
              <Users className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-slate-900 to-blue-900 bg-clip-text text-transparent">Employee Face Registration</h1>
              <p className="text-sm text-slate-600">AI-Powered Biometric Access Control</p>
            </div>
          </div>
          <button
            onClick={onLogout}
            className="flex items-center gap-2 px-5 py-2.5 text-slate-600 hover:text-white hover:bg-gradient-to-r hover:from-slate-600 hover:to-slate-700 rounded-xl transition-all duration-200 border border-slate-200 hover:border-transparent shadow-sm hover:shadow-md"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-5xl mx-auto px-4 py-10">
        <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-slate-200 p-8 lg:p-10">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-gradient-to-br from-blue-600 to-cyan-600 rounded-lg">
              <Users className="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 className="text-3xl font-bold bg-gradient-to-r from-slate-900 to-blue-900 bg-clip-text text-transparent">Register New Employee</h2>
              <p className="text-slate-600">Capture face biometrics and enter employee details</p>
            </div>
          </div>

        {/* Video Container */}
        <div className="relative bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl overflow-hidden mb-8 shadow-2xl border-2 border-slate-700">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-auto"
          />
          <canvas
            ref={canvasRef}
            className="hidden"
          />
          <canvas
            ref={overlayCanvasRef}
            className="absolute top-0 left-0 w-full h-full pointer-events-none"
          />
          
          {/* FIXED CIRCLE in center */}
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 border-4 border-dashed border-cyan-400 rounded-full pointer-events-none opacity-50 animate-pulse" />
          
          {/* Status overlay */}
          <div className="absolute top-4 left-4 bg-gradient-to-r from-slate-900/90 to-blue-900/90 backdrop-blur-sm text-white px-4 py-2.5 rounded-xl text-sm font-medium shadow-lg border border-white/10 flex items-center gap-2">
            {cameraReady ? (
              <>
                <CheckCircle className="h-4 w-4 text-green-400" />
                <span>Camera Ready</span>
              </>
            ) : (
              <>
                <Loader2 className="h-4 w-4 animate-spin text-blue-400" />
                <span>Initializing Camera...</span>
              </>
            )}
          </div>

          {/* Positioning guide */}
          {!capturedImage && (
            <div className={`absolute bottom-6 left-1/2 transform -translate-x-1/2 ${getPositioningColor()} text-white px-8 py-4 rounded-xl text-base font-bold min-w-[360px] text-center shadow-2xl border-2 border-white/20 backdrop-blur-sm flex items-center justify-center gap-3`}>
              {positioningStatus === 'good' && <CheckCircle className="h-5 w-5" />}
              {positioningStatus === 'warning' && <AlertCircle className="h-5 w-5" />}
              {positioningStatus === 'error' && <X className="h-5 w-5" />}
              <span>{positioningMessage}</span>
            </div>
          )}
        </div>

          {/* Preview */}
          {previewUrl && (
            <div className="mb-8 text-center bg-gradient-to-br from-blue-50 to-cyan-50 p-6 rounded-2xl border border-blue-200">
              <div className="flex items-center justify-center gap-2 mb-4">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <p className="font-bold text-slate-800 text-lg">Face Captured Successfully</p>
              </div>
              <img src={previewUrl} alt="Captured face" className="max-w-[240px] mx-auto border-4 border-gradient-to-br from-blue-600 to-cyan-600 rounded-2xl shadow-2xl ring-4 ring-blue-100" />
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-gradient-to-br from-red-50 to-orange-50 border-2 border-red-300 text-red-900 px-6 py-5 rounded-xl shadow-lg">
                <div className="flex items-start gap-4">
                  <div className="p-2 bg-red-100 rounded-lg">
                    <AlertCircle className="h-6 w-6 text-red-600" />
                  </div>
                  <div className="flex-1">
                    <p className="font-bold text-lg mb-2">Registration Issue</p>
                    <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">{error}</pre>
                  </div>
                </div>
              </div>
            )}

            {success && (
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-300 text-green-800 px-6 py-4 rounded-xl shadow-lg flex items-center gap-3">
                <div className="p-2 bg-green-100 rounded-lg">
                  <CheckCircle className="h-6 w-6 text-green-600" />
                </div>
                <span className="font-semibold text-base">{success}</span>
              </div>
            )}

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                Full Name *
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                placeholder="John Doe"
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-100 focus:outline-none text-base transition-all bg-white shadow-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                Email *
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="john.doe@company.com"
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-100 focus:outline-none text-base transition-all bg-white shadow-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                Password *
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                placeholder="Minimum 6 characters"
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-100 focus:outline-none text-base transition-all bg-white shadow-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                Employee ID (Auto-generated) *
              </label>
              <input
                type="text"
                value={employeeId}
                readOnly
                disabled
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl bg-gradient-to-br from-slate-50 to-slate-100 text-slate-700 text-base cursor-not-allowed font-mono font-bold shadow-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                Department *
              </label>
              <select
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                required
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-100 focus:outline-none text-base transition-all bg-white shadow-sm"
              >
                <option value="">Select Department</option>
                {DEPARTMENTS.map((dept) => (
                  <option key={dept} value={dept}>{dept}</option>
                ))}
              </select>
            </div>

            {/* Buttons */}
            <div className="flex gap-4 pt-6">
              <button
                type="button"
                onClick={handleCapture}
                disabled={!captureEnabled || !!capturedImage}
                className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 text-white py-4 px-6 rounded-xl font-bold hover:from-blue-700 hover:to-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed disabled:from-slate-400 disabled:to-slate-500 flex items-center justify-center gap-2 transition-all shadow-lg hover:shadow-xl hover:scale-105 active:scale-95"
              >
                <Camera className="h-5 w-5" />
                Capture Face
              </button>
              
              <button
                type="submit"
                disabled={loading || !capturedImage}
                className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 text-white py-4 px-6 rounded-xl font-bold hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed disabled:from-slate-400 disabled:to-slate-500 flex items-center justify-center gap-2 transition-all shadow-lg hover:shadow-xl hover:scale-105 active:scale-95"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    Registering...
                  </>
                ) : (
                  <>
                    <Check className="h-5 w-5" />
                    Register Employee
                  </>
                )}
              </button>
              
              <button
                type="button"
                onClick={handleClear}
                className="bg-gradient-to-r from-slate-500 to-slate-600 text-white py-4 px-6 rounded-xl font-bold hover:from-slate-600 hover:to-slate-700 flex items-center justify-center gap-2 transition-all shadow-lg hover:shadow-xl hover:scale-105 active:scale-95"
              >
                <X className="h-5 w-5" />
                Clear
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
