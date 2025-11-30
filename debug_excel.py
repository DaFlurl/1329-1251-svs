#!/usr/bin/env python3
"""
Debug Excel file structure
"""
import pandas as pd
from pathlib import Path

def debug_excel():
    """Debug Excel file structure"""
    excel_file = Path('test_gaming_data.xlsx')
    
    if not excel_file.exists():
        logger.info("Excel file not found!")
        return
    
    try:
        # Read Excel file
        df = pd.read_excel(excel_file)
        
        logger.info(f"Excel file: {excel_file.name}")
        logger.info(f"Rows: {len(df)}")
        logger.info(f"Columns: {list(df.columns)}")
        logger.info("/nFirst few rows:")
        logger.info(df.head())
        logger.info("/nData types:")
        logger.info(df.dtypes)
        
        # Convert to records like the processor does
        records = df.fillna('').to_dict('records')
        logger.info(f"/nFirst record: {records[0] if records else 'No records'}")
        
    except Exception as e:
        logger.info(f"Error reading Excel: {e}")

if __name__ == "__main__":
    debug_excel()