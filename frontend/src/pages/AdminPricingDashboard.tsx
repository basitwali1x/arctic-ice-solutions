import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Alert, AlertDescription } from '../components/ui/alert';
import { 
  DollarSign, 
  Users, 
  TrendingUp, 
  AlertTriangle,
  BarChart3,
  PieChart,
  Settings
} from 'lucide-react';
import { Customer, PricingRule, PricingAudit } from '../types/api';
import { apiRequest } from '../utils/api';
// import { useErrorToast } from '../hooks/useErrorToast';

export default function AdminPricingDashboard() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [pricingRules, setPricingRules] = useState<PricingRule[]>([]);
  const [auditData, setAuditData] = useState<PricingAudit | null>(null);
  const [alerts, setAlerts] = useState<Array<{id: number, message: string, severity: string}>>([]);
  const [loading, setLoading] = useState(true);
  // const { showError } = useErrorToast();
  const showError = (message: string) => console.error(message);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [customersRes, rulesRes, auditRes] = await Promise.all([
        apiRequest('/api/customers'),
        apiRequest('/api/pricing/rules'),
        apiRequest('/api/pricing/audit')
      ]);
      
      if (customersRes && Array.isArray(customersRes)) {
        setCustomers(customersRes as unknown as Customer[]);
      } else {
        setCustomers([]);
      }
      if (rulesRes && Array.isArray(rulesRes)) {
        setPricingRules(rulesRes as unknown as PricingRule[]);
      } else {
        setPricingRules([]);
      }
      if (auditRes) setAuditData(auditRes as unknown as PricingAudit);
      
      const newAlerts = [];
      if (auditRes && (auditRes as unknown as PricingAudit).pricing_adjustments?.some((adj: any) => adj.surcharge && adj.surcharge > 10)) {
        newAlerts.push({
          id: 1,
          message: "High surge pricing detected for special events",
          severity: "warning"
        });
      }
      setAlerts(newAlerts);
    } catch (error) {
      showError('Failed to load pricing data');
    } finally {
      setLoading(false);
    }
  };

  const handleTierChange = async (customerId: string, newTier: string) => {
    try {
      await apiRequest(`/api/customers/${customerId}/tier`, {
        method: 'PATCH',
        body: JSON.stringify({ tier: newTier })
      });
      
      setCustomers(customers.map(c => 
        c.id === customerId ? { ...c, tier: newTier as any } : c
      ));
    } catch (error) {
      showError('Failed to update customer tier');
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'gold': return 'bg-yellow-100 text-yellow-800';
      case 'retail': return 'bg-blue-100 text-blue-800';
      case 'special_event': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTierLabel = (tier: string) => {
    switch (tier) {
      case 'gold': return 'Gold (-20%)';
      case 'retail': return 'Retail (Std)';
      case 'special_event': return 'Event (+15%)';
      default: return 'Unknown';
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Pricing Management</h1>
          <p className="text-gray-600">Manage customer tiers and pricing rules</p>
        </div>
        <Button variant="outline">
          <Settings className="h-4 w-4 mr-2" />
          Configure Rules
        </Button>
      </div>

      {alerts.map(alert => (
        <Alert key={alert.id} className={alert.severity === 'warning' ? 'border-orange-200 bg-orange-50' : ''}>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{alert.message}</AlertDescription>
        </Alert>
      ))}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <DollarSign className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Today's Revenue</p>
                <p className="text-2xl font-bold">${auditData?.total_revenue?.toLocaleString() || '0'}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Users className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Orders Today</p>
                <p className="text-2xl font-bold">{auditData?.total_orders_today || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Avg. Order</p>
                <p className="text-2xl font-bold">
                  ${auditData && auditData.total_revenue && auditData.total_orders_today ? (auditData.total_revenue / auditData.total_orders_today).toFixed(2) : '0'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <BarChart3 className="h-8 w-8 text-orange-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Pricing Rules Active</p>
                <p className="text-2xl font-bold">{pricingRules.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <PieChart className="h-5 w-5 mr-2" />
              Customer Tier Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {auditData?.tier_distribution && Object.entries(auditData.tier_distribution).map(([tier, count]) => (
                <div key={tier} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`w-4 h-4 rounded mr-3 ${getTierColor(tier).split(' ')[0]}`}></div>
                    <span className="font-medium">{getTierLabel(tier)}</span>
                  </div>
                  <span className="text-lg font-bold">{count}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Pricing Adjustments Today</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {auditData?.pricing_adjustments?.map((adjustment, index) => (
                <div key={index} className="flex justify-between items-center p-3 border rounded-lg">
                  <div>
                    <p className="font-medium">{adjustment.customer}</p>
                    <Badge className={getTierColor(adjustment.tier)}>
                      {getTierLabel(adjustment.tier)}
                    </Badge>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">
                      ${adjustment.original.toFixed(2)} → ${adjustment.adjusted.toFixed(2)}
                    </p>
                    {adjustment.savings && (
                      <p className="text-sm text-green-600">-${adjustment.savings.toFixed(2)}</p>
                    )}
                    {adjustment.surcharge && (
                      <p className="text-sm text-red-600">+${adjustment.surcharge.toFixed(2)}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Customer Tier Management</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Array.isArray(customers) ? customers.slice(0, 10).map((customer) => (
              <div key={customer.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex-1">
                  <h3 className="font-medium">{customer.name}</h3>
                  <p className="text-sm text-gray-600">{customer.contact_person}</p>
                  <p className="text-sm text-gray-500">{customer.phone}</p>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <p className="text-sm text-gray-600">Total Spent</p>
                    <p className="font-medium">${(customer.total_spent || 0).toLocaleString()}</p>
                  </div>
                  
                  <Select 
                    value={customer.tier || 'retail'} 
                    onValueChange={(value) => handleTierChange(customer.id, value)}
                  >
                    <SelectTrigger className="w-40">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="gold">Gold (-20%)</SelectItem>
                      <SelectItem value="retail">Retail (Std)</SelectItem>
                      <SelectItem value="special_event">Event (+15%)</SelectItem>
                    </SelectContent>
                  </Select>
                  
                  <Badge className={getTierColor(customer.tier || 'retail')}>
                    {getTierLabel(customer.tier || 'retail')}
                  </Badge>
                </div>
              </div>
            )) : (
              <div className="text-center text-gray-500 py-4">
                No customers found
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
