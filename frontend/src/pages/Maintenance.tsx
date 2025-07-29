import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Wrench, CheckCircle, XCircle, Clock, AlertTriangle, RefreshCw } from 'lucide-react';
import { apiRequest } from '../utils/api';
import { useErrorToast } from '../hooks/useErrorToast';

interface WorkOrder {
  id: string;
  vehicle_id: string;
  vehicle_name: string;
  technician_name: string;
  issue_description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'approved' | 'in_progress' | 'completed' | 'rejected';
  submitted_date: string;
  estimated_cost: number;
  estimated_hours: number;
  work_type: 'mechanical' | 'refrigeration' | 'electrical' | 'body';
}


export function Maintenance() {
  const [workOrders, setWorkOrders] = useState<WorkOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { showError } = useErrorToast();

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const workOrdersRes = await apiRequest('/api/maintenance/work-orders');
      const workOrdersData = await workOrdersRes?.json();
      setWorkOrders(Array.isArray(workOrdersData) ? workOrdersData : []);
    } catch (error) {
      console.error('Failed to fetch maintenance data:', error);
      setError('Failed to load maintenance data');
      setWorkOrders([]);
      showError(error, 'Failed to load maintenance data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>;
  }

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardHeader>
          <CardTitle className="flex items-center text-red-800">
            <AlertTriangle className="h-5 w-5 mr-2" />
            Maintenance Data Unavailable
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


  const handleApprove = async (workOrderId: string) => {
    try {
      await apiRequest(`/api/maintenance/work-orders/${workOrderId}/approve`, {
        method: 'POST',
      });
      fetchData();
    } catch (error) {
      console.error('Error approving work order:', error);
      showError(error, 'Failed to approve work order');
    }
  };

  const handleReject = async (workOrderId: string) => {
    try {
      await apiRequest(`/api/maintenance/work-orders/${workOrderId}/reject`, {
        method: 'POST',
      });
      fetchData();
    } catch (error) {
      console.error('Error rejecting work order:', error);
      showError(error, 'Failed to reject work order');
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return <Clock className="h-4 w-4" />;
      case 'approved': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'rejected': return <XCircle className="h-4 w-4 text-red-500" />;
      case 'in_progress': return <Wrench className="h-4 w-4 text-blue-500" />;
      case 'completed': return <CheckCircle className="h-4 w-4 text-green-600" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  const pendingOrders = workOrders.filter(order => order.status === 'pending');
  const approvedOrders = workOrders.filter(order => order.status === 'approved');
  const inProgressOrders = workOrders.filter(order => order.status === 'in_progress');
  const completedOrders = workOrders.filter(order => order.status === 'completed');

  if (loading) {
    return <div className="p-6">Loading maintenance data...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Maintenance Management</h1>
        <div className="flex items-center space-x-4">
          <Badge variant="outline" className="flex items-center space-x-1">
            <AlertTriangle className="h-4 w-4" />
            <span>{pendingOrders.length} Pending</span>
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Pending Approval</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{pendingOrders.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Approved</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{approvedOrders.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{inProgressOrders.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-600">{completedOrders.length}</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-orange-500" />
              <span>Pending Work Orders</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {pendingOrders.length === 0 ? (
              <p className="text-gray-500">No pending work orders</p>
            ) : (
              pendingOrders.map((order) => (
                <div key={order.id} className="border rounded-lg p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Badge className={getPriorityColor(order.priority)}>
                        {order.priority.toUpperCase()}
                      </Badge>
                      <span className="font-medium">{order.vehicle_name}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      {getStatusIcon(order.status)}
                      <span className="text-sm text-gray-500">{order.status}</span>
                    </div>
                  </div>
                  
                  <div className="text-sm space-y-1">
                    <p><strong>Technician:</strong> {order.technician_name}</p>
                    <p><strong>Issue:</strong> {order.issue_description}</p>
                    <p><strong>Type:</strong> {order.work_type}</p>
                    <p><strong>Estimated Cost:</strong> ${order.estimated_cost.toFixed(2)}</p>
                    <p><strong>Estimated Hours:</strong> {order.estimated_hours}h</p>
                  </div>

                  <div className="flex space-x-2">
                    <Button 
                      size="sm" 
                      onClick={() => handleApprove(order.id)}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      <CheckCircle className="h-4 w-4 mr-1" />
                      Approve
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => handleReject(order.id)}
                      className="border-red-500 text-red-500 hover:bg-red-50"
                    >
                      <XCircle className="h-4 w-4 mr-1" />
                      Reject
                    </Button>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Wrench className="h-5 w-5 text-blue-500" />
              <span>Active Work Orders</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {[...approvedOrders, ...inProgressOrders].length === 0 ? (
              <p className="text-gray-500">No active work orders</p>
            ) : (
              [...approvedOrders, ...inProgressOrders].map((order) => (
                <div key={order.id} className="border rounded-lg p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Badge className={getPriorityColor(order.priority)}>
                        {order.priority.toUpperCase()}
                      </Badge>
                      <span className="font-medium">{order.vehicle_name}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      {getStatusIcon(order.status)}
                      <span className="text-sm text-gray-500">{order.status}</span>
                    </div>
                  </div>
                  
                  <div className="text-sm space-y-1">
                    <p><strong>Technician:</strong> {order.technician_name}</p>
                    <p><strong>Issue:</strong> {order.issue_description}</p>
                    <p><strong>Type:</strong> {order.work_type}</p>
                    <p><strong>Cost:</strong> ${order.estimated_cost.toFixed(2)}</p>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
