#!/usr/bin/env python3
"""
Excel to JSON Converter Tool
Converts Excel files to JSON format for the AgentDaf1.1 dashboard
"""

import pandas as pd
import json
import os
import sys
from pathlib import Path
from datetime import datetime

def convert_excel_to_json(excel_path, output_path):
    """
    Convert Excel file to JSON format
    """
    try:
        print(f"Converting {excel_path}...")
        
        # Read all sheets from Excel file
        xls = pd.ExcelFile(excel_path)
        data = {}
        
        for sheet_name in xls.sheet_names:
            print(f"  Processing sheet: {sheet_name}")
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            
            # Clean data: replace NaN with empty string or appropriate default
            df_clean = df.fillna('')
            
            # Convert to records
            records = df_clean.to_dict('records')
            
            # Store in data dictionary with lowercase sheet name
            data[sheet_name.lower()] = records
            
            print(f"    {len(records)} records processed")
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save as JSON with proper formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Successfully converted to {output_path}")
        return True
        
    except Exception as e:
        print(f"Error converting {excel_path}: {str(e)}")
        return False

def process_data_directory(source_dir, output_dir):
    """
    Process all Excel files in a directory
    """
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    
    if not source_path.exists():
        print(f"Source directory {source_dir} does not exist")
        return False
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all Excel files
    excel_files = list(source_path.glob("*.xlsx")) + list(source_path.glob("*.xls"))
    
    if not excel_files:
        print(f"No Excel files found in {source_dir}")
        return False
    
    print(f"Found {len(excel_files)} Excel files")
    
    success_count = 0
    for excel_file in excel_files:
        # Generate output filename
        output_file = output_path / f"{excel_file.stem}.json"
        
        if convert_excel_to_json(excel_file, output_file):
            success_count += 1
    
    print(f"Successfully converted {success_count}/{len(excel_files)} files")
    return success_count > 0

def validate_json_file(json_path):
    """
    Validate JSON file format
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if data has expected structure
        if isinstance(data, dict):
            total_records = sum(len(records) for records in data.values())
            print(f"{json_path} is valid - {total_records} total records")
            return True
        else:
            print(f"{json_path} has invalid structure")
            return False
            
    except Exception as e:
        print(f"{json_path} validation failed: {str(e)}")
        return False

def main():
    """
    Main function
    """
    print("AgentDaf1.1 Excel to JSON Converter")
    print("=" * 50)
    
    # Default paths
    source_dir = "../dataDeployed"
    output_dir = "data"
    
    # Check if custom paths provided
    if len(sys.argv) > 1:
        source_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    print(f"Source: {source_dir}")
    print(f"Output: {output_dir}")
    print()
    
    # Process files
    if process_data_directory(source_dir, output_dir):
        print("/nValidating output files...")
        
        # Validate generated JSON files
        output_path = Path(output_dir)
        json_files = list(output_path.glob("*.json"))
        
        valid_count = 0
        for json_file in json_files:
            if validate_json_file(json_file):
                valid_count += 1
        
        print(f"/nSummary: {valid_count}/{len(json_files)} files are valid")
        
        if valid_count == len(json_files):
            print("All files converted successfully!")
            return 0
        else:
            print("Some files have issues")
            return 1
    else:
        print("Conversion failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())