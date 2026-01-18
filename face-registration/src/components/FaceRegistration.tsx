import { useState, useEffect, useRef } from 'react';
import { Camera, Check, X, Loader2, LogOut, Users } from 'lucide-react';

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
  const [positioningMessage, setPositioningMessage] = useState('📍 Position your face in the circle');
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
      const response = await fetch('http://localhost:8000/api/v1/employees/next-id');
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
            canvasRef.current.width = videoRef.current.videoWidth;
            canvasRef.current.height = videoRef.current.videoHeight;
            overlayCanvasRef.current.width = videoRef.current.videoWidth;
            overlayCanvasRef.current.height = videoRef.current.videoHeight;
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

          const response = await fetch('http://localhost:8001/detect-faces', {
            method: 'POST',
            body: formData
          });

          if (response.ok) {
            const result: FaceDetectionResult = await response.json();
            drawFaceDetection(result);
          }
        } catch (err) {
          // Silently handle detection errors
        }
      }, 'image/jpeg', 0.7);
    }, 300);
  };

  const drawFaceDetection = (result: FaceDetectionResult) => {
    const canvas = overlayCanvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (result.faces_detected === 0) {
      setPositioningMessage('❌ No face detected - Move closer');
      setPositioningStatus('error');
      setCaptureEnabled(false);
    } else if (result.faces_detected > 1) {
      setPositioningMessage('⚠️ Multiple faces - Only one person');
      setPositioningStatus('warning');
      setCaptureEnabled(false);
    } else {
      const face = result.faces[0];
      const [x1, y1, x2, y2] = face.bbox;

      // Calculate face position relative to center
      const faceCenterX = (x1 + x2) / 2;
      const faceCenterY = (y1 + y2) / 2;
      const videoCenterX = canvas.width / 2;
      const videoCenterY = canvas.height / 2;

      const offsetX = faceCenterX - videoCenterX;
      const offsetY = faceCenterY - videoCenterY;
      const faceWidth = x2 - x1;

      // Draw bounding box
      ctx.strokeStyle = '#00ff00';
      ctx.lineWidth = 3;
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

      // Provide positioning guidance
      if (Math.abs(offsetX) > 100) {
        if (offsetX > 0) {
          setPositioningMessage('⬅️ Move LEFT');
        } else {
          setPositioningMessage('➡️ Move RIGHT');
        }
        setPositioningStatus('warning');
        setCaptureEnabled(false);
      } else if (Math.abs(offsetY) > 80) {
        if (offsetY > 0) {
          setPositioningMessage('⬆️ Move UP');
        } else {
          setPositioningMessage('⬇️ Move DOWN');
        }
        setPositioningStatus('warning');
        setCaptureEnabled(false);
      } else if (faceWidth < 150) {
        setPositioningMessage('🔍 Move CLOSER');
        setPositioningStatus('warning');
        setCaptureEnabled(false);
      } else if (faceWidth > 400) {
        setPositioningMessage('🔍 Move BACK');
        setPositioningStatus('warning');
        setCaptureEnabled(false);
      } else {
        setPositioningMessage('✅ Perfect! Click Capture');
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
    setPositioningMessage('🔍 Checking for duplicates...');

    canvas.toBlob(async (blob) => {
      if (!blob) {
        setLoading(false);
        return;
      }

      // CHECK DUPLICATE IMMEDIATELY ON CAPTURE - Call Python service directly for speed
      try {
        const formData = new FormData();
        formData.append('file', blob, 'face.jpg');
        
        const response = await fetch('http://localhost:8001/check-face-duplicate', {
          method: 'POST',
          body: formData
        });

        if (response.status === 400) {
          const errorData = await response.json();
          setError('⚠️ ' + errorData.detail);
          setLoading(false);
          startFaceDetection();
          return;
        }

        if (response.status === 503) {
          setError('⚠️ Face Recognition Service Unavailable');
          setLoading(false);
          startFaceDetection();
          return;
        }

        if (!response.ok) {
          const errorData = await response.json();
          setError('❌ Face Check Failed\n' + (errorData.detail || ''));
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
            `👋 Already Registered!\n\n` +
            `Hi ${employeeName}! You're in the system.\n\n` +
            `📋 Employee ID: ${employeeId}\n` +
            `📋 Department: ${dept}\n\n` +
            `No need to register again! 😊`
          );
          setLoading(false);
          startFaceDetection();
          return;
        }

        // NO DUPLICATE - PROCEED WITH CAPTURE
        setCapturedImage(blob);
        setPreviewUrl(URL.createObjectURL(blob));
        setPositioningMessage('✅ Face verified - Fill the form');
        
        // Clear overlay
        const overlayCtx = overlayCanvasRef.current?.getContext('2d');
        if (overlayCtx && overlayCanvasRef.current) {
          overlayCtx.clearRect(0, 0, overlayCanvasRef.current.width, overlayCanvasRef.current.height);
        }
        
      } catch (err: any) {
        setError('⚠️ Cannot check duplicates: ' + err.message);
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

      const createResponse = await fetch('http://localhost:8000/api/v1/employees/create-with-face', {
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

      const faceResponse = await fetch('http://localhost:8001/register-face', {
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
        throw new Error('⚠️ Face was detected but embedding was not saved! This means duplicate detection won\'t work. Please contact support.');
      }
      
      if (!faceResult.success) {
        throw new Error('Face registration failed: ' + (faceResult.message || 'Unknown error'));
      }

      setSuccess(`✅ Success! ${name} has been registered with face ID and biometric data.`);
      
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
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="inline-flex items-center justify-center w-10 h-10 bg-blue-600 rounded-full">
              <Users className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900">Employee Face Registration</h1>
              <p className="text-sm text-slate-600">Register employees for access control</p>
            </div>
          </div>
          <button
            onClick={onLogout}
            className="flex items-center gap-2 px-4 py-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-slate-900 mb-2">👤 Register New Employee</h2>
          <p className="text-slate-600 mb-6">Capture face photo and enter employee details</p>

        {/* Video Container */}
        <div className="relative bg-black rounded-xl overflow-hidden mb-6">
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
          
          {/* Face guide circle */}
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 border-4 border-dashed border-green-400 rounded-full pointer-events-none" />
          
          {/* Status overlay */}
          <div className="absolute top-4 left-4 bg-black bg-opacity-70 text-white px-4 py-2 rounded-lg text-sm font-medium">
            {cameraReady ? '✅ Camera ready' : '🎥 Initializing camera...'}
          </div>

          {/* Positioning guide */}
          {!capturedImage && (
            <div className={`absolute bottom-4 left-1/2 transform -translate-x-1/2 ${getPositioningColor()} text-white px-6 py-3 rounded-lg text-base font-bold min-w-[320px] text-center shadow-lg`}>
              {positioningMessage}
            </div>
          )}
        </div>

          {/* Preview */}
          {previewUrl && (
            <div className="mb-6 text-center">
              <p className="font-semibold text-slate-700 mb-3">Captured Face:</p>
              <img src={previewUrl} alt="Captured face" className="max-w-[200px] mx-auto border-4 border-blue-600 rounded-xl shadow-lg" />
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-50 border-2 border-red-400 text-red-900 px-6 py-4 rounded-lg shadow-md">
                <div className="flex items-start gap-3">
                  <div className="text-3xl">👋</div>
                  <div className="flex-1">
                    <p className="font-bold text-lg mb-2">Already Registered!</p>
                    <pre className="whitespace-pre-wrap font-sans text-sm">{error}</pre>
                  </div>
                </div>
              </div>
            )}

            {success && (
              <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg flex items-center gap-2">
                <Check className="h-5 w-5" />
                {success}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Full Name *
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                placeholder="John Doe"
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-600 focus:outline-none text-base transition-colors"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Email *
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="john.doe@company.com"
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-600 focus:outline-none text-base transition-colors"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Password *
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                placeholder="Minimum 6 characters"
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-600 focus:outline-none text-base transition-colors"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Employee ID (Auto-generated) *
              </label>
              <input
                type="text"
                value={employeeId}
                readOnly
                disabled
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg bg-slate-100 text-slate-600 text-base cursor-not-allowed"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Department *
              </label>
              <select
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                required
                className="w-full px-4 py-3 border-2 border-slate-200 rounded-lg focus:border-blue-600 focus:outline-none text-base transition-colors"
              >
                <option value="">Select Department</option>
                {DEPARTMENTS.map((dept) => (
                  <option key={dept} value={dept}>{dept}</option>
                ))}
              </select>
            </div>

            {/* Buttons */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={handleCapture}
                disabled={!captureEnabled || !!capturedImage}
                className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all"
              >
                <Camera className="h-5 w-5" />
                📸 Capture Face
              </button>
              
              <button
                type="submit"
                disabled={loading || !capturedImage}
                className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    ⏳ Registering...
                  </>
                ) : (
                  <>
                    <Check className="h-5 w-5" />
                    ✅ Register Employee
                  </>
                )}
              </button>
              
              <button
                type="button"
                onClick={handleClear}
                className="bg-slate-200 text-slate-700 py-3 px-4 rounded-lg font-semibold hover:bg-slate-300 flex items-center justify-center gap-2 transition-colors"
              >
                <X className="h-5 w-5" />
                🔄 Clear
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
