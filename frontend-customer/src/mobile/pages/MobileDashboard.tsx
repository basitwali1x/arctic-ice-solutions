import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Truck, AlertTriangle, CheckCircle, Clock, Wrench } from 'lucide-react';
import { API_BASE_URL } from '../../lib/constants';

interface DashboardData {
  total_vehicles: number;
  vehicles_in_use: number;
  vehicles_available: number;
  vehicles_maintenance: number;
  fleet_utilization: number;
}

interface WorkOrderSummary {
  pending: number;
  approved: number;
  in_progress: number;
  completed: number;
}

export function MobileDashboard() {
  const [fleetData, setFleetData] = useState<DashboardData | null>(null);
  const [workOrderSummary, setWorkOrderSummary] = useState<WorkOrderSummary>({
    pending: 0,
    approved: 0,
    in_progress: 0,
    completed: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [fleetResponse, workOrdersResponse] = await Promise.allSettled([
        fetch(`${API_BASE_URL}/api/dashboard/fleet`),
        fetch(`${API_BASE_URL}/api/maintenance/work-orders`)
      ]);

      let fleetData = null;
      let workOrders = [];

      if (fleetResponse.status === 'fulfilled' && fleetResponse.value.ok) {
        fleetData = await fleetResponse.value.json();
      }

      if (workOrdersResponse.status === 'fulfilled' && workOrdersResponse.value.ok) {
        workOrders = await workOrdersResponse.value.json();
      }

      setFleetData(fleetData);
      
      const summary = Array.isArray(workOrders) 
        ? workOrders.reduce((acc: WorkOrderSummary, order: { status: keyof WorkOrderSummary }) => {
            acc[order.status as keyof WorkOrderSummary]++;
            return acc;
          }, { pending: 0, approved: 0, in_progress: 0, completed: 0 })
        : { pending: 0, approved: 0, in_progress: 0, completed: 0 };
      
      setWorkOrderSummary(summary);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setFleetData(null);
      setWorkOrderSummary({ pending: 0, approved: 0, in_progress: 0, completed: 0 });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-4 space-y-4">
        <div className="animate-pulse space-y-4">
          <div className="h-24 bg-gray-200 rounded-lg"></div>
          <div className="h-24 bg-gray-200 rounded-lg"></div>
          <div className="h-24 bg-gray-200 rounded-lg"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Dashboard</h2>
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center space-x-2">
            <Truck className="h-5 w-5 text-blue-600" />
            <span>Fleet Status</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {fleetData?.vehicles_available || 0}
              </div>
              <div className="text-xs text-gray-500">Available</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {fleetData?.vehicles_in_use || 0}
              </div>
              <div className="text-xs text-gray-500">In Use</div>
            </div>
          </div>
          <div className="text-center">
            <Badge variant="outline" className="text-xs">
              {fleetData?.fleet_utilization || 0}% Utilization
            </Badge>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center space-x-2">
            <Wrench className="h-5 w-5 text-orange-600" />
            <span>Work Orders</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-3">
            <div className="flex items-center space-x-2 p-2 bg-orange-50 rounded-lg">
              <AlertTriangle className="h-4 w-4 text-orange-600" />
              <div>
                <div className="text-lg font-bold text-orange-600">
                  {workOrderSummary.pending}
                </div>
                <div className="text-xs text-gray-600">Pending</div>
              </div>
            </div>
            <div className="flex items-center space-x-2 p-2 bg-blue-50 rounded-lg">
              <Clock className="h-4 w-4 text-blue-600" />
              <div>
                <div className="text-lg font-bold text-blue-600">
                  {workOrderSummary.in_progress}
                </div>
                <div className="text-xs text-gray-600">In Progress</div>
              </div>
            </div>
            <div className="flex items-center space-x-2 p-2 bg-green-50 rounded-lg">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <div>
                <div className="text-lg font-bold text-green-600">
                  {workOrderSummary.approved}
                </div>
                <div className="text-xs text-gray-600">Approved</div>
              </div>
            </div>
            <div className="flex items-center space-x-2 p-2 bg-gray-50 rounded-lg">
              <CheckCircle className="h-4 w-4 text-gray-600" />
              <div>
                <div className="text-lg font-bold text-gray-600">
                  {workOrderSummary.completed}
                </div>
                <div className="text-xs text-gray-600">Completed</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <button className="w-full p-3 bg-blue-600 text-white rounded-lg text-sm font-medium">
              Submit New Work Order
            </button>
            <button className="w-full p-3 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium">
              View Vehicle Status
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
