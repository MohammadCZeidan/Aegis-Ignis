import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Building2, TrendingUp, Users, Plus, Edit, Trash2 } from 'lucide-react';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { toast } from 'react-hot-toast';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  
} from '../components/ui/dialog';
import { useFloors, useCreateFloor, useUpdateFloor, useDeleteFloor, useOccupancy } from '../hooks/useData';
export function Floors() {
  const navigate = useNavigate();
  const { data: floors = [], isLoading, refetch } = useFloors();
  const { data: occupancy = {} } = useOccupancy();
  const createFloor = useCreateFloor();
  const updateFloor = useUpdateFloor();
  const deleteFloor = useDeleteFloor();

  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [editingFloor, setEditingFloor] = useState<any>(null);
  const [formData, setFormData] = useState({
    name: '',
    floor_number: 1,
    max_occupancy: 50,
    description: '',
  });

  const handleCreateFloor = async () => {
    if (!formData.name || !formData.floor_number) {
      alert('Please fill in all required fields');
      return;
    }
    
    await createFloor.mutateAsync(formData);
    setShowCreateDialog(false);
    setFormData({ name: '', floor_number: 1, max_occupancy: 50, description: '' });
  };

  const handleUpdateFloor = async () => {
    if (editingFloor) {
      await updateFloor.mutateAsync({ id: editingFloor.id, data: formData });
      setEditingFloor(null);
      setFormData({ name: '', floor_number: 1, max_occupancy: 50, description: '' });
    }
  };

  const handleDeleteFloor = async (id: number) => {
    const floor = floors.find((f: any) => f.id === id);
    try {
      await deleteFloor.mutateAsync(id);
      toast.success(`${floor?.name || 'Floor'} deleted successfully`);
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Failed to delete floor');
    }
  };

  const openEditDialog = (floor: any) => {
    setEditingFloor(floor);
    setFormData({
      name: floor.name || '',
      floor_number: floor.floor_number,
      max_occupancy: floor.max_occupancy || 50,
      description: floor.description || '',
    });
  };

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading floors...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 lg:p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 mb-2">Building Floors</h1>
          <p className="text-slate-600">Manage and monitor all building floors</p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Add Floor
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {floors.map((floor) => {
          const currentOccupancy = occupancy[floor.id] || 0;
          const maxOccupancy = floor.max_occupancy || 50;
          const occupancyPercent = Math.round((currentOccupancy / maxOccupancy) * 100);
          
          return (
            <Card 
              key={floor.id} 
              className="p-6 hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => navigate(`/floors/${floor.id}`)}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <Building2 className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">{floor.name || `Floor ${floor.floor_number}`}</h3>
                    <p className="text-sm text-slate-500">Floor {floor.floor_number}</p>
                  </div>
                </div>
                <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => openEditDialog(floor)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => handleDeleteFloor(floor.id)}
                  >
                    <Trash2 className="h-4 w-4 text-red-600" />
                  </Button>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-600 flex items-center gap-2">
                    <Users className="h-4 w-4" />
                    Occupancy
                  </span>
                  <span className="font-medium">{currentOccupancy}/{maxOccupancy}</span>
                </div>

                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all ${
                      occupancyPercent > 80 ? 'bg-red-500' : 
                      occupancyPercent > 60 ? 'bg-amber-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${Math.min(occupancyPercent, 100)}%` }}
                  />
                </div>

                <Badge variant={occupancyPercent > 80 ? 'destructive' : 'secondary'}>
                  {occupancyPercent}% Utilization
                </Badge>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Create/Edit Dialog */}
      <Dialog 
        open={showCreateDialog || !!editingFloor} 
        onOpenChange={(open) => {
          if (!open) {
            setShowCreateDialog(false);
            setEditingFloor(null);
            setFormData({ name: '', floor_number: 1, max_occupancy: 50, description: '' });
          }
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingFloor ? 'Edit Floor' : 'Create New Floor'}</DialogTitle>
            <DialogDescription>
              {editingFloor ? 'Update floor information' : 'Add a new floor to the building'}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">Floor Name</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Ground Floor, First Floor"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="floor_number">Floor Number</Label>
              <Input
                id="floor_number"
                type="number"
                value={formData.floor_number}
                onChange={(e) => setFormData({ ...formData, floor_number: parseInt(e.target.value) })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="max_occupancy">Max Occupancy</Label>
              <Input
                id="max_occupancy"
                type="number"
                value={formData.max_occupancy}
                onChange={(e) => setFormData({ ...formData, max_occupancy: parseInt(e.target.value) })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description (Optional)</Label>
              <Input
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Floor description"
              />
            </div>
          </div>

          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => {
                setShowCreateDialog(false);
                setEditingFloor(null);
              }}
            >
              Cancel
            </Button>
            <Button onClick={editingFloor ? handleUpdateFloor : handleCreateFloor}>
              {editingFloor ? 'Update' : 'Create'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
