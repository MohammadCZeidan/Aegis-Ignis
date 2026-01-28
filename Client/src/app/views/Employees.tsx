import { useState, useEffect } from 'react';
import { Users, Building2, Mail, RefreshCw, X, Calendar, Shield, MapPin, Activity } from 'lucide-react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { dataService, Employee } from '../services/dataService';
import { API_CONFIG, getStorageUrl } from '../../config/api';

export function Employees() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedFloor, setSelectedFloor] = useState<number | null>(null);
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  useEffect(() => {
    loadEmployees();
  }, [selectedFloor]);

  const loadEmployees = async () => {
    try {
      setLoading(true);
      const data = selectedFloor
        ? await dataService.getEmployeesByFloor(selectedFloor)
        : await dataService.getEmployees();
      setEmployees(data);
    } catch (err) {
      console.error('Error loading employees:', err);
    } finally {
      setLoading(false);
    }
  };

  // Group employees by floor
  const employeesByFloor = employees.reduce((acc, emp) => {
    const floorName = emp.floor_name || 'Unassigned';
    if (!acc[floorName]) {
      acc[floorName] = [];
    }
    acc[floorName].push(emp);
    return acc;
  }, {} as Record<string, Employee[]>);

  if (loading) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading employees...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 mb-2 flex items-center gap-2">
            <Users className="h-6 w-6" />
            Employees
          </h1>
          <p className="text-slate-600">View all registered employees and their floor assignments</p>
        </div>
        <Button onClick={loadEmployees} variant="outline" className="gap-2">
          <RefreshCw className="h-4 w-4" />
          Refresh
        </Button>
      </div>

      {employees.length === 0 ? (
        <Card className="p-12 text-center">
          <Users className="h-16 w-16 text-slate-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-slate-900 mb-2">No Employees Registered</h3>
          <p className="text-slate-600 mb-4">
            Use the Employee Registration System to register employees with face photos.
          </p>
          <Button 
            onClick={() => window.open('http://localhost:5174', '_blank')}
            className="gap-2"
          >
            <Users className="h-4 w-4" />
            Open Registration System
          </Button>
        </Card>
      ) : (
        <div className="space-y-6">
          <Card className="p-4 bg-blue-50 border-blue-200">
            <div className="flex items-center gap-3">
              <Users className="h-5 w-5 text-blue-600" />
              <div>
                <p className="font-semibold text-blue-900">Total Registered: {employees.length}</p>
                <p className="text-sm text-blue-700">These employees can be recognized by the face detection system</p>
              </div>
            </div>
          </Card>

          {Object.entries(employeesByFloor).map(([floorName, floorEmployees]) => (
            <Card key={floorName} className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <Building2 className="h-5 w-5 text-blue-600" />
                <h2 className="text-xl font-semibold text-slate-900">{floorName}</h2>
                <Badge variant="secondary">
                  {floorEmployees.length} {floorEmployees.length === 1 ? 'employee' : 'employees'}
                </Badge>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {floorEmployees.map((emp) => {
                  const facePhotoUrl = emp.face_photo_path 
                    ? getStorageUrl(emp.face_photo_path)
                    : emp.photo_url;
                  
                  return (
                  <div
                    key={emp.id}
                    className="flex items-center gap-4 p-4 border border-slate-200 rounded-lg hover:bg-slate-50 hover:border-blue-300 transition-colors cursor-pointer"
                    onClick={() => {
                      setSelectedEmployee(emp);
                      setShowDetails(true);
                    }}
                  >
                    {facePhotoUrl ? (
                      <img
                        src={facePhotoUrl}
                        alt={emp.name}
                        className="w-16 h-16 object-cover rounded-full border-2 border-slate-200"
                        onError={(e) => {
                          // Fallback to default icon on error
                          e.currentTarget.style.display = 'none';
                          const fallback = e.currentTarget.nextElementSibling as HTMLElement;
                          if (fallback) fallback.style.display = 'flex';
                        }}
                      />
                    ) : null}
                    <div className={facePhotoUrl ? 'hidden w-16 h-16 bg-slate-200 rounded-full items-center justify-center' : 'w-16 h-16 bg-slate-200 rounded-full flex items-center justify-center'}>
                      <Users className="h-8 w-8 text-slate-400" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-slate-900">{emp.name}</h3>
                      {emp.email && (
                        <p className="text-sm text-slate-600 flex items-center gap-1 mt-1">
                          <Mail className="h-3 w-3" />
                          {emp.email}
                        </p>
                      )}
                      {emp.department && (
                        <p className="text-xs text-slate-500 mt-1">{emp.department}</p>
                      )}
                    </div>
                  </div>
                )})}
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Employee Details Dialog */}
      <Dialog open={showDetails} onOpenChange={setShowDetails}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Employee Details
            </DialogTitle>
          </DialogHeader>

          {selectedEmployee && (
            <div className="space-y-6">
              {/* Photo and Basic Info */}
              <div className="flex items-start gap-6">
                {selectedEmployee.face_photo_path ? (
                  <img
                    src={getStorageUrl(selectedEmployee.face_photo_path)}
                    alt={selectedEmployee.name}
                    className="w-32 h-32 object-cover rounded-lg border-2 border-slate-200 shadow-sm"
                    onError={(e) => {
                      // Fallback if image fails to load
                      e.currentTarget.style.display = 'none';
                      e.currentTarget.nextElementSibling?.classList.remove('hidden');
                    }}
                  />
                ) : null}
                <div className={selectedEmployee.face_photo_path ? 'hidden' : 'w-32 h-32 bg-slate-200 rounded-lg flex items-center justify-center'}>
                  <Users className="h-16 w-16 text-slate-400" />
                </div>
                
                <div className="flex-1">
                  <h2 className="text-2xl font-bold text-slate-900 mb-2">{selectedEmployee.name}</h2>
                  <div className="space-y-2">
                    {selectedEmployee.employee_number && (
                      <p className="text-sm text-slate-600 flex items-center gap-2">
                        <Shield className="h-4 w-4" />
                        Employee #: <span className="font-semibold">{selectedEmployee.employee_number}</span>
                      </p>
                    )}
                    {selectedEmployee.email && (
                      <p className="text-sm text-slate-600 flex items-center gap-2">
                        <Mail className="h-4 w-4" />
                        {selectedEmployee.email}
                      </p>
                    )}
                    {selectedEmployee.department && (
                      <p className="text-sm text-slate-600 flex items-center gap-2">
                        <Building2 className="h-4 w-4" />
                        Department: {selectedEmployee.department}
                      </p>
                    )}
                    {selectedEmployee.role && (
                      <Badge variant="secondary" className="mt-2">
                        {selectedEmployee.role}
                      </Badge>
                    )}
                  </div>
                </div>
              </div>

              {/* Divider */}
              <div className="border-t border-slate-200"></div>

              {/* Location & Status */}
              <div className="grid grid-cols-2 gap-4">
                <Card className="p-4 bg-slate-50">
                  <h3 className="font-semibold text-slate-700 mb-3 flex items-center gap-2">
                    <MapPin className="h-4 w-4" />
                    Current Location
                  </h3>
                  <div className="space-y-2 text-sm">
                    {selectedEmployee.current_floor_id && (
                      <p className="text-slate-600">
                        Floor: <span className="font-semibold">Floor {selectedEmployee.current_floor_id}</span>
                      </p>
                    )}
                    {selectedEmployee.current_room && (
                      <p className="text-slate-600">
                        Room: <span className="font-semibold">{selectedEmployee.current_room}</span>
                      </p>
                    )}
                    {selectedEmployee.last_seen_at && (
                      <p className="text-slate-600">
                        Last Seen: <span className="font-semibold">{new Date(selectedEmployee.last_seen_at).toLocaleString()}</span>
                      </p>
                    )}
                  </div>
                </Card>

                <Card className="p-4 bg-blue-50">
                  <h3 className="font-semibold text-slate-700 mb-3 flex items-center gap-2">
                    <Activity className="h-4 w-4" />
                    Face Recognition
                  </h3>
                  <div className="space-y-2 text-sm">
                    {selectedEmployee.face_registered_at && (
                      <p className="text-slate-600">
                        Registered: <span className="font-semibold">{new Date(selectedEmployee.face_registered_at).toLocaleDateString()}</span>
                      </p>
                    )}
                    {selectedEmployee.face_match_confidence && (
                      <p className="text-slate-600">
                        Confidence: <span className="font-semibold text-blue-600">{selectedEmployee.face_match_confidence}%</span>
                      </p>
                    )}
                    {selectedEmployee.status && (
                      <Badge variant={selectedEmployee.status === 'active' ? 'default' : 'secondary'}>
                        {selectedEmployee.status}
                      </Badge>
                    )}
                  </div>
                </Card>
              </div>

              {/* Registration Date */}
              {selectedEmployee.created_at && (
                <div className="text-sm text-slate-500 flex items-center gap-2 pt-2">
                  <Calendar className="h-4 w-4" />
                  Registered on: {new Date(selectedEmployee.created_at).toLocaleString()}
                </div>
              )}

              {/* Close Button */}
              <div className="flex justify-end pt-4 border-t border-slate-200">
                <Button onClick={() => setShowDetails(false)} variant="outline">
                  Close
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

