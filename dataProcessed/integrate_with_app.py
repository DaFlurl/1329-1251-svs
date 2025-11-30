#!/usr/bin/env python3
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
