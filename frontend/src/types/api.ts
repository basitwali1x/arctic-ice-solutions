export interface Location {
  id: string;
  name: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  location_type: string;
  is_active: boolean;
}

export interface Product {
  id: string;
  name: string;
  product_type: string;
  price: number;
  weight_lbs: number;
  is_active: boolean;
}

export interface Vehicle {
  id: string;
  license_plate: string;
  vehicle_type: string;
  capacity_pallets: number;
  location_id: string;
  is_active: boolean;
  last_maintenance?: string;
}

export interface Customer {
  id: string;
  name: string;
  contact_person?: string;
  phone: string;
  email?: string;
  address: string;
  city?: string;
  state?: string;
  zip_code?: string;
  location_id: string;
  credit_limit?: number;
  payment_terms?: number;
  is_active?: boolean;
  status?: string;
  total_spent?: number;
  total_orders?: number;
  last_order_date?: string;
  current_balance?: number;
}

export interface DashboardOverview {
  total_customers: number;
  total_vehicles: number;
  total_orders_today: number;
  locations: number;
  active_routes: number;
}

export interface ProductionDashboard {
  daily_production_pallets: number;
  target_production_pallets: number;
  production_efficiency: number;
  shift_1_pallets: number;
  shift_2_pallets: number;
  inventory_levels: {
    '8lb_bags': number;
    '20lb_bags': number;
    'block_ice': number;
  };
}

export interface FleetDashboard {
  total_vehicles: number;
  vehicles_in_use: number;
  vehicles_available: number;
  vehicles_maintenance: number;
  fleet_utilization: number;
  vehicles_by_location: Record<string, number>;
}

export interface WorkOrder {
  id: string;
  vehicle_id: string;
  vehicle_name: string;
  technician_name: string;
  issue_description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'approved' | 'in_progress' | 'completed' | 'rejected';
  work_type: 'mechanical' | 'refrigeration' | 'electrical' | 'body';
  submitted_date: string;
  estimated_cost: number;
  estimated_hours: number;
  approved_by?: string;
  approved_date?: string;
}

export interface ProductionEntry {
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

export interface Expense {
  id: string;
  date: string;
  category: 'fuel' | 'maintenance' | 'supplies' | 'utilities' | 'labor' | 'other';
  description: string;
  amount: number;
  location_id: string;
  submitted_by: string;
  submitted_at: string;
}

export interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

export interface FinancialDashboard {
  daily_revenue: number;
  monthly_revenue: number;
  daily_expenses?: number;
  monthly_expenses?: number;
  daily_profit?: number;
  payment_breakdown: {
    cash: number;
    check: number;
    credit: number;
  };
  outstanding_invoices: number;
  tax_liability_ytd: number;
}
