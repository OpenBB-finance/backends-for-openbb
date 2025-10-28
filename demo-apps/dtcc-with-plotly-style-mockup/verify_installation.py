#!/usr/bin/env python3
"""
DTCC OpenBB Dashboard System - Installation Verification Script
Run this script to verify that everything is working correctly.
"""

import sys
import importlib
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'fastapi', 'uvicorn', 'pandas', 'numpy', 'plotly', 
        'httpx', 'requests'
    ]
    
    missing = []
    installed = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            installed.append(package)
            print(f"✅ {package} - Available")
        except ImportError:
            missing.append(package)
            print(f"❌ {package} - Missing")
    
    return len(missing) == 0, missing

def check_application():
    """Check if the DTCC application loads correctly."""
    try:
        # Add current directory to path
        sys.path.insert(0, str(Path.cwd()))
        
        # Import main application
        from main import app
        from shared.decorators import WIDGETS
        
        print(f"✅ Application loads successfully")
        print(f"✅ {len(WIDGETS)} widgets registered")
        
        # Check for DTCC widgets specifically
        dtcc_categories = ['Market Surveillance', 'Risk Management', 'Fixed Income', 
                          'Derivatives', 'Equities & ETF', 'Regulatory & Compliance', 'Trading Strategy']
        
        dtcc_widgets = [w for w in WIDGETS.values() if w.get('category') in dtcc_categories]
        print(f"✅ {len(dtcc_widgets)} DTCC widgets found")
        
        return True
        
    except Exception as e:
        print(f"❌ Application failed to load: {e}")
        return False

def check_server_start():
    """Test if the server can start (quick test)."""
    try:
        print("🧪 Testing server startup...")
        # This is a quick import test, not actually starting the server
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        response = client.get("/")
        
        if response.status_code == 200:
            print("✅ Server startup test successful")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
        return False

def main():
    """Run all verification checks."""
    print("🎯 DTCC OpenBB Dashboard System - Installation Verification")
    print("=" * 65)
    print()
    
    checks_passed = 0
    total_checks = 4
    
    # Check Python version
    print("1. Checking Python version...")
    if check_python_version():
        checks_passed += 1
    print()
    
    # Check dependencies
    print("2. Checking dependencies...")
    deps_ok, missing = check_dependencies()
    if deps_ok:
        checks_passed += 1
    else:
        print(f"   Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
    print()
    
    # Check application
    print("3. Checking application...")
    if check_application():
        checks_passed += 1
    print()
    
    # Check server
    print("4. Testing server...")
    if check_server_start():
        checks_passed += 1
    print()
    
    # Final result
    print("=" * 65)
    print(f"📊 Verification Results: {checks_passed}/{total_checks} checks passed")
    
    if checks_passed == total_checks:
        print("🎉 Installation verified successfully!")
        print()
        print("🚀 Ready to start the DTCC Dashboard System:")
        print("   uvicorn main:app --reload --port 8000")
        print()
        print("🌐 Then visit: http://localhost:8000")
        return True
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)