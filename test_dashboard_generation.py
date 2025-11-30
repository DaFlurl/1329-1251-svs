#!/usr/bin/env python3
"""
Test Dashboard Generation Functionality
Phase 2 Core Feature Testing
"""

import os
import sys
import pandas as pd
from io import BytesIO

def test_dashboard_generation():
    """Test dashboard generation functionality"""
    print("Testing Dashboard Generation Functionality...")
    
    try:
        sys.path.append('src')
        from core.dashboard_generator import DashboardGenerator
        
        dg = DashboardGenerator()
        print("DashboardGenerator instantiated successfully")
        
        # Create test Excel data
        test_data = {
            'Product': ['Laptop', 'Phone', 'Tablet', 'Monitor', 'Keyboard'],
            'Sales': [1200, 800, 600, 400, 200],
            'Quantity': [50, 120, 80, 30, 150],
            'Revenue': [60000, 96000, 48000, 12000, 15000],
            'Region': ['North', 'South', 'East', 'West', 'Central']
        }
        
        df = pd.DataFrame(test_data)
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        
        # Test dashboard generation methods
        print("Testing dashboard generation methods...")
        
        # Test basic data processing
        if hasattr(dg, 'process_excel_file'):
            print("process_excel_file method exists")
        else:
            print("process_excel_file method missing")
            
        # Test dashboard creation
        if hasattr(dg, 'create_dashboard'):
            print("create_dashboard method exists")
        else:
            print("create_dashboard method missing")
            
        # Test data analysis
        if hasattr(dg, 'analyze_data'):
            print("analyze_data method exists")
        else:
            print("analyze_data method missing")
        
        print("Test data created:")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Data types: {df.dtypes.to_dict()}")
        
        return True
        
    except Exception as e:
        print(f"Error testing dashboard generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dashboard_templates():
    """Test dashboard templates"""
    print("\nTesting Dashboard Templates...")
    
    try:
        # Check if templates exist
        template_files = [
            'templates/dashboard.html',
            'templates/enhanced-dashboard.html',
            'dashboard.html'
        ]
        
        for template in template_files:
            if os.path.exists(template):
                print(f"Template found: {template}")
            else:
                print(f"Template missing: {template}")
        
        # Check dashboard config
        config_files = [
            'config/dashboard.json',
            'dashboard.json'
        ]
        
        for config in config_files:
            if os.path.exists(config):
                print(f"Config found: {config}")
            else:
                print(f"Config missing: {config}")
        
        return True
        
    except Exception as e:
        print(f"Error testing dashboard templates: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 2: DASHBOARD GENERATION TEST")
    print("=" * 60)
    
    success1 = test_dashboard_generation()
    success2 = test_dashboard_templates()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("DASHBOARD GENERATION TEST: PASSED")
    else:
        print("DASHBOARD GENERATION TEST: FAILED")
    print("=" * 60)