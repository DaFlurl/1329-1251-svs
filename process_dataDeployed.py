#!/usr/bin/env python3
"""
Data processing workflow for dataDeployed directory
Integrates with the main application for automated data processing
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import sys
import os

class DataProcessor:
    def __init__(self, data_dir="dataDeployed", processed_dir="dataProcessed"):
        self.data_dir = Path(data_dir)
        self.processed_dir = Path(processed_dir)
        self.processed_dir.mkdir(exist_ok=True)
        
    def process_all_files(self):
        """Process all Excel files in dataDeployed directory."""
        logger.info("=== Data Processing Workflow ===")
        
        if not self.data_dir.exists():
            logger.info(f"Error: {self.data_dir} directory not found")
            return False
            
        excel_files = list(self.data_dir.glob("data_*.xlsx"))
        logger.info(f"Found {len(excel_files)} files to process")
        
        processed_count = 0
        for file_path in excel_files:
            if self._process_single_file(file_path):
                processed_count += 1
                
        logger.info(f"Successfully processed {processed_count} files")
        return processed_count > 0
        
    def _process_single_file(self, file_path):
        """Process a single Excel file."""
        try:
            logger.info(f"/nProcessing: {file_path.name}")
            
            # Read the Excel file
            df = pd.read_excel(file_path)
            
            # Data validation and cleaning
            df_clean = self._clean_data(df)
            
            # Generate processed filename
            processed_name = f"processed_{file_path.name}"
            processed_path = self.processed_dir / processed_name
            
            # Save processed data
            df_clean.to_excel(processed_path, index=False)
            
            # Generate metadata
            metadata = self._generate_metadata(df_clean, file_path)
            metadata_path = self.processed_dir / f"{processed_name}.metadata.json"
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
            logger.info(f"  Saved processed file: {processed_name}")
            logger.info(f"  Generated metadata: {metadata_path.name}")
            
            return True
            
        except Exception as e:
            logger.info(f"  Error processing {file_path.name}: {str(e)}")
            return False
            
    def _clean_data(self, df):
        """Clean and validate data."""
        # Make a copy to avoid modifying original
        df_clean = df.copy()
        
        # Remove duplicate rows
        initial_count = len(df_clean)
        df_clean = df_clean.drop_duplicates()
        duplicates_removed = initial_count - len(df_clean)
        
        if duplicates_removed > 0:
            logger.info(f"  Removed {duplicates_removed} duplicate rows")
            
        # Handle missing values
        for col in df_clean.columns:
            if df_clean[col].dtype == 'object':
                df_clean[col] = df_clean[col].fillna('Unknown')
            elif pd.api.types.is_numeric_dtype(df_clean[col]):
                df_clean[col] = df_clean[col].fillna(0)
                
        # Validate data types
        if 'Position' in df_clean.columns:
            df_clean['Position'] = pd.to_numeric(df_clean['Position'], errors='coerce')
            df_clean['Position'] = df_clean['Position'].fillna(0).astype(int)
            
        if 'Score' in df_clean.columns:
            df_clean['Score'] = pd.to_numeric(df_clean['Score'], errors='coerce')
            df_clean['Score'] = df_clean['Score'].fillna(0)
            
        return df_clean
        
    def _generate_metadata(self, df, original_file):
        """Generate metadata for processed file."""
        metadata = {
            "processed_date": datetime.now().isoformat(),
            "original_file": original_file.name,
            "file_size": original_file.stat().st_size,
            "data_shape": df.shape,
            "columns": list(df.columns),
            "data_types": df.dtypes.astype(str).to_dict(),
            "statistics": {}
        }
        
        # Generate basic statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            metadata["statistics"][col] = {
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "mean": float(df[col].mean()),
                "count": int(df[col].count())
            }
            
        return metadata
        
    def create_integration_script(self):
        """Create integration script for main application."""
        integration_script = self.processed_dir / "integrate_with_app.py"
        
        content = '''#!/usr/bin/env python3
"""
Integration script for main application
Provides API endpoints to access processed data
"""

import pandas as pd
import json
from pathlib import Path
from flask import Flask, jsonify

app = Flask(__name__)

class DataIntegration:
    def __init__(self):
        self.processed_dir = Path("dataProcessed")
        self.data_cache = {}
        
    def load_latest_data(self):
        """Load the most recently processed data."""
        processed_files = list(self.processed_dir.glob("processed_*.xlsx"))
        if not processed_files:
            return None
            
        # Get the most recent file
        latest_file = max(processed_files, key=lambda f: f.stat().st_mtime)
        return pd.read_excel(latest_file)
        
    def get_data_summary(self):
        """Get summary of all processed data."""
        summary = {"files": [], "total_records": 0}
        
        for file_path in self.processed_dir.glob("processed_*.xlsx"):
            metadata_path = file_path.with_suffix('.metadata.json')
            
            file_info = {
                "name": file_path.name,
                "size": file_path.stat().st_size
            }
            
            if metadata_path.exists():
                with open(metadata_path) as f:
                    metadata = json.load(f)
                    file_info.update(metadata)
                    summary["total_records"] += metadata.get("data_shape", [0])[0]
                    
            summary["files"].append(file_info)
            
        return summary

data_integration = DataIntegration()

@app.route('/api/data/latest')
def get_latest_data():
    """API endpoint to get latest processed data."""
    data = data_integration.load_latest_data()
    if data is not None:
        return jsonify(data.to_dict('records'))
    return jsonify({"error": "No data available"}), 404

@app.route('/api/data/summary')
def get_data_summary():
    """API endpoint to get data summary."""
    return jsonify(data_integration.get_data_summary())

if __name__ == "__main__":
    app.run(debug=True, port=5001)
'''
        
        integration_script.write_text(content)
        logger.info("Created integration script for main application")
        
    def run(self):
        """Run the complete processing workflow."""
        success = self.process_all_files()
        if success:
            self.create_integration_script()
            logger.info("/n=== Processing Complete ===")
            logger.info("Files are ready for integration with main application")
        else:
            logger.info("/n=== Processing Failed ===")
            logger.info("Please check the errors above")

if __name__ == "__main__":
    processor = DataProcessor()
    processor.run()