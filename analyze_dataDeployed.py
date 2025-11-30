#!/usr/bin/env python3
"""
DataDeployed Directory Analysis and Repair Tool
Analyzes Excel files for corruption, format issues, and fixes naming conventions.
"""

import pandas as pd
import os
import re
from pathlib import Path
from datetime import datetime
import json

class DataDeployedAnalyzer:
    def __init__(self, data_dir="dataDeployed"):
        self.data_dir = Path(data_dir)
        self.report = {
            "analysis_date": datetime.now().isoformat(),
            "files_analyzed": [],
            "issues_found": [],
            "fixes_applied": [],
            "recommendations": []
        }
        
    def analyze_files(self):
        """Analyze all Excel files in the dataDeployed directory."""
        logger.info("=== DataDeployed Directory Analysis ===")
        
        if not self.data_dir.exists():
            logger.info(f"Directory {self.data_dir} does not exist")
            self.report["issues_found"].append("Directory does not exist")
            return
            
        excel_files = list(self.data_dir.glob("*.xlsx"))
        logger.info(f"Found {len(excel_files)} Excel files")
        
        for file_path in excel_files:
            self._analyze_single_file(file_path)
            
    def _analyze_single_file(self, file_path):
        """Analyze a single Excel file."""
        file_info = {
            "name": file_path.name,
            "size": file_path.stat().st_size,
            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }
        
        logger.info(f"/nAnalyzing: {file_path.name}")
        
        # Check naming convention
        naming_issues = self._check_naming_convention(file_path.name)
        if naming_issues:
            file_info["naming_issues"] = naming_issues
            self.report["issues_found"].extend([f"{file_path.name}: {issue}" for issue in naming_issues])
            
        # Try to read the Excel file
        try:
            df = pd.read_excel(file_path)
            file_info["readable"] = True
            file_info["shape"] = df.shape
            file_info["columns"] = list(df.columns)
            
            logger.info(f"  File readable")
            logger.info(f"  Shape: {df.shape}")
            logger.info(f"  Columns: {list(df.columns)}")
            
            # Check for data quality issues
            data_issues = self._check_data_quality(df, file_path.name)
            if data_issues:
                file_info["data_issues"] = data_issues
                self.report["issues_found"].extend([f"{file_path.name}: {issue}" for issue in data_issues])
                
        except Exception as e:
            file_info["readable"] = False
            file_info["error"] = str(e)
            logger.info(f"  ERROR: {str(e)}")
            self.report["issues_found"].append(f"{file_path.name}: Unable to read file - {str(e)}")
            
        self.report["files_analyzed"].append(file_info)
        
    def _check_naming_convention(self, filename):
        """Check if filename follows proper naming conventions."""
        issues = []
        
        # Check for spaces in filename
        if " " in filename:
            issues.append("Contains spaces - should use underscores or hyphens")
            
        # Check for special characters
        if re.search(r'[^/w/s/-.,+()]', filename):
            issues.append("Contains special characters that may cause issues")
            
        # Check date format
        date_pattern = r'(/w+day), /d{1,2} /w+ /d{4}'
        if not re.search(date_pattern, filename):
            issues.append("Date format not standardized")
            
        # Check version format
        version_pattern = r'v /d+/+/d+'
        if not re.search(version_pattern, filename):
            issues.append("Version format not standardized")
            
        return issues
        
    def _check_data_quality(self, df, filename):
        """Check for data quality issues in the DataFrame."""
        issues = []
        
        # Check for empty DataFrame
        if df.empty:
            issues.append("DataFrame is empty")
            return issues
            
        # Check for missing values
        missing_pct = (df.isnull().sum() / len(df)) * 100
        high_missing_cols = missing_pct[missing_pct > 50].index.tolist()
        if high_missing_cols:
            issues.append(f"High missing values (>50%) in columns: {high_missing_cols}")
            
        # Check for duplicate rows
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            issues.append(f"Found {duplicates} duplicate rows")
            
        # Check data types
        if len(df.select_dtypes(include=['object']).columns) > len(df.columns) * 0.8:
            issues.append("Most columns are object type - may need type conversion")
            
        return issues
        
    def fix_naming_conventions(self):
        """Fix file naming conventions."""
        logger.info("/nFixing naming conventions...")
        
        for file_path in self.data_dir.glob("*.xlsx"):
            new_name = self._generate_standardized_name(file_path.name)
            if new_name != file_path.name:
                new_path = self.data_dir / new_name
                try:
                    file_path.rename(new_path)
                    logger.info(f"  Renamed: {file_path.name} -> {new_name}")
                    self.report["fixes_applied"].append(f"Renamed {file_path.name} to {new_name}")
                except Exception as e:
                    logger.info(f"  Failed to rename {file_path.name}: {str(e)}")
                    self.report["issues_found"].append(f"Failed to rename {file_path.name}: {str(e)}")
                    
    def _generate_standardized_name(self, original_name):
        """Generate a standardized filename."""
        # Extract date, version, and other components
        date_match = re.search(r'(/w+day), (/d{1,2}) (/w+) (/d{4})', original_name)
        version_match = re.search(r'v (/d+)/+(/d+)', original_name)
        
        if date_match and version_match:
            day, date_num, month, year = date_match.groups()
            v1, v2 = version_match.groups()
            
            # Standardize date format
            month_map = {
                'January': '01', 'February': '02', 'March': '03', 'April': '04',
                'May': '05', 'June': '06', 'July': '07', 'August': '08',
                'September': '09', 'October': '10', 'November': '11', 'December': '12'
            }
            
            month_num = month_map.get(month, month[:3].lower())
            standardized_date = f"{year}-{month_num}-{date_num.zfill(2)}"
            
            # Generate new name
            new_name = f"data_{standardized_date}_v{v1}+{v2}.xlsx"
            return new_name
            
        return original_name
        
    def create_backup_workflow(self):
        """Create backup and processing workflows."""
        logger.info("/nCreating backup workflow...")
        
        backup_dir = self.data_dir.parent / "dataBackup"
        backup_dir.mkdir(exist_ok=True)
        
        # Create backup script
        backup_script = backup_dir / "backup_data.py"
        backup_content = '''#!/usr/bin/env python3
"""
Backup script for dataDeployed directory
"""
import shutil
from datetime import datetime
from pathlib import Path

def backup_data():
    source = Path("../dataDeployed")
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"data_backup_{timestamp}"
    
    if source.exists():
        shutil.copytree(source, backup_path)
        logger.info(f"Backup created: {backup_path}")
    else:
        logger.info("Source directory not found")

if __name__ == "__main__":
    backup_data()
'''
        
        backup_script.write_text(backup_content)
        self.report["fixes_applied"].append("Created backup workflow script")
        logger.info("  Backup workflow created")
        
    def generate_report(self):
        """Generate comprehensive analysis report."""
        report_path = self.data_dir / "analysis_report.json"
        
        with open(report_path, 'w') as f:
            json.dump(self.report, f, indent=2)
            
        logger.info(f"/nReport generated: {report_path}")
        
        # Print summary
        logger.info("/n=== SUMMARY ===")
        logger.info(f"Files analyzed: {len(self.report['files_analyzed'])}")
        logger.info(f"Issues found: {len(self.report['issues_found'])}")
        logger.info(f"Fixes applied: {len(self.report['fixes_applied'])}")
        
        if self.report["issues_found"]:
            logger.info("/nIssues found:")
            for issue in self.report["issues_found"]:
                logger.info(f"  - {issue}")
                
        if self.report["fixes_applied"]:
            logger.info("/nFixes applied:")
            for fix in self.report["fixes_applied"]:
                logger.info(f"  - {fix}")
                
    def run_full_analysis(self):
        """Run complete analysis and repair process."""
        self.analyze_files()
        self.fix_naming_conventions()
        self.create_backup_workflow()
        self.generate_report()

if __name__ == "__main__":
    analyzer = DataDeployedAnalyzer()
    analyzer.run_full_analysis()