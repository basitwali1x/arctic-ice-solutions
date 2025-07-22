import { CustomerUser, Product, CustomerOrder, CustomerFeedback, Invoice, PaymentRecord } from '../types/api';

export const customerUsers: CustomerUser[] = [
  {
    id: 'cust-001',
    name: 'John Manager',
    email: 'john.manager@walmart.com',
    phone: '(337) 555-0101',
    company: 'Walmart Supercenter #1234',
    address: '100 Walmart Dr, Leesville, LA 71446',
    creditTerms: 'Net 30',
    accountBalance: 2450.00,
    creditLimit: 15000.00,
    isActive: true,
    registeredDate: '2023-01-15',
    tier: 'gold'
  },
  {
    id: 'cust-002',
    name: 'Sarah Rodriguez',
    email: 'sarah.rodriguez@brookshire.com',
    phone: '(409) 555-0102',
    company: 'Brookshire Brothers #45',
    address: '300 Main St, DeRidder, LA 70634',
    creditTerms: 'Net 15',
    accountBalance: 1200.00,
    creditLimit: 8000.00,
    isActive: true,
    registeredDate: '2023-03-22',
    tier: 'retail'
  },
  {
    id: 'cust-003',
    name: 'Mike Thompson',
    email: 'mike.thompson@shell.com',
    phone: '(936) 555-0103',
    company: 'Shell Gas Station #5678',
    address: '200 Highway 90, Lake Charles, LA 70601',
    creditTerms: 'COD',
    accountBalance: 0.00,
    creditLimit: 5000.00,
    isActive: true,
    registeredDate: '2023-05-10',
    tier: 'special_event'
  }
];

export const products: Product[] = [
  {
    id: 'prod-001',
    name: '8lb Ice Bags',
    product_type: '8lb_bag',
    price: 2.50,
    weight_lbs: 8,
    is_active: true
  },
  {
    id: 'prod-002',
    name: '20lb Ice Bags',
    product_type: '20lb_bag',
    price: 5.00,
    weight_lbs: 20,
    is_active: true
  },
  {
    id: 'prod-003',
    name: 'Block Ice',
    product_type: 'block_ice',
    price: 3.75,
    weight_lbs: 10,
    is_active: true
  }
];

export const sampleOrders: CustomerOrder[] = [
  {
    id: 'order-001',
    customerId: 'cust-001',
    orderDate: '2025-01-20',
    requestedDeliveryDate: '2025-01-21',
    status: 'confirmed',
    items: [
      {
        productId: 'prod-001',
        productName: '8lb Ice Bags',
        quantity: 200,
        unitPrice: 2.50,
        totalPrice: 500.00
      },
      {
        productId: 'prod-002',
        productName: '20lb Ice Bags',
        quantity: 100,
        unitPrice: 5.00,
        totalPrice: 500.00
      }
    ],
    subtotal: 1000.00,
    tax: 90.00,
    deliveryFee: 25.00,
    totalAmount: 1115.00,
    deliveryAddress: '100 Walmart Dr, Leesville, LA 71446',
    paymentMethod: 'credit',
    paymentStatus: 'pending',
    invoiceNumber: 'INV-2025-001'
  }
];

export const sampleFeedback: CustomerFeedback[] = [
  {
    id: 'feedback-001',
    customerId: 'cust-001',
    orderId: 'order-001',
    type: 'delivery',
    rating: 5,
    subject: 'Excellent Service',
    message: 'Driver was professional and on time. Ice quality was perfect.',
    submittedAt: '2025-01-20T14:30:00Z',
    status: 'new'
  }
];

export const sampleInvoices: Invoice[] = [
  {
    id: 'inv-001',
    orderId: 'order-001',
    customerId: 'cust-001',
    invoiceNumber: 'INV-2025-001',
    issueDate: '2025-01-20',
    dueDate: '2025-02-19',
    subtotal: 1000.00,
    tax: 90.00,
    totalAmount: 1115.00,
    paidAmount: 0.00,
    balanceDue: 1115.00,
    status: 'sent',
    paymentTerms: 'Net 30',
    items: [
      {
        productId: 'prod-001',
        productName: '8lb Ice Bags',
        quantity: 200,
        unitPrice: 2.50,
        totalPrice: 500.00
      },
      {
        productId: 'prod-002',
        productName: '20lb Ice Bags',
        quantity: 100,
        unitPrice: 5.00,
        totalPrice: 500.00
      }
    ]
  }
];

export const samplePayments: PaymentRecord[] = [
  {
    id: 'payment-001',
    customerId: 'cust-002',
    orderId: 'order-002',
    invoiceId: 'inv-002',
    amount: 650.00,
    paymentMethod: 'check',
    paymentDate: '2025-01-19',
    checkNumber: '1234',
    status: 'completed'
  }
];
