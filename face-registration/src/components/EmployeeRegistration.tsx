import { useState, useEffect, useRef } from 'react';
import { authService } from '../services/auth';
import { api } from '../services/api';
import { Camera, Upload, X, Check, Loader2, LogOut, Users } from 'lucide-react';

interface EmployeeRegistrationProps {
  onLogout: () => void;
}

interface Floor {
  id: number;
  floor_number: number;
  name: string | null;
}

interface Employee {
  id: number;
  name: string;
  email: string | null;
  floor_id: number | null;
  floor_name: string | null;
  photo_url: string | null;
}

export function EmployeeRegistration({ onLogout }: EmployeeRegistrationProps) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [floorId, setFloorId] = useState<number | null>(null);
  const [photo, setPhoto] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [floors, setFloors] = useState<Floor[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [useCamera, setUseCamera] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);

  useEffect(() => {
    // Auto-start camera on mount
    startCamera();
    
    // Cleanup on unmount
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const loadFloors = async () => {
    try {
      const floorsData = await api.getFloors();
      setFloors(floorsData);
    } catch (err) {
      console.error('Error loading floors:', err);
      // Silently fail - floors are optional
      setFloors([]);
    }
  };

  const loadEmployees = async () => {
    try {
      // Temporarily disabled due to API issues - will show empty list
      setEmployees([]);
    } catch (err) {
      console.error('Error loading employees:', err);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setPhoto(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPhotoPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 1280 },
          height: { ideal: 720 }
        } 
      });
      setStream(mediaStream);
      setUseCamera(true);
      
      // Wait a bit for the ref to be available
      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
          videoRef.current.play().catch(err => console.error('Video play error:', err));
        }
      }, 100);
    } catch (err) {
      console.error('Camera error:', err);
      setError('Could not access camera. Please check permissions and ensure you are using HTTPS or localhost.');
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setUseCamera(false);
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  };

  const capturePhoto = () => {
    if (videoRef.current) {
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(videoRef.current, 0, 0);
        canvas.toBlob((blob) => {
          if (blob) {
            const file = new File([blob], 'photo.jpg', { type: 'image/jpeg' });
            setPhoto(file);
            setPhotoPreview(canvas.toDataURL());
            stopCamera();
          }
        }, 'image/jpeg');
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    if (!photo) {
      setError('Please select or capture a photo');
      setLoading(false);
      return;
    }

    try {
      const formData = new FormData();
      formData.append('photo', photo);
      formData.append('name', name);
      formData.append('password', password);
      if (email) formData.append('email', email);
      // Don't send floor_id if it's null/empty
      if (floorId) formData.append('floor_id', floorId.toString());

      await api.registerEmployee(formData);
      setSuccess('Employee registered successfully!');
      setName('');
      setEmail('');
      setPassword('');
      setFloorId(null);
      setPhoto(null);
      setPhotoPreview(null);
      
      // Restart camera after successful registration
      setTimeout(() => {
        setSuccess('');
        startCamera();
      }, 2000);
    } catch (err: any) {
      setError(err.message || 'Failed to register employee');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    if (stream) {
      stopCamera();
    }
    authService.logout();
    onLogout();
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Users className="h-6 w-6 text-blue-600" />
            <h1 className="text-xl font-bold text-slate-900">Employee Face Registration</h1>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2 text-slate-600 hover:text-slate-900"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </div>
      </header>

      <div className="max-w-2xl mx-auto px-4 py-8">
        {/* Registration Form */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-xl font-semibold mb-6">Register New Employee</h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}

            {success && (
              <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded flex items-center gap-2">
                <Check className="h-4 w-4" />
                {success}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Full Name *
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Password *
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Minimum 6 characters"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Floor
              </label>
              <select
                value={floorId || ''}
                onChange={(e) => setFloorId(e.target.value ? parseInt(e.target.value) : null)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Select Floor</option>
                {floors.map((floor) => (
                  <option key={floor.id} value={floor.id}>
                    {floor.name || `Floor ${floor.floor_number}`}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Photo *
              </label>
              
              {/* Always show camera by default */}
              {useCamera && !photoPreview && (
                <div className="space-y-2">
                  <div className="relative bg-slate-900 rounded-lg overflow-hidden" style={{ minHeight: '320px' }}>
                    <video
                      ref={videoRef}
                      autoPlay
                      muted
                      playsInline
                      className="w-full h-80 object-cover"
                    />
                  </div>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={capturePhoto}
                      className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 font-medium"
                    >
                      Capture Photo
                    </button>
                    <button
                      type="button"
                      onClick={stopCamera}
                      className="px-4 py-2 border border-slate-300 rounded-lg hover:bg-slate-50"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
              
              {!useCamera && !photoPreview && (
                <div className="space-y-2">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      className="flex items-center gap-2 px-4 py-2 border border-slate-300 rounded-lg hover:bg-slate-50"
                    >
                      <Upload className="h-4 w-4" />
                      Upload Photo
                    </button>
                    <button
                      type="button"
                      onClick={startCamera}
                      className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      <Camera className="h-4 w-4" />
                      Use Camera
                    </button>
                  </div>
                </div>
              )}

              {photoPreview && !useCamera && (
                <div className="mt-4 relative">
                  <img
                    src={photoPreview}
                    alt="Preview"
                    className="w-full h-64 object-cover rounded-lg border border-slate-300"
                  />
                  <button
                    type="button"
                    onClick={() => {
                      setPhoto(null);
                      setPhotoPreview(null);
                    }}
                    className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              )}
            </div>

            <button
              type="submit"
              disabled={loading || !photo || !name}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Registering...
                </>
              ) : (
                'Register Employee'
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

