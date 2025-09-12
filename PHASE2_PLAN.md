# Phase 2: Authentication & Roles Implementation Plan

## Current State Analysis
- Current system uses simple JWT access tokens only (no refresh tokens)
- User roles are stored as simple strings in user objects
- No proper users/roles tables with relationships
- No audit logging system
- Authentication endpoints: /api/auth/login, /api/auth/logout, /api/auth/me

## Phase 2 Goals
1. **JWT Enhancement**: Add refresh tokens with rotation
2. **RBAC System**: Proper users/roles tables with many-to-many relationships
3. **Role-Based Access**: Restrict endpoints based on user roles
4. **Audit Logging**: Track sensitive actions (who, when, what)

## Implementation Steps

### 1. Database Schema Updates
- Add `refresh_tokens` table for token management
- Add `roles` table with predefined roles
- Add `user_roles` table for many-to-many relationship
- Add `audit_logs` table for action tracking
- Update `users` table to work with new role system

### 2. Enhanced JWT System
- Add refresh token generation and validation
- Implement token rotation on refresh
- Add `/api/auth/refresh` endpoint
- Update logout to revoke refresh tokens
- Add token blacklisting mechanism

### 3. Role-Based Access Control
- Define role permissions matrix:
  - **Manager**: Full access to all endpoints
  - **Dispatcher**: Orders, routes, customers, vehicles
  - **Accountant**: Financial data, customer pricing, payments
  - **Production**: Production entries, inventory, work orders
  - **Technician**: Work orders only (read/write)
- Add role decorators/middleware for endpoint protection
- Update existing endpoints with role checks

### 4. Audit Logging System
- Track sensitive operations:
  - Order creation/modification/deletion
  - Route assignments and changes
  - Financial document uploads/changes
  - User management actions
  - Customer pricing changes
- Log format: user_id, action, resource_type, resource_id, timestamp, details

### 5. Database Models (SQLAlchemy)
```python
class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    
class UserRole(Base):
    __tablename__ = "user_roles"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
    
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_hash = Column(String(255), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE
    resource_type = Column(String(50), nullable=False)  # order, route, customer, etc.
    resource_id = Column(String(100), nullable=False)
    details = Column(JSON)  # Additional context
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
```

### 6. API Endpoints to Add/Update
- `POST /api/auth/refresh` - Refresh access token using refresh token
- Update `POST /api/auth/login` - Return both access and refresh tokens
- Update `POST /api/auth/logout` - Revoke refresh token
- Add role checks to existing endpoints:
  - Orders endpoints (Manager, Dispatcher, Accountant)
  - Routes endpoints (Manager, Dispatcher)
  - Financial endpoints (Manager, Accountant)
  - Work orders endpoints (Manager, Production, Technician)

### 7. Role Permission Matrix
| Endpoint Category | Manager | Dispatcher | Accountant | Production | Technician |
|------------------|---------|------------|------------|------------|------------|
| Users            | ✅      | ❌         | ❌         | ❌         | ❌         |
| Customers        | ✅      | ✅         | ✅         | ❌         | ❌         |
| Orders           | ✅      | ✅         | ✅         | ❌         | ❌         |
| Routes           | ✅      | ✅         | ❌         | ❌         | ❌         |
| Vehicles         | ✅      | ✅         | ❌         | ❌         | ❌         |
| Work Orders      | ✅      | ❌         | ❌         | ✅         | ✅         |
| Production       | ✅      | ❌         | ❌         | ✅         | ❌         |
| Financial        | ✅      | ❌         | ✅         | ❌         | ❌         |
| Inventory        | ✅      | ✅         | ❌         | ✅         | ❌         |

### 8. Testing Strategy
- Test login/logout with refresh token flow
- Test role-based access restrictions
- Test audit logging for sensitive operations
- Test token refresh and expiration handling
- Verify existing functionality still works

## Dependencies
- Requires Phase 1 (Postgres migration) to be merged first
- Will build on existing SQLAlchemy models and repository pattern
- Uses existing JWT infrastructure but enhances it

## Security Considerations
- Refresh tokens stored as hashes, not plaintext
- Token rotation on each refresh
- Audit logs for all sensitive operations
- Role-based access strictly enforced
- Demo credentials disabled in production
