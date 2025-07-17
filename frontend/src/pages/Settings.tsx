import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Users, MapPin, Truck, Package, Save } from 'lucide-react';

export function Settings() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <Button>
          <Save className="h-4 w-4 mr-2" />
          Save Changes
        </Button>
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
              <Input id="company-name" defaultValue="Arctic Ice Solutions" />
            </div>
            <div>
              <Label htmlFor="company-phone">Phone Number</Label>
              <Input id="company-phone" defaultValue="(337) 555-0123" />
            </div>
            <div>
              <Label htmlFor="company-email">Email Address</Label>
              <Input id="company-email" defaultValue="info@arcticeicesolutions.com" />
            </div>
            <div>
              <Label htmlFor="company-website">Website</Label>
              <Input id="company-website" defaultValue="www.arcticeicesolutions.com" />
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
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center space-x-3">
                <MapPin className="h-5 w-5 text-blue-600" />
                <div>
                  <p className="font-medium">Leesville HQ & Production</p>
                  <p className="text-sm text-gray-600">123 Ice Plant Rd, Leesville, LA 71446</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Badge>Headquarters</Badge>
                <Button variant="outline" size="sm">Edit</Button>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center space-x-3">
                <MapPin className="h-5 w-5 text-green-600" />
                <div>
                  <p className="font-medium">Lake Charles Distribution</p>
                  <p className="text-sm text-gray-600">456 Distribution Ave, Lake Charles, LA 70601</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Badge variant="secondary">Distribution</Badge>
                <Button variant="outline" size="sm">Edit</Button>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center space-x-3">
                <MapPin className="h-5 w-5 text-yellow-600" />
                <div>
                  <p className="font-medium">Lufkin Distribution</p>
                  <p className="text-sm text-gray-600">789 Delivery St, Lufkin, TX 75901</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Badge variant="secondary">Distribution</Badge>
                <Button variant="outline" size="sm">Edit</Button>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center space-x-3">
                <MapPin className="h-5 w-5 text-gray-600" />
                <div>
                  <p className="font-medium">Jasper Warehouse</p>
                  <p className="text-sm text-gray-600">321 Storage Blvd, Jasper, TX 75951</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Badge variant="outline">Warehouse</Badge>
                <Button variant="outline" size="sm">Edit</Button>
              </div>
            </div>
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
                  <p className="font-medium">Managers (3 users)</p>
                  <p className="text-sm text-gray-600">Full system access</p>
                </div>
              </div>
              <Button variant="outline" size="sm">Manage</Button>
            </div>

            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center space-x-3">
                <Truck className="h-5 w-5 text-green-600" />
                <div>
                  <p className="font-medium">Dispatchers (4 users)</p>
                  <p className="text-sm text-gray-600">Fleet and route management</p>
                </div>
              </div>
              <Button variant="outline" size="sm">Manage</Button>
            </div>

            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center space-x-3">
                <Package className="h-5 w-5 text-yellow-600" />
                <div>
                  <p className="font-medium">Accountants (3 users)</p>
                  <p className="text-sm text-gray-600">Financial management</p>
                </div>
              </div>
              <Button variant="outline" size="sm">Manage</Button>
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
              <Input className="w-32" defaultValue="160" />
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
    </div>
  );
}
