import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { DollarSign, TrendingUp, FileText, RefreshCw, Download, Upload, CheckCircle, AlertCircle, Plus } from 'lucide-react';
import { FinancialDashboard, Expense } from '../types/api';
import { apiRequest } from '../utils/api';
import { useErrorToast } from '../hooks/useErrorToast';


export function Financial() {
  const [financialData, setFinancialData] = useState<FinancialDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [importStatus, setImportStatus] = useState<Record<string, unknown> | null>(null);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [profitData, setProfitData] = useState<Record<string, unknown> | null>(null);
  const [showExpenseForm, setShowExpenseForm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newExpense, setNewExpense] = useState({
    date: new Date().toISOString().split('T')[0],
    category: 'fuel' as const,
    description: '',
    amount: '',
    location_id: 'loc_1'
  });
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { showError } = useErrorToast();

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [financialResponse, statusResponse, expensesResponse, profitResponse] = await Promise.all([
        apiRequest('/api/dashboard/financial'),
        apiRequest('/api/import/status'),
        apiRequest('/api/expenses'),
        apiRequest('/api/financial/profit-analysis')
      ]);
      
      const financialData = await financialResponse?.json();
      const statusData = await statusResponse?.json();
      const expensesData = await expensesResponse?.json();
      const profitAnalysis = await profitResponse?.json();
      
      setFinancialData(financialData || null);
      setImportStatus(statusData || null);
      setExpenses(Array.isArray(expensesData) ? expensesData : []);
      setProfitData(profitAnalysis || null);
    } catch (error) {
      console.error('Failed to fetch financial data:', error);
      setError('Failed to load financial data');
      showError(error, 'Failed to load financial data');
      setFinancialData(null);
      setImportStatus(null);
      setExpenses([]);
      setProfitData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    setUploadMessage('');

    try {
      const formData = new FormData();
      Array.from(files).forEach(file => {
        formData.append('files', file);
      });

      const response = await apiRequest('/api/import/excel', {
        method: 'POST',
        body: formData,
        headers: {}
      });

      const result = await response?.json();

      if (response?.ok) {
        setUploadMessage(`Successfully imported ${result.summary.customers_imported} customers and ${result.summary.orders_imported} orders!`);
        
        const [financialResponse, statusResponse, expensesResponse, profitResponse] = await Promise.all([
          apiRequest('/api/dashboard/financial'),
          apiRequest('/api/import/status'),
          apiRequest('/api/expenses'),
          apiRequest('/api/financial/profit-analysis')
        ]);
        
        const financialData = await financialResponse?.json();
        const statusData = await statusResponse?.json();
        const expensesData = await expensesResponse?.json();
        const profitAnalysis = await profitResponse?.json();
        
        setFinancialData(financialData);
        setImportStatus(statusData);
        setExpenses(expensesData);
        setProfitData(profitAnalysis);
      } else {
        setUploadMessage(`Error: ${result.detail || 'Failed to import data'}`);
      }
    } catch (error) {
      setUploadMessage(`Error: ${error instanceof Error ? error.message : 'Failed to upload files'}`);
      showError(error, 'Failed to upload files');
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const triggerFileUpload = () => {
    fileInputRef.current?.click();
  };

  const handleExpenseSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const response = await apiRequest('/api/expenses', {
        method: 'POST',
        body: JSON.stringify({
          ...newExpense,
          amount: parseFloat(newExpense.amount)
        }),
      });

      if (response?.ok) {
        const [expensesResponse, profitResponse, financialResponse] = await Promise.all([
          apiRequest('/api/expenses'),
          apiRequest('/api/financial/profit-analysis'),
          apiRequest('/api/dashboard/financial')
        ]);
        
        const expensesData = await expensesResponse?.json();
        const profitAnalysis = await profitResponse?.json();
        const financialData = await financialResponse?.json();
        
        setExpenses(expensesData);
        setProfitData(profitAnalysis);
        setFinancialData(financialData);
        setShowExpenseForm(false);
        setNewExpense({
          date: new Date().toISOString().split('T')[0],
          category: 'fuel',
          description: '',
          amount: '',
          location_id: 'loc_1'
        });
      }
    } catch (error) {
      console.error('Failed to create expense:', error);
      showError(error, 'Failed to submit expense');
    }
  };

  const paymentData = financialData ? [
    { name: 'Cash', value: financialData.payment_breakdown.cash, color: '#0088FE' },
    { name: 'Check', value: financialData.payment_breakdown.check, color: '#00C49F' },
    { name: 'Credit', value: financialData.payment_breakdown.credit, color: '#FFBB28' }
  ] : [];

  const revenueData = [
    { month: 'Jan', revenue: 320000 },
    { month: 'Feb', revenue: 345000 },
    { month: 'Mar', revenue: 365000 },
    { month: 'Apr', revenue: 380000 },
    { month: 'May', revenue: 375000 },
    { month: 'Jun', revenue: 390000 },
  ];


  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>;
  }

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardHeader>
          <CardTitle className="flex items-center text-red-800">
            <AlertCircle className="h-5 w-5 mr-2" />
            Financial Data Unavailable
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

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardHeader>
          <CardTitle className="flex items-center text-red-800">
            <AlertCircle className="h-5 w-5 mr-2" />
            Financial Data Unavailable
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
        <h1 className="text-3xl font-bold text-gray-900">Financial Management</h1>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={triggerFileUpload}
            disabled={uploading}
          >
            <Upload className="h-4 w-4 mr-2" />
            {uploading ? 'Importing...' : 'Import Excel Data'}
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".xlsx,.xls,.xlsm"
            onChange={handleFileUpload}
            style={{ display: 'none' }}
          />
          <Button size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Upload Status Message */}
      {uploadMessage && (
        <Card className={`border-l-4 ${uploadMessage.includes('Error') ? 'border-red-500 bg-red-50' : 'border-green-500 bg-green-50'}`}>
          <CardContent className="pt-4">
            <div className="flex items-center">
              {uploadMessage.includes('Error') ? (
                <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
              ) : (
                <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
              )}
              <span className={uploadMessage.includes('Error') ? 'text-red-700' : 'text-green-700'}>
                {uploadMessage}
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Import Status */}
      {importStatus && importStatus.has_data && (
        <Card className="border-l-4 border-blue-500 bg-blue-50">
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-blue-500 mr-2" />
                <span className="text-blue-700 font-medium">Real Data Loaded</span>
              </div>
              <div className="text-sm text-blue-600">
                {(importStatus as any).customers_count} customers • {(importStatus as any).orders_count} orders • 
                ${(importStatus as any).total_revenue?.toLocaleString()} total revenue
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Financial Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Daily Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${financialData?.daily_revenue?.toLocaleString() || '12,500'}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-600 flex items-center">
                <TrendingUp className="h-3 w-3 mr-1" />
                +15% from yesterday
              </span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Monthly Revenue</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${financialData?.monthly_revenue?.toLocaleString() || '375,000'}</div>
            <p className="text-xs text-muted-foreground">Current month total</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Outstanding Invoices</CardTitle>
            <FileText className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">${financialData?.outstanding_invoices?.toLocaleString() || '25,000'}</div>
            <p className="text-xs text-muted-foreground">Accounts receivable</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Daily Profit</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              ${financialData?.daily_profit?.toLocaleString() || '0'}
            </div>
            <p className="text-xs text-muted-foreground">Revenue - Expenses</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Payment Methods */}
        <Card>
          <CardHeader>
            <CardTitle>Payment Method Breakdown</CardTitle>
            <CardDescription>Revenue distribution by payment type</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={paymentData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {paymentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Revenue Trend */}
        <Card>
          <CardHeader>
            <CardTitle>Revenue Trend</CardTitle>
            <CardDescription>Monthly revenue over time</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={revenueData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => [`$${Number(value).toLocaleString()}`, 'Revenue']} />
                <Line type="monotone" dataKey="revenue" stroke="#3B82F6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Expense Tracking */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Expense Tracking</CardTitle>
              <CardDescription>Today's expenses and profit analysis</CardDescription>
            </div>
            <Button onClick={() => setShowExpenseForm(true)} size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Add Expense
            </Button>
          </CardHeader>
          <CardContent>
            {showExpenseForm && (
              <form onSubmit={handleExpenseSubmit} className="space-y-4 mb-6 p-4 border rounded-lg bg-gray-50">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="date">Date</Label>
                    <Input
                      id="date"
                      type="date"
                      value={newExpense.date}
                      onChange={(e) => setNewExpense({...newExpense, date: e.target.value})}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="category">Category</Label>
                    <Select value={newExpense.category} onValueChange={(value: any) => setNewExpense({...newExpense, category: value})}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="fuel">Fuel</SelectItem>
                        <SelectItem value="maintenance">Maintenance</SelectItem>
                        <SelectItem value="supplies">Supplies</SelectItem>
                        <SelectItem value="utilities">Utilities</SelectItem>
                        <SelectItem value="labor">Labor</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div>
                  <Label htmlFor="description">Description</Label>
                  <Input
                    id="description"
                    value={newExpense.description}
                    onChange={(e) => setNewExpense({...newExpense, description: e.target.value})}
                    placeholder="Enter expense description"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="amount">Amount</Label>
                  <Input
                    id="amount"
                    type="number"
                    step="0.01"
                    value={newExpense.amount}
                    onChange={(e) => setNewExpense({...newExpense, amount: e.target.value})}
                    placeholder="0.00"
                    required
                  />
                </div>
                <div className="flex space-x-2">
                  <Button type="submit">Add Expense</Button>
                  <Button type="button" variant="outline" onClick={() => setShowExpenseForm(false)}>
                    Cancel
                  </Button>
                </div>
              </form>
            )}
            
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="font-medium">Today's Expenses</span>
                <span className="text-lg font-bold text-red-600">
                  ${(profitData as any)?.daily_expenses?.toFixed(2) || '0.00'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="font-medium">Today's Revenue</span>
                <span className="text-lg font-bold text-green-600">
                  ${financialData?.daily_revenue?.toLocaleString() || '0'}
                </span>
              </div>
              <div className="flex justify-between items-center border-t pt-2">
                <span className="font-bold">Today's Profit</span>
                <span className="text-xl font-bold text-blue-600">
                  ${financialData?.daily_profit?.toLocaleString() || '0'}
                </span>
              </div>
            </div>

            <div className="mt-6">
              <h4 className="font-medium mb-3">Recent Expenses</h4>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {expenses.slice(0, 5).map((expense) => (
                  <div key={expense.id} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                    <div>
                      <div className="font-medium">{expense.description}</div>
                      <div className="text-sm text-gray-500">{expense.category} • {expense.date}</div>
                    </div>
                    <div className="text-red-600 font-medium">${expense.amount.toFixed(2)}</div>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Profit Analysis</CardTitle>
            <CardDescription>Revenue vs expenses breakdown</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm">Total Revenue</span>
                <span className="font-bold text-green-600">${profitData?.total_revenue?.toLocaleString() || '0'}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Total Expenses</span>
                <span className="font-bold text-red-600">${profitData?.total_expenses?.toLocaleString() || '0'}</span>
              </div>
              <div className="flex justify-between items-center border-t pt-2">
                <span className="font-bold">Net Profit</span>
                <span className="text-lg font-bold text-blue-600">${profitData?.profit?.toLocaleString() || '0'}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Profit Margin</span>
                <span className="font-medium">{(profitData as any)?.profit_margin?.toFixed(1) || '0'}%</span>
              </div>
            </div>

            {(profitData as any)?.expense_breakdown && (
              <div className="mt-6">
                <h4 className="font-medium mb-3">Expense Breakdown</h4>
                <div className="space-y-2">
                  {Object.entries((profitData as any).expense_breakdown).map(([category, amount]) => (
                    <div key={category} className="flex justify-between items-center">
                      <span className="text-sm capitalize">{category}</span>
                      <span className="font-medium">${(amount as number).toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Integration Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>QuickBooks Integration</CardTitle>
            <CardDescription>Accounting software sync</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm">Connection Status</span>
                <Badge className="bg-yellow-100 text-yellow-800">Setup Required</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Last Sync</span>
                <span className="text-sm text-gray-500">Never</span>
              </div>
              <Button className="w-full" variant="outline">
                Configure QuickBooks
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Excel Integration</CardTitle>
            <CardDescription>Spreadsheet data import/export</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm">Template Status</span>
                <Badge className="bg-green-100 text-green-800">Ready</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Last Import</span>
                <span className="text-sm text-gray-500">
                  {importStatus?.has_data ? 'Just now' : 'Never'}
                </span>
              </div>
              <Button 
                className="w-full" 
                variant="outline"
                onClick={triggerFileUpload}
                disabled={uploading}
              >
                <Upload className="h-4 w-4 mr-2" />
                {uploading ? 'Importing...' : 'Import Excel'}
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Google Sheets</CardTitle>
            <CardDescription>Cloud spreadsheet sync</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm">Connection Status</span>
                <Badge className="bg-yellow-100 text-yellow-800">Setup Required</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Auto Sync</span>
                <span className="text-sm text-gray-500">Disabled</span>
              </div>
              <Button className="w-full" variant="outline">
                Connect Google Sheets
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
