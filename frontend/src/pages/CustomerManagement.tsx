import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Users, Search, Plus, RefreshCw, MapPin, Phone, Mail, AlertCircle, Star, MessageSquare, DollarSign, FileText, Edit, Save, X, Upload } from 'lucide-react';
import { Customer, Location, CustomerPricingDisplay } from '../types/api';
import { apiRequest } from '../utils/api';
import { useErrorToast } from '../hooks/useErrorToast';
import { useAuth } from '../contexts/AuthContext';


export function CustomerManagement() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [customersByLocationData, setCustomersByLocationData] = useState<Array<{location_id: string, location_name: string, customer_count: number}>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [showCustomerDetails, setShowCustomerDetails] = useState(false);
  const [showAddCustomerModal, setShowAddCustomerModal] = useState(false);
  const [showBulkImportModal, setShowBulkImportModal] = useState(false);
  const [importType, setImportType] = useState<'excel' | 'google-sheets'>('excel');
  const [importFiles, setImportFiles] = useState<FileList | null>(null);
  const [sheetsUrl, setSheetsUrl] = useState('');
  const [selectedLocationId, setSelectedLocationId] = useState('');
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState<any>(null);
  const [newCustomer, setNewCustomer] = useState({
    name: '',
    contact_person: '',
    phone: '',
    email: '',
    address: '',
    city: '',
    state: '',
    zip_code: '',
    location_id: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [customerPricing, setCustomerPricing] = useState<CustomerPricingDisplay[]>([]);
  const [editingPricing, setEditingPricing] = useState(false);
  const [pricingChanges, setPricingChanges] = useState<Record<string, number>>({});
  const [savingPricing, setSavingPricing] = useState(false);
  const { showError } = useErrorToast();
  const { user } = useAuth();

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [customersRes, locationsRes, customersByLocationRes] = await Promise.all([
        apiRequest('/api/customers'),
        apiRequest('/api/locations'),
        apiRequest('/api/customers/by-location')
      ]);

      const customersData = await customersRes?.json();
      const locationsData = await locationsRes?.json();
      const customersByLocationData = await customersByLocationRes?.json();

      setCustomers(Array.isArray(customersData) ? customersData : []);
      setLocations(Array.isArray(locationsData) ? locationsData : []);
      setCustomersByLocationData(Array.isArray(customersByLocationData) ? customersByLocationData : []);
    } catch (error) {
      console.error('Failed to fetch data:', error);
      setError('Failed to load customer data');
      setCustomers([]);
      setLocations([]);
      setCustomersByLocationData([]);
      showError(error, 'Failed to load customer data');
    } finally {
      setLoading(false);
    }
  };

  const handleAddCustomer = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newCustomer.name || !newCustomer.contact_person || !newCustomer.phone || 
        !newCustomer.address || !newCustomer.city || !newCustomer.state || 
        !newCustomer.zip_code || !newCustomer.location_id) {
      showError(new Error('Please fill in all required fields'), 'Missing required fields');
      return;
    }

    try {
      setSubmitting(true);
      
      const customerData = {
        id: crypto.randomUUID(),
        ...newCustomer,
        credit_limit: 5000,
        payment_terms: 30,
        is_active: true
      };

      const response = await apiRequest('/api/customers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(customerData),
      });

      if (response?.ok) {
        await fetchData();
        setShowAddCustomerModal(false);
        setNewCustomer({
          name: '',
          contact_person: '',
          phone: '',
          email: '',
          address: '',
          city: '',
          state: '',
          zip_code: '',
          location_id: ''
        });
      } else {
        throw new Error('Failed to create customer');
      }
    } catch (error) {
      console.error('Failed to create customer:', error);
      showError(error, 'Failed to create customer');
    } finally {
      setSubmitting(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const getLocationName = (locationId: string) => {
    if (!Array.isArray(locations)) return 'Unknown Location';
    const location = locations.find(l => l.id === locationId);
    return location ? location.name : 'Unknown Location';
  };

  const filteredCustomers = Array.isArray(customers) ? customers.filter(customer =>
    customer.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (customer.contact_person && customer.contact_person.toLowerCase().includes(searchTerm.toLowerCase())) ||
    customer.phone?.includes(searchTerm)
  ) : [];

  const customersByLocation = Array.isArray(customersByLocationData) ? customersByLocationData.map(item => ({
    location: item.location_name,
    count: item.customer_count
  })) : [];

  const fetchCustomerPricing = async (customerId: string) => {
    try {
      const response = await apiRequest(`/api/customers/${customerId}/pricing`);
      if (response?.ok) {
        const pricingData = await response.json();
        setCustomerPricing(pricingData);
      }
    } catch (error) {
      console.error('Failed to fetch customer pricing:', error);
    }
  };

  const handleEditPricing = () => {
    setEditingPricing(true);
    const changes: Record<string, number> = {};
    customerPricing.forEach(pricing => {
      if (pricing.custom_price !== null) {
        changes[pricing.product_id] = pricing.custom_price;
      }
    });
    setPricingChanges(changes);
  };

  const handlePricingChange = (productId: string, price: string) => {
    const numPrice = parseFloat(price);
    if (!isNaN(numPrice) && numPrice >= 0) {
      setPricingChanges(prev => ({
        ...prev,
        [productId]: numPrice
      }));
    } else if (price === '') {
      setPricingChanges(prev => {
        const newChanges = { ...prev };
        delete newChanges[productId];
        return newChanges;
      });
    }
  };

  const handleSavePricing = async () => {
    if (!selectedCustomer) return;
    
    try {
      setSavingPricing(true);
      
      for (const [productId, price] of Object.entries(pricingChanges)) {
        await apiRequest(`/api/customers/${selectedCustomer.id}/pricing`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            product_id: productId,
            custom_price: price
          }),
        });
      }

      const pricingToDelete = customerPricing.filter(pricing => 
        pricing.custom_price !== null && !pricingChanges[pricing.product_id]
      );

      for (const pricing of pricingToDelete) {
        await apiRequest(`/api/customers/${selectedCustomer.id}/pricing/${pricing.product_id}`, {
          method: 'DELETE',
        });
      }

      await fetchCustomerPricing(selectedCustomer.id);
      setEditingPricing(false);
      setPricingChanges({});
    } catch (error) {
      console.error('Failed to save pricing:', error);
      showError(error, 'Failed to save pricing');
    } finally {
      setSavingPricing(false);
    }
  };

  const handleCancelPricing = () => {
    setEditingPricing(false);
    setPricingChanges({});
  };

  const handleBulkImport = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedLocationId) {
      showError(new Error('Please select a location'), 'Location required');
      return;
    }

    if (importType === 'excel' && (!importFiles || importFiles.length === 0)) {
      showError(new Error('Please select Excel files to import'), 'Files required');
      return;
    }

    if (importType === 'google-sheets' && !sheetsUrl.trim()) {
      showError(new Error('Please enter a Google Sheets URL'), 'URL required');
      return;
    }

    try {
      setImporting(true);
      setImportResult(null);

      let response;
      if (importType === 'excel') {
        const formData = new FormData();
        Array.from(importFiles!).forEach(file => {
          formData.append('files', file);
        });
        formData.append('location_id', selectedLocationId);

        response = await apiRequest('/api/customers/bulk-import', {
          method: 'POST',
          body: formData,
        });
      } else {
        const formData = new FormData();
        formData.append('sheets_url', sheetsUrl);
        formData.append('location_id', selectedLocationId);

        response = await apiRequest('/api/customers/bulk-import-sheets', {
          method: 'POST',
          body: formData,
        });
      }

      if (response?.ok) {
        const result = await response.json();
        setImportResult(result);
        await fetchData();
        
        const summary = result.summary || {};
        let message = `Import successful!\n• ${summary.customers_imported || 0} customers imported\n• Location: ${summary.location_name || 'Unknown'}`;
        if (summary.duplicates_removed && summary.duplicates_removed > 0) {
          message += `\n• ${summary.duplicates_removed} duplicates removed`;
        }
        alert(message);
      } else {
        const errorData = response ? await response.json().catch(() => ({})) : {};
        throw new Error(errorData.detail || 'Import failed');
      }
    } catch (error) {
      console.error('Failed to import customers:', error);
      if (error instanceof Error && error.message.includes('400')) {
        showError(error, 'Invalid data format. Please check your files and try again.');
      } else {
        showError(error, 'Failed to import customers');
      }
    } finally {
      setImporting(false);
    }
  };

  const resetBulkImportModal = () => {
    setShowBulkImportModal(false);
    setImportType('excel');
    setImportFiles(null);
    setSheetsUrl('');
    setSelectedLocationId('');
    setImporting(false);
    setImportResult(null);
  };

  const isManager = user?.role === 'manager';

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>;
  }

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardHeader>
          <CardTitle className="flex items-center text-red-800">
            <AlertCircle className="h-5 w-5 mr-2" />
            Error Loading Data
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-700 mb-4">{error}</p>
          <Button onClick={fetchData} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Try Again
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Customer Management</h1>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline" size="sm" onClick={() => setShowBulkImportModal(true)}>
            <Upload className="h-4 w-4 mr-2" />
            Bulk Import
          </Button>
          <Button size="sm" onClick={() => setShowAddCustomerModal(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Customer
          </Button>
        </div>
      </div>

      {/* Customer Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Customers</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{customers.length}</div>
            <p className="text-xs text-muted-foreground">Active accounts</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">New This Month</CardTitle>
            <Plus className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">24</div>
            <p className="text-xs text-muted-foreground">+12% from last month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Credit Customers</CardTitle>
            <Users className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">156</div>
            <p className="text-xs text-muted-foreground">With credit terms</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Outstanding</CardTitle>
            <MapPin className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">$25,000</div>
            <p className="text-xs text-muted-foreground">Total receivables</p>
          </CardContent>
        </Card>
      </div>

      {/* Customers by Location */}
      <Card>
        <CardHeader>
          <CardTitle>Customers by Location</CardTitle>
          <CardDescription>Customer distribution across your service areas</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {customersByLocation.map((item) => (
              <div key={item.location} className="p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{item.location}</p>
                    <p className="text-2xl font-bold text-blue-600">{item.count}</p>
                  </div>
                  <MapPin className="h-8 w-8 text-gray-400" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Search and Filter */}
      <Card>
        <CardHeader>
          <CardTitle>Customer Directory</CardTitle>
          <CardDescription>Search and manage your customer accounts</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2 mb-6">
            <div className="relative flex-1">
              <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <Input
                placeholder="Search customers by name, contact, or phone..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                autoComplete="off"
                className="pl-10"
              />
            </div>
            <Button variant="outline">Filter</Button>
          </div>

          <div className="space-y-4">
            {filteredCustomers.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                {searchTerm ? 'No customers found matching your search.' : 'No customers found.'}
              </div>
            ) : (
              filteredCustomers.map((customer) => (
                <div key={customer.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                      <Users className="h-6 w-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold">{customer.name}</h3>
                      <p className="text-sm text-gray-600">{customer.contact_person || 'No contact person'}</p>
                      <div className="flex items-center space-x-4 mt-1">
                        <div className="flex items-center">
                          <Phone className="h-3 w-3 text-gray-400 mr-1" />
                          <span className="text-xs text-gray-500">{customer.phone}</span>
                        </div>
                        {customer.email && (
                          <div className="flex items-center">
                            <Mail className="h-3 w-3 text-gray-400 mr-1" />
                            <span className="text-xs text-gray-500">{customer.email}</span>
                          </div>
                        )}
                        <div className="flex items-center">
                          <MapPin className="h-3 w-3 text-gray-400 mr-1" />
                          <span className="text-xs text-gray-500">{customer.address || getLocationName(customer.location_id)}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="text-right mr-4">
                      <p className="text-sm font-medium">${(customer.credit_limit || 5000).toLocaleString()}</p>
                      <p className="text-xs text-gray-500">{customer.payment_terms || 30} day terms</p>
                      <p className="text-xs text-gray-400">Total: ${(customer.total_spent || 0).toLocaleString()}</p>
                    </div>
                    <Badge variant={(customer.status === 'active' || customer.is_active) ? "default" : "secondary"}>
                      {(customer.status === 'active' || customer.is_active) ? "Active" : "Inactive"}
                    </Badge>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={async () => {
                        setSelectedCustomer(customer);
                        setShowCustomerDetails(true);
                        if (isManager) {
                          await fetchCustomerPricing(customer.id);
                        }
                      }}
                    >
                      View Details
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>

      {/* Add Customer Modal */}
      {showAddCustomerModal && (
        <Dialog open={showAddCustomerModal} onOpenChange={setShowAddCustomerModal}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Add New Customer</DialogTitle>
            </DialogHeader>
            
            <form onSubmit={handleAddCustomer} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="name">Company Name *</Label>
                  <Input
                    id="name"
                    value={newCustomer.name}
                    onChange={(e) => setNewCustomer({...newCustomer, name: e.target.value})}
                    placeholder="Enter company name"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="contact_person">Contact Person *</Label>
                  <Input
                    id="contact_person"
                    value={newCustomer.contact_person}
                    onChange={(e) => setNewCustomer({...newCustomer, contact_person: e.target.value})}
                    placeholder="Enter contact person name"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="phone">Phone *</Label>
                  <Input
                    id="phone"
                    value={newCustomer.phone}
                    onChange={(e) => setNewCustomer({...newCustomer, phone: e.target.value})}
                    placeholder="Enter phone number"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={newCustomer.email}
                    onChange={(e) => setNewCustomer({...newCustomer, email: e.target.value})}
                    placeholder="Enter email address"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="address">Address *</Label>
                <Input
                  id="address"
                  value={newCustomer.address}
                  onChange={(e) => setNewCustomer({...newCustomer, address: e.target.value})}
                  placeholder="Enter street address"
                  required
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="city">City *</Label>
                  <Input
                    id="city"
                    value={newCustomer.city}
                    onChange={(e) => setNewCustomer({...newCustomer, city: e.target.value})}
                    placeholder="Enter city"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="state">State *</Label>
                  <Input
                    id="state"
                    value={newCustomer.state}
                    onChange={(e) => setNewCustomer({...newCustomer, state: e.target.value})}
                    placeholder="Enter state"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="zip_code">ZIP Code *</Label>
                  <Input
                    id="zip_code"
                    value={newCustomer.zip_code}
                    onChange={(e) => setNewCustomer({...newCustomer, zip_code: e.target.value})}
                    placeholder="Enter ZIP code"
                    required
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="location_id">Service Location *</Label>
                <Select value={newCustomer.location_id} onValueChange={(value) => setNewCustomer({...newCustomer, location_id: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a service location" />
                  </SelectTrigger>
                  <SelectContent>
                    {locations.map((location) => (
                      <SelectItem key={location.id} value={location.id}>
                        {location.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <DialogFooter>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => setShowAddCustomerModal(false)}
                  disabled={submitting}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={submitting}>
                  {submitting ? 'Creating...' : 'Create Customer'}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      )}

      {/* Bulk Import Modal */}
      {showBulkImportModal && (
        <Dialog open={showBulkImportModal} onOpenChange={setShowBulkImportModal}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Bulk Import Customers</DialogTitle>
              <DialogDescription>
                Import multiple customers from Excel files or Google Sheets
              </DialogDescription>
            </DialogHeader>
            
            <form onSubmit={handleBulkImport} className="space-y-4">
              <div>
                <Label htmlFor="location_id">Target Location *</Label>
                <Select value={selectedLocationId} onValueChange={setSelectedLocationId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select location for imported customers" />
                  </SelectTrigger>
                  <SelectContent>
                    {locations.map((location) => (
                      <SelectItem key={location.id} value={location.id}>
                        {location.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>Import Type</Label>
                <div className="flex space-x-4 mt-2">
                  <label className="flex items-center space-x-2">
                    <input
                      type="radio"
                      value="excel"
                      checked={importType === 'excel'}
                      onChange={(e) => setImportType(e.target.value as 'excel')}
                    />
                    <span>Excel Files</span>
                  </label>
                  <label className="flex items-center space-x-2">
                    <input
                      type="radio"
                      value="google-sheets"
                      checked={importType === 'google-sheets'}
                      onChange={(e) => setImportType(e.target.value as 'google-sheets')}
                    />
                    <span>Google Sheets</span>
                  </label>
                </div>
              </div>

              {importType === 'excel' ? (
                <div>
                  <Label htmlFor="files">Excel Files *</Label>
                  <Input
                    id="files"
                    type="file"
                    multiple
                    accept=".xlsx,.xls,.xlsm"
                    onChange={(e) => setImportFiles(e.target.files)}
                    required
                  />
                  <p className="text-sm text-gray-600 mt-1">
                    Select one or more Excel files containing customer data
                  </p>
                </div>
              ) : (
                <div>
                  <Label htmlFor="sheets_url">Google Sheets URL *</Label>
                  <Input
                    id="sheets_url"
                    type="url"
                    value={sheetsUrl}
                    onChange={(e) => setSheetsUrl(e.target.value)}
                    placeholder="https://docs.google.com/spreadsheets/d/..."
                    required
                  />
                  <p className="text-sm text-gray-600 mt-1">
                    Enter the URL of a Google Sheets document with customer data
                  </p>
                </div>
              )}

              {importResult && (
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <h4 className="font-medium text-green-800">Import Successful!</h4>
                  <p className="text-sm text-green-700">
                    Imported {importResult.summary?.customers_imported || 0} customers
                    {importResult.summary?.location_name && ` to ${importResult.summary.location_name}`}
                  </p>
                </div>
              )}

              <DialogFooter>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={resetBulkImportModal}
                  disabled={importing}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={importing}>
                  {importing ? 'Importing...' : 'Import Customers'}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      )}

      {/* Customer Details Modal */}
      {showCustomerDetails && selectedCustomer && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-xl font-semibold">{selectedCustomer.name}</h3>
                  <p className="text-gray-600">{selectedCustomer.contact_person}</p>
                </div>
                <Button 
                  variant="outline" 
                  onClick={() => {
                    setShowCustomerDetails(false);
                    setSelectedCustomer(null);
                    setCustomerPricing([]);
                    setEditingPricing(false);
                    setPricingChanges({});
                  }}
                >
                  Close
                </Button>
              </div>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Customer Info */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Users className="w-5 h-5 mr-2" />
                    Customer Information
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-600">Phone</label>
                      <p className="flex items-center">
                        <Phone className="w-4 h-4 mr-2 text-gray-400" />
                        {selectedCustomer.phone}
                      </p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-600">Email</label>
                      <p className="flex items-center">
                        <Mail className="w-4 h-4 mr-2 text-gray-400" />
                        {selectedCustomer.email || 'Not provided'}
                      </p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-600">Address</label>
                      <p className="flex items-center">
                        <MapPin className="w-4 h-4 mr-2 text-gray-400" />
                        {selectedCustomer.address}
                      </p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-600">Location</label>
                      <p>{getLocationName(selectedCustomer.location_id)}</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4 pt-4 border-t">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-blue-600">${(selectedCustomer.credit_limit || 5000).toLocaleString()}</p>
                      <p className="text-sm text-gray-600">Credit Limit</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-green-600">{selectedCustomer.payment_terms || 30} days</p>
                      <p className="text-sm text-gray-600">Payment Terms</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-purple-600">${(selectedCustomer.total_spent || 0).toLocaleString()}</p>
                      <p className="text-sm text-gray-600">Total Spent</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Custom Pricing - Only for Managers */}
              {isManager && (
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="flex items-center">
                        <DollarSign className="w-5 h-5 mr-2" />
                        Custom Pricing
                      </CardTitle>
                      {!editingPricing ? (
                        <Button variant="outline" size="sm" onClick={handleEditPricing}>
                          <Edit className="w-4 h-4 mr-2" />
                          Edit Prices
                        </Button>
                      ) : (
                        <div className="flex space-x-2">
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={handleCancelPricing}
                            disabled={savingPricing}
                          >
                            <X className="w-4 h-4 mr-2" />
                            Cancel
                          </Button>
                          <Button 
                            size="sm" 
                            onClick={handleSavePricing}
                            disabled={savingPricing}
                          >
                            <Save className="w-4 h-4 mr-2" />
                            {savingPricing ? 'Saving...' : 'Save'}
                          </Button>
                        </div>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {customerPricing.map((pricing) => (
                        <div key={pricing.product_id} className="flex items-center justify-between p-3 border rounded-lg">
                          <div>
                            <p className="font-medium">{pricing.product_name}</p>
                            <p className="text-sm text-gray-600">
                              Default: ${pricing.default_price.toFixed(2)}
                            </p>
                          </div>
                          <div className="flex items-center space-x-2">
                            {editingPricing ? (
                              <div className="flex items-center space-x-2">
                                <span className="text-sm text-gray-600">$</span>
                                <Input
                                  type="number"
                                  step="0.01"
                                  min="0"
                                  className="w-20"
                                  value={pricingChanges[pricing.product_id] ?? ''}
                                  onChange={(e) => handlePricingChange(pricing.product_id, e.target.value)}
                                  placeholder={pricing.default_price.toFixed(2)}
                                />
                              </div>
                            ) : (
                              <div className="text-right">
                                <p className="font-medium">
                                  ${(pricing.custom_price ?? pricing.default_price).toFixed(2)}
                                </p>
                                {pricing.custom_price !== null && (
                                  <Badge variant="secondary" className="text-xs">
                                    Custom
                                  </Badge>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                      {customerPricing.length === 0 && (
                        <div className="text-center py-4 text-gray-500">
                          Loading pricing information...
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Recent Orders */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <FileText className="w-5 h-5 mr-2" />
                    Recent Orders
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {[1, 2, 3].map((order) => (
                      <div key={order} className="flex justify-between items-center p-3 border rounded-lg">
                        <div>
                          <p className="font-medium">Order #ORD-2025-00{order}</p>
                          <p className="text-sm text-gray-600">January {20 + order}, 2025</p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">${(1200 + order * 100).toFixed(2)}</p>
                          <Badge variant="default">Delivered</Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Customer Feedback */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <MessageSquare className="w-5 h-5 mr-2" />
                    Customer Feedback
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {[
                      { rating: 5, subject: 'Excellent Service', message: 'Always on time and professional drivers.' },
                      { rating: 4, subject: 'Good Quality', message: 'Ice quality is consistently good.' }
                    ].map((feedback, index) => (
                      <div key={index} className="p-3 border rounded-lg">
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex items-center space-x-1">
                            {[1, 2, 3, 4, 5].map((star) => (
                              <Star
                                key={star}
                                className={`w-4 h-4 ${star <= feedback.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
                              />
                            ))}
                          </div>
                          <span className="text-xs text-gray-500">2 days ago</span>
                        </div>
                        <h4 className="font-medium">{feedback.subject}</h4>
                        <p className="text-sm text-gray-600">{feedback.message}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Payment History */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <DollarSign className="w-5 h-5 mr-2" />
                    Payment History
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {[
                      { date: 'Jan 20, 2025', amount: 1200, method: 'Credit Card', status: 'Completed' },
                      { date: 'Jan 15, 2025', amount: 850, method: 'Check', status: 'Completed' },
                      { date: 'Jan 10, 2025', amount: 1500, method: 'Account', status: 'Pending' }
                    ].map((payment, index) => (
                      <div key={index} className="flex justify-between items-center p-3 border rounded-lg">
                        <div>
                          <p className="font-medium">${payment.amount.toFixed(2)}</p>
                          <p className="text-sm text-gray-600">{payment.date} • {payment.method}</p>
                        </div>
                        <Badge variant={payment.status === 'Completed' ? 'default' : 'secondary'}>
                          {payment.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
