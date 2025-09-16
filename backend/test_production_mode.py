import os
import sys
sys.path.append('/home/ubuntu/repos/arctic-ice-solutions/backend')

from app.main import is_production_mode

print("=== Production Mode Detection Test ===")
environment = os.getenv('ENVIRONMENT', '').lower()
fly_app_name = os.getenv('FLY_APP_NAME', '')
port = os.getenv('PORT', '')

print(f'Environment variable ENVIRONMENT: "{environment}"')
print(f'Environment variable FLY_APP_NAME: "{fly_app_name}"')
print(f'Environment variable PORT: "{port}"')
print(f'Production mode result: {is_production_mode()}')

os.environ['ENVIRONMENT'] = 'production'
print(f'After setting ENVIRONMENT=production: {is_production_mode()}')

os.environ['FLY_APP_NAME'] = 'app-hjvipiga'
print(f'After setting FLY_APP_NAME=app-hjvipiga: {is_production_mode()}')

os.environ['PORT'] = '8000'
print(f'After setting PORT=8000: {is_production_mode()}')
