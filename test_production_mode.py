#!/usr/bin/env python3
import os
import sys
sys.path.append('/home/ubuntu/repos/arctic-ice-solutions/backend')

os.environ['ENVIRONMENT'] = 'production'
os.environ['ADMIN_PASSWORD'] = 'secure-admin-password'

from app.main import is_production_mode

print(f'Production mode: {is_production_mode()}')
print(f'Environment: {os.getenv("ENVIRONMENT")}')
print(f'Admin password set: {bool(os.getenv("ADMIN_PASSWORD"))}')
print(f'Port: {os.getenv("PORT", "not set")}')

os.environ.pop('ENVIRONMENT', None)
print(f'\nDevelopment mode: {not is_production_mode()}')
