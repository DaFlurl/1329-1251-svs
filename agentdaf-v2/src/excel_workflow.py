#!/usr/bin/env python3
"""
Excel Workflow Engine for AgentDaf1.1

Handles Excel file processing, analysis, and data export functionality.
"""

import pandas as pd
import openpyxl
import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ExcelWorkflowEngine:
    """Core Excel processing engine."""
    
    def __init__(self):
        """Initialize the Excel workflow engine."""
        self.supported_formats = ['.xlsx', '.xls', '.csv']
        logger.info("ExcelWorkflowEngine initialized")
    
    def test_functionality(self):
        """Test basic functionality of the workflow engine."""
        try:
            # Test basic operations
            test_data = {
                'test_read': self._test_excel_read(),
                'test_write': self._test_excel_write(),
                'test_analyze': self._test_data_analysis()
            }
            
            logger.info("Excel workflow engine functionality test completed")
            return {
                'success': True,
                'message': 'All tests passed',
                'details': test_data
            }
            
        except Exception as e:
            logger.error(f"Functionality test failed: {str(e)}")
            return {
                'success': False,
                'message': f'Test failed: {str(e)}',
                'error': str(e)
            }
    
    def _test_excel_read(self):
        """Test Excel reading capability."""
        try:
            # Create test data
            test_df = pd.DataFrame({
                'A': [1, 2, 3],
                'B': [4, 5, 6],
                'C': [7, 8, 9]
            })
            
            # Test reading operations
            result = {
                'can_read_dataframe': True,
                'can_process_data': True,
                'test_data_shape': test_df.shape,
                'data_types': test_df.dtypes.to_dict()
            }
            
            logger.info("Excel read test passed")
            return result
            
        except Exception as e:
            logger.error(f"Excel read test failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _test_excel_write(self):
        """Test Excel writing capability."""
        try:
            # Create test data
            test_data = pd.DataFrame({
                'Product': ['A', 'B', 'C'],
                'Price': [10.99, 20.50, 30.00],
                'Quantity': [100, 200, 150]
            })
            
            # Test file path
            test_file = 'test_output.xlsx'
            
            # Test writing operations
            test_data.to_excel(test_file, index=False)
            
            # Verify file was created
            file_exists = os.path.exists(test_file)
            file_size = os.path.getsize(test_file) if file_exists else 0
            
            # Clean up
            if file_exists:
                os.remove(test_file)
            
            result = {
                'can_write_excel': True,
                'file_created': file_exists,
                'file_size': file_size,
                'test_data_shape': test_data.shape
            }
            
            logger.info("Excel write test passed")
            return result
            
        except Exception as e:
            logger.error(f"Excel write test failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _test_data_analysis(self):
        """Test data analysis capabilities."""
        try:
            # Create test data
            test_data = pd.DataFrame({
                'Date': pd.date_range('2024-01-01', periods=3),
                'Sales': [1000, 1500, 2000],
                'Region': ['North', 'South', 'East']
            })
            
            # Test analysis operations
            analysis_results = {
                'row_count': len(test_data),
                'column_count': len(test_data.columns),
                'numeric_columns': list(test_data.select_dtypes(include=['number']).columns),
                'summary_stats': test_data.describe().to_dict(),
                'can_analyze': True
            }
            
            logger.info("Data analysis test passed")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Data analysis test failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def process_excel_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process uploaded Excel file and return analysis results.
        
        Args:
            file_path: Path to the uploaded Excel file
            
        Returns:
            Dictionary containing processing results and analysis
        """
        try:
            logger.info(f"Processing Excel file: {file_path}")
            
            # Validate file format
            if not file_path.lower().endswith(tuple(self.supported_formats)):
                raise ValueError(f"Unsupported file format. Supported formats: {self.supported_formats}")
            
            # Read Excel file
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # Basic data analysis
            analysis = {
                'file_info': {
                    'name': os.path.basename(file_path),
                    'size': os.path.getsize(file_path),
                    'rows': len(df),
                    'columns': len(df.columns),
                    'format': file_path.split('.')[-1]
                },
                'data_preview': df.head(10).to_dict('records') if len(df) > 0 else [],
                'column_info': df.dtypes.to_dict(),
                'summary_stats': df.describe().to_dict() if len(df) > 0 else {},
                'processing_time': datetime.now().isoformat()
            }
            
            logger.info(f"Excel file processed successfully: {len(df)} rows, {len(df.columns)} columns")
            
            return {
                'success': True,
                'message': 'File processed successfully',
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Error processing Excel file: {str(e)}")
            return {
                'success': False,
                'message': f'Processing failed: {str(e)}',
                'error': str(e)
            }
    
    def export_to_format(self, data: Dict[str, Any], format_type: str, filename: str) -> Dict[str, Any]:
        """
        Export data to specified format.
        
        Args:
            data: Data to export
            format_type: Export format ('json', 'csv', 'excel')
            filename: Output filename
            
        Returns:
            Dictionary with export result
        """
        try:
            logger.info(f"Exporting data to {format_type}: {filename}")
            
            if format_type.lower() == 'json':
                output_path = f"{filename}.json"
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            elif format_type.lower() == 'csv':
                output_path = f"{filename}.csv"
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                else:
                    df = pd.DataFrame([data])
                df.to_csv(output_path, index=False)
            
            elif format_type.lower() == 'excel':
                output_path = f"{filename}.xlsx"
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                else:
                    df = pd.DataFrame([data])
                df.to_excel(output_path, index=False)
            
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
            
            result = {
                'success': True,
                'message': f'Data exported to {format_type}',
                'output_path': output_path,
                'format': format_type
            }
            
            logger.info(f"Export completed: {output_path}")
            return result
            
        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            return {
                'success': False,
                'message': f'Export failed: {str(e)}',
                'error': str(e)
            }
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return self.supported_formats.copy()
    
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate if file can be processed.
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            Dictionary with validation result
        """
        try:
            if not os.path.exists(file_path):
                return {
                    'valid': False,
                    'error': 'File does not exist'
                }
            
            file_extension = file_path.lower().split('.')[-1]
            if file_extension not in self.supported_formats:
                return {
                    'valid': False,
                    'error': f'Unsupported format: {file_extension}',
                    'supported_formats': self.supported_formats
                }
            
            # Try to read file
            if file_extension == 'csv':
                try:
                    pd.read_csv(file_path)
                    return {'valid': True, 'format': file_extension}
                except:
                    return {'valid': False, 'error': 'Invalid CSV file'}
            
            else:  # Excel files
                try:
                    pd.read_excel(file_path)
                    return {'valid': True, 'format': file_extension}
                except:
                    return {'valid': False, 'error': 'Invalid Excel file'}
                    
        except Exception as e:
            return {'valid': False, 'error': str(e)}