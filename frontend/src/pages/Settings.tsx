import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Users, MapPin, Truck, Package, Save, LogOut, Plus, Edit, Trash2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { apiRequest } from '../utils/api';
import { User, CreateUserRequest, UpdateUserRequest, Location, LocationType } from '../types/api';

export function Settings() {
  const { logout } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [showUserModal, setShowUserModal] = useState(false);
  const [showLocationModal, setShowLocationModal] = useState(false);
  const [selectedRole, setSelectedRole] = useState<string>('');
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [editingLocation, setEditingLocation] = useState<Location | null>(null);
  const [formData, setFormData] = useState<CreateUserRequest>({
    username: '',
    email: '',
    full_name: '',
    role: 'manager',
    location_id: '',
    password: '',
    is_active: true
  });
  const [locationFormData, setLocationFormData] = useState({
    name: '',
    address: '',
    city: '',
    state: '',
    zip_code: '',
    location_type: 'distribution' as LocationType,
    is_active: true
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    fetchUsers();
    fetchLocations();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await apiRequest('/api/users');
      if (response) {
        const userData = await response.json();
        setUsers(userData);
      }
    } catch (error) {
      console.error('Failed to fetch users:', error);
    }
  };

  const fetchLocations = async () => {
    try {
      const response = await apiRequest('/api/locations');
      if (response) {
        const locationData = await response.json();
        setLocations(locationData);
      }
    } catch (error) {
      console.error('Failed to fetch locations:', error);
    }
  };

  const handleManageUsers = (role: string) => {
    setSelectedRole(role);
    setEditingUser(null);
    setFormData({
      username: '',
      email: '',
      full_name: '',
      role: role as any,
      location_id: '',
      password: '',
      is_active: true
    });
    setShowUserModal(true);
  };

  const handleCreateUser = async () => {
    setLoading(true);
    setError('');
    try {
      await apiRequest('/api/users', {
        method: 'POST',
        body: JSON.stringify(formData)
      });
      await fetchUsers();
      setShowUserModal(false);
      resetForm();
    } catch (error: any) {
      setError(error.apiError?.message || 'Failed to create user');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateUser = async () => {
    if (!editingUser) return;
    setLoading(true);
    setError('');
    try {
      const updateData: UpdateUserRequest = { ...formData };
      if (!updateData.password) {
        delete updateData.password;
      }
      await apiRequest(`/api/users/${editingUser.id}`, {
        method: 'PUT',
        body: JSON.stringify(updateData)
      });
      await fetchUsers();
      setShowUserModal(false);
      resetForm();
    } catch (error: any) {
      setError(error.apiError?.message || 'Failed to update user');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId: string) => {
    if (!confirm('Are you sure you want to delete this user?')) return;
    try {
      await apiRequest(`/api/users/${userId}`, { method: 'DELETE' });
      await fetchUsers();
    } catch (error: any) {
      setError(error.apiError?.message || 'Failed to delete user');
    }
  };

  const handleEditUser = (user: User) => {
    setEditingUser(user);
    setFormData({
      username: user.username,
      email: user.email,
      full_name: user.full_name,
      role: user.role,
      location_id: user.location_id,
      password: '',
      is_active: user.is_active
    });
    setSelectedRole(user.role);
    setShowUserModal(true);
  };

  const resetForm = () => {
    setFormData({
      username: '',
      email: '',
      full_name: '',
      role: 'manager',
      location_id: '',
      password: '',
      is_active: true
    });
    setEditingUser(null);
    setError('');
  };

  const handleEditLocation = (location: Location) => {
    setEditingLocation(location);
    setLocationFormData({
      name: location.name,
      address: location.address,
      city: location.city,
      state: location.state,
      zip_code: location.zip_code,
      location_type: location.location_type,
      is_active: location.is_active
    });
    setShowLocationModal(true);
  };

  const handleUpdateLocation = async () => {
    if (!editingLocation) return;
    setLoading(true);
    setError('');
    try {
      await apiRequest(`/api/locations/${editingLocation.id}`, {
        method: 'PUT',
        body: JSON.stringify(locationFormData)
      });
      await fetchLocations();
      setShowLocationModal(false);
      resetLocationForm();
    } catch (error: any) {
      setError(error.apiError?.message || 'Failed to update location');
    } finally {
      setLoading(false);
    }
  };

  const resetLocationForm = () => {
    setLocationFormData({
      name: '',
      address: '',
      city: '',
      state: '',
      zip_code: '',
      location_type: 'distribution',
      is_active: true
    });
    setEditingLocation(null);
    setError('');
  };

  const filteredUsers = users.filter(user => user.role === selectedRole);
  const getUserCountByRole = (role: string) => users.filter(user => user.role === role).length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <div className="flex items-center space-x-2">
          <Button>
            <Save className="h-4 w-4 mr-2" />
            Save Changes
          </Button>
          <Button 
            variant="outline" 
            onClick={logout}
            className="text-red-600 border-red-200 hover:bg-red-50 hover:border-red-300"
          >
            <LogOut className="h-4 w-4 mr-2" />
            Sign Out
          </Button>
        </div>
      </div>

      {/* Company Information */}
      <Card>
        <CardHeader>
          <CardTitle>Company Information</CardTitle>
          <CardDescription>Basic company details and contact information</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="company-name">Company Name</Label>
              <Input id="company-name" defaultValue="Arctic Ice Solutions" autoComplete="organization" />
            </div>
            <div>
              <Label htmlFor="company-phone">Phone Number</Label>
              <Input id="company-phone" defaultValue="(337) 555-0123" autoComplete="tel" />
            </div>
            <div>
              <Label htmlFor="company-email">Email Address</Label>
              <Input id="company-email" defaultValue="info@arcticeicesolutions.com" autoComplete="email" />
            </div>
            <div>
              <Label htmlFor="company-website">Website</Label>
              <Input id="company-website" defaultValue="www.arcticeicesolutions.com" autoComplete="url" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Locations Management */}
      <Card>
        <CardHeader>
          <CardTitle>Locations</CardTitle>
          <CardDescription>Manage your business locations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {locations.map((location) => (
              <div key={location.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-3">
                  <MapPin className={`h-5 w-5 ${
                    location.location_type === 'headquarters' ? 'text-blue-600' :
                    location.location_type === 'distribution' ? 'text-green-600' :
                    location.location_type === 'warehouse' ? 'text-gray-600' : 'text-yellow-600'
                  }`} />
                  <div>
                    <p className="font-medium">{location.name}</p>
                    <p className="text-sm text-gray-600">{location.address}, {location.city}, {location.state} {location.zip_code}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant={
                    location.location_type === 'headquarters' ? 'default' :
                    location.location_type === 'distribution' ? 'secondary' : 'outline'
                  }>
                    {location.location_type.charAt(0).toUpperCase() + location.location_type.slice(1)}
                  </Badge>
                  <Button variant="outline" size="sm" onClick={() => handleEditLocation(location)}>Edit</Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* User Management */}
      <Card>
        <CardHeader>
          <CardTitle>User Management</CardTitle>
          <CardDescription>Manage user accounts and permissions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center space-x-3">
                <Users className="h-5 w-5 text-blue-600" />
                <div>
                  <p className="font-medium">Managers ({getUserCountByRole('manager')} users)</p>
                  <p className="text-sm text-gray-600">Full system access</p>
                </div>
              </div>
              <Button variant="outline" size="sm" onClick={() => handleManageUsers('manager')}>Manage</Button>
            </div>

            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center space-x-3">
                <Truck className="h-5 w-5 text-green-600" />
                <div>
                  <p className="font-medium">Dispatchers ({getUserCountByRole('dispatcher')} users)</p>
                  <p className="text-sm text-gray-600">Fleet and route management</p>
                </div>
              </div>
              <Button variant="outline" size="sm" onClick={() => handleManageUsers('dispatcher')}>Manage</Button>
            </div>

            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center space-x-3">
                <Package className="h-5 w-5 text-yellow-600" />
                <div>
                  <p className="font-medium">Accountants ({getUserCountByRole('accountant')} users)</p>
                  <p className="text-sm text-gray-600">Financial management</p>
                </div>
              </div>
              <Button variant="outline" size="sm" onClick={() => handleManageUsers('accountant')}>Manage</Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* System Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>System Configuration</CardTitle>
          <CardDescription>Application settings and preferences</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Production Target</p>
                <p className="text-sm text-gray-600">Daily pallet production goal</p>
              </div>
              <Input className="w-32" defaultValue="160" autoComplete="off" />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Route Optimization</p>
                <p className="text-sm text-gray-600">Automatic route planning</p>
              </div>
              <Badge className="bg-green-100 text-green-800">Enabled</Badge>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Real-time Tracking</p>
                <p className="text-sm text-gray-600">GPS vehicle monitoring</p>
              </div>
              <Badge className="bg-green-100 text-green-800">Active</Badge>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Mobile App Integration</p>
                <p className="text-sm text-gray-600">Driver and customer apps</p>
              </div>
              <div className="flex items-center space-x-2">
                <Badge className="bg-green-100 text-green-800">Active</Badge>
                <Button variant="outline" size="sm" onClick={() => window.open('/mobile', '_blank')}>
                  Open Mobile App
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Account Management */}
      <Card>
        <CardHeader>
          <CardTitle>Account Management</CardTitle>
          <CardDescription>Manage your account and session</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <p className="font-medium">Sign Out</p>
                <p className="text-sm text-gray-600">End your current session and return to login</p>
              </div>
              <Button 
                variant="outline" 
                onClick={logout}
                className="text-red-600 border-red-200 hover:bg-red-50 hover:border-red-300"
              >
                <LogOut className="h-4 w-4 mr-2" />
                Sign Out
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* User Management Modal */}
      <Dialog open={showUserModal} onOpenChange={setShowUserModal}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              Manage {selectedRole.charAt(0).toUpperCase() + selectedRole.slice(1)}s
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}
            
            {/* User List */}
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold">Current Users</h3>
                <Button onClick={() => {
                  setEditingUser(null);
                  resetForm();
                  setFormData(prev => ({ ...prev, role: selectedRole as any }));
                }}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add New User
                </Button>
              </div>
              
              <div className="space-y-2">
                {filteredUsers.map(user => (
                  <div key={user.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="font-medium">{user.full_name}</p>
                      <p className="text-sm text-gray-600">{user.email} • {user.username}</p>
                      <p className="text-sm text-gray-500">
                        {locations.find(loc => loc.id === user.location_id)?.name || user.location_id}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant={user.is_active ? 'default' : 'secondary'}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                      <Button variant="outline" size="sm" onClick={() => handleEditUser(user)}>
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => handleDeleteUser(user.id)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {/* User Form */}
            {(editingUser || !editingUser) && (
              <div className="border-t pt-6">
                <h3 className="text-lg font-semibold mb-4">
                  {editingUser ? 'Edit User' : 'Add New User'}
                </h3>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="username">Username</Label>
                    <Input
                      id="username"
                      value={formData.username}
                      onChange={(e) => setFormData(prev => ({ ...prev, username: e.target.value }))}
                      placeholder="Enter username"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                      placeholder="Enter email"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="full_name">Full Name</Label>
                    <Input
                      id="full_name"
                      value={formData.full_name}
                      onChange={(e) => setFormData(prev => ({ ...prev, full_name: e.target.value }))}
                      placeholder="Enter full name"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="location">Location</Label>
                    <Select value={formData.location_id} onValueChange={(value) => setFormData(prev => ({ ...prev, location_id: value }))}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select location" />
                      </SelectTrigger>
                      <SelectContent>
                        {locations.map(location => (
                          <SelectItem key={location.id} value={location.id}>
                            {location.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div>
                    <Label htmlFor="password">Password {editingUser && '(leave blank to keep current)'}</Label>
                    <Input
                      id="password"
                      type="password"
                      value={formData.password}
                      onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                      placeholder={editingUser ? "Leave blank to keep current" : "Enter password"}
                    />
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="is_active"
                      checked={formData.is_active}
                      onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.checked }))}
                    />
                    <Label htmlFor="is_active">Active User</Label>
                  </div>
                </div>
              </div>
            )}
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowUserModal(false)}>
              Cancel
            </Button>
            {(editingUser || !editingUser) && (
              <Button 
                onClick={editingUser ? handleUpdateUser : handleCreateUser}
                disabled={loading}
              >
                {loading ? 'Saving...' : (editingUser ? 'Update User' : 'Create User')}
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Location Management Modal */}
      <Dialog open={showLocationModal} onOpenChange={setShowLocationModal}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Location</DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="location-name">Location Name</Label>
                <Input
                  id="location-name"
                  value={locationFormData.name}
                  onChange={(e) => setLocationFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Enter location name"
                />
              </div>
              
              <div>
                <Label htmlFor="location-type">Location Type</Label>
                <Select value={locationFormData.location_type} onValueChange={(value) => setLocationFormData(prev => ({ ...prev, location_type: value as LocationType }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select location type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="headquarters">Headquarters</SelectItem>
                    <SelectItem value="production">Production</SelectItem>
                    <SelectItem value="distribution">Distribution</SelectItem>
                    <SelectItem value="warehouse">Warehouse</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="col-span-2">
                <Label htmlFor="location-address">Address</Label>
                <Input
                  id="location-address"
                  value={locationFormData.address}
                  onChange={(e) => setLocationFormData(prev => ({ ...prev, address: e.target.value }))}
                  placeholder="Enter street address"
                />
              </div>
              
              <div>
                <Label htmlFor="location-city">City</Label>
                <Input
                  id="location-city"
                  value={locationFormData.city}
                  onChange={(e) => setLocationFormData(prev => ({ ...prev, city: e.target.value }))}
                  placeholder="Enter city"
                />
              </div>
              
              <div>
                <Label htmlFor="location-state">State</Label>
                <Input
                  id="location-state"
                  value={locationFormData.state}
                  onChange={(e) => setLocationFormData(prev => ({ ...prev, state: e.target.value }))}
                  placeholder="Enter state"
                />
              </div>
              
              <div>
                <Label htmlFor="location-zip">ZIP Code</Label>
                <Input
                  id="location-zip"
                  value={locationFormData.zip_code}
                  onChange={(e) => setLocationFormData(prev => ({ ...prev, zip_code: e.target.value }))}
                  placeholder="Enter ZIP code"
                />
              </div>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowLocationModal(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdateLocation} disabled={loading}>
              {loading ? 'Updating...' : 'Update Location'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
