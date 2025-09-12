import { useState } from 'react';
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form';
import { Users, MapPin, Truck, Package, Save, LogOut, Plus, Edit, Trash2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { apiRequest, apiJson } from '../utils/api';
import { User, Location } from '../types/api';

const userSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  email: z.string().email('Invalid email').optional().or(z.literal('')),
  full_name: z.string().min(1, 'Full name is required'),
  role: z.enum(['manager', 'dispatcher', 'accountant', 'driver', 'customer']),
  location_id: z.string().min(1, 'Location is required'),
  password: z.string().optional(),
  is_active: z.boolean(),
});

const locationSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  address: z.string().min(1, 'Address is required'),
  city: z.string().min(1, 'City is required'),
  state: z.string().min(2, 'State is required'),
  zip_code: z.string().min(3, 'ZIP code is required'),
  location_type: z.enum(['distribution', 'production', 'warehouse']),
  is_active: z.boolean(),
});

type UserForm = z.infer<typeof userSchema>;
type LocationForm = z.infer<typeof locationSchema>;

export function Settings() {
  const { logout } = useAuth();
  const [showUserModal, setShowUserModal] = useState(false);
  const [showLocationModal, setShowLocationModal] = useState(false);
  const [selectedRole, setSelectedRole] = useState<string>('');
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [editingLocation, setEditingLocation] = useState<Location | null>(null);
  const queryClient = useQueryClient();

  const usersQuery = useQuery({
    queryKey: ['users'],
    queryFn: () => apiJson<User[]>('/api/users')
  });

  const locationsQuery = useQuery({
    queryKey: ['locations'],
    queryFn: () => apiJson<Location[]>('/api/locations')
  });

  const userForm = useForm<UserForm>({
    resolver: zodResolver(userSchema),
    defaultValues: {
      username: '',
      email: '',
      full_name: '',
      role: 'manager',
      location_id: '',
      password: '',
      is_active: true,
    },
  });

  const locationForm = useForm<LocationForm>({
    resolver: zodResolver(locationSchema),
    defaultValues: {
      name: '',
      address: '',
      city: '',
      state: '',
      zip_code: '',
      location_type: 'distribution',
      is_active: true,
    },
  });

  const createUserMutation = useMutation({
    mutationFn: (data: UserForm) =>
      apiJson('/api/users', { 
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data) 
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setShowUserModal(false);
      userForm.reset();
    },
  });

  const updateUserMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<UserForm> }) =>
      apiJson(`/api/users/${id}`, { 
        method: 'PUT', 
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data) 
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setShowUserModal(false);
      setEditingUser(null);
      userForm.reset();
    },
  });

  const deleteUserMutation = useMutation({
    mutationFn: (id: string) =>
      apiRequest(`/api/users/${id}`, { method: 'DELETE' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });

  const createLocationMutation = useMutation({
    mutationFn: (data: LocationForm) =>
      apiJson('/api/locations', { 
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data) 
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['locations'] });
      setShowLocationModal(false);
      locationForm.reset();
    },
  });

  const updateLocationMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<LocationForm> }) =>
      apiJson(`/api/locations/${id}`, { 
        method: 'PUT', 
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data) 
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['locations'] });
      setShowLocationModal(false);
      setEditingLocation(null);
      locationForm.reset();
    },
  });


  const handleManageUsers = (role: string) => {
    setSelectedRole(role);
    setEditingUser(null);
    userForm.reset({
      username: '',
      email: '',
      full_name: '',
      role: role as 'manager' | 'dispatcher' | 'accountant' | 'driver' | 'customer',
      location_id: '',
      password: '',
      is_active: true
    });
    setShowUserModal(true);
  };

  const handleEditUser = (user: User) => {
    setEditingUser(user);
    userForm.reset({
      username: user.username,
      email: user.email || '',
      full_name: user.full_name,
      role: user.role,
      location_id: user.location_id,
      password: '',
      is_active: user.is_active
    });
    setSelectedRole(user.role);
    setShowUserModal(true);
  };

  const handleEditLocation = (location: Location) => {
    setEditingLocation(location);
    locationForm.reset({
      name: location.name,
      address: location.address,
      city: location.city,
      state: location.state,
      zip_code: location.zip_code,
      location_type: location.location_type as 'distribution' | 'production' | 'warehouse',
      is_active: location.is_active
    });
    setShowLocationModal(true);
  };

  const users = usersQuery.data || [];
  const locations = locationsQuery.data || [];
  const filteredUsers = users.filter(user => user.role === selectedRole);
  const getUserCountByRole = (role: string) => users.filter(user => user.role === role).length;

  if (usersQuery.isLoading || locationsQuery.isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p>Loading settings...</p>
        </div>
      </div>
    );
  }

  if (usersQuery.error || locationsQuery.error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-red-600 mb-4">Failed to load settings data</p>
          <Button onClick={() => {
            usersQuery.refetch();
            locationsQuery.refetch();
          }}>
            Retry
          </Button>
        </div>
      </div>
    );
  }

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
              <Input id="company-email" defaultValue="info@yourchoiceice.com" autoComplete="email" />
            </div>
            <div>
              <Label htmlFor="company-website">Website</Label>
              <Input id="company-website" defaultValue="yourchoiceice.com" autoComplete="url" />
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
                <p className="text-sm text-gray-600">Advanced OR-Tools with depot constraints</p>
              </div>
              <Badge className="bg-green-100 text-green-800">Enhanced</Badge>
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
            
            {/* User List */}
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold">Current Users</h3>
                <Button onClick={() => {
                  setEditingUser(null);
                  userForm.reset({
                    username: '',
                    email: '',
                    full_name: '',
                    role: selectedRole as 'manager' | 'dispatcher' | 'accountant' | 'driver' | 'customer',
                    location_id: '',
                    password: '',
                    is_active: true
                  });
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
                      <Button variant="outline" size="sm" onClick={() => deleteUserMutation.mutate(user.id)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {/* User Form */}
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold mb-4">
                {editingUser ? 'Edit User' : 'Add New User'}
              </h3>
              
              <Form {...userForm}>
                <form id="user-form" onSubmit={userForm.handleSubmit((values) => {
                  if (editingUser) {
                    updateUserMutation.mutate({ id: editingUser.id, data: values });
                  } else {
                    createUserMutation.mutate(values);
                  }
                })} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <FormField
                      control={userForm.control}
                      name="username"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Username *</FormLabel>
                          <FormControl>
                            <Input placeholder="Enter username" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={userForm.control}
                      name="email"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Email</FormLabel>
                          <FormControl>
                            <Input type="email" placeholder="Enter email" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={userForm.control}
                      name="full_name"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Full Name *</FormLabel>
                          <FormControl>
                            <Input placeholder="Enter full name" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={userForm.control}
                      name="location_id"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Location *</FormLabel>
                          <FormControl>
                            <Select value={field.value} onValueChange={field.onChange}>
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
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    {!editingUser && (
                      <FormField
                        control={userForm.control}
                        name="password"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Password *</FormLabel>
                            <FormControl>
                              <Input type="password" placeholder="Enter password" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    )}
                    
                    <FormField
                      control={userForm.control}
                      name="is_active"
                      render={({ field }) => (
                        <FormItem className="flex items-center space-x-2">
                          <FormControl>
                            <input
                              type="checkbox"
                              checked={field.value}
                              onChange={field.onChange}
                            />
                          </FormControl>
                          <FormLabel>Active User</FormLabel>
                        </FormItem>
                      )}
                    />
                  </div>
                </form>
              </Form>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowUserModal(false)}>
              Cancel
            </Button>
            <Button 
              type="submit"
              form="user-form"
              disabled={createUserMutation.isPending || updateUserMutation.isPending}
            >
              {createUserMutation.isPending || updateUserMutation.isPending ? 'Saving...' : (editingUser ? 'Update User' : 'Create User')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Location Management Modal */}
      <Dialog open={showLocationModal} onOpenChange={setShowLocationModal}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Location</DialogTitle>
          </DialogHeader>
          
          <Form {...locationForm}>
            <form id="location-form" onSubmit={locationForm.handleSubmit((values) => {
              if (editingLocation) {
                updateLocationMutation.mutate({ id: editingLocation.id, data: values });
              } else {
                createLocationMutation.mutate(values);
              }
            })} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={locationForm.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Location Name *</FormLabel>
                      <FormControl>
                        <Input placeholder="Enter location name" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={locationForm.control}
                  name="location_type"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Location Type *</FormLabel>
                      <FormControl>
                        <Select value={field.value} onValueChange={field.onChange}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select location type" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="distribution">Distribution</SelectItem>
                            <SelectItem value="production">Production</SelectItem>
                            <SelectItem value="warehouse">Warehouse</SelectItem>
                          </SelectContent>
                        </Select>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={locationForm.control}
                  name="address"
                  render={({ field }) => (
                    <FormItem className="col-span-2">
                      <FormLabel>Address *</FormLabel>
                      <FormControl>
                        <Input placeholder="Enter street address" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={locationForm.control}
                  name="city"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>City *</FormLabel>
                      <FormControl>
                        <Input placeholder="Enter city" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={locationForm.control}
                  name="state"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>State *</FormLabel>
                      <FormControl>
                        <Input placeholder="Enter state" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={locationForm.control}
                  name="zip_code"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>ZIP Code *</FormLabel>
                      <FormControl>
                        <Input placeholder="Enter ZIP code" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={locationForm.control}
                  name="is_active"
                  render={({ field }) => (
                    <FormItem className="flex items-center space-x-2">
                      <FormControl>
                        <input
                          type="checkbox"
                          checked={field.value}
                          onChange={field.onChange}
                        />
                      </FormControl>
                      <FormLabel>Active Location</FormLabel>
                    </FormItem>
                  )}
                />
              </div>
            </form>
          </Form>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowLocationModal(false)}>
              Cancel
            </Button>
            <Button 
              type="submit"
              form="location-form"
              disabled={createLocationMutation.isPending || updateLocationMutation.isPending}
            >
              {createLocationMutation.isPending || updateLocationMutation.isPending ? 'Saving...' : (editingLocation ? 'Update Location' : 'Create Location')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
