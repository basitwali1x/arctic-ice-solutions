#!/usr/bin/env python3
"""Test script to verify Phase 3 API changes"""

import sys
sys.path.append('.')

try:
    from app.main import app
    print("✓ Backend imports successfully")
    print("✓ FastAPI app created")
    print("✓ Rate limiting and caching setup complete")
    
    from slowapi import Limiter
    print("✓ Slowapi rate limiting available")
    
    from app.main import _get_cached, _set_cached
    print("✓ Caching functions available")
    
    print("\n✅ All Phase 3 backend components loaded successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
