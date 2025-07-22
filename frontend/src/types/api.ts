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
  tier?: 'gold' | 'retail' | 'special_event';
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

export interface Route {
  id: string;
  name: string;
  driver_id: string;
  vehicle_id: string;
  location_id: string;
  date: string;
  estimated_duration_hours: number;
  status: 'planned' | 'active' | 'completed' | 'cancelled';
  created_at: string;
  stops: RouteStop[];
}

export interface RouteStop {
  id: string;
  route_id: string;
  customer_id: string;
  order_id: string;
  stop_number: number;
  estimated_arrival: string;
  status: 'pending' | 'completed';
}

export interface CustomerUser {
  id: string;
  name: string;
  email: string;
  phone: string;
  company: string;
  address: string;
  creditTerms: 'Net 15' | 'Net 30' | 'COD';
  accountBalance: number;
  creditLimit: number;
  isActive: boolean;
  registeredDate: string;
  tier?: 'gold' | 'retail' | 'special_event';
}

export interface OrderItem {
  productId: string;
  productName: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
}

export interface CustomerOrder {
  id: string;
  customerId: string;
  orderDate: string;
  requestedDeliveryDate: string;
  actualDeliveryDate?: string;
  status: 'pending' | 'confirmed' | 'in-production' | 'out-for-delivery' | 'delivered' | 'cancelled';
  items: OrderItem[];
  subtotal: number;
  tax: number;
  deliveryFee: number;
  totalAmount: number;
  deliveryAddress: string;
  specialInstructions?: string;
  paymentMethod?: 'cash' | 'check' | 'credit' | 'account';
  paymentStatus: 'pending' | 'paid' | 'overdue';
  invoiceNumber?: string;
  trackingInfo?: {
    driverName: string;
    vehicleId: string;
    estimatedArrival: string;
    currentLocation?: {
      lat: number;
      lng: number;
      timestamp: string;
    };
  };
}

export interface CustomerFeedback {
  id: string;
  customerId: string;
  orderId?: string;
  type: 'delivery' | 'product' | 'service' | 'complaint' | 'suggestion';
  rating: 1 | 2 | 3 | 4 | 5;
  subject: string;
  message: string;
  submittedAt: string;
  status: 'new' | 'reviewed' | 'responded' | 'resolved';
  response?: string;
  respondedAt?: string;
  respondedBy?: string;
}

export interface Invoice {
  id: string;
  orderId: string;
  customerId: string;
  invoiceNumber: string;
  issueDate: string;
  dueDate: string;
  subtotal: number;
  tax: number;
  totalAmount: number;
  paidAmount: number;
  balanceDue: number;
  status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled';
  paymentTerms: string;
  items: OrderItem[];
}

export interface PaymentRecord {
  id: string;
  customerId: string;
  orderId: string;
  invoiceId: string;
  amount: number;
  paymentMethod: 'cash' | 'check' | 'credit' | 'bank-transfer';
  paymentDate: string;
  checkNumber?: string;
  transactionId?: string;
  status: 'pending' | 'completed' | 'failed' | 'cancelled';
  notes?: string;
}

export interface EnhancedRouteStop {
  id: string;
  customerId: string;
  customerName: string;
  address: string;
  coordinates: {
    lat: number;
    lng: number;
  };
  orderNumber: string;
  products: {
    bags8lb: number;
    bags20lb: number;
    blockIce: number;
  };
  deliveryWindow: {
    start: string;
    end: string;
  };
  status: 'pending' | 'en-route' | 'arrived' | 'delivered' | 'failed';
  arrivalTime?: string;
  deliveryTime?: string;
  signature?: string;
  notes?: string;
  photos?: string[];
  actualDelivery?: {
    bags8lb: number;
    bags20lb: number;
    blockIce: number;
    totalAmount: number;
    paymentMethod: 'cash' | 'check' | 'credit' | 'debit' | 'account';
    paymentReceived: boolean;
    checkNumber?: string;
    cardLast4?: string;
    signature: string;
    invoiceNumber: string;
    timestamp: string;
  };
}

export interface DeliveryInvoice {
  id: string;
  invoiceNumber: string;
  customerId: string;
  customerName: string;
  customerAddress: string;
  driverId: string;
  driverName: string;
  deliveryDate: string;
  items: {
    productName: string;
    quantity: number;
    unitPrice: number;
    totalPrice: number;
  }[];
  subtotal: number;
  tax: number;
  totalAmount: number;
  paymentMethod: string;
  paymentReceived: boolean;
  signature: string;
  timestamp: string;
}

export interface PaymentTransaction {
  id: string;
  invoiceId: string;
  customerId: string;
  amount: number;
  paymentMethod: 'cash' | 'check' | 'credit' | 'debit' | 'account';
  status: 'pending' | 'completed' | 'failed';
  timestamp: string;
  checkNumber?: string;
  cardLast4?: string;
  authCode?: string;
  driverId: string;
}

export interface PricingRule {
  id: string;
  tier: 'gold' | 'retail' | 'special_event';
  discount_percentage: number;
  is_active: boolean;
}

export interface PricingAudit {
  total_orders_today: number;
  total_revenue: number;
  pricing_adjustments: {
    customer: string;
    tier: string;
    original: number;
    adjusted: number;
    savings?: number;
    surcharge?: number;
  }[];
  tier_distribution: {
    gold: number;
    retail: number;
    special_event: number;
  };
}
