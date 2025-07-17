# Arctic Ice Solutions - Business Management System

A comprehensive web application for managing ice manufacturing and distribution operations across multiple locations.

<!-- Verification comment added by Devin for testing PR workflow -->

## Features

### 🏢 Multi-Location Support
- **Leesville HQ & Production** - Main headquarters and manufacturing
- **Lake Charles Distribution** - Secondary distribution center  
- **Lufkin Distribution** - Texas operations
- **Jasper Warehouse** - Storage facility

### 📊 Core Modules

**Dashboard**
- Real-time business overview
- Production metrics and KPIs
- Fleet utilization tracking
- Financial summaries

**Customer Management**
- 536+ customer accounts imported from Excel
- Customer directory with search and filtering
- Credit terms and payment tracking
- Multi-location customer distribution

**Production & Inventory**
- Daily production tracking (80-160 pallets/day)
- Product management (8lb bags, 20lb bags, block ice)
- Shift management (2 shifts)
- Inventory level monitoring

**Fleet & Route Management**
- 8 refrigerated vehicles (1×53', 1×42', 4×20', 2×16')
- Route optimization and management
- Vehicle maintenance tracking
- Real-time GPS tracking capability

**Financial Management**
- Revenue tracking ($2.7M+ historical data)
- Expense management and profit analysis
- Payment method breakdown (Cash, Check, Credit)
- Tax liability calculations
- Excel data import functionality

**Maintenance System**
- Work order submission and approval workflow
- Vehicle and equipment maintenance tracking
- Technician assignment and scheduling
- Priority-based work management

**Production Manager Dashboard**
- Daily production input by shift
- Pallet tracking (8lb, 20lb, block ice)
- Production efficiency monitoring
- Shift performance analytics

**Notification System**
- Real-time customer order notifications
- Work order status updates
- System alerts and reminders

## Technology Stack

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **shadcn/ui** component library
- **Lucide React** for icons
- **Recharts** for data visualization

### Backend
- **FastAPI** (Python)
- **Pydantic** for data validation
- **JSON-based** persistent storage
- **CORS** enabled for cross-origin requests

### Deployment
- **Frontend**: Deployed on Devin Apps Platform
- **Backend**: Deployed on Fly.io
- **Data Persistence**: JSON file storage with automatic backup

## Data Import Capabilities

- **Excel Integration**: Import historical sales data
- **Customer Data**: 536 customers with complete contact information
- **Order History**: 18,166+ orders spanning January 2024 - July 2025
- **Financial Records**: $2,732,095.42 in total revenue

## Getting Started

### Prerequisites
- Node.js 18+ and pnpm
- Python 3.12+ and Poetry
- Git

### Frontend Setup
```bash
cd frontend
pnpm install
pnpm dev
```

### Backend Setup
```bash
cd backend
poetry install
poetry run fastapi dev app/main.py
```

### Environment Variables
Create `.env` file in frontend directory:
```
VITE_API_URL=http://localhost:8000
```

## Deployment URLs

- **Frontend**: https://ice-management-app-4r16aafs.devinapps.com
- **Backend API**: https://app-dfyyccxe.fly.dev

## Project Structure

```
arctic-ice-solutions/
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Application pages
│   │   ├── types/          # TypeScript type definitions
│   │   └── lib/            # Utility functions
│   └── dist/               # Build output
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # Main application file
│   │   └── excel_import.py # Excel processing utilities
│   └── data/               # JSON data storage
└── README.md
```

## Key Features Implementation

### Data Persistence
- JSON-based storage system
- Automatic data loading on startup
- Persistent across deployments and restarts

### Excel Import System
- Processes multiple Excel files simultaneously
- Extracts customer and order data
- Calculates financial metrics automatically
- Handles data validation and cleaning

### Multi-Role Access
- **Managers**: Full system access and approval workflows
- **Dispatchers**: Route and fleet management
- **Accountants**: Financial reporting and analysis
- **Production Managers**: Daily production input
- **Technicians**: Work order submission (mobile ready)

### Real-Time Features
- Live notification system
- Real-time data updates
- Responsive design for mobile and desktop

## Business Impact

- **Operational Efficiency**: Streamlined workflow management
- **Data-Driven Decisions**: Comprehensive analytics and reporting
- **Cost Reduction**: Optimized route planning and maintenance scheduling
- **Customer Service**: Improved order tracking and communication
- **Scalability**: Multi-location support for business expansion

## Future Enhancements

- Mobile apps for drivers and customers
- QuickBooks integration
- Google Sheets synchronization
- Advanced route optimization with AI
- Real-time GPS tracking integration
- Automated inventory reordering

---

**Developed for Arctic Ice Solutions**  
*Comprehensive business management across Louisiana and Texas operations*
