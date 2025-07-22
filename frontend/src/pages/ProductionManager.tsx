import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Factory, Package, Clock, AlertCircle, RefreshCw } from 'lucide-react';
import { apiRequest } from '../utils/api';
import { useErrorToast } from '../hooks/useErrorToast';

interface ProductionEntry {
  id: string;
  date: string;
  shift: 1 | 2;
  pallets_8lb: number;
  pallets_20lb: number;
  pallets_block_ice: number;
  total_pallets: number;
  submitted_by: string;
  submitted_at: string;
}

interface ProductionTarget {
  daily_target: number;
  shift_1_target: number;
  shift_2_target: number;
}

export function ProductionManager() {
  const [productionEntries, setProductionEntries] = useState<ProductionEntry[]>([]);
  const [targets] = useState<ProductionTarget>({
    daily_target: 160,
    shift_1_target: 80,
    shift_2_target: 80
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { showError } = useErrorToast();
  
  const [formData, setFormData] = useState({
    shift: 1,
    pallets_8lb: '',
    pallets_20lb: '',
    pallets_block_ice: ''
  });

  const fetchProductionData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiRequest('/api/production/entries');
      const data = await response?.json();
      
      setProductionEntries(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error fetching production data:', error);
      setError('Failed to load production data');
      setProductionEntries([]);
      showError(error, 'Failed to load production data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProductionData();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const pallets_8lb = parseInt(formData.pallets_8lb) || 0;
    const pallets_20lb = parseInt(formData.pallets_20lb) || 0;
    const pallets_block_ice = parseInt(formData.pallets_block_ice) || 0;
    
    try {
      const response = await apiRequest('/api/production/entries', {
        method: 'POST',
        body: JSON.stringify({
          shift: formData.shift,
          pallets_8lb,
          pallets_20lb,
          pallets_block_ice,
          total_pallets: pallets_8lb + pallets_20lb + pallets_block_ice
        }),
      });

      if (response?.ok) {
        setFormData({
          shift: 1,
          pallets_8lb: '',
          pallets_20lb: '',
          pallets_block_ice: ''
        });
        fetchProductionData();
      }
    } catch (error) {
      console.error('Error submitting production data:', error);
      showError(error, 'Failed to submit production data');
    }
  };

  const todayEntries = productionEntries.filter(entry => 
    entry.date === new Date().toISOString().split('T')[0]
  );
  
  const todayTotal = todayEntries.reduce((sum, entry) => sum + entry.total_pallets, 0);
  const shift1Today = todayEntries.find(entry => entry.shift === 1)?.total_pallets || 0;
  const shift2Today = todayEntries.find(entry => entry.shift === 2)?.total_pallets || 0;

  const dailyProgress = (todayTotal / targets.daily_target) * 100;
  const shift1Progress = (shift1Today / targets.shift_1_target) * 100;
  const shift2Progress = (shift2Today / targets.shift_2_target) * 100;

  if (loading) {
    return <div className="p-6">Loading production data...</div>;
  }

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardHeader>
          <CardTitle className="flex items-center text-red-800">
            <AlertCircle className="h-5 w-5 mr-2" />
            Production Data Unavailable
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-700 mb-4">{error}</p>
          <Button onClick={fetchProductionData} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Try Again
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Production Manager</h1>
        <Badge variant="outline" className="flex items-center space-x-1">
          <Factory className="h-4 w-4" />
          <span>Leesville HQ Production</span>
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Today's Production</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{todayTotal}</div>
            <div className="text-sm text-gray-500">
              Target: {targets.daily_target} ({dailyProgress.toFixed(1)}%)
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div 
                className="bg-blue-600 h-2 rounded-full" 
                style={{ width: `${Math.min(dailyProgress, 100)}%` }}
              ></div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Shift 1</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{shift1Today}</div>
            <div className="text-sm text-gray-500">
              Target: {targets.shift_1_target} ({shift1Progress.toFixed(1)}%)
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div 
                className="bg-green-600 h-2 rounded-full" 
                style={{ width: `${Math.min(shift1Progress, 100)}%` }}
              ></div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Shift 2</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{shift2Today}</div>
            <div className="text-sm text-gray-500">
              Target: {targets.shift_2_target} ({shift2Progress.toFixed(1)}%)
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div 
                className="bg-orange-600 h-2 rounded-full" 
                style={{ width: `${Math.min(shift2Progress, 100)}%` }}
              ></div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Efficiency</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dailyProgress.toFixed(1)}%</div>
            <div className="text-sm text-gray-500">Daily Target Progress</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Package className="h-5 w-5" />
              <span>Submit Production Data</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="shift">Shift</Label>
                <select
                  id="shift"
                  value={formData.shift}
                  onChange={(e) => setFormData({...formData, shift: parseInt(e.target.value) as 1 | 2})}
                  className="w-full p-2 border rounded-md"
                >
                  <option value={1}>Shift 1</option>
                  <option value={2}>Shift 2</option>
                </select>
              </div>

              <div>
                <Label htmlFor="pallets_8lb">8lb Bag Pallets</Label>
                <Input
                  id="pallets_8lb"
                  type="number"
                  value={formData.pallets_8lb}
                  autoComplete="off"
                  onChange={(e) => setFormData({...formData, pallets_8lb: e.target.value})}
                  placeholder="Enter number of 8lb pallets"
                  min="0"
                />
              </div>

              <div>
                <Label htmlFor="pallets_20lb">20lb Bag Pallets</Label>
                <Input
                  id="pallets_20lb"
                  type="number"
                  value={formData.pallets_20lb}
                  autoComplete="off"
                  onChange={(e) => setFormData({...formData, pallets_20lb: e.target.value})}
                  placeholder="Enter number of 20lb pallets"
                  min="0"
                />
              </div>

              <div>
                <Label htmlFor="pallets_block_ice">Block Ice Pallets</Label>
                <Input
                  id="pallets_block_ice"
                  type="number"
                  value={formData.pallets_block_ice}
                  autoComplete="off"
                  onChange={(e) => setFormData({...formData, pallets_block_ice: e.target.value})}
                  placeholder="Enter number of block ice pallets"
                  min="0"
                />
              </div>

              <div className="pt-2">
                <div className="text-sm text-gray-600 mb-2">
                  Total Pallets: {
                    (parseInt(formData.pallets_8lb) || 0) + 
                    (parseInt(formData.pallets_20lb) || 0) + 
                    (parseInt(formData.pallets_block_ice) || 0)
                  }
                </div>
                <Button type="submit" className="w-full">
                  Submit Production Data
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Clock className="h-5 w-5" />
              <span>Recent Entries</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {productionEntries.slice(0, 5).map((entry) => (
              <div key={entry.id} className="border rounded-lg p-3 space-y-2">
                <div className="flex items-center justify-between">
                  <Badge variant="outline">
                    Shift {entry.shift} - {entry.date}
                  </Badge>
                  <span className="text-sm font-medium">{entry.total_pallets} pallets</span>
                </div>
                <div className="text-sm text-gray-600 grid grid-cols-3 gap-2">
                  <span>8lb: {entry.pallets_8lb}</span>
                  <span>20lb: {entry.pallets_20lb}</span>
                  <span>Block: {entry.pallets_block_ice}</span>
                </div>
                <div className="text-xs text-gray-500">
                  By {entry.submitted_by} at {new Date(entry.submitted_at).toLocaleTimeString()}
                </div>
              </div>
            ))}
            {productionEntries.length === 0 && (
              <p className="text-gray-500">No production entries yet</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
