import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { User, MapPin, Phone, Mail, Settings, LogOut } from 'lucide-react';

export function MobileProfile() {
  const currentUser = {
    name: 'Field Technician',
    role: 'technician',
    location: 'Mobile Unit',
    email: 'technician@arcticeicesolutions.com',
    phone: '(337) 555-0199',
    employeeId: 'TECH-001'
  };

  return (
    <div className="p-4 space-y-4">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Profile</h2>
      </div>

      <Card>
        <CardContent className="p-6 text-center">
          <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <User className="h-10 w-10 text-blue-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900">{currentUser.name}</h3>
          <Badge variant="secondary" className="mt-2">
            {currentUser.role.charAt(0).toUpperCase() + currentUser.role.slice(1)}
          </Badge>
          <p className="text-sm text-gray-500 mt-1">ID: {currentUser.employeeId}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Contact Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center space-x-3">
            <Mail className="h-5 w-5 text-gray-400" />
            <div>
              <p className="text-sm font-medium">{currentUser.email}</p>
              <p className="text-xs text-gray-500">Email</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <Phone className="h-5 w-5 text-gray-400" />
            <div>
              <p className="text-sm font-medium">{currentUser.phone}</p>
              <p className="text-xs text-gray-500">Phone</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <MapPin className="h-5 w-5 text-gray-400" />
            <div>
              <p className="text-sm font-medium">{currentUser.location}</p>
              <p className="text-xs text-gray-500">Location</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Quick Stats</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">12</div>
              <div className="text-xs text-gray-500">Work Orders Submitted</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">8</div>
              <div className="text-xs text-gray-500">Completed This Month</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-2">
        <Button variant="outline" className="w-full justify-start">
          <Settings className="h-4 w-4 mr-2" />
          Settings
        </Button>
        <Button variant="outline" className="w-full justify-start text-red-600 border-red-200 hover:bg-red-50">
          <LogOut className="h-4 w-4 mr-2" />
          Sign Out
        </Button>
      </div>

      <div className="text-center text-xs text-gray-500 pt-4">
        Arctic Ice Solutions Mobile App v1.0
      </div>
    </div>
  );
}
