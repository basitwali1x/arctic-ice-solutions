import React from 'react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Truck, Users, BarChart3, Wrench, Phone, Mail, MapPin, Play } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="text-2xl font-bold text-blue-600">Arctic Ice Solutions</div>
              <Badge variant="secondary" className="ml-3">Business Management System</Badge>
            </div>
            <Button onClick={() => navigate('/login')} className="bg-blue-600 hover:bg-blue-700">
              Staff Login
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Complete Business Management for Ice Manufacturing & Distribution
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Streamline your ice manufacturing and distribution operations with our comprehensive platform. 
            Manage fleet, optimize routes, track production, and serve customers across multiple locations.
          </p>
          <div className="flex justify-center space-x-4">
            <Button size="lg" onClick={() => navigate('/login')} className="bg-blue-600 hover:bg-blue-700">
              Get Started
            </Button>
            <Button size="lg" variant="outline" className="flex items-center">
              <Play className="w-4 h-4 mr-2" />
              Watch Demo
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Everything You Need to Run Your Ice Business
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <Card>
              <CardHeader>
                <Truck className="w-8 h-8 text-blue-600 mb-2" />
                <CardTitle>Fleet Management</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Track 8 refrigerated vehicles, optimize routes with AI, and monitor real-time GPS locations.
                </CardDescription>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <Users className="w-8 h-8 text-blue-600 mb-2" />
                <CardTitle>Customer Management</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Manage 536+ customer accounts with custom pricing, credit terms, and multi-location distribution.
                </CardDescription>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <BarChart3 className="w-8 h-8 text-blue-600 mb-2" />
                <CardTitle>Production Tracking</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Monitor daily production (80-160 pallets/day), track inventory, and manage shift operations.
                </CardDescription>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <Wrench className="w-8 h-8 text-blue-600 mb-2" />
                <CardTitle>Maintenance System</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Submit work orders, track vehicle maintenance, and manage technician assignments.
                </CardDescription>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* QuickStart Guide Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">QuickStart Guide</h2>
          <div className="space-y-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <span className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold mr-3">1</span>
                  Login & Dashboard Overview
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">
                  Access the system with your role-based credentials. The dashboard provides real-time business metrics including:
                </p>
                <ul className="list-disc list-inside text-gray-600 space-y-1">
                  <li>Total customers and active orders</li>
                  <li>Fleet utilization and vehicle status</li>
                  <li>Daily revenue and production metrics</li>
                  <li>Outstanding invoices and payment tracking</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <span className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold mr-3">2</span>
                  Create & Manage Orders
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">
                  Process customer orders efficiently:
                </p>
                <ul className="list-disc list-inside text-gray-600 space-y-1">
                  <li>Navigate to Customer Management → Add New Order</li>
                  <li>Select products (8lb bags, 20lb bags, block ice)</li>
                  <li>Apply customer-specific pricing if configured</li>
                  <li>Assign to appropriate location and delivery route</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <span className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold mr-3">3</span>
                  Optimize Routes & Assign Vehicles
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">
                  Use AI-powered route optimization:
                </p>
                <ul className="list-disc list-inside text-gray-600 space-y-1">
                  <li>Go to Fleet Management → Route Optimization</li>
                  <li>Select delivery date and location constraints</li>
                  <li>Review optimized routes with distance and time estimates</li>
                  <li>Assign routes to available vehicles and drivers</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <span className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold mr-3">4</span>
                  Submit Work Orders
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">
                  Manage vehicle maintenance:
                </p>
                <ul className="list-disc list-inside text-gray-600 space-y-1">
                  <li>Access Maintenance → Submit Work Order</li>
                  <li>Select vehicle and describe the issue</li>
                  <li>Set priority level and estimated cost</li>
                  <li>Track approval status and technician assignment</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <span className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold mr-3">5</span>
                  Monitor Production & Logout
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">
                  Track daily operations and secure logout:
                </p>
                <ul className="list-disc list-inside text-gray-600 space-y-1">
                  <li>Use Production Manager to input daily pallet counts</li>
                  <li>Monitor shift performance and efficiency metrics</li>
                  <li>Review financial summaries and expense tracking</li>
                  <li>Always logout securely using the logout button in header/settings</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section className="py-16 bg-blue-600 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-8">Ready to Get Started?</h2>
          <p className="text-xl mb-8">
            Contact us to set up your pilot depot and begin using the Arctic Ice Solutions platform.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            <div className="flex items-center justify-center">
              <Phone className="w-6 h-6 mr-3" />
              <span>(337) 555-0100</span>
            </div>
            <div className="flex items-center justify-center">
              <Mail className="w-6 h-6 mr-3" />
              <span>support@yourchoiceice.com</span>
            </div>
            <div className="flex items-center justify-center">
              <MapPin className="w-6 h-6 mr-3" />
              <span>Louisiana & Texas</span>
            </div>
          </div>
          <Button size="lg" variant="secondary" onClick={() => navigate('/login')}>
            Start Your Pilot Today
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p>&copy; 2025 Arctic Ice Solutions. All rights reserved.</p>
          <p className="text-gray-400 mt-2">Comprehensive business management across Louisiana and Texas operations</p>
        </div>
      </footer>
    </div>
  );
};
