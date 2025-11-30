#!/usr/bin/env python3
"""
Create a test Excel file for upload testing
"""

import pandas as pd
from pathlib import Path

def create_test_excel():
    """Create a test Excel file with gaming data"""
    
    # Sample gaming data
    data = {
        'Spieler': ['AlphaPlayer', 'BetaPlayer', 'GammaPlayer', 'DeltaPlayer', 'EpsilonPlayer'],
        'Allianz': ['Alpha Alliance', 'Beta Alliance', 'Gamma Alliance', 'Delta Alliance', 'Epsilon Alliance'],
        'Punkte': [1500, 1200, 1800, 900, 1350],
        'Rang': [2, 4, 1, 5, 3],
        'Spiele': [45, 38, 52, 31, 41],
        'Siege': [28, 19, 34, 15, 23]
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save as Excel
    output_file = Path('test_gaming_data.xlsx')
    df.to_excel(output_file, index=False, engine='openpyxl')
    
    print(f"Test Excel file created: {output_file}")
    print(f"Data shape: {df.shape}")
    print("/nSample data:")
    print(df.head())
    
    return str(output_file)

if __name__ == '__main__':
    create_test_excel()